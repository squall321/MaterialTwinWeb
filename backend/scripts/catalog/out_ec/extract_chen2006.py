# Chen 2006 Fig.6·8·10(벡터 힘-변위 곡선)에서 계열별 최대 박리력을 뽑고 축 검산 오차를 남긴다
import json
from parse_svg import parse_paths

def lsq(px, val):
    n = len(px); sx = sum(px); sy = sum(val)
    sxx = sum(t*t for t in px); sxy = sum(t*v for t, v in zip(px, val))
    a = (n*sxy - sx*sy)/(n*sxx - sx*sx); b = (sy - a*sx)/n
    res = [a*t + b - v for t, v in zip(px, val)]
    return a, b, res

def majors(subs, horiz):
    """축 경로에서 major tick 좌표를 뽑는다(첫 서브패스는 축선, 긴 tick 이 major)."""
    axis = subs[0]
    ticks = []
    for s in subs[1:]:
        (x0, y0), (x1, y1) = s[0], s[1]
        ln = abs(y1-y0) if horiz else abs(x1-x0)
        pos = x0 if horiz else y0
        ticks.append((pos, ln))
    L = max(t[1] for t in ticks)
    maj = sorted(p for p, l in ticks if l > 0.75*L)
    return maj, axis

def shape(npt):
    return {7: 'triangle', 9: 'diamond', 21: 'star'}.get(npt, 'circle' if npt > 40 else f'poly{npt}')

SPECS = {
  # page: [(name, xaxis_idx, yaxis_idx, xlabels, ylabels, series_slices, legend_slice)]
  5: [
    ('Fig. 6(a)', 1, 2, [0,.4,.8,1.2], [0,4,8,12], [(3,4,10),(10,11,17),(17,18,24),(24,25,34)], (35,43)),
    ('Fig. 6(b)', 43, 44, [0,.2,.4,.6,.8,1.0], [0,4,8,12], [(45,46,52),(52,53,60),(60,61,67),(67,68,75)], (76,84)),
    ('Fig. 6(c)', 84, 84, [0,.2,.4,.6,.8], [0,4,8,12], [(85,86,90),(90,91,95),(95,96,101),(101,102,108)], (109,117)),
  ],
  6: [
    ('Fig. 8(a)', 40, 41, [0,.2,.4,.6,.8,1.0], [0,4,8,12], [(42,43,48),(48,49,56),(56,57,62),(62,63,71)], (72,80)),
    ('Fig. 8(b)', 80, 81, [0,.2,.4,.6,.8,1.0], [0,2,4,6,8,10,12], [(82,83,88),(88,89,95),(95,96,103),(103,104,111)], (112,120)),
    ('Fig. 8(c)', 120, 121, [0,.2,.4,.6,.8], [0,2,4,6,8,10,12], [(122,123,128),(128,129,132),(132,133,138),(138,139,144)], (145,153)),
  ],
  7: [
    ('Fig. 10(a)', 24, 25, [0,.2,.4,.6,.8], [0,4,8,12], [(26,27,34),(34,35,41),(41,42,49)], (50,56)),
    ('Fig. 10(b)', 56, 57, [0,.2,.4,.6,.8], [0,2,4,6,8,10,12], [(58,59,65),(65,66,71),(71,72,77)], (78,84)),
    ('Fig. 10(c)', 84, 85, [0,.2,.4,.6,.8], [0,2,4,6,8,10,12], [(86,87,93),(93,94,101),(101,102,107)], (108,114)),
  ],
}
LEG = {'Fig. 6': ['160 °C','170 °C','180 °C','190 °C'],
       'Fig. 8': ['9.9 s','15 s','18 s','29.7 s'],
       'Fig. 10': ['0.15 MPa','0.2 MPa','0.25 MPa']}

out = []
for pg, specs in SPECS.items():
    ps = parse_paths(f'chen2006_p{pg}.svg')
    for name, xi, yi, xlab, ylab, series, legsl in specs:
        xsubs = ps[xi]['subs']; ysubs = ps[yi]['subs']
        if xi == yi:  # x·y 가 한 경로에 합쳐진 경우 — 수평/수직으로 가른다
            xs_ = [s for s in xsubs if abs(s[0][1]-s[1][1]) < 1e-6 or abs(s[0][0]-s[1][0]) > 1e-6 and abs(s[0][1]-s[1][1]) > 1e-6]
            xsubs = [s for s in ps[xi]['subs'] if abs(s[0][0]-s[1][0]) > 1e-9 or abs(s[0][1]-s[1][1]) < 1e-9]
            # 간단히: 축선 두 개(수평/수직) 기준으로 분리
            allsubs = ps[xi]['subs']
            horiz_axis = allsubs[0]
            # 두번째 축선 = 수직 축선 (길이 큰 수직 서브패스)
            vi = max(range(len(allsubs)), key=lambda k: abs(allsubs[k][0][1]-allsubs[k][1][1]))
            xsubs = allsubs[:vi]; ysubs = allsubs[vi:]
        xmaj, _ = majors(xsubs, True)
        ymaj, _ = majors(ysubs, False)
        assert len(xmaj) == len(xlab), (name, 'x', xmaj, xlab)
        assert len(ymaj) == len(ylab), (name, 'y', ymaj, ylab)
        ax, bx, rx = lsq(xmaj, xlab); ay, by, ry = lsq(ymaj, ylab)
        xfs = max(xlab)-min(xlab); yfs = max(ylab)-min(ylab)
        fig = name.split('(')[0].strip()
        legend = LEG[fig]
        # 범례 드로잉 순서 확인 — 위에서 아래로 y 내림차순
        legrows = []
        for i in range(*legsl):
            p = ps[i]
            if p['filled'] and len(p['subs']) == 3:
                npt = sum(len(s) for s in p['subs'])
                yy = sum(q[1] for s in p['subs'] for q in s)/npt
                legrows.append((yy, shape(npt)))
        legrows.sort(key=lambda t: -t[0])
        rec = dict(figure=name, x_fit=dict(slope=ax, resid_max=max(abs(r) for r in rx),
                                           resid_pct_fs=100*max(abs(r) for r in rx)/xfs),
                   y_fit=dict(slope=ay, resid_max=max(abs(r) for r in ry),
                              resid_pct_fs=100*max(abs(r) for r in ry)/yfs),
                   legend_order=[s for _, s in legrows], series=[])
        for k, (ci, m0, m1) in enumerate(series):
            pts = [q for s in ps[ci]['subs'] for q in s]
            X = [ax*q[0]+bx for q in pts]; Y = [ay*q[1]+by for q in pts]
            j = max(range(len(Y)), key=lambda t: Y[t])
            marks = []
            for i in range(m0, m1):
                p = ps[i]
                if not p['filled']: continue
                npt = sum(len(s) for s in p['subs'])
                mx = sum(q[0] for s in p['subs'] for q in s)/npt
                my = sum(q[1] for s in p['subs'] for q in s)/npt
                marks.append(dict(shape=shape(npt), x=ax*mx+bx, y=ay*my+by))
            rec['series'].append(dict(label=legend[k], marker=marks[0]['shape'] if marks else None,
                                      n_curve_pts=len(pts), x_min=min(X), x_max=max(X),
                                      peak_force_N=Y[j], peak_disp_mm=X[j],
                                      n_markers=len(marks),
                                      markers=[dict(x=round(m['x'],4), y=round(m['y'],4)) for m in marks]))
        out.append(rec)

json.dump(out, open('ec_digitized_raw.json','w'), ensure_ascii=False, indent=1)
for r in out:
    print(f"\n{r['figure']}  x검산 {r['x_fit']['resid_max']:.5f} ({r['x_fit']['resid_pct_fs']:.3f}% FS)"
          f"  y검산 {r['y_fit']['resid_max']:.5f} N ({r['y_fit']['resid_pct_fs']:.3f}% FS)  범례순 {r['legend_order']}")
    for s in r['series']:
        print(f"   {s['label']:9s} marker={s['marker']:8s} pts={s['n_curve_pts']:4d} marks={s['n_markers']:2d} "
              f"x[{s['x_min']:.3f},{s['x_max']:.3f}]  peak={s['peak_force_N']:.3f} N @ {s['peak_disp_mm']:.3f} mm")
