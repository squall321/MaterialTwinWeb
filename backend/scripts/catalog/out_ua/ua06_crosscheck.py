# 이미 적재된 Doosan 코어 행을 제품 페이지 인쇄값과 대조한다 — 열 배정 검산이자 판 차이 탐지다(§129·615).
import sqlite3,json,sys,os,glob,re
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
sys.path.insert(0,os.path.abspath(os.path.join(HERE,'..')))
import coverage_report as cr
from ua03_parse_pages import parse, DEST
from ua04_extract_core import extract
from ua05_reconcile import SLUG_EXTRA
from collections import defaultdict
pages={}
for p in sorted(glob.glob(DEST+'/Doosan_CCL_*_ProductPage_en_*.html')):
    slug=os.path.basename(p).split('Doosan_CCL_')[1].rsplit('_ProductPage',1)[0]
    title,rows=parse(p); hdr,vals=extract(rows)
    d=defaultdict(list)
    for s,lab,v,u,cond,tm in vals: d[s].append(v)
    pages[slug]=d
def nums(v):
    return [float(x) for x in re.findall(r'\d+\.?\d*',v.replace('~',' '))]
SCALE={'rho':1000.0,'E':1e9,'nu':1.0,'UTS':1e6,'k':1.0}
KEY={'physical.density':'rho','mechanical.youngs_modulus':'E','mechanical.poisson_ratio':'nu',
     'mechanical.tensile_strength':'UTS','thermal.conductivity':'k'}
c=sqlite3.connect('file:'+cr.DB+'?mode=ro',uri=True)
bad=0; ok=0
for mid,name,attrs in c.execute("select id,name,attributes from material where name like 'Doosan%' order by name"):
    a=json.loads(attrs or "{}")
    if a.get("subsystem")!="pcb": continue
    grade=a.get('grade','')
    row=c.execute("""select s.url from property_value v join source s on s.id=v.source_id
                     where v.material_id=? group by s.id order by count(*) desc limit 1""",(mid,)).fetchone()
    url=row[0] if row else ''
    slug=url.rsplit('/',1)[-1] if url and 'Copper_Clad_Laminate/' in url else None
    if slug not in pages: slug=SLUG_EXTRA.get(grade)
    d=pages.get(slug)
    if d is None: continue
    for k,s in KEY.items():
        db=[r[0] for r in c.execute("select distinct value_num from property_value where material_id=? and property_key=?",(mid,k))]
        if not db: continue
        printed=[]
        for v in d.get(s,[]): printed += [x*SCALE[s] for x in nums(v)]
        if not printed: 
            print(f'  [PAGE-NOROW] {grade:20s} {s:4s} DB={db}'); continue
        miss=[x for x in db if not any(abs(x-p)<=max(abs(p)*0.02,1e-12) for p in printed)]
        if miss:
            bad+=1
            print(f'  [DIFF] {grade:20s} {s:4s} DB={sorted(set(round(x,6) for x in miss))} page={sorted(set(printed))}')
        else: ok+=1
print('일치 물성-재료 조합',ok,'· 어긋남',bad)
