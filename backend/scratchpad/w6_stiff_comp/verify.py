# 수집한 각 값이 인용 출처 원문에 '토큰 단위'로 실제 존재하고 행 라벨 문맥까지 맞는지 대조한다
import json, re, os, sys

OUT='/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/w6parts/D_stiff_comp.json'
d=json.load(open(OUT))
URL2TXT={
 'https://repository.gatech.edu/server/api/core/bitstreams/d378984a-1232-4800-9d74-95ce185f5200/content':'dl/liu2013.txt',
 'https://www.isola-group.com/wp-content/uploads/data-sheets/370hr.pdf':'dl/iso370hr.txt',
 'https://www.qdcircuits.com/uploads/admin/file/20200902/20200902191624_52530.pdf':'dl/tu933.txt',
 'https://www.isola-group.com/wp-content/uploads/data-sheets/i-speed.pdf':'dl/iso_ispeed.txt',
}
# (재료, 키, 값) -> 그 값이 실려 있어야 할 행 라벨 정규식
# 기본 문맥 + (재료명, 키) 별 예외 문맥
CTX={'mechanical.poisson_ratio':r"Poisson", 'mechanical.youngs_modulus':r"Young|E \(GPa\)|Substrate core"}
CTX_OVERRIDE={
 # Liu 2013 Table 5.7은 pdftotext가 ν 헤더 글리프를 통째로 날린다.
 # bbox로 x=288 열이 포아송비 열임을 이미 확인했으므로 행 라벨로 문맥을 건다.
 ('Organic flip-chip package substrate laminate, core + build-up layers (Liu 2013 Georgia Tech TSV dissertation, DMA Prony characterization)','mechanical.poisson_ratio', 0.2): r"Substrate core",
 ('Organic flip-chip package substrate laminate, core + build-up layers (Liu 2013 Georgia Tech TSV dissertation, DMA Prony characterization)','mechanical.poisson_ratio', 0.258): r"Build-up layer|ABF-GX13",
}

def printed_forms(v):
    for scale in (1, 1e-6, 1e-9):
        x=v*scale
        for fmt in ('%g','%.1f','%.2f','%.3f'):
            s=fmt%x
            if re.fullmatch(r'-?\d+\.?\d*', s): yield s

ok=fail=0
for m in d['materials']:
    body=open(URL2TXT[m['source']['url']],encoding='utf-8',errors='ignore').read()
    lines=body.split('\n')
    for p in m['properties']:
        forms=sorted(set(printed_forms(p['value'])), key=len, reverse=True)
        hits=[]
        for s in forms:
            tok=re.compile(r'(?<![\d.])'+re.escape(s)+r'(?![\d.])')
            for i,l in enumerate(lines):
                if tok.search(l):
                    # 같은 줄 또는 앞뒤 3줄 안에 행 라벨이 있어야 한다
                    win='\n'.join(lines[max(0,i-3):i+4])
                    ctx=CTX_OVERRIDE.get((m['match_name'],p['key'],p['value']), CTX[p['key']])
                    if re.search(ctx, win, re.I):
                        hits.append((s,i+1,l.strip()[:90])); break
            if hits: break
        if hits:
            ok+=1; s,ln,txt=hits[0]
            print('OK   %-38s %-26s %-13s "%s" @L%d :: %s'%(m['match_name'][:38],p['key'].split('.')[1],p['value'],s,ln,txt))
        else:
            fail+=1
            print('FAIL %-38s %-26s %-13s tried=%s'%(m['match_name'][:38],p['key'].split('.')[1],p['value'],forms))
print('\nverified=%d  failed=%d'%(ok,fail)); sys.exit(1 if fail else 0)
