# 69차 EB — Panasonic 자국어 총합 카탈로그(2013·2021 두 판)에서 확인한 값만 JSON 으로 낸다
import json, os

SRC2013 = {
    "kind": "datasheet",
    "title": "Panasonic 「電子回路基板材料」総合カタログ (2013) — 印刷ページ17 『特性一覧表《参考値》板厚：1.6mm（R-1515B, R-1515Sは0.8mm）、貫層耐電圧：0.2mm』 (PDF 18쪽). 열 머리글 verbatim: 試験項目 比重|比熱|熱伝導率|ポアソン比|ガラス転移温度(Tg)|熱分解温度 / 試験方法 JISK6911|DSC法|レーザーフラッシュ法|JISK7113|TMA法·DSC法·DMA法|TG/DTA法(5%減) / 処理条件 −|25℃|25℃|23±3℃ / 単位 −|J/kg℃|W/m・K|−|℃",
    "url": None,
    "publisher": "Panasonic Corporation (Electronic Materials / 電子材料事業部)",
    "year": 2013,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Panasonic_ElectronicMaterials_catalog_2013_JP_YoungsModulus_ASTM-D3039_table.pdf",
    "url_note": "industrial.panasonic.com 이 이 실행환경에서 전부 타임아웃(000)이라 원문 URL 을 재확인하지 못했다. PDF 안에 URL 문자열이 없고(암호화 PDF) XMP 에도 없다. 파일은 68차 DC 가 이미 받아 둔 것이고, 이 배치는 그 로컬 파일을 300~350 dpi 렌더로 눈 대조만 했다."
}
SRC2021 = {
    "kind": "datasheet",
    "title": "Panasonic 「電子回路基板材料」特性一覧表《参考値》 2021년판 — 印刷ページ 9·10 두 쪽. 쪽머리 verbatim: 『特性一覧表《参考値》 板厚: 1.6mm、ポアソン比: 0.8mm、ヤング率(引張りモード): 0.1mm、貫層耐電圧: 0.2mm』",
    "url": None,
    "publisher": "Panasonic Corporation (Electronic Materials / 電子材料事業部)",
    "year": 2021,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Panasonic_CircuitBoardMaterials_PropertyList_FlexModulus_YoungsModulus_Poisson_2021-03.pdf",
    "url_note": "PDF CreationDate 2021-03-08, 암호화(AES-256), 2쪽. industrial.panasonic.com 이 이 실행환경에서 전부 타임아웃이라 URL 재확인 불가. 68차 DC 가 쓴 2013 판의 '뒷 판'(DC §5-4 가 요구한 것)에 해당한다."
}

def gpa(x): return x * 1e9

mats = []

# ---------- R-1566S : 68차 DC 가 못 닫은 등급. 2021 판에만 행이 있다 ----------
mats.append({
 "match_name": "Panasonic R-1566S Halogen-Free Automotive Glass Epoxy Laminate",
 "source": SRC2021,
 "properties": [
  {"key":"mechanical.youngs_modulus","value":gpa(20.7),"unit":"Pa","method":"measured","tier":1,
   "conditions":{"test_standard":"ASTM D3039","test_mode":"tensile","test_mode_verbatim":"ヤング率（引張りモード）",
     "orientation":"warp","orientation_verbatim":"タテ","specimen_thickness_mm":0.1,
     "specimen_thickness_note":"쪽머리 verbatim 『ヤング率(引張りモード): 0.1mm』 — 이 표에서 영률만 0.1 mm 시편이다(다른 항목은 1.6 mm)",
     "temperature_note":"이 열에는 시험온도가 인쇄돼 있지 않다. 같은 표의 ポアソン比 열만 23±3℃ 를 찍는다 — 영률에 그 온도를 옮겨 붙이지 마라"},
   "notes":"2021년판 특성일람표 印刷ページ10 verbatim 행: `R-1566S  5.2  4.7  0.011  0.010  70  50  24  22  20.7  19.7  0.2`. 열 순서(머리글 verbatim) = 比誘電率 1MHz|1GHz · 誘電正接 1MHz|1GHz · 貫層耐電圧 kV/mm · 沿層耐電圧 kV · 曲げ弾性係数(JIS C 6481) タテ|ヨコ GPa · ヤング率(引張りモード)(ASTM D3039) タテ|ヨコ GPa · ポアソン比(JIS K 7161-1) 23±3℃.\n환산 — 20.7 GPa x 1e9 = 2.07e10 Pa. 검산: 2.07e10 / 1e9 = 20.7 GPa.\n**굽힘과 갈라 읽었다** — 같은 행의 曲げ弾性係数(JIS C 6481) タテ 는 24 GPa 로 이 값보다 16 % 높다. 영률 칸에는 ASTM D3039 인장 쪽을 넣었다.\n**왜 새 값인가** — 68차 DC 가 쓴 2013년판 표에는 R-1566S 행 자체가 없다(DC §4-다·§5-4). 2021년판이 DC 가 요구한 '뒷 판'이고 이 등급이 거기 처음 실렸다."},
  {"key":"mechanical.youngs_modulus","value":gpa(19.7),"unit":"Pa","method":"measured","tier":1,
   "conditions":{"test_standard":"ASTM D3039","test_mode":"tensile","test_mode_verbatim":"ヤング率（引張りモード）",
     "orientation":"fill","orientation_verbatim":"ヨコ","specimen_thickness_mm":0.1,
     "specimen_thickness_note":"쪽머리 verbatim 『ヤング率(引張りモード): 0.1mm』",
     "temperature_note":"열에 시험온도 미인쇄"},
   "notes":"같은 행 ヨコ 칸 19.7 GPa. 환산 19.7 x 1e9 = 1.97e10 Pa. 검산 1.97e10/1e9 = 19.7.\n경사(タテ 20.7)와 위사(ヨコ 19.7)를 두 행으로 갈랐다 — 평균 내지 않았다."},
  {"key":"thermal.conductivity","value":0.62,"unit":"W/(m*K)","method":"measured","tier":1,
   "conditions":{"test_method":"レーザーフラッシュ法 (laser flash)","temperature_c":25,"specimen_thickness_mm":1.6,
     "direction_note":"원문이 방향을 안 찍는다. 레이저플래시는 통상 두께방향(z)이지만 이 표는 그 말을 하지 않는다 — 방향을 지정된 값으로 쓰지 마라"},
   "notes":"2021년판 印刷ページ9 verbatim 행: `R-1566S  170  175  195  355  40  180  11~13  13~15  0.62`. 열 순서 = Tg(TMA/DSC/DMA) · 熱分解温度 TGA(5%重量減) · 熱膨張係数 厚さ方向 α1|α2 · 当社試験法 タテ α1|ヨコ α1 · 熱伝導率(レーザーフラッシュ法, 25℃, W/m・K).\n단위 그대로 W/m・K = W/(m*K). 환산 없음.\n**교차검증** — 같은 열에서 R-1755D 0.63 · R-1755E 0.55 · R-1566 0.62 · R-1766 0.38 은 2013년판 표의 값과 소수점까지 같다. 두 판이 8년 간격으로 같은 값을 찍는다."},
  {"key":"mechanical.poisson_ratio","value":0.2,"unit":"1","method":"measured","tier":1,
   "conditions":{"test_standard":"JIS K 7161-1","temperature_c":23,"temperature_tolerance_c":3,
     "temperature_verbatim":"23±3℃","specimen_thickness_mm":0.8,
     "specimen_thickness_note":"쪽머리 verbatim 『ポアソン比: 0.8mm』"},
   "notes":"2021년판 印刷ページ10 의 ポアソン比 열 = 0.2. 인쇄 자릿수가 한 자리다 — 0.20 으로 부풀려 읽지 마라.\n**현재 DB 값을 갈아탄다** — 이 재료의 포아송비는 지금 t4 클래스 중앙값 0.172 다. 이건 제조사가 그 등급에 인쇄한 t1 이다.\n2013년판은 같은 값을 JIS K7113 로 찍었고 2021년판은 JIS K 7161-1 로 찍는다(K7113 이 K7161 로 대체된 것). 값은 둘 다 0.2."}
 ]})

# ---------- 2013 판이 여는 比熱·熱伝導率 (DC §5-1 인계) ----------
G2013 = [
 ("Panasonic R-1755V / R-1650V High-Tg Low-CTE High-Reliability Glass Epoxy Laminate", "R-1755V", 910, 0.53),
 ("Panasonic R-1755M / R-1650M Mid-Tg Low-CTE High-Reliability Glass Epoxy Laminate",  "R-1755M", 930, 0.57),
 ("Panasonic R-1755D (HIPER D) High-Heat-Resistance Automotive Glass Epoxy Laminate",  "R-1755D", 900, 0.63),
 ("Panasonic R-1755E (HIPER E) High-Reliability Automotive Glass Epoxy Laminate",      "R-1755E", 930, 0.55),
 ("Panasonic R-1566 Halogen-Free Automotive Glass Epoxy Laminate",                     "R-1566",  950, 0.62),
 ("Panasonic R-1766 Standard FR-4 Automotive Glass Epoxy Laminate",                    "R-1766",  920, 0.38),
]
ROW2013 = {  # 印刷ページ17 verbatim 행 (品番 比重 比熱 熱伝導率 ポアソン比 TMA DSC DMA Td)
 "R-1755V":"R-1755V  1.96  910  0.53  0.2  165  173  190  350",
 "R-1755M":"R-1755M  2.00  930  0.57  0.2  150  153  175  355",
 "R-1755D":"R-1755D  1.98  900  0.63  0.2  154  163  185  345",
 "R-1755E":"R-1755E  1.98  930  0.55  0.2  133  133  153  370",
 "R-1566" :"R-1566   2.00  950  0.62  0.2  145  148  170  350",
 "R-1766" :"R-1766   1.91  920  0.38  0.2  140  140  150  315",
}
IN2021 = {"R-1755D":0.63, "R-1755E":0.55, "R-1566":0.62, "R-1766":0.38}  # 2021 판에도 있는 등급

for name, grade, cp, k in G2013:
    x2 = IN2021.get(grade)
    cross = (f"\n**교차검증** — 2021년판 특성일람표(印刷ページ9)도 이 등급의 熱伝導率 를 {x2} 로 찍는다. 8년 간격 두 판이 같은 값이다."
             if x2 is not None else
             f"\n**교차검증 못 했다** — {grade} 는 2021년판 특성일람표 목록에 없다(그 판은 R-1755S·R-1755D·R-1755E·R-1566·R-1766·R-1566S 만 싣는다). 2013년판 한 판만 근거다.")
    mats.append({
     "match_name": name,
     "source": SRC2013,
     "properties": [
      {"key":"thermal.specific_heat","value":float(cp),"unit":"J/(kg*K)","method":"measured","tier":1,
       "conditions":{"test_method":"DSC法 (DSC)","temperature_c":25,"specimen_thickness_mm":1.6},
       "notes":f"印刷ページ17 『特性一覧表《参考値》』 verbatim 행: `{ROW2013[grade]}`. 열 순서 = 比重(JISK6911) | 比熱(DSC法, 25℃, J/kg℃) | 熱伝導率(レーザーフラッシュ法, 25℃, W/m・K) | ポアソン比(JISK7113, 23±3℃) | Tg TMA法 | Tg DSC法 | Tg DMA法 | 熱分解温度 TG/DTA法(5%減).\n단위 — 원문 J/kg℃ 는 섭씨 '간격' 당이라 J/(kg*K) 와 수치가 같다. {cp} J/kg℃ = {cp} J/(kg*K). 환산 계수 없음.\n**열 밀림 확인** — pdftotext -layout 로 뽑은 이 행을 해당 쪽 350 dpi 렌더와 눈으로 대조했다. 比重 {ROW2013[grade].split()[1]} 이 왼쪽 첫 값이고 比熱 {cp} 이 그 오른쪽임을 그림에서 확인했다."},
      {"key":"thermal.conductivity","value":float(k),"unit":"W/(m*K)","method":"measured","tier":1,
       "conditions":{"test_method":"レーザーフラッシュ法 (laser flash)","temperature_c":25,"specimen_thickness_mm":1.6,
         "direction_note":"원문이 방향을 안 찍는다 — 방향을 지정된 값으로 쓰지 마라"},
       "notes":f"같은 행 熱伝導率 칸 = {k} W/m・K. 단위 그대로, 환산 없음.{cross}"}
     ]})


# ---------- Nan Ya NP-175FR / NP-175FTL : 68차 DC 가 §5-2 로 넘긴 칸. 문서는 이미 코퍼스에 있었다 ----------
SRC_TL = {
 "kind":"datasheet",
 "title":"Data Sheet / Datenblatt NP-175FTL, NP-175FR, NP-175FB — `Performance List / Leistungsspektrum 2/2` (파일 3쪽). 시트머리 verbatim: `Revision Date: Jan. 2021` · `SPECIFICATION SHEET  NP-175FTL, NP-175FR, NP-175FB` · `SPECIFICATION SHEET #: IPC-4101/126` · `REINFORCEMENT 1: Woven E-glass` · `RESIN SYSTEM Primary: Epoxy` · `GLASS TRANSITION (Tg): 170 °C minimum`. 값은 IPC-4101 서식 바깥의 `19. Other / weitere` 절에 있다",
 "url":"https://www.technolam.de/fileadmin/user_upload/pdf/produkt_datenblaetter/np/NP-175FTL__NP-175FR__NP-175FB.pdf",
 "publisher":"Technolam GmbH (Troisdorf, Germany) — Nan Ya 의 유럽 파트너",
 "year":2021,
 "local_path":"/data/paper_patent_corpus/standards_appnotes/pcb/Technolam_NanYa_NP-175FTL-NP-175FR-NP-175FB_Datasheet_2021-01.pdf"
}
GS_TL = ("이 시트 한 장이 NP-175FTL·NP-175FR·NP-175FB 세 등급을 함께 덮고 이 행은 세 등급을 가르지 않는다. "
 "발행처도 제조사 Nan Ya 가 아니라 유럽 파트너 Technolam 이다 — 그래서 t1 이 아니라 t2 다(68차 DC 가 같은 시트의 영률에 매긴 등급과 같다). "
 "**다만 이 값은 상용구가 아니다** — 같은 발행처의 다른 계열 시트가 서로 다른 값을 찍는다: 비열 NPG-170TL/R/B·NPG-150N `0,946` · NPG-170D `0,95` vs 이 시트 `0,91`; "
 "열전도율 NPG-170TL/R/B `0,43 / 0,39` · NPG-150N `0,42 / 0,37` · NPG-180BH `0,55 / 0,46` vs 이 시트 `0,53 / 0,46`. 계열마다 갈린 값이다.")
NOTE_TL_TAIL = ("\n**두 판 교차검증** — 같은 발행처의 `Datasheet_2018-02` 판도 `0,53 / 0,46 / 0,91 / 2,10` 을 그대로 찍는다(3년 간격 동일). "
 "가장 새 `2024-08` 판은 텍스트층이 474자뿐인 이미지 스캔이라 대조하지 못했다.\n"
 "**열 밀림 확인** — 이 쪽(파일 3/6)을 300 dpi 로 렌더해 눈으로 대조했다. 표 머리는 `Laminate Requirement | Specification <0,50mm [Specification|Property] | Specification >=0,50mm [Specification|Property] | Units metric [English] | Test Method (IPC-TM-650) | Ref. Para.` 이고, "
 "이 행들의 `Specification` 칸은 둘 다 `-` 이며 `Property` 칸에만 값이 있다 — **규격 한계가 아니라 전형값**이라는 뜻이다. 두 두께 구간의 Property 값이 서로 같다.\n"
 "**시트 하단 각주 verbatim** — `Performance List 1. to 18. follows IPC-4101 template for specification sheets and shows minimum or maximum properties expectable. This overview covers all laminate thicknesses and claddings, therefore actual values are typically better.` "
 "→ 그 min/max 단서는 **1~18 항에 걸리고**, 이 값들은 그 바깥의 `19. Other` 절이다.")

for nm in ("Nan Ya NP-175FR Dicy-Free Low-CTE FR-4 Copper Clad Laminate",
           "Nan Ya NP-175FTL Low-Transmission-Loss FR-4 Copper Clad Laminate"):
    mats.append({
     "match_name": nm,
     "source": SRC_TL,
     "properties": [
      {"key":"thermal.specific_heat","value":910.0,"unit":"J/(kg*K)","method":"measured","tier":2,
       "conditions":{"temperature_c":25,"test_standard":"not printed",
         "test_standard_note":"이 행의 `Test Method (IPC-TM-650)` 칸과 `Ref. Para.` 칸이 둘 다 `-` 다 — 원문이 시험법을 안 찍는다",
         "specimen":"두 두께 구간(`<0,50 mm` · `>=0,50 mm`)의 Property 칸이 둘 다 0,91 로 같다",
         "grade_scope":GS_TL},
       "notes":"`19. Other / weitere` 절 verbatim:\n`  Specific Heat at 25 °C               Spezifische Wärmekapzität bei 25 °C          -                0,91             -            0,91           J/g°C            -            -`\n환산 — 0,91 J/g°C 는 소수점이 유럽식 쉼표다. 0.91 J/(g·K) x 1000 g/kg = 910 J/(kg*K). 검산: 910 / 1000 = 0.91 로 되돌아온다. (℃ 는 간격 단위라 K 와 수치가 같다.)"+NOTE_TL_TAIL},
      {"key":"thermal.conductivity","value":0.53,"unit":"W/(m*K)","method":"measured","tier":2,
       "conditions":{"test_standard":"ASTM E1461","test_standard_verbatim":"ASTM-E-1461",
         "test_method":"laser flash","temperature_note":"원문이 시험온도를 안 찍는다 — 온도를 지정된 값으로 쓰지 마라",
         "direction_note":"원문이 방향을 안 찍는다","grade_scope":GS_TL},
       "notes":"`19. Other` 절 verbatim(한 물성 이름 아래 두 줄):\n`                                                                                    -               0,53            -                0,53                    ASTM-E-1461`\n`   Thermal Conductivity l                         Thermisch Leitfähigkeit l                                                                      W/mK                        3.9.1.5`\n`                                                                                    -               0,46            -                0,46                    ASTM-D-5470`\n단위 W/mK 그대로 = W/(m*K), 환산 없음. 0,53 → 0.53.\n**두 시험법을 두 행으로 갈랐다** — 같은 물성인데 레이저플래시(ASTM E1461)가 0.53, 정상법 스택(ASTM D5470)이 0.46 이다. 평균 내지 않았다."+NOTE_TL_TAIL},
      {"key":"thermal.conductivity","value":0.46,"unit":"W/(m*K)","method":"measured","tier":2,
       "conditions":{"test_standard":"ASTM D5470","test_standard_verbatim":"ASTM-D-5470",
         "test_method":"steady-state guarded stack","temperature_note":"원문이 시험온도를 안 찍는다",
         "direction_note":"ASTM D5470 은 통상 두께방향(z)이지만 원문이 그 말을 하지 않는다","grade_scope":GS_TL},
       "notes":"같은 물성의 두 번째 줄 `-  0,46  -  0,46  ASTM-D-5470`. 단위 W/mK 그대로.\nASTM E1461(0.53)과 D5470(0.46)의 차 15 % 는 두 시험법의 차이지 등급 차가 아니다 — 두 행으로 나란히 넣었다."+NOTE_TL_TAIL}
     ]})

out = {"batch":"69차 EB","materials":mats}
d = "/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_eb"
os.makedirs(d, exist_ok=True)
with open(os.path.join(d,"eb01_materials.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=1)
n=sum(len(m["properties"]) for m in mats)
print("materials",len(mats),"rows",n)
