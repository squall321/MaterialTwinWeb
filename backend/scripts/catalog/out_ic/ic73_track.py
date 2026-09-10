# Kenner 1995 Fig.2 마스터커브 3벌을 컬럼 추적으로 뽑는다 (밴드 중심 = 곡선)
import numpy as np

curve = np.load('ic73_curvemask.npy')
H, W = curve.shape

def raw_runs(x):
    idx = np.where(curve[:, x])[0]
    out = []
    if len(idx) == 0: return out
    s = idx[0]; p = idx[0]
    for v in idx[1:]:
        if v != p + 1:
            out.append((int(s), int(p))); s = v
        p = v
    out.append((int(s), int(p))); return out

def track(x0, y0, x1):
    pts = {}
    y = float(y0); slope = 0.0; hw = 19.0
    xs = list(range(x0, x1 + 1)) if x1 >= x0 else list(range(x0, x1 - 1, -1))
    d = 1 if x1 >= x0 else -1
    for x in xs:
        pred = y + slope * d
        win = min(26.0, max(18.0, hw + 6.0))
        rr = raw_runs(x)
        sel = [(s, e) for s, e in rr if not (e < pred - win or s > pred + win)]
        if not sel:
            pts[x] = None; continue
        lo = min(s for s, e in sel); hi = max(e for s, e in sel)
        yc = (lo + hi) / 2.0
        hw = 0.6 * hw + 0.4 * ((hi - lo) / 2.0)
        step = yc - y
        if abs(step) > 6: step = np.sign(step) * 6
        slope = 0.7 * slope + 0.3 * step
        y = y + step
        pts[x] = (y, lo, hi, len(sel))
    return pts
