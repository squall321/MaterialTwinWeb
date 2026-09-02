# 제품 페이지 69장에서 코어 관련 라벨(밀도·포아송비·영률·인장강도·열전도율)을 뽑아 찍는다.
# 판형이 둘이다 — 긴 판(Parameter|Condition|Test Method|Unit|Value, 빈 행도 인쇄)과
# 짧은 판(Parameter|Value|Unit|Condition|Test Method, 값 있는 행만 인쇄).
# **바로 다음 행이 라벨 없는 연장행이면 같은 라벨로 읽는다** — RAPIDON-10W 의 인장강도 180 MPa 이
# `- | IPC-TM-650 2.4.19C | MPa | 180` 한 행에만 있어서 라벨만 보면 통째로 놓친다.
import re,glob,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from ua03_parse_pages import parse, DEST
LABELS={'density':'rho','poisson':'nu',"young's modulus":'E','tensile strength':'UTS',
        'thermal conductivity':'k','specific heat':'Cp','flexural strength':'flex','storage':'storage'}
def norm(x): return re.sub(r'\s+',' ',x).strip().lower()
def _find(n):
    for i,c in enumerate(n):
        for lab,short in LABELS.items():
            if c.startswith(lab): return i,lab,short
    return None
def extract(rows):
    hdr=None
    for r in rows:
        n=[norm(c) for c in r]
        if 'parameter' in n or 'property' in n:
            i=n.index('parameter') if 'parameter' in n else n.index('property')
            hdr='short' if (i+1<len(n) and n[i+1]=='value') else 'long'
            break
    out=[]; prev=None
    for r in rows:
        n=[norm(c) for c in r]
        f=_find(n)
        if f:
            i,lab,short=f
            if hdr=='long':
                v,u,cond,tm=(r[i+4] if i+4<len(r) else ''),(r[i+3] if i+3<len(r) else ''),\
                            (r[i+1] if i+1<len(r) else ''),(r[i+2] if i+2<len(r) else '')
            else:
                v,u,cond,tm=(r[i+1] if i+1<len(r) else ''),(r[i+2] if i+2<len(r) else ''),\
                            (r[i+3] if i+3<len(r) else ''),(r[i+4] if i+4<len(r) else '')
            out.append((short,r[i],v.strip(),u.strip(),cond.strip(),tm.strip()))
            prev=(short,r[i]); continue
        # 연장행은 **바로 다음 한 행**만 인정한다(그 뒤로 끌면 Dk/Df 의 SPDR 행까지 딸려 온다).
        if prev and len(r)>=2 and (n[0]=='-' or n[0].startswith('ipc-tm') or n[0].startswith('astm')):
            out.append((prev[0],prev[1]+' (연장행)',r[-1].strip(),
                        r[-2].strip() if len(r)>=3 else '',r[0].strip(),
                        r[1].strip() if len(r)>=3 else ''))
        prev=None
    return hdr,out
if __name__=='__main__':
    for p in sorted(glob.glob(DEST+'/Doosan_CCL_*_ProductPage_en_*.html')):
        slug=os.path.basename(p).split('Doosan_CCL_')[1].rsplit('_ProductPage',1)[0]
        title,rows=parse(p)
        hdr,vals=extract(rows)
        print('#### %-18s [%s] title=%s' % (slug,hdr,title.split(' :')[0]))
        for s,lab,v,u,cond,tm in vals:
            print('    %-8s %-28s v=%-18s u=%-8s cond=%-24s tm=%s' % (s,lab,repr(v),u,cond,tm))
