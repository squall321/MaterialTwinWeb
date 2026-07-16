# 이식 가능한 데이터 번들 export + 손실 없는 병합 import — 운영에 추가된 데이터를 보존한다.
from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app import curve_store
from app.models import (
    ConstitutiveFit,
    Material,
    ProcessedResult,
    RawCurveRef,
    Specimen,
    Test,
)

SCHEMA_VERSION = 1

# ProcessedResult에서 옮길 스칼라 필드(계산 산출물). id/test_id/computed_at 제외.
_PR_FIELDS = [
    "youngs_modulus_pa", "yield_strength_pa", "uts_pa", "uniform_elongation",
    "fracture_elongation", "reduction_of_area", "strain_hardening_n",
    "strength_coeff_k_pa", "params", "extra_metrics",
]
_SPEC_FIELDS = [
    "geometry_type", "gauge_length_m", "width_m", "thickness_m", "diameter_m",
    "area0_m2", "orientation", "standard",
]
_TEST_FIELDS = ["test_type", "strain_source", "source_format", "valid", "invalid_reason"]
_FIT_FIELDS = ["model", "params", "r2", "rmse_pa", "n_points"]


# ── 안정 식별키 ───────────────────────────────────────────────────────────────
def material_key(mat: Material) -> str:
    """재료의 안정 식별키. material_code 우선, 없으면 name(대소문자 정규화)."""
    if mat.material_code:
        return f"code:{mat.material_code}"
    return f"name:{(mat.name or '').strip().lower()}"


def _curve_bytes_hash(df: pd.DataFrame | None) -> str:
    """곡선 DataFrame의 내용 해시(컬럼 정렬·부동소수 반올림으로 결정론적)."""
    if df is None or df.empty:
        return "nocurve"
    d = df.reindex(sorted(df.columns), axis=1).round(9)
    return hashlib.sha256(d.to_csv(index=False).encode()).hexdigest()[:16]


def test_content_hash(test_type: str | None, strain_source: str | None,
                      curve_hash: str) -> str:
    """시험 식별 해시 — 유형·strain_source·곡선 내용. 재동기화 중복 방지 키."""
    payload = f"{test_type}|{strain_source}|{curve_hash}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


# ── EXPORT ────────────────────────────────────────────────────────────────────
def build_bundle(session: Session) -> tuple[dict, dict[str, bytes]]:
    """DB → (manifest dict, {parquet 파일명: bytes}). 곡선은 content-hash로 키잉."""
    curves: dict[str, bytes] = {}
    materials = []
    for mat in session.query(Material).order_by(Material.id).all():
        specs_out = []
        for sp in session.query(Specimen).filter_by(material_id=mat.id).order_by(Specimen.id).all():
            tests_out = []
            for t in session.query(Test).filter_by(specimen_id=sp.id).order_by(Test.id).all():
                try:
                    df = curve_store.read_curve(t.id)
                except (FileNotFoundError, OSError):
                    df = None
                chash = _curve_bytes_hash(df)
                curve_file = None
                if df is not None:
                    curve_file = f"curves/{chash}.parquet"
                    if curve_file not in curves:
                        buf = io.BytesIO()
                        df.to_parquet(buf, engine="pyarrow", compression="zstd")
                        curves[curve_file] = buf.getvalue()
                pr = session.query(ProcessedResult).filter_by(test_id=t.id).one_or_none()
                fits = session.query(ConstitutiveFit).filter_by(test_id=t.id).all()
                tests_out.append({
                    "content_hash": test_content_hash(t.test_type, t.strain_source, chash),
                    **{f: getattr(t, f) for f in _TEST_FIELDS},
                    "curve_file": curve_file,
                    "channels": (t.raw_curve_ref.channels if t.raw_curve_ref else None),
                    "processed_result": ({f: getattr(pr, f) for f in _PR_FIELDS} if pr else None),
                    "constitutive_fits": [{f: getattr(fi, f) for f in _FIT_FIELDS} for fi in fits],
                })
            specs_out.append({"label": sp.label,
                              **{f: getattr(sp, f) for f in _SPEC_FIELDS},
                              "tests": tests_out})
        materials.append({
            "key": material_key(mat),
            "name": mat.name, "material_code": mat.material_code,
            "category": mat.category, "description": mat.description,
            "attributes": mat.attributes, "specimens": specs_out,
        })
    manifest = {"schema_version": SCHEMA_VERSION, "n_materials": len(materials),
                "materials": materials}
    return manifest, curves


def export_bundle(session: Session, out_path: str | Path) -> dict:
    """번들을 tar.gz로 저장. 반환: 요약 통계."""
    manifest, curves = build_bundle(session)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n_tests = sum(len(s["tests"]) for m in manifest["materials"] for s in m["specimens"])
    with tarfile.open(out_path, "w:gz") as tar:
        mbytes = json.dumps(manifest, ensure_ascii=False, default=str).encode()
        info = tarfile.TarInfo("manifest.json"); info.size = len(mbytes)
        tar.addfile(info, io.BytesIO(mbytes))
        for name, data in curves.items():
            info = tarfile.TarInfo(name); info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return {"path": str(out_path), "materials": manifest["n_materials"],
            "tests": n_tests, "curves": len(curves)}


# ── IMPORT (병합) ─────────────────────────────────────────────────────────────
def _read_bundle(bundle_path: str | Path) -> tuple[dict, dict[str, bytes]]:
    with tarfile.open(bundle_path, "r:gz") as tar:
        manifest = json.loads(tar.extractfile("manifest.json").read())
        curves = {}
        for m in tar.getmembers():
            if m.name.startswith("curves/"):
                curves[m.name] = tar.extractfile(m).read()
    return manifest, curves


def _existing_test_hashes(session: Session, material_id: int) -> set[str]:
    """재료 하위 모든 시험의 content_hash 집합(중복 판정용)."""
    hashes = set()
    tests = (session.query(Test).join(Specimen)
             .filter(Specimen.material_id == material_id).all())
    for t in tests:
        try:
            df = curve_store.read_curve(t.id)
        except (FileNotFoundError, OSError):
            df = None
        hashes.add(test_content_hash(t.test_type, t.strain_source, _curve_bytes_hash(df)))
    return hashes


def _write_test(session: Session, spec: Specimen, tb: dict,
                curves: dict[str, bytes]) -> None:
    """번들의 한 시험을 새 test로 적재(곡선·물성·피팅 포함). test.id는 새로 부여."""
    test = Test(specimen_id=spec.id,
                **{f: tb.get(f) for f in _TEST_FIELDS})
    session.add(test); session.commit()  # test.id 확정.

    cf = tb.get("curve_file")
    if cf and cf in curves:
        df = pd.read_parquet(io.BytesIO(curves[cf]), engine="pyarrow")
        rel = curve_store.write_curve(test.id, df)  # 새 test.id 경로로 저장.
        session.add(RawCurveRef(test_id=test.id, storage="parquet_fs", file_path=rel,
                                n_points=int(len(df)),
                                channels=tb.get("channels") or []))
    prb = tb.get("processed_result")
    if prb:
        session.add(ProcessedResult(test_id=test.id, **{f: prb.get(f) for f in _PR_FIELDS}))
    for fb in tb.get("constitutive_fits", []):
        session.add(ConstitutiveFit(test_id=test.id, **{f: fb.get(f) for f in _FIT_FIELDS}))
    session.commit()


def import_bundle(session: Session, bundle_path: str | Path, merge: bool = True) -> dict:
    """번들을 DB에 병합 적재한다. merge=True면 기존 데이터를 절대 삭제하지 않는다.

    - 재료: 안정키(material_code/name) 일치 시 기존 재료 재사용, 없으면 생성.
    - 시험: content_hash가 이미 재료에 있으면 skip(중복), 없으면 추가.
    - 시편: 라벨 일치 시 재사용, 없으면 생성(라벨 충돌은 접미사).
    운영에서 추가된 재료·시험은 번들에 없어도 그대로 보존된다(union merge).
    """
    if not merge:
        raise NotImplementedError("현재는 병합 모드만 지원(손실 방지). merge=True 사용.")
    manifest, curves = _read_bundle(bundle_path)
    stats = {"materials_added": 0, "materials_matched": 0,
             "tests_added": 0, "tests_skipped": 0, "specimens_added": 0}

    # 기존 재료 안정키 인덱스.
    by_key = {material_key(m): m for m in session.query(Material).all()}

    for mb in manifest["materials"]:
        key = mb.get("key") or f"name:{(mb.get('name') or '').strip().lower()}"
        mat = by_key.get(key)
        if mat is None:
            mat = Material(name=mb["name"], material_code=mb.get("material_code"),
                           category=mb.get("category"), description=mb.get("description"),
                           attributes=mb.get("attributes") or {})
            session.add(mat)
            try:
                session.commit()
            except Exception:
                # material_code 충돌 등 — code 없이 재시도(이름 기반 병합으로 강등).
                session.rollback()
                mat = Material(name=mb["name"], material_code=None,
                               category=mb.get("category"), description=mb.get("description"),
                               attributes=mb.get("attributes") or {})
                session.add(mat); session.commit()
            by_key[key] = mat
            stats["materials_added"] += 1
        else:
            stats["materials_matched"] += 1

        existing_hashes = _existing_test_hashes(session, mat.id)
        # 라벨→specimen 인덱스(재사용).
        spec_by_label = {sp.label: sp for sp in
                         session.query(Specimen).filter_by(material_id=mat.id).all()}

        for sb in mb["specimens"]:
            # 이 시편의 시험 중 새로운(미보유) 것만.
            new_tests = [tb for tb in sb["tests"]
                         if tb.get("content_hash") not in existing_hashes]
            if not new_tests:
                stats["tests_skipped"] += len(sb["tests"])
                continue

            spec = spec_by_label.get(sb["label"])
            if spec is None:
                spec = _add_specimen_merge(session, mat.id, sb)
                spec_by_label[spec.label] = spec
                stats["specimens_added"] += 1

            for tb in sb["tests"]:
                if tb.get("content_hash") in existing_hashes:
                    stats["tests_skipped"] += 1
                    continue
                _write_test(session, spec, tb, curves)
                existing_hashes.add(tb.get("content_hash"))
                stats["tests_added"] += 1
    return stats


def _add_specimen_merge(session: Session, material_id: int, sb: dict) -> Specimen:
    """번들 시편을 생성. (material_id,label) UNIQUE 충돌 시 접미사로 유일화."""
    base = sb["label"]
    for attempt in range(8):
        label = base if attempt == 0 else f"{base}-{attempt + 1}"
        spec = Specimen(material_id=material_id, label=label,
                        **{f: sb.get(f) for f in _SPEC_FIELDS})
        session.add(spec)
        try:
            session.commit()
            return spec
        except Exception:
            session.rollback()
    raise RuntimeError("시편 라벨 유일화 재시도 초과")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    """python -m app.sync export <out.tar.gz> | import <bundle.tar.gz>."""
    import sys
    from app.db import SessionLocal, init_db

    if len(sys.argv) < 3 or sys.argv[1] not in ("export", "import"):
        print("사용: python -m app.sync export <out.tar.gz> | import <bundle.tar.gz>")
        raise SystemExit(2)
    cmd, path = sys.argv[1], sys.argv[2]
    init_db()
    with SessionLocal() as s:
        if cmd == "export":
            print(json.dumps(export_bundle(s, path), ensure_ascii=False))
        else:
            print(json.dumps(import_bundle(s, path, merge=True), ensure_ascii=False))


if __name__ == "__main__":
    main()
