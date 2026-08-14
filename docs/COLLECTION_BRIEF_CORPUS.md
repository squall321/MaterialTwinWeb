# 로컬 논문 코퍼스 수집 브리프

`docs/COLLECTION_BRIEF.md`(정본)의 **코퍼스 전용 부록**이다. 규칙 1~7과 tier 규약은 정본에 있고,
여기에는 `/data/paper_patent_corpus` 에서만 겪는 함정과 도구 사용법을 적는다.

> **이 파일은 저장소에 있다.** 14~17차 파동은 이 내용을 세션 스크래치패드에 두었다가
> 세션이 끊기면서 통째로 잃었다. 파동이 얻은 함정 지도는 반드시 저장소에 남겨라.

---

## 이 코퍼스가 다른 점

지금까지 파동은 웹에서 원문을 구하느라 IP 차단·reCAPTCHA·403·페이월과 싸웠다.
**이번엔 디스크에 전문이 있다.** `/data/paper_patent_corpus/structured` 에 고유 논문 16,007편의
마크다운 전문이 있다(표 71% 보존). 네트워크를 먼저 두드리지 마라 —
**코퍼스를 먼저 다 훑고**, 거기서 못 찾은 것만 웹으로 간다.

원본 PDF는 `structured` **밖 병렬 트리**에 있다.

```
structured/cae_papers/10_underfill_stress/<논문>/<논문>.md   ← docling 추출본
          cae_papers/10_underfill_stress/<논문>.pdf          ← 원본
```

---

## 도구

```bash
cd /home/koopark/claude/MaterialTwinWeb/backend

# 문서 찾기(FTS5)
python3 scripts/catalog/corpus_index.py search '<FTS5 질의>' -n 20 [-d materials_papers]

# 질의로 좁힌 뒤 정규식이 걸린 줄을 앞뒤 문맥과 함께 — 값을 옮기기 전 필수
python3 scripts/catalog/corpus_index.py near '<질의>' -r '<정규식>' -n 8 -c 2

# 물성표를 가진 논문만, 적중 물성 수 순으로 (색인에 구워 둬 즉시 끝난다)
python3 scripts/catalog/corpus_index.py tables -m 2 -n 60 [-d cae_papers] [-k conductivity]

# 논문 제목으로 DOI 회수 (catalog.csv → document.docling.json)
python3 scripts/catalog/corpus_index.py doi "<논문 제목>"

# 색인 재생성(코퍼스가 바뀌었을 때만)
python3 scripts/catalog/corpus_index.py build   # FTS
python3 scripts/catalog/corpus_index.py scan    # 물성표
```

`near` 로 **원문 문장을 눈으로 본 다음에만 값을 옮겨라.** 검색 적중만 보고 넣으면
표의 인접 열을 그대로 오독한다(여러 파동에서 실제로 그랬다).

---

## 0. `grep` 은 반드시 `-a` 를 붙여라 (최우선)

**코퍼스 md가 `file` 기준 binary로 판정된다.** 제어문자가 섞여 있어 `grep` 이 매치를
**조용히 버린다.** 실제로 `grep -n "activation energy" Pickett2009.md` 가 0건을 냈는데
그 파일에 8군데 있었다. 정찰 배치가 이 함정으로 **"표 0개"·"표가 잘렸다" 두 건을 오판**해
갈래 하나를 통째로 버릴 뻔했다.

`grep -a` / `grep -ari` / `grep -ac`. 예외 없다.
`corpus_index.py`(파이썬 read)는 이 문제가 없다 — **둘의 결과가 어긋나면 grep을 의심해라.**

## 1. 물성표를 먼저 찾아라 — 문장을 뒤지지 마라

14차가 희귀 주제(UV 투과·가수분해 kinetics·오존)를 문장으로 뒤지다 **16,007편에서 106행**밖에
못 캤다. 15차가 표적을 "정의는 있는데 값이 거의 없는 물성"으로 바꾸자 **하루 830행**이 됐다.

`tables` 는 한 표 안에 **라벨·단위·숫자가 같이 있는** 논문만 골라 낸다.
"modulus라는 단어가 본문에 있는 논문"이 아니라 **"물성 숫자가 표로 실린 논문"**이 나온다.

**수율의 정체** — 수백 행을 내는 논문은 예외 없이 **파라미터 격자**를 싣는다.
온도 × 율속 × 노화시점, 조성 시리즈, 경화도 스윕. 그런 주제를 먼저 골라라.
(17차 실측: 논문 96편이 2,018행을 냈는데 **상위 7편이 절반**을 냈다.)

## 2. DOI는 웹에 묻지 말고 코퍼스에서 되찾아라

`corpus_index.py doi` 가 `catalog.csv`(7,788건) → 없으면 그 논문 폴더의
`document.docling.json` 에서 뽑는다. **출처에 DOI를 꼭 채워라** — 안 채우면 무결성 검사에 걸린다.

IEEE/ASME **학회논문은 PDF에 DOI가 안 박혀 있어** 이 경로가 실패한다. 그때만 Crossref를 써라.

```bash
curl -s -H 'User-Agent: MaterialTwin/1.0 (mailto:mxcaegroup@gmail.com)' \
 "https://api.crossref.org/works?query.bibliographic=<제목>&rows=3&select=DOI,title,type"
```

**제목이 앞 40자라도 일치하는지 확인하고 넣어라.** 비슷한 제목의 다른 논문이 1위로 온다.

## 3. **FEA 입력표의 값은 실측이 아닐 수 있다**

해석 논문의 `Table 1. Material properties` 는 **저자가 해석을 돌리려고 모아 놓은 입력값**이다.
이걸 옮기면 **우리 tier4 가정을 남의 tier1으로 세탁하는 것**이 된다 — 근거만 바뀌고 값은 그대로다.

판별법.
- 포아송비가 0.3 / 0.35 / 0.33처럼 관용값이고 유효숫자가 2자리면 의심해라.
- 같은 표의 다른 물성에는 출처 각주가 있는데 그 행만 없으면 가정이다.
- 논문이 그 물성을 **측정했다고 방법절에 적었는지** 확인해라. 안 적었으면 tier3 이하다.
- **측정 방법이 적힌 값만 tier1이다** — 나노인덴테이션·DMA·인장시험·레이저플래시·TMA·DSC 등.
- 캡션의 `[15]`, `Parameters used in ... model`, `based on limited data`, `idealized from`,
  `provided by the manufacturers`, `a compilation of properties` 는 전부 2차 인용 신호다.

## 4. 같은 논문을 여러 재료에 쓸 때 `source` 를 글자 단위로 똑같이 적어라

인제스트가 재료 항목마다 출처 행을 새로 만든다. 제목이 한 글자라도 다르면 중복 행이 생긴다
(14차에 Bernstein 하나가 6행이 됐다). 같은 논문이면 `source` 딕셔너리를 **복사해서** 써라.

## 5. **부재를 선언하기 전에 질의를 의심해라**

`grep -a` 함정보다 **질의 설계 실패가 오판을 더 많이 냈다.**

- **비열** — `"specific heat" AND "DSC"` 로 물어 3편이 나오자 "약함"으로 판정했다.
  곁다리 AND를 빼니 **118편**이었다. 질의 하나가 결과를 **40배** 눌렀다.
- **유리 압축층 깊이** — 카탈로그 용어 `DOL` 로만 물어 "부재"로 적었다.
  업계 표준어 **`"case depth"`** 로 물으니 15편 중 값 있는 것 9편이었다.

**"없다"고 쓰기 전에 동의어 2~3개로 다시 물어라.** `AND` 를 덧붙일수록 모수가 줄어든다 —
**좁히는 것은 검색이 아니라 눈으로 해라.**

## 6. 포아송비는 표적에서 내렸다

tier4가 327칸이지만 **채워도 실익이 없다.** 코퍼스의 ν는 대부분 3번 함정에 해당한다.
근거만 tier1으로 바뀌고 숫자는 0.3 그대로다. **지표만 좋아지고 카탈로그는 나아지지 않는다.**

예외 — **측정법이 명시된 것**은 넣어라(초음파 속도법, ASTM C1259 임펄스 가진, 스트레인게이지).
18차에 Denry·Wiesner·Chowdhury가 SD까지 붙은 실측 ν를 줬고 값도 0.275/0.250/0.266처럼 관용값이 아니었다.

## 7. `tables/` 사이드카는 무시해도 된다 (확인 끝났다)

논문별 `tables/table-N.md` 사이드카가 **28,966개** 있는데 FTS 색인에는 안 들어 있다
(파일명이 전부 같아 제목 중복 제거에 뭉개진다). **재조사하지 마라** —
무작위 157개를 본문과 글자 단위로 대조해 **157개 전부 본문에도 있음**을 확인했다.
다만 사이드카는 **표 캡션을 함께 담아** 본문에서 캡션이 표와 떨어져 있을 때 참고 가치가 있다.

## 8. 코퍼스에 없다고 **확정된** 것 — 다시 찾지 마라

`grep -a` 전수로 교차검증했다.

- **동적증가계수(DIF)** — `"dynamic increase factor"` 전수 0건. 용어 자체가 없다.
- **Cowper-Symonds** — 4편 중 값 있는 것 1편(솔더). tier4 98칸 중 96칸은 못 채운다.
- **Johnson-Cook C** — 12편이 언급하나 계수표는 0편.
- **오존** — `ozone resistance`·`ISO 1431`·`D1149`·`antiozonant` 전부 0건.
- **UV 차단 OCA** — 논문·특허 전수에서 0편.
- **METGLAS·나노결정 FeSiB·분말코어 피로계수**, **커버레이 물성**, **IGZO 기계물성**,
  **LCP 열물성**, **ScAlN 전 물성**, **Gorilla/UTG 열물성**, **Parylene 열물성 실측** — 전부 0.
- **솔더/IMC 응집영역** — 후보 4편이 전부 벌크 UTF 대입 또는 남의 K_IC 역산이다.
- **불소수지 RF 적층판 S-N** — J-Stage 疲労 표제 18,750건 전수에 불소수지 0건.

## 9. **지수 부호가 추출에서 죽는다** (`-a` 다음으로 자주 걸린다)

md·docling 추출에서 `×` 와 `−` 가 제어문자로 바뀌거나 사라진다.
- `'3.17 \x02 10 \x00 8'` — 원래 `3.17 × 10⁻⁸`
- `'9.02e6'` — 부호 문자가 **아예 사라졌다**. 원래 `9.02e-6`
- `'2070C'` = 207 °C, `'(@250C)'` = @25 °C — 도(°) 기호가 `0` 이 된다
- `'0.18 6 0.008'` — `±` 가 `6` 이 된다

**복원 규율 — 추측하지 말고 근거를 만들어라.**
- 같은 표·같은 논문의 **주지의 값**으로 문자 대응을 확정해라
  (실리콘 CTE 셀 `'2.8 \x02 10 \x00 6'` → `\x02`=×, `\x00`=− 확정).
- **물리적 불가능성**으로 갈라라 (`9.02e+6 mm²/s = 9.02 m²/s` 는 존재하지 않는다).
- **본문 서술과 대소 방향**을 대조해라 ("C가 가장 빠르다" → 부호가 정해진다).
- **인쇄된 다른 값으로 재현**해 봐라 (ρ·Cp·α 가 인쇄된 k 와 2% 이내로 맞는 것은 음의 지수뿐).

근거를 못 만들면 **그 값을 버려라.** 자릿수를 우리가 정하면 규칙 1 위반이다.

## 10. 해석 입력표를 판별한 실제 수법

- **같은 논문 안에서 열을 대조해라.** An 2011은 계면 트랙션 표의 E 열이 솔더 **벌크** E 열과
  글자 그대로 같았다 — 계면값이 아니라 벌크값을 옮겨 적은 것이다.
- **표 안에 주지 물성이 있으면 그것으로 표 전체를 검산해라.** Zenner 2008은 같은 표의
  구리 밀도가 5300 kg/m³ 였고(실제 8960), Noh 2018은 Cu 열전도율이 120 W/m·K 였다(실제 400).
  **둘 다 표 전체를 폐기했다.**
- **카탈로그의 기존 tier4 추정과 소수점까지 같으면 같은 조상에서 왔다.**
  Parylene C CTE 35 ppm/°C 가 우리 tier4 3.5e-5 와 정확히 같았다 — 넣지 마라.
- **E/G = 2(1+ν) 가 정확히 성립하면 역산이다.** Darveaux 1992의 유명한 솔더 탄성계수가
  전 행에서 E/G = 2.7 = 2(1+0.35) 을 만족하고, 원문이 *"Assuming a Poisson's ratio of 0.35"* 라 밝힌다.

## 11. 학회논문 DOI는 Crossref로 (2번 절 참조)

## 12. md가 잃은 것은 PDF에서 되찾을 수 있다

```bash
base=$(basename "<논문폴더>")
find /data/paper_patent_corpus -maxdepth 3 -name "$base.pdf"
pdftotext -layout "<pdf>" - | sed -n '400,460p'
pdftotext -layout "<pdf>" - | grep -naiE "Table 4|creep rate"
pdftotext -f 7 -l 8 -layout "<pdf>" -
```

(pdfplumber·pymupdf는 없다. `pdftotext` 만 있다.)

17차 G1이 이 방법으로 **1,201행**을 되찾았다 — Chowdhury 크리프율 48칸, Springer Prony 부록 955행,
Darveaux 1992 비탄성 상수, Fan/Yang 단위·행 라벨.

**md와 PDF가 어긋나면 PDF를 믿되 둘 다 notes에 적어라** — "md는 X로 추출됐으나 PDF 원문은 Y".
그림 안 곡선은 여전히 규칙 3이다. **표와 캡션은 대부분 나온다.**

## 13. **그림 안에 인쇄된 파라미터 상자는 규칙 3이 아니다**

규칙 3은 **곡선에서 좌표를 읽는 것**을 막는다. 축 눈금과 스캔 해상도가 유효숫자를 정하므로
읽으면 그 자릿수를 우리가 만든 것이 된다.

**그림 안에 저자가 타이핑해 넣은 파라미터 상자는 인쇄된 텍스트다.** `pdftotext -layout` 이 뽑는다.
17차에 Sadeghinia Fig.14의 `C1= 19.5 / C2=107.4 / TgDMA [C]= 132 / H [kJ/mol]= 187` 이
그렇게 복구됐고, 상자의 `TgDMA = 132` 가 같은 논문 Table 3과 일치해 상자 전체가 교차검증됐다.

**쓸 때 지킬 것.**
- notes에 **PDF 원문 문자열을 verbatim으로** 적고 "그림 안 상자"임을 명시해라.
- **상자 안의 다른 값 하나를 본문·표와 대조해 상자 자체를 검증해라.** 검증 없이 쓰지 마라.
- 축 라벨에서 읽은 **단위**는 값이 아니라 물리량의 정체다 — 허용하되 근거를 적어라.
  더 나은 방법은 **인쇄된 식의 차원**으로 확정하는 것이다(G1이 Chowdhury에 그렇게 했다).
- 곡선 위의 점을 읽는 것은 **여전히 금지다.**

## 14. `corpus_index.py tables` 의 한계 둘

**(가) 출처를 보지 않는다.** 라벨·단위·숫자가 한 표에 있으면 물성표로 센다.
그래서 **문헌 비교표와 해석 입력표가 상위에 올라온다.** 17차에 "표 밀도 1위"로 지목한
Yao 2003은 각주가 `Material data from Minerals Technologies Inc.` 인 벤더 시트 전재였다.
**스캐너 순위는 후보 목록이지 근거가 아니다.** 열어서 방법절을 봐라.

**(나) `_SIG` 에 정의된 물성만 찾는다.** 현재 23종 —
youngs_modulus · poisson_ratio · density · expansion_linear · conductivity · specific_heat ·
tensile_strength · yield_strength · elongation_at_break · dielectric_constant ·
dissipation_factor · glass_transition · refractive_index · resistivity_volume · transmittance ·
fracture_toughness · hardness · weibull_modulus · contact_angle_water · surface_energy ·
viscosity · interface_strength · flexural_strength.
**여기 없는 물성은 `tables` 로 못 찾는다 — "표 0편"을 부재로 읽지 마라.** `near` 로 따로 물어라.

## 15. **`catalog.csv` 의 DOI는 틀릴 수 있다**

Darveaux 1992 `Constitutive relations for tin-based solder joints` 의 DOI를
`10.1016/0026-2714(94)90180-5` 로 적어 놓았는데, 그건 **한 쪽짜리 Microelectronics Reliability
공지문**이다. 정답은 `10.1109/33.206925` 다.

**넣기 전에 최소한 이것을 봐라.**
- **출판사 접두어가 학회·저널과 맞는가.** IEEE 논문에 `10.1016/`(Elsevier)이면 의심해라.
- **연도가 맞는가.** 1992년 논문에 `(94)` 가 든 DOI는 다른 문헌이다.
- 의심되면 Crossref로 DOI를 직접 조회해 **제목을 대조**해라.

## 16. Prony 완화시간의 상한은 1e21이다

인제스트 범위검사가 `prony_relaxation_time` 을 1e16 s로 막고 있었는데,
**TTS로 20 decade를 덮는 급수는 1e17~1e19 s 항을 정상적으로 포함한다**(Springer 2020·Chiu 2018).
17차에 31항이 잘려 급수 꼬리가 사라질 뻔했다.
**완화시간은 물리적 완화시간이 아니라 마스터커브를 덮는 피팅 항이다** — 세트가 온전해야 쓸 수 있다.

## 17. 단위가 인쇄되지 않는 분야 관행이 있다

- **언더필 2차 크리프율** — `cae_papers/10_underfill_stress` 전수에서 단위를 인쇄한 논문이 0편이다.
  **인쇄된 식의 차원**으로 확정해라(`ε_cr = … + K₄t`, ε 무차원, t 초 → K₄는 1/s).
- **CHS/CME(흡습팽창)** — Fan 2008·Yang 2016 둘 다 단위가 없다.
  **같은 표의 Csat 단위와 맞춰 dimensional check** 로 확정하고, 결과가 카탈로그 기존 대역
  (1.7~4.0e-4 m³/kg)에 드는지 확인해라.
- 근거를 만들지 못하면 넣지 마라.

## 18. 단위 오식은 **같은 표 안의 모순**일 때만 고쳐라

18차 H3가 Liu 2010의 `Flexural strength (GPa)` 헤더를 MPa로 고쳤다. 근거는
**같은 행에 인쇄된 탄성률 306 GPa** 다 — 527 GPa로 읽으면 파단변형률이 172%가 된다.
읽는 방법이 하나뿐이므로 규칙 6이 작동한 것이다.

반대로 English 2016의 `G_I 0.282 J/mm²` 는 **고치지 않았다.** 282 kJ/m² 는 물리적으로
불가능하지만 같은 표에 모순이 없어서, kJ/m² 로 뒤집으면 **우리가 자릿수를 고르는 것**이 된다.

**경계 — 같은 표·같은 행 안에서 모순이 닫히면 고치고, 바깥 지식으로만 이상하면 버려라.**
어느 쪽이든 근거 사슬을 notes에 verbatim으로 남겨라.

---

## 산출 형식

`.../w<N>parts/<배치>/chunk_NN.json` 에 **재료 10~12종마다(또는 행 120개마다)** 파일을 쓴다.
**끝에 몰아 쓰지 마라 — 배치가 죽으면 전부 잃는다(6차 파동에서 실제로 잃었다).**

```json
{"materials": [
  {"match_name": "<카탈로그의 재료명 정확히 그대로>",
   "source": {"title": "<논문 제목 그대로>", "doi": "...", "url": "...",
              "kind": "journal", "authors": "<제1저자>", "year": "2011"},
   "properties": [
     {"key": "chemical.hydrolysis_rate_constant", "value": 1.2e-07, "unit": "1/s",
      "quality_tier": 1, "method": "measured",
      "conditions": {"temperature_k": 358, "humidity_pct": 100, "property": "Mn"},
      "notes": "원문 Table 3 verbatim: '...'. 원값 4.3e-4 1/h → ÷3600 = 1.2e-7 1/s."}
   ]}
]}
```

새 재료면 `match_name` 대신 `"new_material": {"name": "...", "category": "polymer"}`.
**DB에 직접 쓰지 마라.** JSON만 만들면 적재는 코디네이터가 한다.

## 보고에 반드시 담을 것

1. 닫은 재료·행 수와 tier 분포.
2. **찾았지만 버린 값과 그 이유** — 이게 가장 중요하다. 규칙 몇 번에 걸렸는지 적어라.
3. **코퍼스에 없어서 못 채운 것**과, 어느 디렉터리를 어떤 질의로 훑었는지.
4. **덤으로 발견한 것** — 이 배치 주제가 아니어도 "어느 논문에 무엇이 있다"를 목록으로 남겨라.
