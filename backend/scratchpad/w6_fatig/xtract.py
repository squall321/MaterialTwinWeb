# PMC fullTextXML을 표 중심 평문으로 변환하는 헬퍼
import re,sys,html
from xml.etree import ElementTree as ET
def txt(e):
    return ''.join(e.itertext())
def dump(path, tables_only=False):
    raw=open(path,encoding='utf-8',errors='replace').read()
    try: root=ET.fromstring(raw)
    except Exception:
        raw2=re.sub(r'&[a-zA-Z]+;',' ',raw); root=ET.fromstring(raw2)
    out=[]
    ti=root.find('.//article-title')
    out.append('TITLE: '+(txt(ti) if ti is not None else '?'))
    for tw in root.iter('table-wrap'):
        lbl=tw.find('.//label'); cap=tw.find('.//caption')
        out.append('\n===== '+(txt(lbl) if lbl is not None else '')+' :: '+(txt(cap) if cap is not None else ''))
        for tr in tw.iter('tr'):
            cells=[' '.join(txt(c).split()) for c in tr]
            out.append(' | '.join(cells))
    if not tables_only:
        for p in root.iter('p'):
            out.append(' '.join(txt(p).split()))
    return '\n'.join(out)
if __name__=='__main__':
    print(dump(sys.argv[1], len(sys.argv)>2))
