$==============================================================================
$ 낙하시험 미변환 재질 — 카탈로그 DB 대조 물성 카드
$   단위계: ton-mm-s  (응력 MPa · 밀도 ton/mm^3 · 길이 mm)
$   E·PR 은 **원본 모델 값 그대로** 둔다. DB 에서 가져온 것은 SIGY·ETAN·RO 뿐이다.
$   각 카드 위 주석에 근거 재료·등급(t1 실측 ~ t4 추정)·E 차이를 적었다.
$==============================================================================
$
$------------------------------------------------------------------------------
$ Cu-Alloy   (E=105356 MPa · PR=0.31)
$   근거: [37] C26000_Cartridge_Brass Bilinear  (metal)
$          DB E = 110000 MPa (모델 대비 +4.4%, t2)
$   SIGY  = 340 MPa   [yield t2]
$   ETAN  = 243.6 MPa   [(UTS 500 - SIGY 340)/(eps_u 0.660 - eps_y 0.0032)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.66 를 넣어라 — DB 파단연신이다.
$   RO    = 8.53e-09 ton/mm^3  [t2]
$   · 구리합금. DB C26000 카트리지황동(E=110 GPa, 4.4% 차)
$   · sigy/UTS 가 t2 실측이다. 모델 nu=0.31 은 DB 0.34 보다 낮아 Corson 계열(C7025 등)일 수 있으나 DB 에 그 등급이 없다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Cu-Alloy
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900001  8.53e-09    105356      0.31       340    243.62         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ Cu   (E=114000 MPa · PR=0.31)
$   근거: [122] TSV Copper (through-silicon via)  (metal)
$          DB E = 140410 MPa (모델 대비 +23.2%, t1)
$   SIGY  = 74.6 MPa   [yield t1]
$   ETAN  = 2068 MPa   [(UTS 280 - SIGY 75)/(eps_u 0.100 - eps_y 0.0007)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.1 를 넣어라 — DB 파단연신이다.
$   RO    = 8.92e-09 ton/mm^3  [t2]
$   · 순동. DB TSV Copper(전해동, E=140 GPa)
$   · sigy 74.6 · UTS 280 · eps 0.10 이 **전부 t1** 인 완전 이선형 세트다. **연질(어닐드) 전해동이라 항복이 낮다
$   · 보수적 하한이다.** 모델 부품이 압연 반경질이면 sigy 가 200~250 으로 오른다. E 는 DB 가 23% 높지만 **모델 E 를 그대로 두므로** 카드는 정합한다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Cu
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900002  8.92e-09    114000      0.31      74.6    2067.5         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ Ground   (E=207000 MPa · PR=0.288)
$   근거: [11] SPCC_mild_steel Bilinear  (metal)
$          DB E = 206000 MPa (모델 대비 -0.5%, t2)
$   SIGY  = 250 MPa   [yield t2]
$   ETAN  = 372 MPa   [(UTS 350 - SIGY 250)/(eps_u 0.270 - eps_y 0.0012)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.27 를 넣어라 — DB 파단연신이다.
$   RO    = 7.87e-09 ton/mm^3  [t2]
$   · 접지 금속. DB SPCC 연강(E=206 GPa, 0.5% 차 · sigy 250 · UTS 350 · eps 0.27, 전부 t2)
$   · 거의 정확히 맞는다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Ground
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900003  7.87e-09    207000     0.288       250    372.03         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ C7701_1_2H   (E=124000 MPa · PR=0.28)
$   근거: [39] C51000_Phosphor_Bronze Bilinear  (metal)
$          DB E = 110316 MPa (모델 대비 -11.0%, t1)
$   SIGY  = 552 MPa   [yield t1]
$   ETAN  = 411.9 MPa   [(UTS 579 - SIGY 552)/(eps_u 0.070 - eps_y 0.0045)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.07 를 넣어라 — DB 파단연신이다.
$   RO    = 8.86e-09 ton/mm^3  [t1]
$   · C7701 은 양백(Cu-Ni-Zn) 1/2H. DB 에 양백이 없어 **같은 구리계 스프링재** C51000 인청동(E=110 GPa, 11% 차)을 대리로 쓴다. sigy 552 · UTS 579 가 전부 t1 이다. **양백 실측이 들어오면 교체할 자리.**
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
C7701_1_2H
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900004  8.86e-09    124000      0.28       552    411.91         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ PA-GF30%   (E=9300 MPa · PR=0.4)
$   근거: [305] Ultramid B3WG6 (PA6-GF30, BASF)  (polymer)
$          DB E = 9500 MPa (모델 대비 +2.2%, t2)
$   SIGY  = 185 MPa   [UTS 대용 t1]
$   ETAN  = 9.3 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.035 를 넣어라 — DB 파단연신이다.
$   RO    = 1.36e-09 ton/mm^3  [t2]
$   · PA6-GF30. DB Ultramid B3WG6(E=9500, **2% 차**)
$   · UTS 185 · eps 0.035 · nu 0.43 이 t1 이다. 최상 매칭.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
PA-GF30%
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900005  1.36e-09      9300       0.4       185       9.3         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ Kalix9950   (E=18000 MPa · PR=0.35)
$   근거: [297] Amodel A-1145 HS (PPA-GF45, Solvay/Syensqo)  (polymer)
$          DB E = 17200 MPa (모델 대비 -4.4%, t1)
$   SIGY  = 259 MPa   [UTS 대용 t1]
$   ETAN  = 18 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.026 를 넣어라 — DB 파단연신이다.
$   RO    = 1.59e-09 ton/mm^3  [t1]
$   · Kalix 9950 은 PPA 계열. DB Amodel A-1145 HS(PPA-GF45, E=17200, 4.4% 차)
$   · UTS 259 · eps 0.026 · nu 0.41 전부 t1. 같은 폴리머·같은 충전율대라 대리로 강하다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Kalix9950
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900006  1.59e-09     18000      0.35       259        18         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ PBT-GF45   (E=12400 MPa · PR=0.358)
$   근거: [307] Ultradur B 4300 G6 (PBT-GF30, BASF)  (polymer)
$          DB E = 9800 MPa (모델 대비 -21.0%, t2)
$   SIGY  = 140 MPa   [UTS 대용 t1]
$   ETAN  = 12.4 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.03 를 넣어라 — DB 파단연신이다.
$   RO    = 1.53e-09 ton/mm^3  [t2]
$   · PBT-GF45. DB 에 GF45 등급이 없다
$   · 같은 BASF Ultradur B4300 계열의 **GF30(G6, E=9800)** 을 하한으로 쓴다. **주의: 실제 GF45 는 이보다 강하다**(같은 계열 GF50 은 UTS 160). 보수적 하한이다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
PBT-GF45
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900007  1.53e-09     12400     0.358       140      12.4         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ PC-GF50%   (E=12000 MPa · PR=0.43)
$   근거: [313] LEXAN 3412R (PC-GF20, SABIC)  (polymer)
$          DB E = 6000 MPa (모델 대비 -50.0%, t1)
$   SIGY  = 109.8 MPa   [UTS 대용 t1]
$   ETAN  = 12 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.05 를 넣어라 — DB 파단연신이다.
$   RO    = 1.356e-09 ton/mm^3  [t1]
$   · PC-GF50. DB 최고 충전율이 **GF20(LEXAN 3412R, E=6000)** 이라 E 가 절반이다. UTS 110(t1) 을 하한으로 쓰되 **GF50 은 실제로 더 강하다**
$   · 교체 1순위.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
PC-GF50%
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900008 1.356e-09     12000      0.43    109.83        12         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ PI   (E=1490 MPa · PR=0.3)
$   근거: [68] Kapton PI Adhesive Tape  (polymer)
$          DB E = 1390 MPa (모델 대비 -6.7%, t3)
$   SIGY  = 69 MPa   [yield t4]
$   ETAN  = 240.5 MPa   [(UTS 231 - SIGY 69)/(eps_u 0.720 - eps_y 0.0463)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.72 를 넣어라 — DB 파단연신이다.
$   RO    = 1.42e-09 ton/mm^3  [t1]
$   · E=1490 은 PI **필름**(2500~3500)이 아니라 **PI 점착테이프** 대역이다. DB Kapton PI Adhesive Tape(E=1390, 7% 차). UTS 231 · eps 0.72 는 t1 이고 sigy 69 는 t4(추정)다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
PI
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900009  1.42e-09      1490       0.3        69    240.47         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ POL-PI   (E=2000 MPa · PR=0.3)
$   근거: [194] PI Base Film — Kapton HN (DuPont)  (polymer)
$          DB E = 2500 MPa (모델 대비 +25.0%, t1)
$   SIGY  = 69 MPa   [yield t1]
$   ETAN  = 236.3 MPa   [(UTS 231 - SIGY 69)/(eps_u 0.720 - eps_y 0.0345)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.72 를 넣어라 — DB 파단연신이다.
$   RO    = 1.42e-09 ton/mm^3  [t1]
$   · 폴리이미드 계열. DB Kapton HN(E=2500, 25% 차)
$   · sigy 69 · UTS 231 · eps 0.72 가 **전부 t1** 인 표준 PI 필름이다. E 차가 크지만 **모델 E 를 그대로 두고 강도만 가져오므로** 카드는 정합한다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
POL-PI
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900010  1.42e-09      2000       0.3        69    236.32         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ LCP   (E=7100 MPa · PR=0.3)
$   근거: [109] LCP (Liquid Crystal Polymer)  (polymer)
$          DB E = 7800 MPa (모델 대비 +9.9%, t1)
$   SIGY  = 148 MPa   [UTS 대용 t1]
$   ETAN  = 7.1 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.057 를 넣어라 — DB 파단연신이다.
$   RO    = 1.4e-09 ton/mm^3  [t1]
$   · DB LCP(neat, E=7800, **9% 차**)
$   · UTS 148 · eps 0.057 이 t1. nu 는 DB 가 0.488 로 모델 0.30 과 크게 다르다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
LCP
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900011   1.4e-09      7100       0.3       148       7.1         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ Panel_1187M   (E=1187 MPa · PR=0.3)
$   근거: [2248] Transparent polyimide film, pure PI 25 um (Tsai 2013)  (polymer)
$          DB E = 1100 MPa (모델 대비 -7.3%, t1)
$   SIGY  = 85 MPa   [UTS 대용 t1]
$   ETAN  = 1.187 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   · DB 투명 PI 필름(E=1100, 7% 차)
$   · UTS 85 t1. **연신율이 없어 etan 을 못 만든다** → 항복 후 거의 완전소성으로 둔다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Panel_1187M
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900012         0      1187       0.3        85     1.187         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ SUZY_1520M   (E=1520 MPa · PR=0.4)
$   근거: [1105] Underfill Dexter FP4527, silica-filled epoxy 68 wt% (flip-chip capillary underfill, Hohlfelder 2001)  (composite)
$          DB E = 2000 MPa (모델 대비 +31.6%, t1)
$   SIGY  = 46 MPa   [yield t1]
$   ETAN  = 1.52 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   · **낙하 보강용 도포 수지.** DB Dexter FP4527 언더필(실리카 68 wt% 에폭시)
$   · 기능이 정확히 같다(모세관 언더필은 낙하충격에서 접합부를 보강하려고 바르는 수지다). sigy 46(0.2% 오프셋) · UTS 51 이 **둘 다 t1 실측**이고 298 K 벌크 인장이다. E 는 DB 가 32% 높다. **주의: E=1524 로 0.3% 차인 EME-G770H 는 함정이다**
$   · 그 1524 는 **장기 완화 모듈러스**이고 그 재료의 순간 E 는 16.5 GPa 다. 낙하 속도의 탄성계수와 맞대면 안 되는 값이다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
SUZY_1520M
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900013         0      1520       0.4        46      1.52         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ ZNDC   (E=82000 MPa · PR=0.26)
$   근거: [2370] ZAMAK 3 zinc die casting alloy (ASTM AG-40A, NADCA No. 3, Zn-4Al)  (metal)
$          DB E = 85500 MPa (모델 대비 +4.3%, t2)
$   SIGY  = 221 MPa   [yield t2]
$   ETAN  = 637.2 MPa   [(UTS 283 - SIGY 221)/(eps_u 0.100 - eps_y 0.0027)]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.1 를 넣어라 — DB 파단연신이다.
$   RO    = 6.6e-09 ton/mm^3  [t2]
$   · 아연 다이캐스팅. **36차 AO 가 카탈로그에 아연합금 8종을 넣어 대리재를 걷어냈다**
$   · 직전까지 ADC12(알루미늄)를 공정 계통 대리로 쓰고 있었다.|DB ZAMAK 3(ASTM AG-40A · NADCA No.3)
$   · E=85500(**+4.3%**) · nu=0.27(모델 0.26) 로 **E 와 포아송비가 둘 다 맞는다.** sigy 221 · UTS 283 · eps 0.10 이 전부 t2(NADCA 규격표)다.|ZAMAK 3 을 고른 이유는 **아연 다이캐스팅의 표준 등급**이기 때문이다(전체 주조량의 대부분). 부품이 더 강한 등급이면 ZAMAK 5(sigy 228 · UTS 331) 나 ZAMAK 2(sigy 283 · UTS 359)로 바꿔라
$   · 셋 다 E 와 nu 가 같아 **카드에서 sigy·etan 만 갈면 된다.**|**주의**: NADCA 는 ZAMAK 열의 탄성계수에 숫자를 안 내고 각주로 *"하중 수준에 따라 변한다"* 라 적는다. 85500 은 Eastern Alloys 값이고 NADCA 의 1차근사(68.9 GPa)와 19% 차가 있다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
ZNDC
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900014   6.6e-09     82000      0.26       221    637.17         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ FPCB_CTC_13.4G   (E=13400 MPa · PR=0.4)
$   근거: [255] TAIFLEX 2L FCCL 2UPDR2010JD (adhesiveless polyimide)  (polymer)
$          DB E = 7300 MPa (모델 대비 -45.5%, t1)
$   SIGY  = 504 MPa   [UTS 대용 t1]
$   ETAN  = 13.4 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.85 를 넣어라 — DB 파단연신이다.
$   RO    = 1.42e-09 ton/mm^3  [t3]
$   · 연성 동박적층(FCCL). DB TAIFLEX 2L 무접착 폴리이미드 FCCL
$   · UTS 504 · eps 0.85 가 t1 이다. DB E 가 7300 이라 모델(13400)의 절반인데, 이는 **동박 비율이 다르기 때문**이다
$   · 모델 쪽이 동박이 더 두껍다. **모델 E 를 그대로 두므로 카드는 정합한다.** UTS 504 는 항복이 사실상 안 오는 값이라 낙하에서 탄성처럼 굴 것이다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
FPCB_CTC_13.4G
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900015  1.42e-09     13400       0.4       504      13.4         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ PCB_10G_1   (E=10000 MPa · PR=0.275)
$   근거: [94] FR4 Glass-Epoxy Laminate  (composite)
$          DB E = 21000 MPa (모델 대비 +110.0%, t1)
$   SIGY  = 310 MPa   [UTS 대용 t4]
$   ETAN  = 10 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.02 를 넣어라 — DB 파단연신이다.
$   RO    = 1.9e-09 ton/mm^3  [t1]
$   · PCB 적층판. DB FR4 유리에폭시(E=21 GPa)가 근거다
$   · **모델 E 10 GPa 는 DB 최저 적층판의 절반**이라 수지 비율이 높은 다층 균질화 값으로 보인다. UTS 는 t4(추정)이고 굽힘강도 567 이 t1 이다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
PCB_10G_1
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900016   1.9e-09     10000     0.275       310        10         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ PCB_30G_1   (E=30000 MPa · PR=0.275)
$   근거: [97] BT Resin  (composite)
$          DB E = 28000 MPa (모델 대비 -6.7%, t1)
$   SIGY  = 270 MPa   [UTS 대용 t1]
$   ETAN  = 30 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   FAIL  = 0 (비활성). 파단을 켜려면 0.02 를 넣어라 — DB 파단연신이다.
$   RO    = 2.1e-09 ton/mm^3  [t1]
$   · **E 를 10000 → 30000 으로 고쳤다.** 모델의 명명규칙이 `G`=GPa 인 것이 6/6 성립한다(ZNDC_19G=19000 · MIDSUS_127G=127000 · SOLDER_50G=50000 · BGA40G=40000 · Epoxy_1000M=1000 · FPCB_CTC_13.4G=13400). 그러니 `30G`=30000 이고, 10000 은 PCB_10G_1 에서 복사할 때 안 고친 값이다. 30 GPa 는 물리적으로도 가능하다
$   · DB 프리프레그가 32000(t1), BT 수지가 28000(t1)이다. 근거는 BT 수지(E=28 GPa, -6.7% 차)
$   · UTS 270 · 굽힘 450 이 t1 이다.
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
PCB_30G_1
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900017   2.1e-09     30000     0.275       270        30         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ Glastic   (E=11721 MPa · PR=0.25)
$   근거: [2377] GPO-3 glass-mat polyester laminate, The Gund Company (NEMA LI-1 GPO-3 / IEC 60893 UPGM 203 / MIL-I-24768-6)  (composite)
$          DB E = 11721 MPa (모델 대비 +0.0%, t1)
$   SIGY  = 62.05 MPa   [UTS 대용 t1]
$   ETAN  = 11.72 MPa   [UTS·연신율이 없어 **거의 완전소성**(E/1000)으로 둔다 — 임의값이 아니라 관례다]
$   RO    = 1.8e-09 ton/mm^3  [t1]
$   · Glastic 은 **GPO-3**(유리매트 강화 불포화 폴리에스터) 상표명이다. **36차 AO 가 GPO-3 3종을 카탈로그에 넣어 규격 등급값 카드를 걷어냈다.**|**E 를 1258 → 11721 로 고쳤다**
$   · 이름을 믿는 규칙(zRO2 · PCB_30G_1 과 같다)이고, 이번엔 **DB 의 t1 실측값**으로 고쳤다. 1258 은 폴리에스터 **필름** 대역이라 판재 물성이 아니었다.|근거는 The Gund Company GPO-3 시트
$   · E 11721 · UTS 62.1 · 굽힘 152 가 **전부 t1** 이다. 독립 벤더 4곳이 압축 32.8~33.1 ksi · 비중 1.80~1.83 · CTE 2.0e-5 로 수렴했고, 굽힘강도는 시험법이 갈려도(ASTM D790 152.4 ↔ ISO 178 152.0) 소수점 첫자리까지 맞았다.|**PR 0.25 는 우리가 골랐다**
$   · DB 의 GPO-3 3종에 포아송비가 없다. 모델의 0.40 은 무른 고분자 값이라 유리강화 적층판 대역이 아니다.|**파손 판정은 굽힘강도 152 MPa 로 하라.** SIGY 62.1 은 응력 상한이지 진짜 항복이 아니다(취성 열경화성이다).
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Glastic
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900018   1.8e-09     11721      0.25    62.053    11.721         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$
$------------------------------------------------------------------------------
$ zRO2   (E=179000 MPa · PR=0.31)  — **소성 카드를 만들지 않는다**
$   근거: [131] Zirconia (ZrO2) Ceramic Back  (ceramic), DB E=210000 MPa(+17.3%)
$   · **E 를 179 → 179000 으로 고쳤다.** 같은 파일의 zr02 가 179000 이고 지르코니아는 200 GPa 대역이라 179 쪽이 1000배 오타다. DB Zirconia(ZrO2) Ceramic Back E=210 GPa(t2)와 -15% 차
$   · 등급 차로 설명된다. **취성이라 소성 카드를 만들지 않는다.** 파손은 굽힘강도 1000 MPa(t1)로 판정하라.
$   · 굽힘강도 1000 MPa (t1) — **파손 판정은 이 값으로 하라.**
$   · **취성재라 항복이 정의되지 않는다** — 소성 카드는 물리적으로 틀린다.
$   · *MAT_ELASTIC 유지가 옳다. 파손을 보려면 소성이 아니라 **최대주응력 기준**을 써라.
$
$------------------------------------------------------------------------------
$ sensor   (E=80000 MPa · PR=0.21)  — **소성 카드를 만들지 않는다**
$   근거: [274] Corning Gorilla Glass Victus 2  (ceramic), DB E=79000 MPa(-1.2%)
$   · nu=0.21·E=80 GPa 는 **유리** 대역이다(실리콘은 130~170 GPa). DB Gorilla Glass Victus 2(E=79000, 1.3% 차). **취성이라 소성 카드를 만들지 않는다**
$   · *MAT_ELASTIC 유지가 옳다.
$   · **취성재라 항복이 정의되지 않는다** — 소성 카드는 물리적으로 틀린다.
$   · *MAT_ELASTIC 유지가 옳다. 파손을 보려면 소성이 아니라 **최대주응력 기준**을 써라.
$
$==============================================================================
$ TAPE_1620MPa — **점탄성으로 바꾼다**
$==============================================================================
$   근거: [282] OCA acrylic (Micromachines 2022, doi:10.3390/mi13020301)
$          DMA 5 Hz 스윕이 통째로 t1 이다 — 유리상 E'=1666 MPa(-40 C) · 고무상 0.663 MPa(125 C).
$          **모델의 1620 MPa 는 사실상 이 유리상 값이다**(2.9% 차). 억지값이었다지만 t=0 강성은 맞았다.
$          빠져 있던 것은 **완화**다 — 테이프가 에너지를 먹지 않고 순수 스프링으로 굴었다.
$
$   G0   = 574.6 MPa   [E'_glassy 1666.3 / (2(1+nu))]
$   BULK = 5554 MPa   [E'_glassy / (3(1-2nu))]
$   nu   = 0.45  — **DB 클래스값은 0.49(t4·가정)인데 우리가 0.45 로 낮췄다.**
$          0.49 면 체적탄성률이 3배가 돼 음속이 올라가고 **시간증분이 그만큼 줄어든다.**
$          이건 측정값이 아니라 **수치 선택**이다 — 비압축성을 엄격히 보려면 0.49 로 올려라.
$   RO   = 1.05e-09 ton/mm^3  [아크릴 PSA/OCA 계열값, t4]
$
$   Prony 는 **273.15 K 마스터커브**(같은 논문, t1)다. 이 OCA 의 Tg 가 0 C 라 기준온도가 Tg 다.
$   tau = 2.19e-4 · 1.77e-3 · 0.091 s — **낙하 창(1e-5~5e-3 s)에 그대로 들어온다.** 그래서 이 세트를 골랐다.
$   **유효 범위는 낙하까지다.** 가장 긴 항이 0.091 s 라 그보다 긴 시간은 G_inf 로 굳는다 —
$   실제 고무상은 0.663 MPa 인데 이 카드의 장기값은 그보다 훨씬 크다. **크리프·장기하중에 쓰지 마라.**
$   기준온도가 0 C 라 상온(25 C)에서는 실제 테이프가 이보다 무르다 — **강성 쪽으로 안전한 편이다.**
*MAT_GENERAL_VISCOELASTIC_TITLE
TAPE_1620MPa
$#     mid        ro      bulk       pcf        ef      tref         a         b
    900019  1.05e-09    5554.3         0         0         0         0         0
$#      gi     betai        ki    betaki
    98.254   4566.21         0         0
    127.56   564.972         0         0
    40.968    10.989         0         0
    307.81         0         0         0
$   위 4행 = g1..g3 (합 0.4643) + **장기항 G_inf = 0.5357xG0, BETA=0**.
$   076 은 G(t)=sum(Gi*exp(-BETAi*t)) 라 장기강성을 BETA=0 항으로 넣어야 남는다.
$
$==============================================================================
$ 규격값 카드 — **DB 에 그 등급이 없어 공개 규격의 등급값으로 만들었다.**
$   카탈로그 값이 아니다. 아래 사유에 근거와 한계를 그대로 적었다.
$==============================================================================
$
$==============================================================================
$ A그룹 — 이름만 다르고 이미 검증된 재질. **값은 사용자 검증표 그대로**다.
$   DB 대조를 하지 않았다 — 검증된 값을 우리가 덮을 이유가 없다.
$==============================================================================
$
$ ZNDC_1  ← ZNDC_19G (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
ZNDC_1
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900020         0     19000      0.26       200      1500         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$ SUS_127  ← MIDSUS_127G (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
SUS_127
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900021         0    127000      0.29       450      2000         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$ SUS_127G  ← MIDSUS_127G (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
SUS_127G
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900022         0    127000      0.29       450      2000         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$ Panel-MAT1  ← Panel (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Panel-MAT1
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900023         0      7500       0.3       100       500         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$ Solder-50G  ← SOLDER_50G (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Solder-50G
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900024         0     50000      0.36        35       500         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$ BGA40G.1.1  ← BGA40G (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
BGA40G.1.1
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900025         0     40000      0.36       200      2000         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$ Epoxy_1000M.1.1  ← Epoxy_1000M (E 일치)
*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE
Epoxy_1000M.1.1
$#     mid        ro         e        pr      sigy      etan      fail      tdel
    900026         0      1000      0.35        30       100         0         0
$#       c         p      lcss      lcsr        vp
         0         0         0         0         0
$   · RO 는 0 이다 — 원본 카드의 밀도를 그대로 쓰라는 뜻이다(우리가 모른다).
$
$==============================================================================
$ 카드를 만들지 않은 재질 — 값을 지어내지 않는다
$==============================================================================
