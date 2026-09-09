# EDL 다국어판 쌍의 9절 밀도 칸을 언어판별로 판독한다 (71차 GC)
import json,collections,os,re,glob,sys
BASE='/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/gc'
IDX='/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_ed/indexes/ellsworth_edl_sds_index.json'
meta={e['item_id']:e for e in json.load(open(IDX))['entries'] if e['topic_code']=='SDS'}
L=[r'density\s*(?:and\s*/\s*or|/|and)\s*relative\s+density', r'relative\s+density', r'density',
   r'specific\s+gravity',
   r'densidad\s*(?:y\s*/\s*o|/)\s*densidad\s+relativa', r'densidad\s+relativa', r'densidad',
   r'peso\s+espec\w+', r'gravedad\s+espec\w+',
   r'densit[ée]\s+relative', r'densit[ée]', r'masse\s+volumique',
   r'relative\s+dichte', r'dichte',
   r'densit[àa]\s+relativa', r'densit[àa]', r'peso\s+specifico',
   r'densidade\s+relativa', r'densidade',
   r'relatieve\s+dichtheid', r'dichtheid',
   r'相对密度', r'相對密度', r'密度', r'比重']
LAB='('+'|'.join(L)+')'
SKIP=re.compile(r'vapou?r|vapor|vapeur|蒸[气氣]|bulk|apparent|aparente|granel|tap(ped)?\s|packing|schutt|de\s+part[ií]cul|de\s+vapor',re.I)
EMPTYW=re.compile(r'^(no\s*data|not\s*available|not\s*determined|not\s*applicable|not\s*established|no\s*aplica|sin\s*datos|no\s*disponible|no\s*determinado|non\s*disponible|non\s*d[ée]termin|aucune|pas\s*de|nicht\s*(verf|bestimmt|zutreffend)|keine|n\.?d\.?$|n\.?a\.?$|n/a$|s\.?o\.?$|not\s*known|unknown|no\s*information|no\s*hay|dato\s*no)',re.I)
EMPTYC=re.compile(r'(无资料|无相关|不适用|没有|無資料|無相關)')
def readable(t):
    b=re.sub(r'\s','',t)
    if len(b)<1200: return False
    if len(re.findall(r'[A-Za-zÀ-ɏ一-鿿]',b))/len(b)<=0.55: return False
    # 9절 표제가 어느 언어로도 안 잡히면 텍스트층이 깨진 것으로 본다
    return bool(re.search(r'(physical\s+and\s+chemical|propiedades\s+f|propri[ée]t[ée]s\s+physi|physikalische|propriet[àa]\s+fisiche|理化性|物理.{0,4}化学)',t,re.I))
def cells(t):
    lines=t.splitlines(); out=[]
    for li,line in enumerate(lines):
        segs=[s for s in re.split(r'\s{2,}',line.strip()) if s]
        for i,s in enumerate(segs):
            s=s.lstrip(' \t\u00b7\ua78f\u2022\u25aa\u25e6*->\u2013\u2014.')
            s=re.sub(r'^\s*(?:[0-9]{1,2}(?:\.[0-9]{1,3})*|[a-z])\s*[\.\)]\s*','',s,flags=re.I)
            m=re.match(r'^\W{0,2}'+LAB+r'\s*(\([^)]{0,30}\))?\s*[:：]{0,2}\s*(.*)$',s,re.I)
            if not m: continue
            lab,paren,rest=m.group(1),(m.group(2) or ''),(m.group(3) or '').strip()
            if SKIP.search(lab+' '+paren): continue
            cand=[rest]+segs[i+1:]+[x for nl in lines[li+1:li+3] for x in re.split(r'\s{2,}',nl.strip()) if x]
            val=''
            for x in cand:
                x=x.strip().lstrip(':：').strip()
                if not x: continue
                if re.match(r'^\W{0,3}'+LAB,x,re.I) and not re.search(r'\d',x): continue
                if SKIP.search(x[:26]): break
                val=x; break
            out.append((lab.strip(),(paren+' '+val).strip()))
    return out
def verdict(t):
    if not readable(t): return ('unreadable',None)
    cs=cells(t)
    if not cs: return ('norow',None)
    for l,v in cs:
        vv=v.strip()
        if not vv or EMPTYW.match(vv) or EMPTYC.search(vv): continue
        if re.search(r'\d',vv): return ('number',(l,vv[:80]))
    return ('blank',(cs[0][0],cs[0][1][:80] or '(empty)'))
items=collections.defaultdict(dict)
for p in glob.glob(BASE+'/pairs/*.txt'):
    b=os.path.basename(p)[:-4]; item,lg=b.rsplit('_',1)
    items[item][lg]=verdict(open(p,encoding='utf-8',errors='replace').read())
res=[{'item':i,'name':meta.get(i,{}).get('name'),'publisher':meta.get(i,{}).get('publisher'),
      'langs':{k:{'state':v[0],'cell':v[1]} for k,v in La.items()}} for i,La in items.items()]
json.dump(res,open(BASE+'/pairs_scored.json','w'),ensure_ascii=False,indent=1)
st=collections.Counter(); usable=[]
for r in res:
    La=r['langs']
    if 'en' not in La: continue
    for o in [k for k in La if k!='en']:
        a,b=La['en']['state'],La[o]['state']
        if a in ('nofile','unreadable') or b in ('nofile','unreadable'): st['못 읽음 %s/%s'%(a,b)]+=1; continue
        usable.append((r,o,a,b))
print('items',len(res),'usable pairs',len(usable))
for k,v in sorted(st.items(),key=lambda x:-x[1]): print('  ',k,v)
c=collections.Counter((a=='number',b=='number') for _,_,a,b in usable)
print('\n both print %d | only-en %d | only-other %d | neither %d'%(c[(1,1)],c[(1,0)],c[(0,1)],c[(0,0)]))
print('\n=== DISAGREEMENTS ===')
for r,o,a,b in usable:
    if (a=='number')!=(b=='number'):
        print('%-7s %-24s %-30s en[%s]=%s || %s[%s]=%s'%(r['item'],(r['publisher'] or '')[:24],(r['name'] or '')[:30],a,r['langs']['en']['cell'],o,b,r['langs'][o]['cell']))
