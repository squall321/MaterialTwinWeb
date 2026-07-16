# FE 솔버 재료카드 생성 — LS-DYNA *MAT_024·*MAT_098, 단위계 전환 지원, PLAN §6.3.
from __future__ import annotations

import numpy as np

from app.fitting import johnson_cook_card_params
from app.unit_systems import UnitSystem, get_system


def poisson_from_attributes(attributes: dict | None, default: float = 0.3) -> float:
    """재료 attributes.nu가 물리적으로 유효한 등방 포아송비(0<nu<0.5)면 그 값, 아니면 기본값.

    단축 인장은 포아송비를 산출하지 못하므로 사용자가 attributes에 수동 저장한 값을
    카드의 PR 필드에 반영한다(미저장/무효 시 0.3 폴백).
    """
    nu = (attributes or {}).get("nu")
    return float(nu) if isinstance(nu, (int, float)) and not isinstance(nu, bool) \
        and 0 < float(nu) < 0.5 else default


def _resample_curve(
    ep: np.ndarray, sig: np.ndarray, n: int = 20
) -> tuple[np.ndarray, np.ndarray]:
    """소성진변형률-진응력을 단조증가 εp 기준 n점으로 재샘플(*MAT_024 곡선용)."""
    m = np.isfinite(ep) & np.isfinite(sig) & (ep >= 0) & (sig > 0)
    ep, sig = ep[m], sig[m]
    if ep.size < 2:
        return np.array([0.0]), np.array([float(sig[0]) if sig.size else 0.0])
    order = np.argsort(ep)
    ep, sig = ep[order], sig[order]
    # 중복 εp 제거(보간 안정).
    uniq, idx = np.unique(ep, return_index=True)
    ep, sig = uniq, sig[idx]
    grid = np.linspace(ep[0], ep[-1], n)
    sg = np.interp(grid, ep, sig)
    # εp=0 에서 시작하도록 앞에 항복점 삽입(중복 아니면).
    if grid[0] > 1e-9:
        grid = np.concatenate([[0.0], grid])
        sg = np.concatenate([[sg[0]], sg])
    return grid, sg


def _unit_header(u: UnitSystem) -> str:
    """카드 주석용 단위계 한 줄."""
    return f"$ 단위계: {u.label} → 응력 {u.stress_unit}, 밀도 {u.density_unit}"


def lsdyna_mat024_card(
    title: str,
    E_pa: float,
    yield_pa: float | None,
    plastic_strain: np.ndarray,
    true_stress: np.ndarray,
    mid: int = 1,
    rho: float = 7850.0,
    nu: float = 0.3,
    units: UnitSystem | str | None = None,
) -> str:
    """*MAT_PIECEWISE_LINEAR_PLASTICITY(024) + *DEFINE_CURVE 카드 문자열.

    내부 물성은 SI(Pa·kg/m³) 기준. units 단위계로 변환해 출력(기본 ton, mm, s → MPa).
    """
    u = units if isinstance(units, UnitSystem) else get_system(units)
    fs = u.f_stress
    ep, sig = _resample_curve(np.asarray(plastic_strain), np.asarray(true_stress))
    sigy = yield_pa if (yield_pa and np.isfinite(yield_pa)) else float(sig[0])
    lcid = 100

    lines: list[str] = []
    lines.append("$ MaterialTwinWeb — LS-DYNA *MAT_024 자동 생성 카드")
    lines.append(f"$ material: {title}")
    lines.append(_unit_header(u))
    lines.append("*MAT_PIECEWISE_LINEAR_PLASTICITY")
    lines.append("$#     mid        ro         e        pr      sigy      etan      fail      tdel")
    lines.append(
        f"{mid:>10}{rho * u.f_density:>10.4g}{E_pa * fs:>10.4g}{nu:>10.4g}{sigy * fs:>10.4g}"
        f"{0.0:>10.4g}{1.0e21:>10.4g}{0.0:>10.4g}"
    )
    lines.append("$#       c         p      lcss      lcsr        vp")
    lines.append(f"{0.0:>10.4g}{0.0:>10.4g}{lcid:>10}{0:>10}{0.0:>10.4g}")
    lines.append("*DEFINE_CURVE")
    lines.append("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp")
    lines.append(f"{lcid:>10}{0:>10}{1.0:>10.4g}{1.0:>10.4g}{0.0:>10.4g}{0.0:>10.4g}{0:>10}")
    lines.append("$#                a1                  o1")
    for e, s in zip(ep, sig):
        lines.append(f"{e:>20.6e}{s * fs:>20.6e}")
    lines.append("*END")
    return "\n".join(lines) + "\n"


def lsdyna_mat098_card(
    title: str,
    E_pa: float,
    yield_pa: float | None,
    plastic_strain: np.ndarray,
    true_stress: np.ndarray,
    mid: int = 1,
    rho: float = 7850.0,
    nu: float = 0.3,
    units: UnitSystem | str | None = None,
) -> str:
    """*MAT_SIMPLIFIED_JOHNSON_COOK(098) 카드. σ=(A+B·εp^n)(1+C·ln ε̇*), C=0(준정적).

    EOS 불필요한 단순화 J-C. A는 항복응력 고정, B·n은 소성경화 적합(물리값 보장).
    변형률속도 자료가 없어 C=0(율속 무관). 내부 SI → units 변환(기본 ton, mm, s).
    """
    u = units if isinstance(units, UnitSystem) else get_system(units)
    fs = u.f_stress
    ep = np.asarray(plastic_strain)
    st = np.asarray(true_stress)
    sigy = yield_pa if (yield_pa and np.isfinite(yield_pa)) else float(np.min(st[st > 0]))
    jc = johnson_cook_card_params(ep, st, sigy)
    A = jc.get("A_pa", sigy)
    B = jc.get("B_pa", 0.0)
    n = jc.get("n", 1.0)
    r2 = jc.get("r2")

    lines: list[str] = []
    lines.append("$ MaterialTwinWeb — LS-DYNA *MAT_098 (Simplified Johnson-Cook) 자동 생성")
    lines.append(f"$ material: {title}")
    lines.append(_unit_header(u))
    lines.append("$ sigma_y = A + B*eps_p^n  (C=0, 준정적·상온; A=측정 항복응력)")
    if r2 is not None:
        lines.append(f"$ 경화적합 R^2 = {r2:.4f} (A 고정, B·n 적합)")
    lines.append("*MAT_SIMPLIFIED_JOHNSON_COOK")
    lines.append("$#     mid        ro         e        pr        vp")
    lines.append(
        f"{mid:>10}{rho * u.f_density:>10.4g}{E_pa * fs:>10.4g}{nu:>10.4g}{1.0:>10.4g}"
    )
    lines.append("$#       a         b         n         c    psfail    sigmax    sigsat      epso")
    lines.append(
        f"{A * fs:>10.4g}{B * fs:>10.4g}{n:>10.4g}{0.0:>10.4g}{0.0:>10.4g}"
        f"{0.0:>10.4g}{0.0:>10.4g}{u.f_rate:>10.4g}"
    )
    lines.append("*END")
    return "\n".join(lines) + "\n"
