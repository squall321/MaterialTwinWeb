# Doosan CCL 제품 페이지 HTML 을 표 한 줄씩 정규화해 찍는다 — <title> 로 신원부터 확인한다(57차 SD).
import re,html,glob,os,sys,json
DEST='/data/paper_patent_corpus/standards_appnotes/pcb'
def cells(tr):
    cs=[html.unescape(re.sub(r'<[^>]+>',' ',c)) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',tr,re.S)]
    return [re.sub(r'\s+',' ',c).strip() for c in cs]
def parse(p):
    s=open(p,encoding='utf-8',errors='replace').read()
    t=re.search(r'<title[^>]*>(.*?)</title>',s,re.S)
    title=html.unescape(t.group(1)).strip() if t else ''
    rows=[]
    for tb in re.findall(r'<table.*?</table>',s,re.S):
        for tr in re.findall(r'<tr.*?</tr>',tb,re.S):
            c=cells(tr)
            if any(c): rows.append(c)
    return title,rows
if __name__=='__main__':
    for p in sorted(glob.glob(DEST+'/Doosan_CCL_*_ProductPage_en_*.html')):
        slug=os.path.basename(p).split('Doosan_CCL_')[1].rsplit('_ProductPage',1)[0]
        title,rows=parse(p)
        print('#### %s | title=%s | rows=%d' % (slug,title.split(' :')[0],len(rows)))
        for c in rows: print('   '+' | '.join(c))
