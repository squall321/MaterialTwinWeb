# F_dew.json의 각 값이 인용 출처 원문에 실제로 문자열로 존재하는지 대조하는 검증 스크립트
import json,re,os,glob,html,subprocess,sys
OUT="/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/w6parts/F_dew.json"
d=json.load(open(OUT,encoding='utf-8'))

cache={}
def text_for(url):
    if url in cache: return cache[url]
    t=''
    m=re.search(r'polymer_surface_data/([^.]+)\.pdf',url)
    if m:
        p=f'txt/{m.group(1)}.txt'
        t=open(p,encoding='utf-8',errors='replace').read()
    elif 'PMC13164644' in url:
        t=html.unescape(re.sub('<[^>]+>',' ',open('cufoil_ed.xml',encoding='utf-8',errors='replace').read()))
    elif 'koreascience' in url:
        t=open('rafoil.txt',encoding='utf-8',errors='replace').read()
    cache[url]=re.sub(r'\s+',' ',t)
    return cache[url]

def variants(v,unit):
    s=('%g'%v)
    out={s}
    if unit=='J/m^2':
        mj=v*1000.0
        out|={'%g'%mj, '%.1f'%mj}
    if unit=='deg':
        out|={'%.1f'%v}
    return out

bad=0; ok=0
for m in d['materials']:
    url=m['source']['url']; t=text_for(url)
    if not t:
        print('NO TEXT',url); bad+=1; continue
    for p in m['properties']:
        cands=variants(p['value'],p['unit'])
        hit=[c for c in cands if c in t]
        if not hit:
            print('MISS',m['match_name'][:44],p['key'],p['value'],p['unit'],'| tried',sorted(cands),'|',url)
            bad+=1
        else:
            ok+=1
print('verified',ok,'missing',bad)

# taxonomy key check
import sqlite3
c=sqlite3.connect('/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db')
keys={r[0]:r[1] for r in c.execute("select key,si_unit from property_definition")}
names={}
for line in open('/home/koopark/claude/MaterialTwinWeb/.agent_work/targets/g_dew.txt',encoding='utf-8'):
    if line.startswith('#'): continue
    q=line.rstrip('\n').split('\t')
    if len(q)>=4: names[q[1]]=q[3]
prob=0
for m in d['materials']:
    if m['match_name'] not in names:
        print('NAME NOT IN TARGET FILE:',m['match_name']); prob+=1
    for p in m['properties']:
        if p['key'] not in keys: print('BAD KEY',p['key']); prob+=1
        elif keys[p['key']].replace('*','').replace('^','') != p['unit'].replace('*','').replace('^',''):
            print('UNIT MISMATCH',p['key'],keys[p['key']],'vs',p['unit']); prob+=1
        if p['tier']==4: print('TIER4!',m['match_name']); prob+=1
print('schema problems',prob)
