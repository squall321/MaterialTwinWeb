# Fig.9(원시 f,T)와 Fig.10(이동 f')의 같은 점을 모듈러스로 짝지어 이동인자 a_T 를 되뽑고
# 원문 WLF 상수(C1=10.84, C2=58.17, Tref=16.4 C)가 ln 규약인지 log10 규약인지 수치로 가린다
import json, math
f9=json.load(open('ec_jung2019_fig9.json')); f10=json.load(open('ec_jung2019_mastercurve.json'))
A9=f9['Fig. 9(a) storage modulus G′']['series']; A10=f10['Fig. 10(a) storage modulus G′']['points']
B9=f9['Fig. 9(b) loss modulus G″']['series'];   B10=f10['Fig. 10(b) loss modulus G″']['points']

def shifts(ser9, pts10):
    out=[]
    for s in ser9:
        rs=[]
        for f,m in s['points']:
            cand=min(pts10, key=lambda p: abs(math.log10(p[1])-math.log10(m)))
            if abs(math.log10(cand[1])-math.log10(m))>0.01: continue
            rs.append(cand[0]/f)
        if rs:
            lg=[math.log10(r) for r in rs]
            out.append((s['temperature_c'], sum(lg)/len(lg), max(lg)-min(lg), len(rs)))
    return out

for name, sh in (("G'", shifts(A9,A10)), ('G"', shifts(B9,B10))):
    print(f"\n=== {name} 로 되뽑은 log10(a_T) (Tref = 16.4 °C) ===")
    print(f"{'T(°C)':>7} {'log10 aT':>10} {'계열내 산포':>10} {'n':>3}  {'WLF ln 규약':>12} {'WLF log10 규약':>14}")
    C1,C2,T0=10.84,58.17,16.4
    for T,lg,spread,n in sh:
        dT=T-T0
        ln_conv = (-C1*dT/(C2+dT))/math.log(10)   # ln(aT)=... → log10 으로 환산
        log_conv = -C1*dT/(C2+dT)                  # log10(aT)=...
        print(f"{T:7.1f} {lg:10.4f} {spread:10.4f} {n:3d}  {ln_conv:12.4f} {log_conv:14.4f}")
    # 오차 합
    e_ln=sum((lg-(-C1*(T-T0)/(C2+(T-T0)))/math.log(10))**2 for T,lg,_,_ in sh)**.5
    e_lg=sum((lg-(-C1*(T-T0)/(C2+(T-T0))))**2 for T,lg,_,_ in sh)**.5
    print(f"  잔차노름: ln 규약 {e_ln:.4f} · log10 규약 {e_lg:.4f}  →  {'ln' if e_ln<e_lg else 'log10'} 규약이 맞다")
    # 우리 데이터로 직접 WLF 적합(log10 규약 기준 C1,C2)
    import itertools
    best=None
    for c1 in [x/100 for x in range(100,3000)]:
        for c2 in [x/2 for x in range(200,3000)]:
            pass
    # 2변수 그리드는 비싸므로 선형화: 1/log10(aT) = -(C2/C1)/dT - 1/C1
    xs=[];ys=[]
    for T,lg,_,_ in sh:
        dT=T-T0
        if abs(dT)<1e-9 or abs(lg)<1e-9: continue
        xs.append(1/dT); ys.append(1/lg)
    n=len(xs); sx=sum(xs);sy=sum(ys);sxx=sum(x*x for x in xs);sxy=sum(x*y for x,y in zip(xs,ys))
    a=(n*sxy-sx*sy)/(n*sxx-sx*sx); b=(sy-a*sx)/n
    C1f=-1/b; C2f=a*C1f
    print(f"  우리 데이터 직접 적합(log10 규약): C1 = {C1f:.3f} · C2 = {C2f:.3f} K  (원문 C1/ln10 = {10.84/math.log(10):.3f})")
