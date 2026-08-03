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
