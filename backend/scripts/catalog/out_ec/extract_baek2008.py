# Baek 2008 Fig.1 (정규화 전단완화계수 마스터커브, 150 dpi 래스터) — 삼각 마커 중심 추출
import json, math, sys
import numpy as np
from PIL import Image

SRC = ('/data/paper_patent_corpus/structured/snowball_papers/from_expert/'
       'Baek - 2008 - Effect of processing conditions on warpage of film insert molded parts/figures/figure-1.png')
D = np.asarray(Image.open(SRC).convert('L')) < 100
H, W = D.shape

def lsq(px, val):
    n=len(px);sx=sum(px);sy=sum(val);sxx=sum(t*t for t in px);sxy=sum(t*v for t,v in zip(px,val))
    a=(n*sxy-sx*sy)/(n*sxx-sx*sx);b=(sy-a*sx)/n
    return a,b,[a*t+b-v for t,v in zip(px,val)]

# 눈금 픽셀 — 자동검출로 얻은 것만 쓰고, 결측 십년눈금은 쓰지 않는다(보간하지 않는다)
PANELS = [
 dict(name='Fig. 1(a) film (PMMA/ABS laminated film)', box=(4,320,56,442),
      xpx=[136.0,247.0,302.0,357.0,412.0], xval=[1e-1,1e1,1e2,1e3,1e4],
      ypx=[17.0,75.0,133.0,248.0,306.0],   yval=[1.0,0.8,0.6,0.2,0.0]),
 dict(name='Fig. 1(b) substrate (PC/ABS blend)', box=(414,718,56,442),
      xpx=[79.0,130.0,180.0,230.0,331.0,381.0,432.0], xval=[1e-2,1e-1,1,10,1e3,1e4,1e5],
      ypx=[427.0,538.0,594.0,650.0], yval=[1.0,0.6,0.4,0.2]),
]

def components(y0,y1,x0,x1,minpix=25):
    sub=D[y0:y1,x0:x1]; seen=np.zeros(sub.shape,bool); out=[]
    for i in range(sub.shape[0]):
        for j in range(sub.shape[1]):
            if not sub[i,j] or seen[i,j]: continue
            st=[(i,j)]; seen[i,j]=True; cells=[]
            while st:
                a,b=st.pop(); cells.append((a,b))
                for da,db in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                    na,nb=a+da,b+db
                    if 0<=na<sub.shape[0] and 0<=nb<sub.shape[1] and sub[na,nb] and not seen[na,nb]:
                        seen[na,nb]=True; st.append((na,nb))
            if len(cells)>=minpix: out.append(cells)
    return [(y0+np.mean([c[0] for c in cs]), x0+np.mean([c[1] for c in cs]), len(cs)) for cs in out]

res={}
for P in PANELS:
    ax,bx,rx = lsq(P['xpx'], [math.log10(v) for v in P['xval']])
    ay,by,ry = lsq(P['ypx'], P['yval'])
    y0,y1,x0,x1 = P['box']
    comps = components(y0,y1,x0,x1)
    # 마커+연결선이 한 덩어리로 붙어 있으면 큰 성분 하나가 나온다 — 그 경우 x 열별 최소 y(위쪽 윤곽)로는 못 가른다.
    med=sorted(c[2] for c in comps)[len(comps)//2]
    drop=[c for c in comps if not (0.55*med <= c[2] <= 1.7*med)]
    comps=[c for c in comps if 0.55*med <= c[2] <= 1.7*med]   # 마커 크기에서 크게 벗어난 성분(축·라벨·겹친 마커)은 버린다
    comps.sort(key=lambda c:-c[2])
    print(f"\n{P['name']}: 마커 {len(comps)}개(버린 성분 {len(drop)}개, 크기 {[int(c[2]) for c in drop]}), 최대 {comps[0][2]}px, 중앙 {sorted(c[2] for c in comps)[len(comps)//2]}px")
    pts=[(10**(ax*cx+bx), ay*cy+by, n) for cy,cx,n in comps]
    pts.sort()
    res[P['name']]=dict(dropped_components=[[round(float(c[1]),1),round(float(c[0]),1),int(c[2])] for c in drop], x_resid_decades=max(abs(r) for r in rx), y_resid=max(abs(r) for r in ry),
                        n_components=len(comps),
                        points=[[round(a,5),round(b,4),int(n)] for a,b,n in pts])
    print(f"  x 눈금 잔차 {max(abs(r) for r in rx):.4f} decade · y 눈금 잔차 {max(abs(r) for r in ry):.5f}")
    print(f"  성분 좌표(t s, g): {[(round(a,3),round(b,3)) for a,b,_ in pts][:25]}")
json.dump(res, open('ec_baek2008_relaxation.json','w'), ensure_ascii=False, indent=1)
with open('ec_baek2008_relaxation.csv','w') as f:
    f.write('figure,time_s,normalized_relaxation_modulus,component_px\n')
    for k,v in res.items():
        for a,b,n in v['points']: f.write(f'"{k}",{a:.6g},{b:.6g},{n}\n')
