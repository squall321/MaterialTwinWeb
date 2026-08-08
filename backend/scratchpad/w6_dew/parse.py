# accudynetest 폴리머 표면에너지 시트 텍스트를 행 단위로 파싱하는 헬퍼
import re,sys,glob,os

MST = ['Contact angle','Critical ST','From polymer melt','Calculated','Unknown','From melt','Polymer melt']

def parse(path):
    lines=open(path,encoding='utf-8',errors='replace').read().split('\n')
    rows=[]; cur=None; section=None
    for ln in lines:
        if not ln.strip(): continue
        s=ln.strip()
        if s.startswith('Surface Energy Data') or s.startswith('Source(a)') or s.startswith('©'): continue
        # section header (ends with ':' and no mst type)
        mst=None
        for m in MST:
            idx=ln.find(m)
            if idx>0 and idx<40:
                mst=m; break
        if mst:
            src=ln[:ln.find(mst)].strip()
            rest=ln[ln.find(mst)+len(mst):]
            cur={'section':section,'source':src,'mst':mst,'data':rest.strip()}
            rows.append(cur)
        else:
            if s.endswith(':') and not s.startswith('θ') and not s.startswith('γ'):
                section=s.rstrip(':'); cur=None
            elif cur is not None:
                cur['data']+=' | '+s
            else:
                pass
    return rows

if __name__=='__main__':
    for p in sys.argv[1:]:
        name=os.path.basename(p)
        for r in parse(p):
            print(f"{name}\t{r['section'] or ''}\t{r['source']}\t{r['mst']}\t{r['data']}")
