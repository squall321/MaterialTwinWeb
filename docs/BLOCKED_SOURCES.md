# 미확보 문헌 대장

수집 중 **막혀서 못 얻은 자료**를 남긴다. 값이 없어서 못 채운 게 아니라 **문서에 접근을 못 해서**
못 채운 것들이라, 접근 수단이 생기면 즉시 채울 수 있다. 매번 같은 곳을 다시 뒤지지 않기 위한 대장이다.

기록 규칙 — 한 줄이라도 아래 셋은 반드시 적는다.
1. **무엇을 얻을 수 있나** (재료·물성 키)
2. **왜 막혔나** (유료 / 로그인 / 봇차단 / 그림뿐 / 문서 삭제)
3. **뚫리면 뭐가 되나** (몇 건이 채워지는지)

---

## A. 유료 문헌 (구독·구매하면 즉시 확보)

| 자료 | 얻을 것 | 막힌 이유 | 뚫리면 |
|---|---|---|---|
| **Avalle 원논문** `10.1016/j.ijimpeng.2006.06.012` | 폼 Avalle 모델 E·σ₀·A·B·m·n 표 (EPP/PUR/PPO-PS 다밀도) | Elsevier 유료 | 폼 압축모델 다밀도 세트. 초탄성 수집에서 **가장 아쉬운 미확보** |
| `10.1016/j.microrel.2012.03.011` | 경화 진행도 의존 EMC Prony + 시프트 인자 | Elsevier 유료 | EMC 점탄성의 정본 |
| `10.1016/j.jmbbm.2016.02.019` | Sylgard 184(10:1) 경과일수별 대변형 초탄성 | 유료 | 실리콘 시효 의존 |
| `10.1016/j.compositesb.2018.11.045` | 경질 PU 폼 하이퍼폼 μᵢ·αᵢ·βᵢ 직접 피팅값 | 유료 | 폼 Ogden 세트 |
| `10.1002/app.47025` | Ecoflex neo-Hookean/Ogden/MR/Yeoh (압축성·비압축성) | 유료 | 초연질 실리콘 |
| `10.1088/0960-1317/24/3/035017` | Sylgard 184 경화온도 25~200 °C별 물성 | 유료 | 공정 의존성 |
| LANL **LA-UR 07-0298** | Sylgard 184 Prony **1차 출처**(Sandia 메모의 원본) | 리포트 미공개 | 현재는 2차 인용만 |
| `10.3934/matersci.2019.1.97` | PDMS **이축** MR/Ogden | OA인데 사이트가 JS 셸만 반환 | 이축 검증 데이터 |
| Motalab / Lall, SAC305 고변형률속도 시험 (IEEE **ECTC** · **ITherm** 논문집) | `mechanical.cowper_symonds_c`·`_p`, 율속별 항복강도 | IEEE Xplore 유료 | SAC305 C·p **3~4쌍**. 낙하충격 해석의 핵심 입력 |
| Auburn Univ. 학위논문 `etd 10415/9752` (같은 원 데이터) | 〃 | 리포지터리가 다운로드 차단(`isAllowed=n`) | 〃 |
| ACF 본딩 신뢰성 논문 (ECTC / **Microelectronics Reliability**) | `Dexerials ACF` 3종의 E·CTE·Tg | Elsevier·IEEE 유료 | ACF 벌크 물성 **6~9건**. 현재는 일반 ACF 문헌값만 있다 |
| **IPC-4412C** 유리포 규격 (E-glass 직물 사양) | 유리포 스타일별 **면밀도(g/m²)** | IPC 표준 유료 | **라미네이트 밀도 10종**. 아래 C절 참조 |
| Alq3/NPB 나노인덴테이션 `10.1016/j.orgel.2009.11.026` | OLED 유기층 영률 | Elsevier 유료 | OLED 유기 3종의 E. 현재 전 계열에 영률이 없다 |
| Ir(ppy)₃ 타원계측 `10.1016/j.cap.2005.01.034` | `optical.refractive_index`·`extinction_coefficient` (파장별) | 유료 + 본문에 수치표 없음 | Ir 인광체 n·k |
| AIP *Nanotechnology and Precision Engineering* `10.1063/10.0017693` | NiCr 박막 비저항 | Cloudflare 403 (기관 접속 필요) | NiCr 저항체 실측 비저항 |

## B. 로그인·회원 전용

| 자료 | 얻을 것 | 막힌 이유 | 뚫리면 |
|---|---|---|---|
| TUC `TU-872 SLK_SDS of Laminate.pdf` | `physical.density` (SDS 9항 비중) | TUC 회원 로그인 | TU-872 SLK 밀도 |
| DuPont / Celanese **Zytel** 전 계열 TDS (70G33L·70G43L·HTN51G45HSL) | PA66-GF30/GF43, PPA-GF45 전 물성 | CAMPUS·MatWeb·UL Prospector가 JS 렌더링이라 표 추출 불가 | GF 사출재 **3~4종 × 12물성** |
| UL Prospector / UL Yellow Card | 일부 라미네이트 비중, CTI 전압 | 회원 전용 | 라미네이트 밀도 보조 경로 |

## C. 벤더가 애초에 공표하지 않음 (문서를 열어도 없다)

| 대상 | 없는 물성 | 확인한 문서 | 대안 |
|---|---|---|---|
| Isola 370HR·IS400·I-Tera MT40·Astra MT77, ITEQ IT-180A·IT-968, TUC TU-872·TU-933, Panasonic MEGTRON 6·7, Taconic RF-35 | `physical.density` | 영문 TDS·Product Guide·일본어/중문판·IPC 슬래시시트·SDS. 370HR SDS에는 `SPECIFIC GRAVITY: Not Available for product`라고 **명시** | FR-4 계열은 구성(유리포×수지함량)에 따라 달라 단일 밀도가 없다. **Isola는 Dk/Df 표에 유리포·수지함량·두께를 공개**하므로 `ρ = W_glass·n/((1−RC)·t)`로 산출 가능 — 단 **IPC-4412 면밀도(A절)가 필요**하다. 방법 검증은 마쳤다(3313이 통용값 81 g/m²에 0.4% 일치) |
| Taimide TH/TL/BK-025 | 밀도·Tg·CTE | 공식 TDS가 1페이지(인장·연신·저항만) | — |
| Dexerials ACF 제품 페이지 | 접착강도·벌크 물성 | 제품 페이지에 본딩 조건(온도·압력·시간)만 | A절 논문 |
| Rogers ULTRALAM 3908 | 접착력 | 무접착 LCP 본드플라이라 항목 자체가 없음 | — |
| Nitto ELEP HOLDER 라인업 표 | BG 테이프 등급별 스펙 | 전 지역 미러가 **비어 있음**(봇 차단 아님 — 공개 중단) | 개별 제품 페이지에서 4종만 확보됨 |

## D. 문서가 사라짐

| 대상 | 얻을 것 | 상태 |
|---|---|---|
| Kaneka **Graphinity** | 그래파이트 시트 열전도·밀도 | 제품 페이지 전부 404, **Wayback 스냅샷도 없음**. 무역기사의 "1200 W/mK"는 데이터시트도 논문도 아니라 채택 불가 | 
| Kuraray Genestar, DIC PPS FZ-1140, Sumitomo SUMIKASUPER | LCP·PPS-GF 물성 | 영문 TDS PDF 미확보 |

## E. 그림으로만 있음 (디지타이즈 가능성 있음)

| 자료 | 얻을 것 | 상태 |
|---|---|---|
| 3M VHB **PSTC 2005** 발표자료 | VHB 율속별 응력 | 그래프만. 축 눈금이 읽히면 `digitize_curve.py`로 추출 가능 |
| **ACS Omega** PORON XRD | 폼 율속 응답 | 그래프만 |
| PSTC **Tsaur & Allen** | PSA 필 속도별 박리력 | 그래프만 |
| Rogers *Handheld Shock Control Design Guide* | 92-12·79-09의 1 /s vs 2000 /s | 수치가 **흡수에너지(mJ)** 뿐이라 응력 DIF로 변환 불가 |
| 일반 OCA DMA 온도스윕 (Micromachines 13, 301 Fig.10) | 저장탄성률 마스터커브 | 축 캘리브레이션은 됐으나 저해상도에서 곡선 4개가 병합돼 분리 불가. 게다가 논문이 제품명 없는 "OCA material"이라 귀속 불가 |
| Ir 인광체 · Ag 본딩와이어 | n·k, 기계물성 | 수치가 그래프에만 |
| 3M **VHB 5952**(Black 1.1mm) 율속 | 율속별 응력 | 공개 그래프를 못 찾음. TDS의 정적 설계값뿐이고 언급된 PSTC 2005 발표자료는 공개본이 없다 |
| ACS Omega Fig.4 (절대 G′·G″) | 폼 주파수 응답 | 축력 1~5N 곡선 5쌍이 같은 색으로 겹쳐 곡선 식별 불가 |
| OCA DMA Fig.10의 1·2 Hz | 저장탄성률 | 4곡선이 같은 색·선종류이고 60 °C 미만에서 2군집으로 뭉쳐 분리 불가(60~120 °C 구간만 사용) |

## F. 원문에 단위가 없어 기록하지 않음

수치는 표에 있는데 **논문 전체에 단위 표기가 없어** SI 환산이 불가능한 것들.
저자에게 문의하거나 원 데이터가 공개되면 회수할 수 있다.

`10.3390/polym15163388`(EPDM Yeoh·Ogden) · `10.3390/inventions8050116` ·
`10.3390/ma17225675`(EPDM·LSR 6모델) · `10.3390/ma16196561`(CB충전 NR Yeoh) ·
`10.3390/ma15165529`(HNBR) · `10.3390/polym15102266`(**신에츠 KE-1950-30 LSR 등2축** —
논문 전체에 MPa/kPa 표기 0회) · `10.4186/ej.2021.25.4.11`(PDMS 전 모델) ·
`10.3390/polym18111344`(실리콘 폼 Ogden) · `10.3390/polym18141729`(경질 PU 3차 Ogden) ·
`10.3390/ma18133037`(Ecoflex Yeoh — PDF 글리프 누락).

`10.3390/polym16243601`(NR 라텍스)은 C10≈0.01로 스케일이 의심스러워 제외했다.

## G. 유도 규칙이 원문에 없어 보류

| 자료 | 상태 |
|---|---|
| PORON `10.1016/j.ijimpeng.2021.104100` | PDF는 확보했으나 Table 2가 Avalle 상수가 아니라 **율속 스케일링 계수(C, α, M₁, M₂)** 다. 상수를 얻으려면 `P(ε̇)=C·ε̇^α`와 `m=M₁·log(ε̇)+M₂`를 계산해야 하는데 **m 식의 log 밑(10 vs 자연로그)이 원문에 없다.** 밑이 정해지면 PORON XRD LD/HD는 DB에 이미 있으므로 바로 산출 가능 |

## H2. 벤더가 싣지 않아 산출도 불가

| 대상 | 없는 물성 | 확인 방법 |
|---|---|---|
| 테이프 31종(Avery 14·Lohmann 9·Nitto 3·3M 3·tesa 1·Intertape 1) | `physical.density` | **면중량 ÷ 두께 기법이 통하지 않는다.** TDS의 `g/m²`는 전부 **이형지(release liner) 평량**이다(tesa 4965 "PV0 red MOPP 72 g/m²", Nitto "Si paper 90 g/m²"). 테이프 자체 도포량이 아니라 두께로 나누면 지어낸 숫자가 된다. Lohmann은 평량을 아예 싣지 않는다. 14개 PDF 전문 grep으로 확인 |
| PCB 라미네이트 12종 | `physical.density` | 12종 TDS를 전부 열었으나 **밀도 행 자체가 없다.** 라미네이트 TDS는 Dk/Df·Tg·CTE·Td·박리력만 싣는다. AGC RF-35 현행 TDS는 호스팅 중단(302), MatWeb·everythingRF는 봇 차단 |

## H. 오픈액세스에 아예 없음

- **부틸고무(IIR) 초탄성 상수** — OA 문헌 172편 전수 스크리닝 결과 IIR은 감쇠·투과도에
  집중돼 있고 상수표가 없다. **자체 시험 피팅이 현실적인 경로.**
- **디스플레이용 OCA/PSA의 조성 명시** — 논문들이 아크릴/실리콘 여부 자체를 밝히지 않아
  재료 귀속이 불가능한 경우가 많다.

---

## 뚫렸던 경로 (다음에도 먼저 시도할 것)

같은 "막힘"이라도 아래 방법으로 실제로 뚫린 사례들이다.

- **Cloudflare / 403** → `curl -A "Mozilla/5.0" -e "https://<그 사이트 자체 도메인>/"`.
  Referer를 **벤더 자신의 도메인**으로 주는 게 결정적이었다(ITEQ SDS가 이걸로 열렸다).
  Corning은 UA+Referer로 PI Sheet가 열렸다.
- **벤더 TDS가 비공개** → 제품 페이지 본문, 대리점 미러, SDS 9항, **철도 화재시험 성적서**
  (NFPA 130 / ASTM E1354 — 콘칼로리미터는 밀도를 반드시 기재한다. Isola 370HR·IS400이 이 경로).
- **페이월 논문** → 한국 OA(Polymer(Korea)), **J-STAGE `_pdf` 직링크**, `mdpi-res.com` 직링크
  (www.mdpi.com은 403), Europe PMC, arXiv, Zenodo/DataCite.
- **PDF 표가 텍스트로 안 뽑힘** → `pdftotext -layout`(열 정렬 보존). 그래도 안 되면
  `scripts/catalog/extract_datasheet.py`의 300dpi OCR 폴백.
- **JS 렌더링 사이트** → 아직 못 뚫었다. 대리점이 재배포한 PDF를 찾는 게 빨랐다
  (Envalior CAMPUS 출력물을 이탈리아 대리점 PDF로 확보).

## I. 규격 자체에 항목이 없어 벤더가 생산하지 않는 물성 (2026-08-04)

포아송비를 폴리머 99종에서 수집한 결과 **3종만** 확보됐다. 개별 검색 실패가 아니라 구조적 이유가 있다.

**엔지니어링 열가소성 수지 TDS는 ISO 10350-1 / CAMPUS 항목 체계를 따르는데 그 체계에 포아송비가 없다.**
그래서 아래가 한꺼번에 막힌다 — 개별 조회로는 뚫리지 않으니 재시도하지 말 것.

- BASF Ultramid 11종 · Ultradur 3종, SABIC LEXAN 3412R, DSM Stanyl 2종, EMS Grivory 2종
- Victrex PEEK 450GL30, Rogers ULTRALAM 3850HT/3908, UBE Upilex(카탈로그+RN), Kaneka Apical
- SCS Parylene(독립 2부), Henkel ABLESTIK 2025D, DOWSIL 993

**PSA 테이프 TDS도 같은 이유로 막힌다.** 박리력·유지력·두께만 싣고 탄성상수는 싣지 않는다.
3M VHB 4910만 구조접착 FEA 용도로 예외적으로 공표했고(그마저 2025-10 개정판 V-6에서 삭제됨),
같은 판 VHB 4905 TDS가 "Poisson's Ratio — See 3M VHB Tape 4910"이라 적어 교차 확인됐다.

**결론.** 남은 90여 종은 수집으로 풀리지 않는다. 자체 측정이나 명시적 가정값(그렇게 표기한 채)
둘 중 하나를 택해야 하는 항목이다. 빈칸이 틀린 값보다 낫다는 원칙에 따라 비워 둔다.

### 등급 불일치로 버린 것
- Kapton ν=0.34 — DuPont이 HN·FPC TDS에 실제로 인쇄했으나 대상은 140EN-Z/150EN-A/150EN-C/150MT+.
  EN 시리즈 TDS를 직접 받아 grep한 결과 ν 항목 없음. 다른 등급 값을 옮겨 붙이지 않는다.
- Bauer 1989 PMDA-ODA ν=0.34(1% 변형)/0.48(5%) — Kapton 화학계이나 상용 등급 특정 없음.
- Micromachines 2022 OCA · Sci Rep 2024 PSA — 대상이 지목한 바로 그 논문 2편을 전문 확인했으나
  **ν 수치를 인쇄하지 않았다.** 비압축성 전제로 초탄성 모델만 세웠다.

### 값이 서로 어긋나 확정 못 한 것
- **Sylgard 184 ν** — 0.45±0.03(인장 직접측정, bioRxiv 2023/ACS 2024)과 0.495±0.001(Soft Matter 2019,
  열팽창+광학 프로파일로미터)이 어긋난다. 비압축성 근처에서 0.05 차이는 체적거동을 크게 바꾼다.
  원문을 verbatim 확인할 수 있었던 0.45를 등록했으나 확정값이 아니다. RSC는 Cloudflare 403.

## J. 클래스 대표값을 거절한 사례 — 클래스가 균질하지 않으면 대표값이 없다 (2026-08-04)

수집 에이전트가 "class representative"로 제안했으나 **내가 거절한** 건들이다.
tier3 클래스 대표값은 클래스가 균질할 때만 성립한다.

**NAMICS CHIPCOAT die attach (DA series) 열전도율 1.2 W/(m·K) — 거절.**
*(2026-08-04 후속: 재조사에서 진짜 DA 등급값이 나와 거절 판단이 수치로 확인됐다 —
**DA8465-12(Transparent, 무충전) 0.2** vs **DA8472-1(White, 충전) 2.4**, 같은 클래스 안에서 12배 차이.
XS8488-1의 1.2를 클래스 대표로 썼다면 무충전 등급에 6배 과대, 충전 등급에 2배 과소가 됐다.
두 값을 각각 `conditions.grade`를 달아 등록했다. 컬럼 귀속은 브로슈어 p.32를 `pdftoppm`으로
이미지 렌더링해 육안 재확인했고, 좌열 Transparent/"No Bleeding"↔0.2, 우열 White/"High Thermal
Conductivity"↔2.4로 물리적 정합까지 교차검증했다.)*
값의 출처 제품이 XS8488-1(알루미나 충전 비전도성)로 아예 다른 제품군이다. 게다가 대상 클래스가
균질하지 않다 — NAMICS Product Guides 2015의 DA 시리즈는 DA8483(printable B-stage) ·
DA8481-8(dispensing) · **DA8465(Transparent, LED용)** 로, transparent 등급은 무충전이라
알루미나 충전값 1.2를 대표로 쓰면 크게 틀린다. 진짜 DA 시리즈 표에는 열전도율 컬럼 자체가 없다
(Viscosity / Curing condition / Tg만 있음). DB의 이 재료는 모든 값이 `conditions.grade`에
DA 등급을 달고 있어, 다른 제품군 값을 섞으면 그 규율도 깨진다.

**2K Polyurethane Coating 열전도율 0.19 / 비열 1700 — 거절.**
출처가 BASF Elastollan **TPU(열가소성 선형 엘라스토머, 벌크)** 인데 대상은 **2액형 가교
열경화 도막**이다. 화학·경화 방식이 다르고 벌크 대 박막 도막이라는 형태 차이도 있다.
실제 2K PU 도막 TDS 4종(AkzoNobel 58 Series, Jotun Hardtop XP, Polytek Ultimate Top Coat,
Awlgrip Topcoat)을 받아 grep한 결과 열전도율이 인쇄돼 있지 않음을 확인했다.

**추적할 가치가 있는 유료 단서.** "conventional polyurethane coating, hot disk 0.2093 W/(m·K)"가
ScienceDirect `S0167577X21006340`에 있는 것으로 보이나 페이월이라 원문을 못 읽었다.
대상에 정확히 맞는 값이므로 기관 접근이 생기면 이것부터 확인할 것.

**대안으로 검토했으나 쓰지 않은 것.** PMC12171350(Angew. Chem., 불소화 폴리우레탄)에
`we set Λa to the thermal conductivity of 16H-IPDI (0.16 W m−1K−1)`이 실제로 인쇄돼 있으나,
16H-IPDI는 불소화 연구용 실험실 합성 비정질 PU이고 0.16은 명시적으로 **비정질 하한값**이다.
안료 충전 2K 도막의 대표값으로는 BASF 벌크 PU보다 더 나쁘다.

## K. 표 정렬은 맞는데 값 자체가 물리적으로 안 맞는 경우 (2026-08-04)

**EMC 비열 236 J/(kg·K) — 거절.** *Micromachines* 2022, 13(10), 1704 (PMC9611615) Table 1
"Parameters for modeling on hygroscopic tests"에 실제로 이렇게 인쇄돼 있다.

    Parameters                | EMC     | PCB     | Si      | Al
    Specific heat (J/(kg·K))  | 236 [18]| 920 [18]| 700 [19]| 900 [19]

**열 정렬을 원문 XML로 직접 확인했고 정상이다** — Si 700, Al 900은 정확한 값이라 컬럼이
밀리지 않았다. 즉 오귀속이 아니라 **값 자체가 이상하다.**

EMC는 실리카 충전 에폭시다. 용융실리카 비열 ~740, 에폭시 ~1000–1200이므로 혼합칙으로는
60~80% 충전에서 ~800–960이 나온다. 236은 어떤 조합으로도 나오지 않는다.
공교롭게 **은(Ag) 비열이 235**라 2차 인용 과정의 전사 오류로 의심된다.

게다가 이 값은 논문의 1차 측정이 아니라 ref [18](Lau, Abdullah, Ani, *Solder. Surf. Mt. Technol.*
2012, doi 10.1108/09540911211214659)의 **2차 인용**이고 원문은 유료라 확인하지 못했다.
2차 인용 + 물리적 부정합 + 1차 미확인 → 넣지 않는다.

**Epoxy die attach (MEMS) 열전도율 2.5 W/(m·K) — 거절.** 값의 출처는 EPO-TEK H20E(은 충전).
다이어태치 클래스는 **무충전 0.2에서 소결은 60까지** 걸쳐 있어 균질하지 않다. 게다가 MEMS
가속도계용은 응력 최소화를 위해 저모듈러스·저충전을 고르는 경우가 많아 은 충전값과 성격이 다르다.
같은 이유로 에이전트도 ABLESTIK ABP 6395T(30 W/mK)를 이미 배제했다 — 2.5도 같은 논리로 배제한다.

**반면 EMC 열전도율 1.0 W/(m·K)는 채택 가능하다.** Sumitomo SUMIKON EME-G770H Type D TDS의
인쇄값(`THERMAL CONDUCTIVITY SB-U-02-004 W/m•°C 100x 10-2`)이고, 같은 계열 EME-6300HR이
ASTM C177로 0.67을 인쇄해 클래스 범위 0.67~1.0이 교차 확인된다. EMC 클래스는 실리카 충전
몰딩 컴파운드로 비교적 균질하다.


## L. 부호·규약이 인쇄되지 않아 넣지 못한 것 (2026-08-05)

수집 에이전트가 값을 찾고도 **판단을 넘긴** 두 건이다. 둘 다 내가 골라 주면 역산이 되므로 비운다.

**LFP 결정셀 체적변화 6.81% — 부호 미인쇄.**
Materials 16(17) 리뷰(PMC10488970) verbatim: "the volume change of the crystal cell before and
after discharge is only 6.81%". 크기만 있고 **부호가 없다.** 게다가 서술이 "before and after
**discharge**"라서 방전(FePO₄→LiFePO₄) 기준이면 팽창(+), 충전 기준이면 수축(−)이다.
새 부호 규약(팽창 양수)에 넣으려면 부호를 골라야 하는데 그건 인쇄값이 아니다.
게다가 리뷰의 2차 인용([17])이다 — **1차 출처를 찾는 쪽이 맞다.**

**실리콘 체적팽창 약 300% — 변형률 규약 미정의.**
Nanomaterials 리뷰(PMC12734434)에 "~300–400% volume expansion"과 "approximately 300%"가
함께 인쇄된다. **"300% volume expansion"이 ΔV/V₀ = 3.0인지 V/V₀ = 3.0(즉 ΔV/V₀ = 2.0)인지
원문이 정의하지 않는다.** 두 해석의 차이가 1.5배다. 문헌 관행은 전자지만 그건 인쇄된 정의가
아니다. 게다가 활물질 입자 스케일이지 전극층이 아니고, 범위(300~400)와 단일값(300)이
같은 논문 안에서 엇갈린다.

**공통 원칙.** 값이 있어도 **그 값을 해석하는 규약이 인쇄돼 있지 않으면** 넣지 않는다.
부호·기준·정의를 내가 고르는 순간 그건 측정값이 아니라 내 가정이 된다.

## M. 접근 가능/차단 목록 — 2026-08-05 재확인

**내가 브리핑에 적어 온 차단 목록에 오류가 있었다.** 에이전트가 신고해 직접 확인했다.

### 차단이 아니었던 곳 (내 오류)
- **rogerscorp.com — 정상이다.** RO4000/RT-duroid/CLTE-AT 데이터시트가 HTTP 200 · `%PDF`로
  내려온다(직접 확인: 872 KB, Tensile Modulus/Strength 행 판독됨). `rogerscorp.cn`도 동작한다.
  세션 초반 한 번 403이 났던 것을 계속 차단으로 전파했다 — **여러 배치에 잘못된 정보를 줬다.**

### 이관된 곳
- **DuPont Kapton → `qnityelectronics.com`.** `dupont.com/.../electronics/...`는 404이고
  동일 경로가 qnityelectronics.com에 살아 있다.

### 새로 뚫린 경로
- **`res.mdpi.com`** — `www.mdpi.com`은 403이지만
  `https://res.mdpi.com/d_attachment/{slug}/{slug}-{vol}-{art:05d}/article_deploy/{slug}-{vol}-{art:05d}.pdf`
  로 전 저널 PDF 직접 수신. **Metals·Polymers는 PMC 미수록이라 이 경로가 유일하다.**
- **Georgia Tech SMARTech REST API** — 검색 + 본문 직접 다운로드. 앞 배치가 "Elsevier 유료라
  불가"로 포기한 Ferguson & Qu 원문이 여기 학위논문으로 통째로 있었다.
  TU Delft·TU Berlin DepositOnce·Loughborough·NEU도 같은 방식이 가능할 것이다.
- **`download.basf.com`** — `p1/<hash>/en/ULTRAMID®_<GRADE>` 패턴, `/de/`→`/en/` 치환 통함.
- OSTI purl · NTRS · NIST nvlpubs · DiVA · arXiv · SciELO · Frontiers · WIT Press ·
  Europe PMC · J-Stage · OpenAlex API · 대학 리포지터리 대부분.

### 실제 차단 (재확인)
ScienceDirect · Springer · Wiley · T&F · Hindawi · **IOP(Radware 봇매니저 — 세션 중간에
막혔다, 앞 배치에서는 되던 곳이다)** · EDP Sciences(DataDome) · IEEE · DTIC · CORE ·
Zenodo API · ResearchGate · nitto.com · corning.com(Akamai) · norlandprod.com(연결 거부)

### JS 렌더링이라 curl로 못 읽는 곳
campusplastics.com · my.basf.com · plasticsfinder.envalior.com · industrial.panasonic.com(타임아웃)

**교훈.** 차단 목록은 시간에 따라 변한다(IOP은 세션 중에 막혔고 rogerscorp는 애초에 안 막혀
있었다). **한 번 403이 났다고 영구 차단으로 전파하지 말 것** — 재확인 비용이 잘못된 정보를
여러 배치에 퍼뜨리는 비용보다 훨씬 싸다.

## N. 항복강도 212종 결측은 검색 실패가 아니라 구조적이다 (2026-08-05)

폴리머·복합재 157종을 훑어 `yield_strength`가 **단 1건**(Parylene HT) 나왔다.
이유가 명확하다 — **유리섬유 강화 등급은 항복점이 없다.**

BASF 제품군 총괄표가 ISO 527 행을 이렇게 적는다.

    Yield stress (v=50 mm/min), (Stress at break (v=5 mm/min)*

그리고 **GF 등급 값에 `*`를 붙여** 5 mm/min 파단응력임을 명시한다. 제조사가
"이 등급에는 항복을 재지 않는다"고 문서로 선언한 것이다.
Amodel·Grivory·Stanyl·Victrex PEEK·Vectra도 전부 `Tensile stress at break`뿐이고,
Kapton EN/MT+·Apical·Upilex-25RN도 항복 항목이 없다. 적층판은 `ultimate stress`만 인쇄한다.

**따라서 낙하 해석의 "항복강도 결측"은 채워서 해결할 문제가 아니다.**
이 재료들은 항복 없이 파단하므로 `*MAT_024`의 SIGY를 억지로 만들면 안 되고,
파단응력·파단연신율로 취성 파괴를 모델링하거나(`*MAT_ELASTIC` + 파괴 기준),
GF 등급이면 이방성 카드를 써야 한다. **해석 준비도 지표에서 이 구분을 반영해야 한다.**

### 함정 3건
- **Kaneka Apical의 `Yield, ft²/lb`는 항복강도가 아니라 단위질량당 면적**(area yield)이다.
- **Amodel의 `Flexural Stress — Yield 363 MPa`는 굽힘 항복**이지 인장 항복이 아니다.
- **Parylene HT 검색 요약이 두 번 틀렸다** — 인장 "7,000–11,000 psi"는 **옆 칸 Acrylic 열**,
  항복 "5,000–9,000 psi"는 Parylene N~D 열 범위를 뭉갠 것. HT 단일 셀은 인장 7,500 · 항복 5,000 psi다.

## O. 비열 — 벤더가 아예 인쇄하지 않는 물성이다 (2026-08-05)

무기·복합재 비열 31종 전수를 훑어 **0건**이었다. 검색 실패가 아니라 문서에 없다.

**CCL·프리프레그 — 벤더 6곳이 일관된다.** Rogers · Isola · AGC/Taconic · 중흥화성 ·
Panasonic · TUC 전부 TDS에 열전도율·CTE·Td/Tg만 싣고 비열은 없다. 원문을 직접 열어
확인한 것만 18종이다(TSM-DS3, CGN-500, CGS-500A, Isola 370HR·IS400·Astra MT77·I-Tera MT40,
Ryton R-4, MEGTRON 6·7, CLTE-AT, RO4003C·RO4350B·RO4835, RF-35, TLX-8, TLY-5, TU-933).
수지 함량별 비열 구분은 애초에 인쇄된 사례가 없어 `resin_content_pct` 조건을 쓸 일도 없었다.

**연자성·영구자석 합금도 같다.** METGLAS 2605SA1(Technical Bulletin), MUMETALL(VAC),
VACOFLUX 50(VAC), Alnico 5(MMPA 0100-00 Table II-4·II-5, Eclipse, Dura, Arnold TN 0205)
전부 밀도·열전도율·CTE·저항률까지만 싣고 비열 행이 없다.

**커버글래스도 없다.** Corning Gorilla Glass Victus·Victus 2의 PI Sheet를 전문 확인했다.
밀도·영률·포아송·전단·Vickers·K1c·CTE·점도점·화학내구성·Dk·굴절률까지 있는데 비열만 없다.

### 에이전트가 클래스 대표값 투입을 스스로 중단했다

FR-4 ≈ 1100, PTFE-glass ≈ 1000 J/(kg·K)를 tier3로 넣을 수 있었지만 그러지 않았다.
사유가 정확하다 — **그 숫자를 인쇄한 실제 접근 가능한 문서를 확보하지 못했고,
기억에서 적으면 지어내기다.**

이 물성은 벤더 경로가 막혔으므로 핸드북(CRC, ASM, NIST)이나 측정 논문으로 가야 한다.

### 운영 제약 — WebSearch 세션 한도

이 파동에서 WebSearch가 200회 한도에 도달했다. 이후 에이전트들은 URL 직접 추정과
프록시 경유 fetch로 진행했고 그 방식으로도 원문 20여 개를 열었지만, 탐색형 작업은
품질이 떨어진다. 아래 3종은 "부재 확인"이 아니라 **"덜 찾아봤다"** 로 분류해야 한다.
PET Felt Acoustic Panel · PSA Rubber Hot-Melt(SIS/C5) · Silicone OCA(Momentive).
벤더 사이트 접근 실패로 미검증인 비열 6종도 같다 — Doosan DS-7402, ITEQ IT-180A,
ITEQ IT-968, Nan Ya NP-155FR, Shengyi S1000-2, TUC TU-872 SLK.

## P. 접근 경로 — 이번 파동에서 확인된 것 (2026-08-05)

**뚫린 것.**

| 경로 | 상태 | 비고 |
|---|---|---|
| OSTI | **가장 잘 된다** | `/servlets/purl/{id}`, `/api/v1/records?q=`. Sandia SAND 보고서가 여기 있다 |
| bzycj.cn (爆炸与冲击) | **엔드포인트 확보** | 아래 참조. 로그인·봇월 없음 |
| Europe PMC | 정상 | `/{PMCID}/fullTextXML`이 표를 구조화해 준다 |
| res.mdpi.com | 정상 | `.../{journal}-{vol:02d}-{art:05d}.pdf` — **볼륨 2자리 제로패딩 필수** |
| Crossref · DOAJ · J-Stage | 정상 | |
| Georgia Tech SMARTech DSpace | 정상 | 학위논문 bitstream은 항목별 200/401 갈림 |

**bzycj.cn 검색 엔드포인트** — 앞 배치가 못 찾았던 것을 확보했다.

    검색  POST https://www.bzycj.cn/search
          form: q=<검색어>&searchField=<""|titleCn|keywordCn|abstractinfoCn|doi>&pageType=cn
    본문  https://www.bzycj.cn/cn/article/doi/{DOI}
    PDF   https://www.bzycj.cn/cn/article/pdf/preview/{DOI}.pdf

`preview` 경로인데 **전문이 나온다**(10.11883/bzycj-2016-0266에서 10쪽 전체 확인).
다만 이 저널의 금속 내용은 방호탄도 중심이라(장갑강, W-Ni-Fe 관통자, 폭발용접 복합재,
콘크리트, 우라늄 합금) 스마트폰 재료 66종과는 겹치지 않았다. **수확 0건.**
중국계 합금·장갑강 작업에는 쓸모가 있으므로 경로만 남긴다.

**막힌 것.**

- **OpenAlex · Semantic Scholar** — 세션 내내 HTTP 429. "Anonymous search is temporarily
  rate-limited… use a free API key". **다음 배치 수확량을 가장 크게 좌우할 병목이다.**
  무료 API 키를 발급받으면 해소된다.
- **NTRS** — `/api/citations/search`가 이번 세션엔 모든 질의에 `total: 0`을 돌려줬다
  (GET·POST 모두). 앞 배치에서는 동작했으므로 일시적일 수 있다.
- **DYMAT proceedings** (10.1051/dymat/*) — DataDome이 curl을 403으로 막는다.
  **명목상 오픈액세스인 1차 SHPB 데이터가 대량으로 여기 있다.** Playwright로는 뚫릴 수 있다.
- DuckDuckGo · Searx · Brave · Mojeek · Startpage · Ecosia — 이 환경에서 전부 차단.
- `www.mdpi.com/article/{doi}/pdf` — 403. res.mdpi.com 직링크를 써야 한다.

**참고 — 재인쇄본을 못 쓰는 대가.** 황동·구리의 정전 Johnson-Cook 상수는 원출처가
Johnson & Cook 1983(7th Int. Symp. Ballistics)과 Johnson & Holmquist LA-11463-MS인데
둘 다 OSTI·NTRS·Crossref에 색인이 없다. 접근 가능한 사본은 전부 재인쇄본이라
"원출처를 따라가라"는 규칙에 걸려 구리·황동 계열이 통째로 비었다. 규칙을 어길 이유는 없지만,
이 대가가 어디서 발생하는지는 적어 둔다.

## Q. 열을 좌표로 검증해야 하는 경우가 있다 (2026-08-05)

자성재 배치가 검색엔진이 반복 보고하는 값을 **x좌표로 열 귀속을 검증해 기각**했다.
이 프로젝트에서 나온 오독 방어 중 가장 엄밀했으므로 방법을 남긴다.

**Alliance LLC "Physical Properties of Permanent Magnet Materials"** 를 두고 검색엔진들이
일관되게 이렇게 말한다 — *"Cast Alnico: thermal conductivity 10–200 W/(m·K),
specific heat 350–500 J/kg°C, Young's Modulus 100–200 GPa"*.

**틀렸다.** 단어별 x좌표를 뽑아 보면,

    "Cast Alnico" 헤더      x ≈ 175–202
    "Sintered Alnico" 헤더  x ≈ 222–259
    Young's Modulus 100-200 x = 219–261   → Sintered 열
    Thermal Conductivity 10-200 x = 222–259 → Sintered 열
    Specific Heat 350-500   x = 219–261   → Sintered 열

**Cast Alnico의 세 칸은 비어 있다.** 표를 텍스트로만 평탄화하면 빈 칸이 사라지면서
옆 열 값이 붙어 보인다. `pdftotext -layout`도 이 경우엔 안전하지 않다.

같은 배치가 Deutsche Techna 카탈로그에서도 함정을 하나 더 걸렀다 —
`Spezifische Wärme ~440 J/(kg·K)` · `E-Modul 150 kN/mm²` 블록이 **NdFeB 절**에 있었다
(Curie ~330 °C가 단서). Alnico 값이 아니다.

### 자성재는 이 물성들을 아예 공표하지 않는다

- **MUMETALL(VAC)** — 데이터시트 7종(2024 strip/solid, PHT-001 영·독, PHT-002, CoFe, Cutting)을
  전부 받아 확인. 물리물성 블록이 밀도·열전도율·열팽창·비저항·퀴리·영률로 고정돼 있고
  **비열 열 자체가 없다.**
- **METGLAS 2605SA1** — 기술회보 전 개정판(2001·2009·2011·2016·2021)과 SDS, NETL 코어
  데이터시트까지 확인. 밀도·경도·인장·탄성계수·적층률·열팽창·결정화온도·연속사용온도로
  고정이고 **비열·열전도율이 없다.**
- **Alnico** — Arnold·Eclipse·MMPA 0100-00·ChenYang·IBS·Maurer 어디에도 없다. MMPA의 유일한
  modulus 열은 `Transverse Modulus of Rupture`(굽힘강도)다.
  thyssenkrupp만 **AlNiCo 전 계열 한 행**으로 셋을 싣는다 — 주조·소결·전 등급을 묶은 값이다.
  비열 `~400 J/kg K`만 tier3 클래스값으로 등록했고, 영률 `100–200 kN/mm²`와
  열전도율 `10–100 W/m K`는 **범위라 스칼라화가 불가능해** 넣지 않았다(열전도율은 10배 범위다).

## R. 점탄성(Prony) — 어디에 있고 어디에 없는지 (2026-08-05)

두 배치가 각각 다른 방향으로 훑어 경계가 분명해졌다.

### 새로 뚫린 경로

**NSF PAR — `https://par.nsf.gov/servlets/purl/{ID}`.** ASME·IEEE **게재승인원고**를 공개한다.
공개 검색 엔드포인트는 없지만 purl 직링크는 PDF를 바로 준다. 패키징 분야에서 아직 안 판
광맥이고, FR-4 PCB의 10항 Prony(155·165 °C 두 마스터커브)를 여기서 건졌다.
다만 "Accepted Manuscript Not Copyedited" 워터마크가 셀을 가로지르는 경우가 있으니
가려진 값은 쓰지 말 것.

**J-Stage 검색 API** — `service=3&text=…&count=N`(Atom XML). JIEP·ejisso·jsms PDF가 전부
무료다. **다만 2010년 이전 PDF는 텍스트층 없는 스캔이라** `pdftoppm -r 220`으로 렌더해
눈으로 읽어야 한다(Nitto Denko EMC 3종의 G·K 18항 표가 이 경우였다).

### 한국 오픈액세스는 닫혔다

**마이크로전자및패키징학회지 109개 호 1,146편을 전수 내려받아 grep했다.**
Prony를 언급한 논문이 **4편**, 수치표를 인쇄한 것은 **2편**뿐이고 둘 다 EMC이며
**둘 다 비한국 문헌을 인용한 것**이다(Microelectronics Reliability 2011 / Lin & Lee).
KSME·KSAE·Composites Research·접착및계면·반도체디스플레이기술학회지까지 167편을 더 훑었으나
폴리이미드 필름·OCA/PSA·PET/PEN·커버윈도 하드코트·솔더레지스트·ABF·ACF·다이어태치·TIM·
LCP·PEEK·PC/PMMA·TPU·VHB·배터리 세퍼레이터·PVDF 바인더·언더필 **어느 것도 없었다.**

**한국 패키징 해석 문헌은 EMC·기판 Prony를 측정하지 않고 인용한다.** 이 경로는 더 파지 않는다.
(kpubs.org는 현재 접속 불가, koreascience.kr에 미러돼 있다. scienceon.kisti.re.kr은 JS 껍데기다.)

### 구조적 결론 — 오픈액세스에 있는 것과 없는 것

| 있다 | 없다 |
|---|---|
| EMC · FR-4/프리프레그 · 언더필 | OCA/PSA · 무색 PI · 커버윈도 하드코트 · ACF · ABF · 솔더마스크 · PET 필름 |

없는 쪽은 **IEEE ECTC/EPTC/ICEPT와 SID Digest에 실리고 전부 유료다.**
PV(태양광) 폴리머 논문이 PET-폴리에스터·PC 필름의 가장 좋은 대용 자료다.

### 접근 실패 기록

OpenAlex는 이제 HTTP 429 "Insufficient budget"(유료 전환) · Semantic Scholar는 키 필요 ·
scholar.archive.org는 JS 봇월(Playwright로도 막힘) · MDPI 사이트 검색은 curl 403 ·
**IOPscience는 Radware 캡차**라 curl·헤드리스 크롬 둘 다 막힌다.
Crossref `query.bibliographic`은 이 분야에서 포화된다 — "Prony"가 응용 패키징 논문의
제목에 거의 안 나오기 때문에 같은 3~4건만 반복된다.
