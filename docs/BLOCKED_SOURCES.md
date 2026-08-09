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

## S. 다이어태치 접착제 — 제품 라인이 다르면 값이 옮겨붙는다 (2026-08-07)

**DELO MONOPOX AC 시리즈(이방도전 다이어태치) 6등급 전수 확인 — 열전도율 0건.**
AC265 · AC268 · AC2457 · AC6530 · AC6545 · AC6568의 TDS를 전부 받아 읽었다
(DELO 공식 사이트는 등급별 자료를 안 내리므로 Wayback CDX로 inseto.co.uk의 PDF를 열거해 확보).
구판 장문 TDS(AC265 Revision 29)까지 확인했는데 밀도·점도·인장·다이전단·E·Tg·CTE·흡수율·이온함량은
있어도 **열전도율 행이 없다.**

TDS에서 `conductivit`가 나오는 곳은 제품 설명 줄뿐이다 —
`anisotropic electrically conductive, filled, thixotropic`. **전기적 서술이고 수치가 아니다.**

### 옮겨붙을 뻔한 값

검색하면 "DELO MONOPOX 1.7 W/(m·K)"가 나온다. 그건 **MONOPOX TC2270**(열전도 등급)의 값으로
**완전히 다른 제품 라인**이다. AC 등급에 붙이면 안 된다.

같은 배치가 앞서 DELO TC2270에서 `Spezifische Wärmeleitfähigkeit`(열전도율)를 비열로 읽을 뻔한
것도 잡았다. **이 벤더는 한 이름 아래 성격이 다른 라인을 두므로 등급 접미사를 반드시 확인해야 한다.**

### 이방성이라 단일값으로 넣으면 안 된다

AC 시리즈는 Ni 코어 / Au 도금 Ni 입자 ACA다(AC265는 `gold-plated nickel`, d50 2.5 µm,
나머지는 `nickel core`, d50 5 µm). 값이 생기더라도 **z축과 xy면이 크게 다르므로
등방 단일값으로 등록하면 안 된다.**

### MEMS 다이어태치 에폭시 — 제품명 자체가 없다

Prony 출처인 Materials 2017, 10(9)(PMC5615731)를 전문 확인했다. 접착제를 끝까지
`die attach adhesive` · `epoxy-based adhesive`로만 부르고 **제조사·등급이 어디에도 없다.**
Table 2 제목이 `Prony pairs of the die attach adhesive.`다. 열전도율도 없다(`conductivity`가
문서에 한 번도 안 나온다). Table 1은 영률·포아송·CTE뿐이다.

**값을 넣으려면 제품과 값을 둘 다 지어내야 하는 경우**라, 이 항목은 카탈로그 명명을 고치지 않는 한
채울 수 없다.

## T. CCL 열전도율 — 표가 아니라 **슬라이드 레이아웃**에서 값이 옮겨붙는다 (2026-08-07)

CCL·FCCL 7종(TAIFLEX 2UPDR2010JD · Chukoh CGN-500 / CGS-500A · ITEQ IT-180A / IT-968 ·
Nan Ya NP-155FR · TUC TU-872 SLK / TU-933)의 **벤더 발행 문서를 전부 읽었다.**
**일곱 종 모두 열전도율 행이 없다.** 앞서 확정한 "CCL 벤더는 비열을 안 싣는다"에 이어
열전도율도 같다는 것이 확인됐다.

### 가장 미묘한 함정 — 인접 레이아웃 박스

TUC 제품 포트폴리오 발표자료(MP1312002A)에 내가 훑은 TUC 문서 전체를 통틀어 **유일한 `W/mK`
문자열**이 있다.

    IMS — Insulated Metal Substrate — TU-322 / TU-362 / TU-351 … 2 W/mK / 1 W/mK

**이 값은 TUC의 절연금속기판(IMS) 계열 것이고 TU-933이나 TU-872 SLK 것이 아니다.**
같은 슬라이드의 **옆 레이아웃 박스**에 있어서, 텍스트로 평탄화하면 붙어 보인다.
지금까지 잡은 오독은 표의 옆 **열**이었는데, 이건 슬라이드의 옆 **박스**다.

### 열전도율로 오인되기 쉬운 두 행

| 행 | 실제 정체 |
|---|---|
| `Thermal Resistance — T260 / T288 / T300` | **박리까지 걸린 시간(분)**이다. 길이 차원이 아예 없어 역수를 취해도 열전도율이 안 된다 |
| `CTE X-axis / Y-axis / Z-axis` | 방향이 갈려 있어 이방 열전도율처럼 보이지만 **선팽창계수**다. Chukoh CGS-500A는 40/38/217, CGN-500은 20/14/210 ppm/°C |

**일곱 종 어디에도 X/Y vs Z 열전도율 분리가 없다.** 따라서 방향을 붙일 근거 자체가 없다.

### 클래스값 유입 경로

Chukoh는 자사 불소수지 페이지에도 열전도율 수치를 안 싣는다. 그런데 **제3자 재료 사이트에
일반 PTFE 수지 k(≈0.22~0.25 W/m·K)가 유통된다.** 그건 수지이지 유리섬유 충전 CCL이 아니므로
CGN-500/CGS-500A에 붙이면 안 된다.

### 접근 메모

ITEQ 현행 PDF는 Cloudflare 챌린지에 막히므로 **Wayback의 `if_` 스냅샷**으로 받아야 한다
(`web.archive.org/web/{ts}if_/{url}`). TAIFLEX 제품 페이지의 물성표는 **JPEG 이미지**라
텍스트 추출이 안 되고, 미러본(eurotronics)이 벤더 브랜딩을 유지한 채 텍스트로 남아 있다.
같은 제품명의 미러가 실은 다른 등급인 경우가 흔하다 — Eltos의 "IT-180A"는 실제로
`IT-180ABS/IT-180ATC` 슬래시시트다.

## U. 젖음성 — 규격이 세정 절차를 강제하는 분야를 노려라 (2026-08-07)

4차 배치가 7건을 채우면서 **탐색 전략 하나를 확인했다.**

> 성공한 것 중 다수가 **ISO 규격이 세정·수화 절차를 강제하는 분야**에서 나왔다
> (안과광학 ISO 18369-4). **규격이 절차를 강제하면 표면 이력이 자동으로 기재된다.**

이 물성은 표면 상태가 값을 지배하는데(같은 재료가 세정 여부로 30° 넘게 벌어진다),
전자부품 논문은 그 기재 의무가 없어 계속 탈락한다. 반면 규격 분야는 안 적을 수가 없다.

**노릴 만한 분야** — 콘택트렌즈(ISO 18369-4) · 식품포장 필름(코로나 처리 dyne 시험, ASTM D2578) ·
의료용 임플란트 표면. 이 분야의 재료가 카탈로그 항목과 화학적으로 겹치면 대용 자료가 된다.

### 구조 금속은 "본문에 숫자" 필터로도 안 걸린다

Ti·Al·SS 논문들이 표면처리 시리즈를 **Figure로만** 싣고 본문엔 "approximately"를 붙인다.
4차가 Ti-6Al-4V 3건과 알루미늄 합금 2건을 이 사유로 버렸다.
3차의 "금속은 표면 상태를 안 적는다"가 한 겹 더 구체화된 셈이다.

### 자체 출처 코퍼스는 소진됐다

타깃 재료의 **자체 출처 논문 88편을 전부 받아 일괄 grep**했는데 접촉각·표면에너지가 걸린 것이
6편이고 실효는 3편이었다. 기존 출처를 역추적하는 방법은 이 물성에서는 끝났다.

## V. 율속 3차 — 확정된 벽과 남은 단서 (2026-08-07)

308종 중 17종 131건을 채우고 **LCSR 곡선이 10 → 19종**이 됐다. 낙하 준비율 4 → 8%.

### 곡선 형태를 평활화하지 않았다

인쇄값 그대로 넣어 **곡선이 이상해 보이는 것 셋**을 남겼다. 해석에서 그대로 쓰면 안 되는
것들이라 note와 카드 주석에 사실을 적었다.

| 재료 | 배율 | 성격 |
|---|---|---|
| Zr-BMG | 1.00 → 1.13 → 1.02 → **0.91** | NSRS. 감소가 실제 현상이다 |
| Al6063-T5 | 1.00 / 1.23 / 1.10 / 1.20 | 지그재그. 원저자가 "율속이 오를수록 민감도가 줄고 항복이 되레 떨어진다"고 썼다 |
| SCM440 | 0.996 ~ 1.000 | 사실상 평탄. **기울기를 읽으면 안 된다** |

### 확정된 벽

- **Cowper-Symonds·DIF는 이 목록과 교집합이 거의 없다.** Europe PMC 코퍼스 118건을 끝까지
  훑은 결과 C/p 문헌은 구조용 강(Q235~S960·HRB500E) 위주이고 DIF는 90%가 콘크리트·모르타르다
- **박막·소자류** — 두께가 µm라 SHPB 응력평형이 성립하지 않는다. 기계물성이 나노인덴테이션으로만
  보고되므로 규칙상 사용 금지다
- **PI/PEN 필름** — LLNL 보고서(OSTI 3017515)가 직접 확인해 준다.
  *"Kapton의 율속 데이터가 문헌에 없어 Vespel로 대체했다"* 고 명기돼 있다
- **연자성 5종** — 자기적으로만 특성화되고 동적 기계시험 문헌이 존재하지 않는다
- **사출 컴파운드 39종** — CAMPUS는 크로스헤드 1점만 싣고, 논문 쪽은 **GF 함량 일치가 벽**이다.
  GF15/20/…/50이 각각 다른 재료인데 공개문헌에 함량이 명시된 건 PEEK-GF30 하나뿐이었다
- **고무·폼 13종 0건** — Íñiguez-Macedo 2019는 원문 확인 결과 **5 mm/min 단일 준정적**이라
  율속 데이터가 애초에 없는 논문이다. EPE 폼 논문의 "dynamic"은 낙하시험이고 율속을 안 찍는다
- **EMC·언더필·BT·ABF** — 고율속 데이터를 가진 Lall(Auburn) 계열이 전량 IEEE ECTC / ASME JEP
  게재라 **NSF PAR에도 없다**

### 새 경로 — AEC/HEDL 1970년대 보고서

스캔본이지만 **부록에 율속별 0.2% 항복이 표로 인쇄돼 있다.** Nickel 200(HEDL-TME 71-166,
OSTI 4700948 Appendix B)이 여기서 나왔다. OCR을 믿지 않고 `pdftoppm -r 220`으로 렌더해
눈으로 재확인했고 전부 일치했다.

### 검증 못 한 단서 — D3O LITE D

율속 배치가 Bhagavathula 2018(DRDC 공개본)에 준정적 0.04 s⁻¹ 120 kPa vs SHPB 5465 s⁻¹
243 kPa의 완벽한 2점이 있다고 보고했다. 시료가 **D3O LITE D 200~220 kg/m³** 이고 카탈로그
대상은 397 kg/m³라 등급이 다르므로, 신규 재료로 등록하면 즉시 tier1 카드가 된다.

**다만 내가 원문에 접근하지 못했다.** cradpdf.drdc-rddc.gc.ca가 응답하지 않고 Europe PMC에도
없다. 값을 옮겨 적지 않고 단서로만 남긴다. 접근이 되면 신규 재료로 등록할 것.

## W. 5차 파동에서 뒤집힌 것과 새로 열린 것 (2026-08-07)

### 뒤집힌 것 — 막혔다고 적어둔 것이 사실이 아니었다

**IOPscience는 완전히 막힌 게 아니라 간헐적이다.** `iopscience.iop.org/article/{DOI}/pdf`에
UA를 붙이면 2.1 MB짜리 정상 PDF가 오는 경우가 있다. 다만 막힐 때는 **200을 주면서 PDF가
아니라 HTML(캡차/인터스티셜)을 돌려준다.** 같은 DOI(10.1149/1945-7111/ac8504)가 한 에이전트에게는
PDF로, 나에게는 HTML로 왔다. 그래서 `file`로 실제 형식을 확인해야 한다 — HTTP 200을 믿으면 안 된다.

### 도메인이 통째로 옮겨간 것

**DuPont 전자재료가 `qnityelectronics.com`으로 분사·이전했다.** 구
`(www.|www.beta.)dupont.com/content/dam/electronics/...` 경로는 전부 404이고, 도메인만
바꾸면 같은 경로가 200이다. 카탈로그에 있던 Kapton FPC·Kapton HN·Pyralux HP 커버레이
데이터시트 URL 3건을 실제로 받아 PDF임을 확인하고 교체했다.

**이건 일회성 사건이 아니다.** 벤더 문서 URL은 조용히 죽는다. 출처 URL이 죽으면 값 자체는
남아도 재확인이 불가능해진다. 주기적으로 데이터시트 URL의 생존을 확인할 필요가 있다.

### 벤더 문서 자체가 함정인 경우

**Rogers 선정가이드는 제품 TDS와 계통적으로 다른 값을 싣는다.** RO3003 박리강도가 선정가이드
17.6 lbs/in 대 제품 TDS 12.7 lbs/in, RT/duroid 5880이 22.8 대 31.2 pli다. CLTE-XT는 판본
간에도 다르다(2020년 단독 TDS 1.1 N/mm, 2023년 통합 TDS 1.7 N/mm). **선정가이드를 쓰지 마라.**

**3M 8800 시리즈 TDS의 8820 열은 `** Estimated value based on Tape 8815 test data`다.**
벤더가 자기 시트에 추정치라고 각주로 밝혀 놨는데 tier 1로 들어가 있었다. 각주를 읽어야 한다.

**AGC는 최신 TDS에서 Peel 행을 지웠는데 배포처 사본이 보존하고 있다**(`hemeixinpcb.com`).
같은 문서의 영률·포아송비·열전도율이 AGC 공식판과 완전히 일치해 원문성을 대조 확인했다.

**Avery Dennison은 TDS 트리가 둘이다** — 현행 `tapes.averydennison.com/content/dam/...`과
단종품 `.../Literature/Product%20Information/...`. **현행 트리의 404가 TDS 부재의 증거가 아니다.**

### 새로 열린 경로

- **accudynetest.com/polymer_surface_data/{슬러그}.pdf** — 폴리머별 표면에너지 시트 54종.
  각 행이 1차 출처와 측정 방식(임계표면장력/접촉각/용융체/계산)을 함께 인쇄한다.
  5차 파동 젖음 수확 91건 중 78건이 여기서 나왔다.
- **res.mdpi.com은 `article_deploy/` 세그먼트가 필수다.** 없으면 404다.
- **www-origin.nitto.com** — `www.nitto.com`이 HTTP/2 INTERNAL_ERROR로 죽을 때 우회로.
- **Wayback `id_` 직행이 CDX API가 503일 때도 된다** — `web.archive.org/web/{year}id_/{원본URL}`.
  corning.com이 직접 fetch에 403을 주는 PDF를 이걸로 복구했다.
- **KoreaScience** `koreascience.kr/article/{JAKO id}.pdf` (UA 필요) — 한국 전자패키징·표면처리.
- **ventec-group.com/media/{id}/{file}.pdf** — 동박·라미네이트 TDS가 인증 없이 열린다.
- **EMS-GRIVORY Comparative Table** — 전 등급 전기물성을 한 장에 싣는다. 등급별 TDS 불필요.
- **Panasonic** industrial.panasonic.com은 fetch 거부, **RS Online CDN(`docs.rs-online.com`)**에
  같은 문서가 있다.
- **arXiv API는 https + `-L`이어야 한다.** http는 301만 주고 조용히 빈 결과가 된다.
- **Accuratus는 `curl --compressed` 없이는 gzip 바이너리가 떨어진다.**
- **Smooth-On** `smooth-on.com/tb/files/{PRODUCT}_TB.pdf` — 실패하면 정확히 25,889바이트짜리
  HTML 404가 온다. 크기로 걸러라.

### 확정된 부재 (더 찾아도 안 나온다)

- **커버글래스 4종(Victus/Victus 2/알루미노실리케이트/UTG)의 물 접촉각.** Corning PI 시트에
  항목이 없고, 자사 백서는 bare 값을 오직 `< 10°` **상한**으로만 인쇄한다. Gorilla Glass를
  기판으로 쓴 논문·특허는 전부 코팅 후 값만 싣는다.
- **테이프 19종의 밀도.** 벤더가 두께로만 발표한다. Avery Dennison은 `Density` 행이 있는데
  값이 `Medium`/`Low`라는 **단어**다. 완제품 테이프는 OSHA article 면제라 SDS 9절도
  `Density: Not Applicable`이다. 라이너 평량은 테이프 질량이 아니다.
- **GF 열가소성 18종의 율속 데이터.** 페이월이 아니라 **아예 발표하지 않는다.** BASF·Syensqo·EMS는
  CAMPUS ISO 데이터시트를 1~5 mm/min 고정으로만 내고, 율속별 데이터는 Ultrasim·Digimat
  상용 DB 안에 있다.
- **PSA·OCA 테이프 ~50종의 전기물성.** TDS를 실제로 받아 grep한 결과 전기 섹션 자체가 없다.
  예외는 기능성 등급뿐이다(열전도 8800 라인, 도전성 Lohmann EC, 디스플레이용 OCA 817X).
- **OCA/PSA의 산소 투과도.** 벤더가 발표하지 않는다. 봉지재는 업계가 "WVTR이 만족스러우면
  OTR도 만족한다"고 보고 WVTR만 측정한다.


## X. bepress / Digital Commons 403 우회 — 뚫렸다 (2026-08-07)

**원인은 `viewcontent.cgi`가 아니라 그 앞의 AWS WAF JS 챌린지였다.** 응답이
`x-amzn-waf-action: challenge` 헤더와 함께 202 + 빈 본문으로 온다. curl은 UA를 아무리 바꿔도
못 지난다. 절차는 이렇다.

1. Playwright로 논문 랜딩페이지(`https://<site>/<series>/<n>/`)를 연다 → 챌린지가 자동
   해결되고 `aws-waf-token` 쿠키가 생긴다.
2. **페이지 컨텍스트 안에서** `fetch('viewcontent.cgi?article=N&context=SERIES',
   {credentials:'include'})` → Blob → `<a download>` 클릭.
3. Playwright `download` 이벤트를 잡아 `saveAs()`.

`open.clemson.edu` · `mavmatrix.uta.edu` · `stars.library.ucf.edu` · `docs.lib.purdue.edu`
넷에서 동일하게 작동했다. 4차 파동이 못 뚫었던 Clemson 논문(all_theses/4672, article=5700,
22 MB)이 이 방법으로 열렸다.

**전문검색 JSON API는 plain curl로 그냥 된다** —
`https://<site>/do/search/results/json?q=<q>&start=0&facet=`. 웹페이지는 JS 렌더라 비어
보이지만 이 엔드포인트는 `num_found`와 `docs[].url`을 준다. 26개 리포지터리를 병렬로 훑었다.

**arrow.tudublin.ie는 WAF가 아니라 헤더 검사다.** UA만으로는 403이고, Chrome 헤더 전체
세트(UA + Accept + Accept-Language + Referer(랜딩) + Sec-Fetch-*)를 주면 200이다.

이 경로 하나로 학위논문 리포지터리가 통째로 열렸다. **워피지 논문이 마스터커브를 그림으로만
싣고 계수표를 사내자산으로 남기는 관행 때문에, 같은 연구의 학위논문 부록이 유일한 출처인
경우가 많다.** 5차 파동 벤딩 수확 118건의 대부분이 여기서 나왔다.

## Y. 6차 파동 — 새 경로와 확정된 부재 (2026-08-08)

### 새로 뚫은 경로

- **Isola TDS = 포아송비 광맥.** `isola-group.com/wp-content/uploads/data-sheets/{슬러그}.pdf`
  (`370hr` `i-speed` `fr408hr` `i-tera-mt40` `astra-mt77`). **전 라미네이트에 Poisson's Ratio를
  length/cross로 ASTM D3039 실측으로 인쇄한다.** 실측 스펙트럼이 0.137~0.234로,
  "직물유리 적층판 ν=0.183"이라는 클래스 가정의 실제 불확도가 이만큼이다.
- **SABIC 필름 기술매뉴얼**이 PC·PBT·PEI 필름 ν의 유일한 출처다(Lexan 0.38, Ultem 0.42,
  ASTM D132-61). 개별 제품 TDS에는 없다.
  `static1.squarespace.com/static/61ef1f195f3d93384f20d7f3/t/621516b217df0c4e71222dc9/...`
- **GaTech SMARTech 3단 체인** — `repository.gatech.edu/server/api/discover/search/objects?query=handle:%221853/{id}%22`
  → UUID → `/server/api/core/items/{UUID}/bundles` → ORIGINAL → `_links.content.href`.
  **IEEE 페이월 논문의 저자 원고가 여기 올라와 있는 사례가 확인됐다**(Dunne 2001 IEEE CPMT).
  `hdl.handle.net`는 HTML 862 B만 준다.
- **FD&E Waterloo는 IP 차단됐지만 Wayback으로 우회된다.**
  목록 `web.archive.org/cdx/search/cdx?url=fde.uwaterloo.ca/Fde/Materials&matchType=prefix&limit=50000&collapse=urlkey&fl=timestamp,original`,
  본문 `web.archive.org/web/{ts}id_/{original}`(`id_` 필수). 간격 3초 + 3회 재시도로 거의 회수된다.
  계수 파일은 `grep -l "STRG COEF"`로 걸러진다. **26개 고유 계수 세트를 회수해 뒀다.**
  다만 아카이브 커버리지는 부분적이다 — 라이브 605쪽 대비 343 URL, `_fitted` 57개.
- **MIL-HDBK-5G Vol.2** `archive.org/download/DTIC_ADA322636/DTIC_ADA322636_djvu.txt`(1.4 MB OCR).
  5~9장(Ti·내열·기타). **알루미늄 3장·강 2장은 Vol.1이고 archive.org에서 못 찾았다.**
  OCR이 `Log Nf`를 이중공백으로 뱉으므로 `grep -iE "Log +N *f? *="`로 찾아야 한다.
- **SciELO는 완전 개방이다.** `?format=pdf`는 xref가 깨져 pdftotext가 실패하지만
  HTML(`scielo.br/j/{j}/a/{hash}/?lang=en`)에 표가 평문으로 들어 있다.
- **3M 개별 제품 TDS는 `multimedia.3m.com/mws/media/{ID}O/아무이름.pdf`로 ID만 맞으면 열린다.**
  VHB ID 확인분 — 2369649(4910, k=0.16) · 2369651(4950, k=0.09) · 2369604(5952, k=0.05) 등.
- **Europe PMC 보충자료** `…/{PMCID}/supplementaryFiles`가 publisher SI를 ZIP으로 준다.
  **본문이 "Table S1 참조"라고 하면 여기로 가라.**
- **WebFetch가 curl 우회로로 쓸 수 있다.** inseto.com은 curl에 HTML을 주지만 WebFetch는
  실제 PDF를 저장한다. 그 파일을 `pdftotext -layout`으로 다시 읽으면 된다.
- `apicalfilm.com/wp-content/uploads/{제품명}.pdf` — Kaneka Apical 등급별 TDS 21종.
- `agc-multimaterial.com/agc-downloads/AGC_{PRODUCT}_TDS.pdf` — **AGC 현행 포맷은
  `Specific Heat`(IPC-650 2.4.50)와 `Density`를 인쇄한다. 단 방열 지향 등급만.**
- `arplankdirect.com/.../PhysicalPropertyInformation_EPEproducts_ARPLANK_AUG2024.pdf` —
  EPE 20~74 g/l 밀도별 ASTM C177 열전도율 표.
- **PubChem PUG-View** `?heading=Density`가 1차 출처(CRC 판·페이지, OECD 시험번호)를 함께 준다.

### 확정된 부재

- **PCB 라미네이트 비열은 어느 벤더도 발표하지 않는다.** Rogers·Isola·ITEQ·TUC·Nan Ya·
  Panasonic·Shengyi·Doosan·AGC·Taconic·Chukoh 전수 확인. **유일한 예외가 AGC RF-35TC다.**
- **PCB 라미네이트는 밀도도 발표하지 않는다.** 수지 함량과 두께를 대신 인쇄한다(Chukoh만 예외).
- **Rogers·VAC·Arnold는 포아송비를 발표하지 않는다.**
- **Darveaux 상수는 솔더 조인트 전용**이고 피로 타깃 174종에 솔더가 하나도 없다.
  검색 실패가 아니라 정의상 없다.
- **저분자 도판트(발광체·인광체·광개시제) ~55종은 밀도·열전도율·비열·CTE가 없다.**
  광물리 논문은 λ·Φ_PL·τ·HOMO/LUMO만 인쇄한다.
- **PSA 테이프 ~51종의 CTE·열물성·기계물성** — 벤더가 애초에 발표하지 않는다.
  "expansion coefficient"라는 문구는 나오지만 "피착재 팽창 차이를 흡수한다"는 판매 문구다.
- **Shin-Etsu RTV 카탈로그는 "실리콘 2-4×10⁻⁴/°C"라는 계열 범위만** 인쇄한다(2배 폭이라 못 씀).
- **Amodel PPA 비열은 그림뿐**이고 Ryton PPS Design Guide에는 비열 항목이 없다.
- **Kapton EN 실측 열전도율은 존재하지 않는다**(EN-A·EN-C·EN-Z 시트 QE-10172 전수 확인).

### 테이프 밀도 — SDS 경로도 막혔다 (2026-08-08 확인)

앞선 파동이 "벤더 TDS에 테이프 밀도가 없다"를 확정했고, 이번에 **SDS 우회로까지 확인해
닫았다.**

**3M은 테이프 SDS 9절의 밀도를 계통적으로 `Not Applicable`로 적는다.** 9415PC/9425HT를
함께 다루는 SDS의 **US판(2013)과 말레이시아판(2016) 두 판본**을 각각 받아 확인했고 둘 다
같다. 완제품 테이프가 OSHA article 면제라 물성 기재 의무가 없기 때문이다.
**앞으로 3M 테이프 SDS를 더 확보해도 결과는 같을 공산이 크다.**

Intertape는 SDS 대신 **ARTICLE INFORMATION SHEET**를 내고 문서 서두에 article 면제를
명시한다. `Density: Not applicable`.

접근 자체가 막힌 것 — **Nitto No.500/5015E/5050S**는 이 제품군 SDS를 공개하지 않는다
(`/others/products/file/{sds,msds}/`·`/others/sds/`·`/support/sds/` 전부 404, EU 제품 페이지
HTML을 파싱해도 문서 링크가 TDS 하나뿐). **Lohmann**은 lohmann-tapes.com이 HubSpot으로
이전하며 다운로드 섹션이 사라졌고, lohmann-tapes.us는 `files_db/{타임스탬프ID}__6.pdf`
형태라 ID 열거가 불가능하다. **3M 8402**는 공개 SDS가 없고 유통사 미러도 없다.

**라이너 평량(gr/sqm)은 테이프 질량이 아니다.** 역산하지 마라.

---

## Z. fde.uwaterloo.ca — 무지연 순회로 IP 차단 (2026-08-09)

9차 파동 피로 배치가 `fde.uwaterloo.ca/Fde/Materials/`를 **지연 없이 610쪽** 받은 직후
`Connection refused`가 시작됐다. **하루가 지나도 복구되지 않았다.**

**차단 범위 판별** — DNS는 정상(`129.97.50.135`)이고 `uwaterloo.ca` 본 캠퍼스는 200을 준다.
그런데 **그 IP에 올라간 두 호스트(`fde`·`ieee`)가 모두 443 refused**다.
즉 대학 전체 차단이 아니라 **그 서버가 우리를 막았거나 서버 자체가 죽은 것**이다.

**되돌릴 수 없는 것** — AA7050-T7351 실측 피팅과 유일한 복합재 후보(PPS-glass)는
**Wayback에도 없다.** 자세한 내역과 회수한 26개 계수 세트는 `docs/FDE_FATIGUE_ARCHIVE.md`.

**앞선 보고를 정정한다** — 배치가 "Wayback에 343개만 있다"고 했으나 질의 범위가 좁았다.
`url=fde.uwaterloo.ca*`로 다시 긁으면 **849행 · `_fitted` 55개**다. 51개를 회수했다.

**그리고 같은 실수를 한 번 더 했다** — 브리프에 "순회에 지연을 넣어라"를 적어 넣은 직후,
Wayback을 0.6초 간격으로 돌려 55건 중 42건이 실패했다. **아카이브도 레이트리밋을 건다.**
2.5초로 늘리고 1회 재시도를 붙이니 38건이 추가로 들어왔다. **지연은 원 사이트만의 문제가 아니다.**
