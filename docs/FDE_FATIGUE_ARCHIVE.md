# FD&E 피로계수 아카이브 회수분 (2026-08-09)

`fde.uwaterloo.ca`가 9차 파동에서 IP 차단된 뒤 Wayback에서 회수한 SAE FD&E 표준 포맷
피팅 계수다. **원 사이트는 여전히 접속 불가**(DNS는 되는데 443 refused)이므로,
다음 파동은 이 표를 먼저 보고 필요한 것만 Wayback에서 다시 받아라.

회수 방법 —
1. `http://web.archive.org/cdx/search/cdx?url=fde.uwaterloo.ca*&output=text&fl=original,timestamp,statuscode&collapse=urlkey&limit=8000`
   (849행. 앞선 보고의 343은 질의 범위가 좁아서 나온 과소치다)
2. `https://web.archive.org/web/{timestamp}id_/{original}`
3. **요청 간격 2.5초 이상.** 0.6초로 돌렸더니 55건 중 42건이 실패했다 — Wayback도 레이트리밋을 건다.

규약은 전부 `Δε/2` 대 `2Nf`다. `ratio`는 σf′/Su이고, 추정식 검산에 쓴다
(Meggiolaro-Castro Medians는 강 1.5 · Al/Ti 1.9 · Ni 1.4를 쓴다).

| 파일 | Su [MPa] | σf′ [MPa] | b | εf′ | c | σf′/Su |
|---|---:|---:|---:|---:|---:|---:|
| `AA_A356-T6_fitted.txt` | 262 | 559 | -0.1150 | 0.0302 | -0.5595 | 2.13 |
| `Ti6Al4V_Su179_f112_fitted.txt` | 1234 | 2034 | -0.1041 | 0.8413 | -0.6877 | 1.65 |
| `aa1100_non_os_fitted.html` | 117 | 166 | -0.0959 | 1.6433 | -0.6689 | 1.42 |
| `aa2014-T6Nachtigall_nonOS_fitted.html` | 534 | 886 | -0.0921 | 0.3559 | -0.7274 | 1.66 |
| `aa2014-T6Smith_nonOS_fitted.html` | 510 | 1008 | -0.1144 | 1.4182 | -0.8703 | 1.98 |
| `aa2024T351_Leis_non_os_fitted.html` | 483 | 793 | -0.0897 | 0.4501 | -0.6826 | 1.64 |
| `aa2024T4_Endo_Morrow_non_os_fitted.html` | 476 | 758 | -0.0760 | 0.7306 | -0.8375 | 1.59 |
| `aa6061merged_fitted.html` | 298 | 491 | -0.0757 | 2.0289 | -0.8874 | 1.65 |
| `aa7075_fitted.txt` | 578 | 876 | -0.0751 | 0.4664 | -0.7779 | 1.52 |
| `aa_2014-T6_fitted.txt` | 524 | 937 | -0.1039 | 0.4064 | -0.7181 | 1.79 |
| `aa_2024-T4_fitted.txt` | 476 | 758 | -0.0760 | 0.7306 | -0.8375 | 1.59 |
| `aa_7075-T6_fitted.txt` | 578 | 876 | -0.0751 | 0.4664 | -0.7779 | 1.52 |
| `merged3_SAE950X_fitted.html` | 496 | 744 | -0.0724 | 0.2342 | -0.4990 | 1.50 |
| `mergedTi6Al4V_fitted.html` | 1234 | 2005 | -0.1157 | 2.1110 | -0.8774 | 1.62 |
| `pm488sae_fitted.txt` | 767 | 1518 | -0.1122 | 0.4807 | -0.6396 | 1.98 |
| `sae1015_fitted.txt` | 415 | 884 | -0.1235 | 0.7290 | -0.5814 | 2.13 |
| `sae1045Bhn187_fitted.txt` | 654 | 1252 | -0.1189 | 0.2382 | -0.4471 | 1.91 |
| `sae1045Bhn563_fitted.txt` | 2296 | 4973 | -0.1385 | 0.3238 | -0.8342 | 2.17 |
| `sae1522H_Bhn155RobinsWeldMetal_fitted.html` | 507 | 708 | -0.0620 | 0.1786 | -0.4602 | 1.40 |
| `sae1522H_Bhn155Robins_fitted.html` | 517 | 662 | -0.0633 | 0.3609 | -0.4933 | 1.28 |
| `sae950X_merged_fitted.html` | — | 805 | -0.0865 | 0.2613 | -0.5103 | — |
| `ss_409_400C_fitted.txt` | 257 | 248 | -0.0253 | 1.1246 | -0.6883 | 0.96 |
| `ti5al2.5sn_fitted.html` | 862 | 1202 | -0.0622 | 6.2042 | -0.9843 | 1.39 |
| `ti6al4v_Nachtigall_fitted.html` | 1007 | 1519 | -0.0763 | 6.2160 | -1.0101 | 1.51 |
| `ti6al4v_Smith_fitted.html` | 1234 | 1786 | -0.0846 | 0.8413 | -0.6877 | 1.45 |
| `ti8al1mo1v_fitted.html` | 1020 | 2140 | -0.1192 | 1.3423 | -0.7090 | 2.10 |

## 회수하지 못한 것 — 아카이브에 없다

- **AA7050-T7351 실측 피팅** — CDX 849행에 7050이 전혀 없다. 아카이브된 `aa7075T651_Kurath_fitted.html`은
  **계수 블록이 없고 피팅 데이터점만** 있다(Su=580도 'assumed from Endo Morrow data file'이다).
- **`ShortFiberComposites/PolyPhenylene/mandell_PPSglass_fitted.html`** — 유일한 복합재 후보였는데
  아카이브에 `ShortFiberComposites/Srim/fitting_SRIM_fatigueCurve.html` 하나뿐이다.

## 이 회수로 실제로 바뀐 것 — 1건

**Al7050-T7451**의 피로계수를 tier4 추정(Meggiolaro-Castro, 1.9×Su = 996 MPa)에서
**tier3 실측 계열대체**(AA7075-T6 FD&E 피팅 876 MPa)로 바꿨다. 둘 다 7xxx 석출경화 Al이고
Su가 524 대 578 MPa로 10% 차이다 — **피로강도를 10% 과대평가하는 쪽**이라 notes에 명시했다.

나머지 25개 세트는 카탈로그가 **이미 실측 계수를 갖고 있는 재료**(Al1100·6061·7075·2024,
Ti6Al4V)이거나 **카탈로그에 없는 재료**(SAE 구조강, A356 주조 Al, Ti-8Al-1Mo-1V 등)다.
**아카이브를 다 뒤져도 남은 피로 빈칸은 안 닫힌다.**

**[2026-08-10 정정] 위 문장의 근거 하나가 틀렸다.** "구리 계열은 FD&E 자체에 없다"고 적었으나
**`Fde/Materials/Other/`에 구리가 있다** — `hatanakaCopper.html`, `nachtigall-CopperAnnealed.html`
(+ −195 °C, −269 °C판). 9차 CDX 파일에 이미 들어 있었는데 `Alum/`·`Steel/` 위주로만 훑어 놓쳤다.
**정확한 서술은 "구리는 있으나 피팅 계수가 없다"다** — 두 건 모두 `DataType= raw`라 계수 블록이
없고, hatanaka는 "Data digitized from graph"라 규칙 3에 걸리며 nachtigall(NASA TN D-7532)은
원시 6점뿐이다. **결론(빈칸이 안 닫힌다)은 바뀌지 않지만 이유가 다르다.**

**FD&E 실제 디렉터리는 14개다** — `Alum, Alumcast, Composites, Iron, Mag, Other, Plastics,
PM, ShortFiberComposites, SMDIdbase, SSteel, Steel, Titan, ToolSteel`.
`Mag/`에 마그네슘(az91-T4, AZ91E-T6, magcast)도 있다.
**CDX는 전역 `limit=8000` 한 번보다 디렉터리별로 좁혀 조회하는 편이 누락이 없다.**
회수 URL은 `https://web.archive.org/web/{timestamp}id_/http://fde.uwaterloo.ca/{path}`,
**요청 간격 3초 이상.**
