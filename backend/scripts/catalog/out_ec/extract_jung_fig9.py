# Jung 2019 Fig.9 (온도별 G'·G" vs 주파수, 로그-로그 벡터) — 계열 폴리라인 꼭짓점 = 데이터점
import json, math, re
from parse_svg import parse_paths_abs

PS = parse_paths_abs('jung2019_p9.svg')

def lsq(px, val):
    n=len(px);sx=sum(px);sy=sum(val);sxx=sum(t*t for t in px);sxy=sum(t*v for t,v in zip(px,val))
    a=(n*sxy-sx*sy)/(n*sxx-sx*sx);b=(sy-a*sx)/n
    return a,b,[a*t+b-v for t,v in zip(px,val)]

def ticks(box, horiz, lo=1.4, hi=2.5):
    x0,x1,y0,y1=box; out=[]
    for p in PS:
        pts=[q for s in p['subs'] for q in s]
        if len(pts)!=2 or not p['sw']: continue
        (ax,ay),(bx,by)=pts; L=math.hypot(bx-ax,by-ay)
        if not (lo<=L<=hi): continue
        if horiz:
            if abs(bx-ax)>1e-6 or abs(ay-y1)>0.5 or not (x0-1<=ax<=x1+1): continue
            out.append(round(ax,3))
        else:
            if abs(by-ay)>1e-6 or abs(ax-x0)>0.5 or not (y0-1<=ay<=y1+1): continue
            out.append(round(ay,3))
    return sorted(set(out))

def scol(p):
    m=re.search(r'stroke:rgb\(([^)]*)\)', p['style']); return m.group(1) if m else None

# idx_range = 계열 폴리라인이 그려지는 인덱스 구간(축·범례보다 앞선다 — 드로잉 순서)
FRAMES = [('Fig. 9(a) storage modulus G′', (74.0,211.6,55.8,183.9), (7,97)),
          ('Fig. 9(b) loss modulus G″',   (249.1,386.6,55.8,183.9), (276,366))]
SERIES = [('0%,0%,0%','filled square',16.4),('100%,0%,0%','open circle',11.7),
          ('0%,0%,100%','filled up triangle',7.6),('100%,0%,100%','open down triangle',3.8),
          ('0%,50.196838%,0%','filled diamond',0.3),('0%,0%,50.196838%','open left triangle',-3.3),
          ('50.196838%,0%,100%','filled right triangle',-5.5)]

res={}
for fname, box, (i0,i1) in FRAMES:
    x0,x1,y0,y1=box
    xt=ticks(box,True); yt=ticks(box,False)
    ax,bx,rx=lsq(xt,[math.log10(v) for v in (0.1,1.0,10.0)])
    ay,by,ry=lsq(sorted(yt),[math.log10(v) for v in (1000.0,100.0,10.0)])
    # 계열 폴리라인 = sw 0.473, 색이 계열색, 프레임 안, 축선이 아닌 것
    poly={}
    for i,p in enumerate(PS):
        if not (i0<=i<i1): continue
        if p['sw'] is None or abs(p['sw']-0.473)>1e-3: continue
        c=scol(p)
        if c not in {s[0] for s in SERIES}: continue
        pts=[q for s in p['subs'] for q in s]
        xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
        if not (x0-1<=min(xs) and max(xs)<=x1+1 and y0-1<=min(ys) and max(ys)<=y1+1): continue
        poly.setdefault(c,[]).extend(pts)
    # 마커 윤곽(sw 0.605) — 검산용
    mk={}
    for i,p in enumerate(PS):
        if not (i0<=i<i1): continue
        if p['sw'] is None or abs(p['sw']-0.605)>1e-3: continue
        c=scol(p)
        if c not in {s[0] for s in SERIES}: continue
        pts=[q for s in p['subs'] for q in s]
        xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
        cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
        if not (x0-3<=cx<=x1+3 and y0-3<=cy<=y1+3): continue
        mk.setdefault(c,[]).append((cx,cy))
    ser=[]; devs=[]
    for c,shape,T in SERIES:
        v=[]
        for px,py in poly.get(c,[]):
            if any(abs(px-q[0])<0.2 and abs(py-q[1])<0.2 for q in v): continue
            v.append((px,py))
        v.sort()
        # 마커 검산 — 폴리라인 꼭짓점마다 가장 가까운 마커 중심과의 거리
        for px,py in v:
            d=min((math.hypot(px-a,py-b) for a,b in mk.get(c,[])), default=None)
            if d is not None: devs.append(d)
        ser.append(dict(temperature_c=T, marker=shape, color=c, n=len(v),
                        points=[[round(10**(ax*px+bx),5), round(10**(ay*py+by),4)] for px,py in v]))
    res[fname]=dict(x_ticks_px=xt,y_ticks_px=yt,
                    x_resid_decades=max(abs(r) for r in rx), y_resid_decades=max(abs(r) for r in ry),
                    marker_vs_polyline_max_pt=max(devs), series=ser,
                    n_points=sum(s['n'] for s in ser))
    print(f"\n{fname}  x잔차 {max(abs(r) for r in rx):.6f} dec · y잔차 {max(abs(r) for r in ry):.6f} dec · "
          f"폴리라인↔마커중심 최대 {max(devs):.3f} pt · 총 {sum(s['n'] for s in ser)}점")
    for s in ser:
        print(f"   {s['temperature_c']:6.1f} °C {s['marker']:22s} n={s['n']} "
              f"f {s['points'][0][0]:.4g}~{s['points'][-1][0]:.4g}  M {min(p[1] for p in s['points']):.4g}~{max(p[1] for p in s['points']):.4g} kPa")
json.dump(res, open('ec_jung2019_fig9.json','w'), ensure_ascii=False, indent=1)
with open('ec_jung2019_fig9.csv','w') as f:
    f.write('figure,temperature_c,marker,frequency_Hz,modulus_kPa\n')
    for k,v in res.items():
        for s in v['series']:
            for fq,mo in s['points']:
                f.write(f'"{k}",{s["temperature_c"]},{s["marker"]},{fq:.6g},{mo:.6g}\n')
