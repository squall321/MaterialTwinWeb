# KooRemapper material_db.json → MaterialTwin DB 시드러. 탄소성 곡선 재구성 + 점탄성 완화곡선.
from __future__ import annotations

import io
import csv
import json
from pathlib import Path

import numpy as np
from sqlalchemy.orm import Session

from app import curve_store, fitting, viscoelastic
from app.ingest import ingest_upload
from app.models import Material, ProcessedResult, RawCurveRef, Specimen, Test

# 시드용 명목 시편 치수(SI). 재구성 곡선의 절대 힘·변위 스케일용(물성엔 무관).
_W0, _T0, _L0 = 12.5e-3, 2.0e-3, 50.0e-3
_A0 = _W0 * _T0


# ── 탄소성: 진응력-소성변형률 테이블/바이리니어 → 공칭 σ-ε 재구성 ──────────────
def _hardening_points(mech: dict, cards: dict) -> tuple[np.ndarray, np.ndarray] | None:
    """진응력 σ_t(MPa) vs 소성변형률 εp 테이블을 추출/구성. 없으면 None."""
    E = mech.get("E")
    sigy = mech.get("SIGY") or mech.get("yield_stress_SIGY")
    if not E or not sigy:
        return None
    # 1) PIECEWISE EPS/ES 카드 텍스트 파싱.
    txt = ""
    if isinstance(cards, dict):
        txt = cards.get("MAT_PIECEWISE_LINEAR_PLASTICITY", "") or ""
    eps, es = _parse_eps_es(txt)
    if eps is not None and len(eps) >= 2:
        return eps, es
    # 2) 바이리니어(ETAN): σ = SIGY + ETAN·εp.
    etan = mech.get("ETAN")
    if etan and etan > 0:
        epv = np.array([0.0, 0.05, 0.12, 0.20])
        return epv, sigy + etan * epv
    # 3) 접선계수 없음 → 완만한 멱법칙 경화 가정(n=0.12).
    epv = np.array([0.0, 0.02, 0.06, 0.12, 0.20])
    K = sigy / (0.002 ** 0.12)  # σy 근처 통과
    return epv, K * np.power(np.clip(epv + 0.002, 1e-6, None), 0.12)


def _parse_eps_es(txt: str) -> tuple[np.ndarray | None, np.ndarray | None]:
    """PIECEWISE 카드에서 EPS1..8 / ES1..8 행을 뽑아 (소성변형률, 진응력) 반환."""
    if "EPS1" not in txt:
        return None, None
    lines = txt.splitlines()
    eps = es = None
    for i, ln in enumerate(lines):
        if "EPS1" in ln and i + 1 < len(lines):
            eps = [float(x) for x in lines[i + 1].split() if _isnum(x)]
        if "ES1" in ln and i + 1 < len(lines):
            es = [float(x) for x in lines[i + 1].split() if _isnum(x)]
    if not eps or not es:
        return None, None
    n = min(len(eps), len(es))
    e = np.array(eps[:n]); s = np.array(es[:n])
    # 유효점(단조 증가 소성변형률)만.
    keep = np.concatenate([[True], np.diff(e) > 1e-9])
    return e[keep], s[keep]


def _isnum(x: str) -> bool:
    try:
        float(x); return True
    except ValueError:
        return False


def reconstruct_tensile(E_mpa: float, sigy_mpa: float, eps_p: np.ndarray, sig_t: np.ndarray,
                        n: int = 600) -> tuple[np.ndarray, np.ndarray]:
    """진응력-소성변형률 경화곡선 → 공칭 응력-변형률(엔지니어링). SI 반환(strain, stress[Pa]).

    탄성: σ=E·ε (ε≤εy). 소성: 진변형률 εt=εp+σt/E, 공칭 εn=e^εt−1, σn=σt·e^−εt.
    """
    E = E_mpa * 1e6
    ey = sigy_mpa / E_mpa  # 항복 공칭변형률(≈진변형률)
    # 탄성 구간.
    e_el = np.linspace(0.0, ey, max(2, n // 6))
    s_el = E * e_el
    # 소성 구간: 소성변형률 그리드에서 진응력 보간 → 공칭 변환.
    epmax = float(min(eps_p.max(), 0.30)) if eps_p.size else 0.20
    epg = np.linspace(eps_p.min() if eps_p.size else 0.0, epmax, n - e_el.size)
    st = np.interp(epg, eps_p, sig_t) * 1e6  # Pa (진응력)
    et = epg + st / E  # 총 진변형률
    en = np.expm1(et)  # 공칭 변형률
    sn = st * np.exp(-et)  # 공칭 응력
    strain = np.concatenate([e_el, ey + en])
    stress = np.concatenate([s_el, sn])
    # 단조 정렬.
    order = np.argsort(strain)
    return strain[order], stress[order]


def _tensile_csv(strain: np.ndarray, stress_pa: np.ndarray) -> bytes:
    """공칭 σ-ε → force(kN)·disp(mm) CSV(단위행 포함). ingest 파이프라인 입력."""
    force_kN = stress_pa * _A0 / 1e3
    disp_mm = strain * _L0 * 1e3
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Time", "Force", "Displacement"])
    w.writerow(["s", "kN", "mm"])
    for i in range(len(strain)):
        w.writerow([f"{i * 0.01:.4f}", f"{force_kN[i]:.6f}", f"{disp_mm[i]:.6f}"])
    return buf.getvalue().encode()


def seed_elastoplastic(session: Session, m: dict) -> int | None:
    """탄소성 재료 1건 적재: 곡선 재구성 → 정식 ingest → 물성·피팅. 반환 test_id."""
    mech = m.get("mechanical", {})
    hp = _hardening_points(mech, m.get("cards_structural", {}))
    if hp is None:
        return None
    eps_p, sig_t = hp
    strain, stress = reconstruct_tensile(mech["E"], mech.get("SIGY") or mech.get("yield_stress_SIGY"), eps_p, sig_t)
    if strain.size < 20 or not np.all(np.isfinite(stress)):
        return None

    mat = Material(
        name=m["name"], material_code=None,  # KooRemapper tag는 유니크 아님 → 코드 미사용.
        category="metal", description=(m.get("description") or "")[:500] or None,
        attributes={"source": "KooRemapper", "tag": m.get("tag"), "mat_type": m.get("mat_type"),
                    "E_GPa": mech.get("E_GPa"), "rho_g_cm3": mech.get("rho_g_cm3"),
                    "SIGY_MPa": mech.get("SIGY") or mech.get("yield_stress_SIGY")},
    )
    session.add(mat); session.commit()
    spec = Specimen(material_id=mat.id, label="S1", geometry_type="flat",
                    gauge_length_m=_L0, width_m=_W0, thickness_m=_T0, area0_m2=_A0,
                    standard="reconstructed")
    session.add(spec); session.commit()
    spec = session.get(Specimen, spec.id)
    res = ingest_upload(session, spec, _tensile_csv(strain, stress), f"{m['name']}.csv")
    if not res.test:
        return None
    # 연질 저항복 재료(εy < 회귀창 하한)는 고정창이 소성구간에 빠져 E가 틀림 →
    # 알려진 E/SIGY로 탄성창을 계산해 재산출(재구성 시드에서만 가능한 정밀 보정).
    _fix_modulus(session, res.test.id, mech["E"], mech.get("SIGY") or mech.get("yield_stress_SIGY"))
    # 구성방정식 피팅도 계산·저장(mat 카드 도출 준비).
    _compute_fits(session, res.test.id)
    return res.test.id


def _fix_modulus(session: Session, tid: int, E_mpa: float, sigy_mpa: float | None) -> None:
    """항복변형률 εy=SIGY/E 기준으로 탄성창을 잡아 E·물성을 재산출·갱신."""
    if not E_mpa or not sigy_mpa:
        return
    from app import analysis
    ey = sigy_mpa / E_mpa
    # 탄성창: [0.15εy, 0.7εy]. εy가 충분히 크면(>0.0036) 기본창 유지.
    if ey >= 0.0036:
        return
    lo, hi = max(1e-4, 0.15 * ey), max(2e-4, 0.7 * ey)
    pr = session.query(ProcessedResult).filter_by(test_id=tid).one_or_none()
    if pr is None:
        return
    df = curve_store.read_curve(tid)
    strain = np.asarray(df["eng_strain"], dtype=float)
    stress = np.asarray(df["eng_stress_Pa"], dtype=float)
    metrics = analysis.compute_all(strain, stress, A0=None, e_range=(lo, hi))
    pr.youngs_modulus_pa = metrics["youngs_modulus_pa"]
    pr.yield_strength_pa = metrics["yield_strength_pa"]
    pr.strain_hardening_n = metrics["strain_hardening_n"]
    pr.strength_coeff_k_pa = metrics["strength_coeff_k_pa"]
    pr.params = metrics["params"].model_dump()
    session.commit()


def _compute_fits(session: Session, tid: int) -> None:
    """탄소성 test에 대해 Hollomon/Swift/Voce/JC 피팅을 계산·저장."""
    from app.models import ConstitutiveFit
    from app.routers.properties import _plastic_true
    pr = session.query(ProcessedResult).filter_by(test_id=tid).one_or_none()
    if pr is None:
        return
    df = curve_store.read_curve(tid)
    ep, st = _plastic_true(df, pr.youngs_modulus_pa)
    for r in fitting.fit_all(ep, st):
        if r.get("params") is None:
            continue
        session.add(ConstitutiveFit(test_id=tid, model=r["model"], params=r["params"],
                                    r2=r.get("r2"), rmse_pa=r.get("rmse_pa"), n_points=r.get("n_points")))
    session.commit()


# ── 점탄성: Prony(G0,GI,BETA) → 완화 영률 곡선 + Prony 피팅 저장 ──────────────
def seed_viscoelastic(session: Session, m: dict) -> int | None:
    """점탄성 재료 1건 적재: 완화곡선 생성 → Parquet 저장 → Prony 피팅 → extra_metrics."""
    mech = m.get("mechanical", {})
    G0, GI, BETA = mech.get("G0"), mech.get("GI"), mech.get("BETA")
    if not all(isinstance(v, (int, float)) for v in (G0, GI, BETA)) or BETA <= 0:
        return None
    nu = mech.get("PR", 0.45)
    rc = viscoelastic.relaxation_curve_from_lsdyna(G0, GI, BETA, nu)
    t, E_t = rc["time_s"], rc["E_pa"]
    fit = viscoelastic.fit_prony(t, E_t, n_terms=3)

    cat = m.get("category", "polymer")
    mat = Material(
        name=m["name"] or f"visco-{m.get('mat_type_id')}",
        material_code=str(m.get("tag") or "")[:100] or None,
        category=cat if cat in ("polymer", "rubber") else "polymer",
        description=(m.get("description") or f"{m.get('mat_type')} 점탄성")[:500],
        attributes={"source": "KooRemapper", "mat_type": m.get("mat_type"),
                    "prony_lsdyna": {"G0": G0, "GI": GI, "BETA": BETA, "BULK": mech.get("BULK")},
                    "E0_GPa": rc["E0_pa"] / 1e9, "Einf_GPa": rc["Einf_pa"] / 1e9, "tau_s": rc["tau_s"]},
    )
    session.add(mat); session.commit()
    spec = Specimen(material_id=mat.id, label="S1", geometry_type="flat",
                    gauge_length_m=_L0, width_m=_W0, thickness_m=_T0, area0_m2=_A0,
                    standard="relaxation")
    session.add(spec); session.commit()

    test = Test(specimen_id=spec.id, test_type="relaxation", strain_source="relaxation",
                source_format="viscoelastic", valid=True)
    session.add(test); session.commit()

    # 완화곡선을 curve_store에 저장(채널: time_s, relax_modulus_Pa).
    import pandas as pd
    df = pd.DataFrame({"time_s": t, "relax_modulus_Pa": E_t})
    rel_path = curve_store.write_curve(test.id, df)
    session.add(RawCurveRef(test_id=test.id, storage="parquet_fs", file_path=rel_path,
                            n_points=len(t), channels=[{"name": "time_s", "unit_si": "s"},
                                                       {"name": "relax_modulus_Pa", "unit_si": "Pa"}]))
    # Prony 결과를 extra_metrics에 저장(인장 필드는 null).
    pr = ProcessedResult(
        test_id=test.id, params={"schema_version": 1, "kind": "viscoelastic"},
        youngs_modulus_pa=rc["E0_pa"],  # 순간 영률 E0
        extra_metrics={"kind": "viscoelastic", "E0_pa": rc["E0_pa"], "Einf_pa": rc["Einf_pa"],
                       "tau_s": rc["tau_s"], "prony_fit": {"E_inf_pa": fit.get("E_inf_pa"),
                       "terms": fit.get("terms"), "r2": fit.get("r2"), "n_terms": fit.get("n_terms")},
                       "lsdyna_prony": {"G0": G0, "GI": GI, "BETA": BETA, "BULK": mech.get("BULK")}},
    )
    session.add(pr); session.commit()
    return test.id


# ── 오케스트레이션 ────────────────────────────────────────────────────────────
def run(session: Session, json_path: str | Path, max_elastoplastic: int = 60,
        max_viscoelastic: int = 30) -> dict:
    """DB를 채운다. 다양성 우선(스틸·알루미늄·구리·티탄 + 점탄성 테이프/고무/폴리머)."""
    d = json.loads(Path(json_path).read_text())
    mats = d["materials"]; idx = d["category_index"]

    ep_ids, vi_ids = [], []
    # 탄소성: SIGY 있는 금속 우선(다양성). 스틸·알루미늄 먼저.
    metal = [mats[str(i)] for i in idx.get("metal", [])]
    def has_yield(m): return bool(m.get("mechanical", {}).get("SIGY"))
    priority = [m for m in metal if has_yield(m)]
    # 스틸/알루미늄이 앞에 오도록 정렬.
    def rank(m):
        nm = (m["name"] or "").upper()
        if any(k in nm for k in ("SUS", "STS", "STEEL", "SPC", "STK")): return 0
        if any(k in nm for k in ("AL", "ALUM")): return 1
        return 2
    priority.sort(key=rank)

    seen = set()
    for m in priority:
        if len(ep_ids) >= max_elastoplastic: break
        if m["name"] in seen: continue
        seen.add(m["name"])
        try:
            tid = seed_elastoplastic(session, m)
            if tid: ep_ids.append(tid)
        except Exception as exc:
            session.rollback()
            print(f"  [skip ep] {m['name']}: {exc}")

    # 점탄성: G0/GI/BETA 있는 것(테이프·폴리머·고무).
    visco_cats = ["tape", "rubber", "polymer"]
    visco = []
    for c in visco_cats:
        visco += [mats[str(i)] for i in idx.get(c, [])]
    seenv = set()
    for m in visco:
        if len(vi_ids) >= max_viscoelastic: break
        mech = m.get("mechanical", {})
        if not all(k in mech for k in ("G0", "GI", "BETA")): continue
        key = m["name"] or id(m)
        if key in seenv: continue
        seenv.add(key)
        try:
            tid = seed_viscoelastic(session, m)
            if tid: vi_ids.append(tid)
        except Exception as exc:
            session.rollback()
            print(f"  [skip vi] {m.get('name')}: {exc}")

    return {"elastoplastic": len(ep_ids), "viscoelastic": len(vi_ids),
            "ep_test_ids": ep_ids, "vi_test_ids": vi_ids}


# ── CLI: python -m app.seed [json_path] ──────────────────────────────────────
def main() -> None:
    """DB를 초기화(create_all)하고 KooRemapper material_db.json으로 채운다.

    사용: MATERIALTWIN_DATA_DIR/DATABASE_URL 설정 후
          python -m app.seed [/path/to/material_db.json]
    """
    import sys
    from app.db import SessionLocal, init_db

    json_path = sys.argv[1] if len(sys.argv) > 1 else \
        "/home/koopark/claude/KooRemapper/materials/material_db.json"
    init_db()
    with SessionLocal() as s:
        r = run(s, json_path)
    print(f"적재 완료 — 탄소성 {r['elastoplastic']} · 점탄성 {r['viscoelastic']}")


if __name__ == "__main__":
    main()
