# 같은 시험상태(원시/TCT/HTHT) 패널 안에서 어떤 곡선이 다른 라벨로 재사용됐는지 전수로 잰다
import json
from parse_svg import parse_paths

def lsq(px, val):
    n=len(px);sx=sum(px);sy=sum(val);sxx=sum(t*t for t in px);sxy=sum(t*v for t,v in zip(px,val))
    a=(n*sxy-sx*sy)/(n*sxx-sx*sx); return a,(sy-a*sx)/n
def majors(subs,horiz):
    ticks=[(s[0][0] if horiz else s[0][1], abs(s[1][1]-s[0][1]) if horiz else abs(s[1][0]-s[0][0])) for s in subs[1:]]
    L=max(t[1] for t in ticks); return sorted(p for p,l in ticks if l>0.75*L)

PANELS = {  # tag: (page, xaxis, yaxis, xlab, ylab, [(curve_idx,label)])
 '6a': (5,1,2,[0,.4,.8,1.2],[0,4,8,12],[(3,'160 °C'),(10,'170 °C'),(17,'180 °C'),(24,'190 °C')]),
 '6b': (5,43,44,[0,.2,.4,.6,.8,1.],[0,4,8,12],[(45,'160 °C'),(52,'170 °C'),(60,'180 °C'),(67,'190 °C')]),
 '6c': (5,84,84,[0,.2,.4,.6,.8],[0,4,8,12],[(85,'160 °C'),(90,'170 °C'),(95,'180 °C'),(101,'190 °C')]),
 '8a': (6,40,41,[0,.2,.4,.6,.8,1.],[0,4,8,12],[(42,'9.9 s'),(48,'15 s'),(56,'18 s'),(62,'29.7 s')]),
 '8b': (6,80,81,[0,.2,.4,.6,.8,1.],[0,2,4,6,8,10,12],[(82,'9.9 s'),(88,'15 s'),(95,'18 s'),(103,'29.7 s')]),
 '8c': (6,120,121,[0,.2,.4,.6,.8],[0,2,4,6,8,10,12],[(122,'9.9 s'),(128,'15 s'),(132,'18 s'),(138,'29.7 s')]),
 '10a':(7,24,25,[0,.2,.4,.6,.8],[0,4,8,12],[(26,'0.15 MPa'),(34,'0.2 MPa'),(41,'0.25 MPa')]),
 '10b':(7,56,57,[0,.2,.4,.6,.8],[0,2,4,6,8,10,12],[(58,'0.15 MPa'),(65,'0.2 MPa'),(71,'0.25 MPa')]),
 '10c':(7,84,85,[0,.2,.4,.6,.8],[0,2,4,6,8,10,12],[(86,'0.15 MPa'),(93,'0.2 MPa'),(101,'0.25 MPa')]),
}
STATE = {'a':'original','b':'TCT 1000 h','c':'HTHT 500 h'}

_cache={}
def curves(tag):
    if tag in _cache: return _cache[tag]
    pg,xi,yi,xlab,ylab,ser = PANELS[tag]
    ps = parse_paths(f'chen2006_p{pg}.svg')
    if xi==yi:
        A=ps[xi]['subs']; vi=max(range(len(A)),key=lambda k:abs(A[k][0][1]-A[k][1][1])); xs,ys=A[:vi],A[vi:]
    else: xs,ys=ps[xi]['subs'],ps[yi]['subs']
    ax,bx=lsq(majors(xs,True),xlab); ay,by=lsq(majors(ys,False),ylab)
    res=[]
    for ci,lab in ser:
        pts=[q for s in ps[ci]['subs'] for q in s]
        res.append((lab,[(ax*q[0]+bx, ay*q[1]+by) for q in pts]))
    _cache[tag]=res; return res

def interp(c,x):
    for i in range(1,len(c)):
        if min(c[i-1][0],c[i][0])<=x<=max(c[i-1][0],c[i][0]):
            x0,y0=c[i-1];x1,y1=c[i]
            return y0 if x1==x0 else y0+(y1-y0)*(x-x0)/(x1-x0)
    return None

def rms(A,B):
    lo=max(min(p[0] for p in A),min(p[0] for p in B)); hi=min(max(p[0] for p in A),max(p[0] for p in B))
    if hi<=lo: return None
    d=[]
    for k in range(81):
        x=lo+(hi-lo)*k/80
        a=interp(A,x); b=interp(B,x)
        if a is not None and b is not None: d.append(a-b)
    return (sum(v*v for v in d)/len(d))**.5

if __name__=='__main__':
    for st in 'abc':
        tags=[t for t in PANELS if t.endswith(st)]
        items=[(t,lab,c) for t in tags for lab,c in curves(t)]
        print(f"\n===== 상태 {STATE[st]} — 계열 {len(items)}개 교차 RMS(<0.2 N = 같은 트레이스로 본다)")
        for i in range(len(items)):
            for j in range(i+1,len(items)):
                if items[i][0]==items[j][0]: continue
                r=rms(items[i][2],items[j][2])
                if r is not None and r<0.25:
                    print(f"  {items[i][0]:4s}{items[i][1]:9s} == {items[j][0]:4s}{items[j][1]:9s}  RMS {r:.4f} N")
