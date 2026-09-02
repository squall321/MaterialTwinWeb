# 43종 V5 빈칸 80개를 제품 페이지 값과 대조한다 — 채울 수 있는 칸과 부재 확정 칸을 가른다.
import sqlite3,json,sys,os,glob
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
sys.path.insert(0,os.path.abspath(os.path.join(HERE,'..')))
import coverage_report as cr
from ua03_parse_pages import parse, DEST
from ua04_extract_core import extract
from collections import defaultdict
SLUG_EXTRA={'DS-7409DJG (S)':'DS-7409DJG_S','DS-7409DJL2+':'DS-7409DJL2','DS-7409DJN+':'DS-7409DJN',
 'DS-7409DV (NT)':'DS-7409DV_NT','DS-7409DV (T)':'DS-7409DV_T','DS-7409DX (C)':'DS-7409DX_C',
 'DS-7409HG (I)':'DS-7409HG_I','DS-7409HG (KN)':'DS-7409HG_KN','DS-7409S (N)':'DS-7409S_N',
 'DS-9530':None,'DSF-900LC':'DSF-900LC','DSflex-600D':'DSflex-600D','DSflex-600UF (DS)':'DSflex-600UF_DS',
 'DSflex-600UK (SS)':'DSflex-600UK_SS','DSflex-600UY':'DSflex-600UY'}
KEY2SHORT={'physical.density':'rho','mechanical.youngs_modulus':'E','mechanical.poisson_ratio':'nu',
 'thermal.conductivity':'k','mechanical.tensile_strength':'UTS','thermal.specific_heat':'Cp',
 'thermal.expansion_linear':'CTE'}
pages={}
for p in sorted(glob.glob(DEST+'/Doosan_CCL_*_ProductPage_en_*.html')):
    slug=os.path.basename(p).split('Doosan_CCL_')[1].rsplit('_ProductPage',1)[0]
    title,rows=parse(p)
    hdr,vals=extract(rows)
    d=defaultdict(list)
    for s,lab,v,u,cond,tm in vals: d[s].append((v,u,cond,tm,lab))
    pages[slug]=(title.split(' :')[0],os.path.basename(p),d)
c=sqlite3.connect('file:'+cr.DB+'?mode=ro',uri=True)
have=defaultdict(set)
for mid,k in c.execute("select material_id,property_key from property_value"): have[mid].add(k)
res=[]
for mid,name,attrs in c.execute("select id,name,attributes from material where name like 'Doosan%'"):
    a=json.loads(attrs or "{}")
    if a.get("subsystem")!="pcb": continue
    blank=[k for k in cr.CORE7 if k not in have[mid]]
    na=a.get(cr.VERDICT_ATTR_NA); nk=set(na) if isinstance(na,dict) else set(); nall=isinstance(na,str)
    vd=a.get(cr.VERDICT_ATTR_VENDOR); vk=set(vd) if isinstance(vd,dict) else set()
    rj=a.get(cr.VERDICT_ATTR_REJECT); rk=set(rj) if isinstance(rj,dict) else set()
    free=any(k in a for k in cr.FREE_VERDICT_ATTRS)
    gu=("anonymised_code" in a or str(a.get("identification_status","")).startswith("미식별"))
    v5=[k for k in blank if not(nall or k in nk or k in vk or k in rk or gu or free)]
    if not v5: continue
    grade=a.get('grade','')
    row=c.execute("""select s.url from property_value v join source s on s.id=v.source_id
                     where v.material_id=? group by s.id order by count(*) desc limit 1""",(mid,)).fetchone()
    url=row[0] if row else ''
    slug=url.rsplit('/',1)[-1] if url and 'Copper_Clad_Laminate/' in url else None
    if slug not in pages: slug=SLUG_EXTRA.get(grade)
    pg=pages.get(slug)
    for k in v5:
        s=KEY2SHORT[k]
        if pg is None:
            res.append((mid,grade,k,'NO_PAGE','','','',''))
        else:
            title,fn,d=pg
            if s in d:
                v,u,cond,tm,lab=d[s][0]
                res.append((mid,grade,k,'FILL' if v else 'BLANK_ROW',v,u,tm,fn))
            else:
                res.append((mid,grade,k,'NO_ROW','','','',fn))
    res.append(None)
print('mid\tgrade\tkey\tstatus\tvalue\tunit\ttest_method\tfile')
for r in res:
    if r is None: continue
    print('\t'.join(str(x) for x in r))
