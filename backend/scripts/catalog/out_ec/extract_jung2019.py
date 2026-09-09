# Jung 2019 Fig.10 마스터커브(로그-로그 산점도, 벡터) 에서 마커 좌표를 뽑는다
import json, math
from parse_svg import parse_paths_abs

def lsq(px, val):
    n=len(px);sx=sum(px);sy=sum(val);sxx=sum(t*t for t in px);sxy=sum(t*v for t,v in zip(px,val))
    a=(n*sxy-sx*sy)/(n*sxx-sx*sx); b=(sy-a*sx)/n
    return a,b,[a*t+b-v for t,v in zip(px,val)]

PS = parse_paths_abs('jung2019_p10.svg')

FRAMES = {
 'Fig. 10(a) storage modulus G′': dict(
    x=[(73.35,0.1),(99.78,1.0),(126.12,10.0),(152.55,100.0),(178.93,1000.0),(205.32,10000.0)],
    y=[(179.91,10.0),(117.92,100.0),(55.88,1000.0)], box=(73.3,206.6,55.9,179.9)),
 'Fig. 10(b) loss modulus G″': dict(
    x=None, y=None, box=(248.6,381.8,55.9,179.9)),
}

def ticks_in(box, horiz, long_len=1.6):
    x0,x1,y0,y1 = box
    out=[]
    for p in PS:
        pts=[q for s in p['subs'] for q in s]
        if len(pts)!=2 or not p['sw']: continue
        (ax,ay),(bx,by)=pts
        L=math.hypot(bx-ax,by-ay)
        if L < long_len or L > 2.5: continue
        if horiz:   # x축 tick — 수직 짧은 선, y 가 축선 위
            if abs(bx-ax)>1e-6: continue
            if not (x0-1<=ax<=x1+1) or abs(ay-y1)>0.5: continue
            out.append(ax)
        else:
            if abs(by-ay)>1e-6: continue
            if not (y0-1<=ay<=y1+1) or abs(ax-x0)>0.5: continue
            out.append(ay)
    return sorted(set(round(v,3) for v in out))

# (b) 프레임 tick 자동 추출
bx = ticks_in(FRAMES['Fig. 10(b) loss modulus G″']['box'], True)
by = ticks_in(FRAMES['Fig. 10(b) loss modulus G″']['box'], False)
FRAMES['Fig. 10(b) loss modulus G″']['x']=list(zip(bx,[0.1,1.0,10.0,100.0,1000.0,10000.0]))
FRAMES['Fig. 10(b) loss modulus G″']['y']=list(zip(sorted(by,reverse=True),[10.0,100.0,1000.0]))

def markers(box):
    x0,x1,y0,y1=box
    seen=[]
    for p in PS:
        if not p['filled'] or p.get('tf_matrix',(1,))[0]!=1: continue
        pts=[q for s in p['subs'] for q in s]
        if not (4<=len(pts)<=6): continue
        xs=[q[0] for q in pts]; ys=[q[1] for q in pts]
        w=max(xs)-min(xs); h=max(ys)-min(ys)
        if not (1.2<w<3.2 and 1.2<h<3.2): continue
        cx=(max(xs)+min(xs))/2; cy=(max(ys)+min(ys))/2
        if not (x0-1.0<=cx<=x1+1.0 and y0-1.0<=cy<=y1+1.0): continue  # 프레임 경계에 걸친 마커 1개를 놓치지 않으려고 1 pt 여유
        if any(abs(cx-a)<0.3 and abs(cy-b)<0.3 for a,b in seen): continue
        seen.append((cx,cy))
    return seen

out={}
for name,F in FRAMES.items():
    xp=[t[0] for t in F['x']]; xv=[math.log10(t[1]) for t in F['x']]
    yp=[t[0] for t in F['y']]; yv=[math.log10(t[1]) for t in F['y']]
    ax,bx_,rx=lsq(xp,xv); ay,by_,ry=lsq(yp,yv)
    pts=markers(F['box'])
    data=sorted(((10**(ax*cx+bx_), 10**(ay*cy+by_)) for cx,cy in pts))
    out[name]=dict(x_ticks_px=xp, y_ticks_px=yp,
                   x_resid_decades=max(abs(r) for r in rx), y_resid_decades=max(abs(r) for r in ry),
                   n=len(data), points=[[round(a,5),round(b,4)] for a,b in data])
    print(f"\n{name}: 점 {len(data)}개")
    print(f"  x tick 잔차 최대 {max(abs(r) for r in rx):.6f} decade (= {100*(10**max(abs(r) for r in rx))-100:.4f} %)")
    print(f"  y tick 잔차 최대 {max(abs(r) for r in ry):.6f} decade (= {100*(10**max(abs(r) for r in ry))-100:.4f} %)")
    print(f"  x 범위 {data[0][0]:.4g}~{data[-1][0]:.4g} Hz | y 범위 {min(d[1] for d in data):.4g}~{max(d[1] for d in data):.4g} kPa")
json.dump(out, open('ec_jung2019_mastercurve.json','w'), ensure_ascii=False, indent=1)
with open('ec_jung2019_mastercurve.csv','w') as f:
    f.write('figure,shifted_frequency_Hz,modulus_kPa\n')
    for name,d in out.items():
        for a,b in d['points']: f.write(f'"{name}",{a:.6g},{b:.6g}\n')
