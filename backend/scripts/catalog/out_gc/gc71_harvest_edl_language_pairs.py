# EDL 다국어판 쌍을 내려받아 9절 밀도 칸의 채움 여부를 언어판별로 비교하는 수집기 (71차 GC)
import json,collections,subprocess,os,re,sys,random,concurrent.futures as cf
IDX='/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_ed/indexes/ellsworth_edl_sds_index.json'
BASE='/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/gc'
OUT=BASE+'/pairs'
E=json.load(open(IDX))['entries']
by=collections.defaultdict(dict); meta={}
for e in E:
    if e['topic_code']!='SDS': continue
    by[e['item_id']][e['lang_code']]=e; meta[e['item_id']]=e
multi=[(k,sorted(v)) for k,v in by.items() if len(v)>1]
random.seed(71); random.shuffle(multi)
N=int(sys.argv[1]) if len(sys.argv)>1 else 160
sel=multi[:N]
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'

LAB=r'(relative\s+density|density|specific\s+gravity|densidad\s+relativa|densidad|gravedad\s+espec\w+|peso\s+espec\w+|densit[ée]\s+relative|densit[ée]|masse\s+volumique|相对密度|密度|比重)'
SKIP=re.compile(r'vapou?r|vapor|de\s*vapeur|de\s*vapor|蒸[气氣]|bulk|apparent|aparente|granel|tap(ped)?\s*densit|packing|densidad\s+de\s+vapor',re.I)
EMPTY=re.compile(r'^(no\s*data|not\s*available|not\s*determined|not\s*applicable|no\s*aplica|sin\s*datos|no\s*disponible|no\s*determinado|non\s*disponible|aucune|pas\s*de|无|不适用|n\.?d\.?|n/?a|s\.?o\.?|-+|–|—|\.+|not\s*known)\b',re.I)
def readable(t):
    if len(t)<1500: return False
    body=re.sub(r'\s','',t)
    if not body: return False
    good=len(re.findall(r'[A-Za-zÀ-ɏ一-鿿]',body))
    return good/len(body)>0.55
def cells(t):
    out=[]
    for line in t.splitlines():
        for m in re.finditer(LAB+r'\s*(?:\(.{0,25}?\))?\s*[:：]?\s{0,60}([^\s].{0,60})?$|'+LAB+r'\s*(?:\(.{0,25}?\))?\s*[:：]\s*([^\n]{0,60})',line,re.I):
            pass
    # simpler: split multi-column lines on 2+ spaces, then look for "label ... value" segments
    for line in t.splitlines():
        segs=re.split(r'\s{3,}',line.strip())
        for i,s in enumerate(segs):
            m=re.match(r'^\W*'+LAB+r'\s*(\(.{0,25}?\))?\s*[:：]?\s*(.*)$',s,re.I)
            if not m: continue
            lab=m.group(1); paren=m.group(2) or ''; rest=(m.group(3) or '').strip()
            ctx=lab+' '+paren
            if SKIP.search(ctx) or SKIP.search(s[:40]): continue
            val=rest if rest else (segs[i+1].strip() if i+1<len(segs) else '')
            out.append((lab.strip(),(paren+' '+val).strip()))
    return out
def verdict(t):
    if not readable(t): return ('unreadable',None)
    cs=cells(t)
    if not cs: return ('norow',None)
    for l,v in cs:
        vv=v.strip()
        if EMPTY.match(vv) or not vv: continue
        if re.search(r'\d',vv): return ('number',(l,vv[:70]))
    return ('blank',(cs[0][0],cs[0][1][:70]))
def get(item,lang):
    p=f'{OUT}/{item}_{lang}.pdf'
    if not os.path.exists(p) or os.path.getsize(p)<3000:
        subprocess.run(['curl','-gsS','--max-time','70','-A',UA,'-o',p,
            f'https://webaps.ellsworth.com/edl/Actions/?document={item}&language={lang}&region=1'],capture_output=True)
    if not os.path.exists(p) or os.path.getsize(p)<3000: return None
    t=p[:-4]+'.txt'
    if not os.path.exists(t): subprocess.run(['pdftotext','-layout',p,t],capture_output=True)
    try: return open(t,encoding='utf-8',errors='replace').read()
    except Exception: return None
def work(args):
    item,langs=args
    r={'item':item,'name':meta[item]['name'],'publisher':meta[item]['publisher'],'langs':{}}
    for lg in langs:
        t=get(item,lg)
        if t is None: r['langs'][lg]={'state':'nofile'}; continue
        v,c=verdict(t)
        r['langs'][lg]={'state':v,'cell':c,'chars':len(t)}
    return r
res=[]
with cf.ThreadPoolExecutor(4) as ex:
    for i,r in enumerate(ex.map(work,sel)):
        res.append(r)
        if i%25==0: print(i,flush=True)
json.dump(res,open(BASE+'/pairs_result.json','w'),ensure_ascii=False,indent=1)
print('done',len(res))
