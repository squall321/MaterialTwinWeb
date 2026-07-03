# FE 솔버 재료카드 생성 — LS-DYNA *MAT_024(piecewise linear plasticity), PLAN §6.3.
from __future__ import annotations

import numpy as np


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


def lsdyna_mat024_card(
    title: str,
    E_pa: float,
    yield_pa: float | None,
    plastic_strain: np.ndarray,
    true_stress: np.ndarray,
    mid: int = 1,
    rho: float = 7850.0,
    nu: float = 0.3,
) -> str:
    """*MAT_PIECEWISE_LINEAR_PLASTICITY(024) + *DEFINE_CURVE 카드 문자열.

    단위계는 SI(kg, m, s, Pa) 기준 예시. 실제 해석 단위계에 맞춰 조정 필요.
    """
    ep, sig = _resample_curve(np.asarray(plastic_strain), np.asarray(true_stress))
    sigy = yield_pa if (yield_pa and np.isfinite(yield_pa)) else float(sig[0])
    lcid = 100

    lines: list[str] = []
    lines.append("$ MaterialTwinWeb — LS-DYNA *MAT_024 자동 생성 카드")
    lines.append(f"$ material: {title}")
    lines.append("$ 단위계: SI(kg, m, s, Pa). 해석 단위계에 맞춰 확인 필요.")
    lines.append("*MAT_PIECEWISE_LINEAR_PLASTICITY")
    lines.append("$#     mid        ro         e        pr      sigy      etan      fail      tdel")
    lines.append(
        f"{mid:>10}{rho:>10.4g}{E_pa:>10.4g}{nu:>10.4g}{sigy:>10.4g}"
        f"{0.0:>10.4g}{1.0e21:>10.4g}{0.0:>10.4g}"
    )
    lines.append("$#       c         p      lcss      lcsr        vp")
    lines.append(f"{0.0:>10.4g}{0.0:>10.4g}{lcid:>10}{0:>10}{0.0:>10.4g}")
    lines.append("*DEFINE_CURVE")
    lines.append("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp")
    lines.append(f"{lcid:>10}{0:>10}{1.0:>10.4g}{1.0:>10.4g}{0.0:>10.4g}{0.0:>10.4g}{0:>10}")
    lines.append("$#                a1                  o1")
    for e, s in zip(ep, sig):
        lines.append(f"{e:>20.6e}{s:>20.6e}")
    lines.append("*END")
    return "\n".join(lines) + "\n"
