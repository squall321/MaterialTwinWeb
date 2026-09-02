# 재조정 결과에서 적재 JSON(값 11행)과 판정 JSON(43종 73칸)을 만든다.
import csv,json,os,sys,re
HERE=os.path.dirname(os.path.abspath(__file__))
BASE='https://www.doosanelectromaterials.com/en/product/Copper_Clad_Laminate/'
CORPUS='/data/paper_patent_corpus/standards_appnotes/pcb/'
TDS_TITLE=('Doosan Corporation Electro-Materials — Copper Clad Laminate (CCL) '
           'Technical Data Sheet, all products (ver. 2024.09.30, v9)')
# TDS v9 [Mechanical] 시트의 등급이 실린 쪽 — 400 dpi 렌더로 전수 확인했다.
P3="DS-7402 DS-7402M DS-7402BS (DF) DS-7402BS (DFM) DS-7402LC DS-8402HL DS-8402H BS (DFL) DS-8502LC DS-8502SQ DS-8502SQN DSR-1000 DSF-900LC DSF-900SQ DST-9000 DST-9000S DST-9000HT".split('|')
P3=["DS-7402","DS-7402M","DS-7402BS (DF)","DS-7402BS (DFM)","DS-7402LC","DS-8402HL","DS-8402H BS (DFL)",
    "DS-8502LC","DS-8502SQ","DS-8502SQN","DSR-1000","DSF-900LC","DSF-900SQ","DST-9000","DST-9000S","DST-9000HT",
    "DSflex-600","DSflex-600P","DSflex-600U","DSflex-600D","DSflex-600UY","DSflex-600UF (DS)",
    "DSflex-600UK (SS)","DSflex-900"]
COL={'physical.density':'`Density` (g/cm3)',
     'mechanical.poisson_ratio':'`Poisson Ratio`',
     'mechanical.youngs_modulus':"`Young's Modulus` (GPa · IPC-TM-650 2.4.18.3)",
     'mechanical.tensile_strength':'`Tensile Strength` 두 하위열(IPC-TM-650 2.4.18.3 · 2.4.19C, 둘 다 MPa)',
     'thermal.conductivity':'`Thermal Conductivity` 두 열(ASTM E 1461 · ASTM D 5470)'}
rows=list(csv.DictReader(open(os.path.join(HERE,'ua05_reconcile.tsv'),encoding='utf-8'),delimiter='\t'))
by={}
for r in rows: by.setdefault((r['mid'],r['grade']),[]).append(r)

# ── 판정 ────────────────────────────────────────────────────────────────────
verdicts=[]; cells=0
for (mid,grade),rs in by.items():
    absent={}
    for r in rs:
        if r['status']=='FILL': continue
        k=r['key']; f=r['file']
        sheet='[Thermal Properties]' if k=='thermal.conductivity' else '[Mechanical Properties]'
        pg=('p.1~2' if k=='thermal.conductivity' else ('p.3' if grade in P3 else 'p.4'))
        if r['status']=='NO_PAGE':
            page_says=(f'제품 페이지가 존재하지 않는다 — 슬러그 `DS-9530` 이 en·kr 둘 다 500 이고 '
                       f'이 사이트는 없는 슬러그에 500 을 준다(57차 SD). 열 문서는 TDS v9 뿐이다.')
        elif r['status']=='BLANK_ROW':
            page_says=(f'2026-09-02 에 받은 제품 페이지 `{f}` 는 그 행을 **인쇄하되 값 칸이 비어 있다**'
                       f'(긴 판형은 값 없는 행도 라벨·단위·시험법까지 찍는다).')
        else:
            page_says=(f'2026-09-02 에 받은 제품 페이지 `{f}` 에는 **그 행 자체가 없다**'
                       f'(짧은 판형은 값 있는 행만 찍는다).')
        absent[k]=(f'전제품 TDS v9(2024-09-30) {sheet} 시트 {pg} 의 `{grade}` 행에서 {COL[k]} 칸이 비어 있다 '
                   f'— 400 dpi 렌더와 `pdftotext -bbox-layout` 열좌표로 둘 다 확인했다(§603·606). '
                   f'{page_says} 두 문서를 다 열고 확정한 구조적 부재다(§601·127). '
                   f'[59차 UA]')
        cells+=1
    if absent:
        verdicts.append({"material_id":int(mid),"name":grade,
                         "core_absent_from_vendor_sheet":absent})
print('판정 재료',len(verdicts),'· 칸',cells)
json.dump({"batch":"59차 UA — Doosan CCL 코어 빈칸 부재 확정",
           "verdicts":verdicts},
          open(os.path.join(HERE,'ua11_doosan_core_verdicts.json'),'w',encoding='utf-8'),
          ensure_ascii=False,indent=1)

# ── 값 ──────────────────────────────────────────────────────────────────────
PAGE={'DS-7409DJL2+':'DS-7409DJL2','DS-7409DJN+':'DS-7409DJN','DS-7409DX (C)':'DS-7409DX_C'}
FILE={'DS-7409DJL2+':'Doosan_CCL_DS-7409DJL2_ProductPage_en_2026-09-02.html',
      'DS-7409DJN+':'Doosan_CCL_DS-7409DJN_ProductPage_en_2026-09-02.html',
      'DS-7409DX (C)':'Doosan_CCL_DS-7409DX_C_ProductPage_en_2026-09-02.html'}
TITLESELF={'DS-7409DJL2+':'DS-7409DJL2+','DS-7409DJN+':'DS-7409DJN+','DS-7409DX (C)':'DS-7409D (XC)'}
MAT={'DS-7409DJL2+':'Doosan DS-7409DJL2+ Copper Clad Laminate',
     'DS-7409DJN+':'Doosan DS-7409DJN+ Copper Clad Laminate',
     'DS-7409DX (C)':'Doosan DS-7409DX (C) Copper Clad Laminate'}
VALS={  # 등급 → [(키, 인쇄문자열, 단위환산배수, SI단위, 조건틀)]
 'DS-7409DJL2+':[('mechanical.youngs_modulus','25',1e9,'Pa'),('mechanical.poisson_ratio','0.16~0.18',1.0,'1')],
 'DS-7409DJN+':[('physical.density','1.53',1000.0,'kg/m^3'),
                ('mechanical.youngs_modulus','24~25',1e9,'Pa'),
                ('mechanical.poisson_ratio','0.16~0.18',1.0,'1')],
 'DS-7409DX (C)':[('mechanical.youngs_modulus','24',1e9,'Pa'),('mechanical.poisson_ratio','0.16~0.18',1.0,'1')],
}
DIRNOTE=('미기재 — 벤더가 축 라벨 없이 한 칸만 인쇄한다(IPC-TM-650 2.4.18.3). '
         'CCL 은 이방성이지만 이 시트는 warp/fill 을 가르지 않는다.')
mats=[]
for grade,items in VALS.items():
    src={"kind":"datasheet",
         "title":f"Doosan Corporation Electro-Materials — {grade} CCL(Copper Clad Laminate) General Properties (제품 페이지)",
         "url":BASE+PAGE[grade],
         "publisher":"Doosan Corporation Electro-Materials",
         "year":2026,
         "local_path":CORPUS+FILE[grade]}
    props=[]
    for key,printed,scale,unit in items:
        nums=[float(x) for x in printed.split('~')]
        base_note=(f"제품 페이지 `{FILE[grade]}`(2026-09-02 수신) 표 verbatim. "
                   f"**전제품 TDS v9(2024-09-30) [Mechanical Properties] 시트 p.4 의 `{grade}` 행은 이 칸이 비어 있다** "
                   f"— 400 dpi 렌더로 확인했다. 등급마다 문서 층이 다르다는 §601 의 재현이고, "
                   f"이번에는 **TDS v9 안에 행이 있는 등급**에서 났다(57차 RC 는 TDS 밖 15등급에서 냈다). "
                   f"[신원 확인] 페이지 `<title>` 이 `{TITLESELF[grade]}` 다(§438 — 이 사이트는 없는 슬러그에 500 을 준다).")
        if key=='mechanical.youngs_modulus':
            base_note+=(" [방향] 벤더가 축을 안 찍어 `direction` 에 미기재임을 명시했다 — "
                        "이 카탈로그의 Doosan 영률 기존 행 전부가 같은 열에서 왔다(§612 — 한 재료·한 열의 규약을 가르지 않는다).")
        for i,v in enumerate(nums):
            cond={}
            if key=='mechanical.youngs_modulus':
                cond={"conditioning":"As received","test_standard":"IPC-TM-650 2.4.18.3",
                      "grade":grade,"direction":DIRNOTE}
            elif key=='physical.density':
                cond={"grade":grade}
            else:
                cond={"grade":grade}
            note=base_note
            if len(nums)==2:
                cond["bound"]="lower" if i==0 else "upper"
                note+=(f" 원문이 구간 `{printed}` 으로 인쇄해 하한·상한을 별개 행으로 갈랐다(§76) — 중앙값을 만들지 않았다.")
            props.append({"key":key,"value":round(v*scale,10),"unit":unit,
                          "method":"measured","tier":1,"conditions":cond,"notes":note})
    mats.append({"match_name":MAT[grade],"source":src,"properties":props})
json.dump({"materials":mats},open(os.path.join(HERE,'ua10_doosan_page_values.json'),'w',encoding='utf-8'),
          ensure_ascii=False,indent=1)
print('값 재료',len(mats),'· 행',sum(len(m['properties']) for m in mats))
