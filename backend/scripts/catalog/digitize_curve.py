#!/usr/bin/env python
# 논문·데이터시트의 곡선 그래프 이미지 → 좌표 추출(디지타이즈). σ-ε 실측 곡선 등록용.
#
# 사용:
#   digitize_curve.py chart.png --x0 0 --y0 0 --x1 0.3 --y1 500 \
#       --px0 80 --py0 520 --px1 900 --py1 40 [--color "#1f77b4"] [--tol 60] [--n 60]
#
#   (--px*/--py*) 는 축 눈금의 픽셀 좌표. --probe 로 이미지 정보와 색 후보를 먼저 확인한다.
#
# 원리: 지정 색과 가까운 픽셀만 곡선으로 보고, x 픽셀열마다 y 중앙값을 취해 단조 곡선을 만든 뒤
# 축 캘리브레이션(픽셀↔데이터 선형/로그)으로 실좌표로 변환한다.
from __future__ import annotations

import argparse
import sys

import numpy as np


def hex2rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def probe(img: np.ndarray, top: int = 12) -> None:
    """이미지 크기와 자주 나오는 색(배경·축 제외 후보)을 보여준다."""
    h, w = img.shape[:2]
    print(f"· 이미지 {w}x{h}px", file=sys.stderr)
    flat = img.reshape(-1, 3)
    # 무채색(배경·격자·축·글자) 제외 — 채도가 있는 색이 곡선일 가능성이 높다.
    mx = flat.max(axis=1).astype(int)
    mn = flat.min(axis=1).astype(int)
    chroma = mx - mn
    cand = flat[chroma > 40]
    if cand.size == 0:
        print("  (유채색 픽셀 없음 — 흑백 그래프면 --color 000000 --tol 80 시도)", file=sys.stderr)
        return
    q = (cand // 24 * 24)
    uniq, cnt = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-cnt)[:top]
    print("  곡선 색 후보(빈도순):", file=sys.stderr)
    for i in order:
        r, g, b = uniq[i]
        print(f"    #{r:02x}{g:02x}{b:02x}  {cnt[i]}px", file=sys.stderr)


def digitize(img: np.ndarray, color: tuple[int, int, int], tol: float,
             px0: int, py0: int, px1: int, py1: int,
             x0: float, y0: float, x1: float, y1: float,
             logx: bool, logy: bool, n_out: int) -> tuple[np.ndarray, np.ndarray]:
    d = np.linalg.norm(img.astype(float) - np.array(color, dtype=float), axis=2)
    mask = d < tol
    if mask.sum() < 20:
        raise SystemExit(f"✗ 색 일치 픽셀이 너무 적음({mask.sum()}). --color/--tol 조정 필요.")
    cols = np.where(mask.any(axis=0))[0]
    xs_px, ys_px = [], []
    for c in cols:
        rows = np.where(mask[:, c])[0]
        xs_px.append(c)
        ys_px.append(np.median(rows))          # 선 두께 → 중앙값으로 1점화
    xs_px = np.asarray(xs_px, float)
    ys_px = np.asarray(ys_px, float)

    def lin(p, p_a, p_b, v_a, v_b, log):
        t = (p - p_a) / (p_b - p_a)
        if log:
            return 10 ** (np.log10(v_a) + t * (np.log10(v_b) - np.log10(v_a)))
        return v_a + t * (v_b - v_a)

    X = lin(xs_px, px0, px1, x0, x1, logx)
    Y = lin(ys_px, py0, py1, y0, y1, logy)
    o = np.argsort(X)
    X, Y = X[o], Y[o]
    # 균일 격자로 재샘플(중복 x 제거 후).
    uq, idx = np.unique(np.round(X, 10), return_index=True)
    X, Y = uq, Y[idx]
    grid = np.linspace(X.min(), X.max(), n_out)
    return grid, np.interp(grid, X, Y)


def main() -> int:
    ap = argparse.ArgumentParser(description="곡선 그래프 이미지 → 좌표 디지타이즈")
    ap.add_argument("image")
    ap.add_argument("--probe", action="store_true", help="이미지 크기·색 후보만 출력")
    ap.add_argument("--color", default="#1f77b4", help="곡선 색(hex)")
    ap.add_argument("--tol", type=float, default=60.0, help="색 허용 거리")
    for k in ("px0", "py0", "px1", "py1"):
        ap.add_argument(f"--{k}", type=float, help="축 기준점의 픽셀 좌표")
    for k in ("x0", "y0", "x1", "y1"):
        ap.add_argument(f"--{k}", type=float, help="축 기준점의 데이터 값")
    ap.add_argument("--logx", action="store_true")
    ap.add_argument("--logy", action="store_true")
    ap.add_argument("--n", type=int, default=60, help="출력 점 수")
    ap.add_argument("--csv", help="CSV 저장 경로")
    a = ap.parse_args()

    from PIL import Image
    img = np.asarray(Image.open(a.image).convert("RGB"))

    if a.probe:
        probe(img)
        return 0
    need = [a.px0, a.py0, a.px1, a.py1, a.x0, a.y0, a.x1, a.y1]
    if any(v is None for v in need):
        raise SystemExit("✗ 축 캘리브레이션(--px0/py0/px1/py1, --x0/y0/x1/y1)이 모두 필요합니다. "
                         "--probe 로 먼저 좌표를 확인하세요.")
    X, Y = digitize(img, hex2rgb(a.color), a.tol,
                    a.px0, a.py0, a.px1, a.py1, a.x0, a.y0, a.x1, a.y1,
                    a.logx, a.logy, a.n)
    print(f"· {len(X)}점 / x {X.min():.4g}~{X.max():.4g} / y {Y.min():.4g}~{Y.max():.4g}", file=sys.stderr)
    lines = [f"{x:.6g},{y:.6g}" for x, y in zip(X, Y)]
    if a.csv:
        with open(a.csv, "w") as f:
            f.write("x,y\n" + "\n".join(lines) + "\n")
        print(f"· 저장: {a.csv}", file=sys.stderr)
    else:
        print("x,y")
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
