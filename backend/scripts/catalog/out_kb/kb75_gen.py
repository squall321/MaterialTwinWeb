# 75차 KB 수집 배치 산출물 생성기 — Elite Material 카드 없는 34등급을 로컬 43장 전수에서 세운다
#
# 값은 전부 이 파일에 verbatim 으로 박혀 있다(재현 가능). 원문은
#   /data/paper_patent_corpus/standards_appnotes/pcb/EMC_*_Datasheet_*.pdf
# 부재 사유문은 74차 JB 의 `jb74_gen.em_absent_reason()` 을 그대로 불러 쓰고,
# 등급별 실측 행 구성을 KB 가 덧댄다.
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out_jb"))
import jb74_gen as JB   # noqa: E402  — 사유문 생성기 재사용

OUT = os.path.dirname(os.path.abspath(__file__))
BATCH = "75차 KB"
C2K = JB.C2K
LBIN = JB.LBIN                 # 1 lb/in -> N/m
KGCM = 980.665                 # 1 kgf/cm -> N/m  (9.80665 N / 0.01 m)
KNM = 1000.0                   # 1 kN/m -> N/m
MPa, GPa, ppm, prop = JB.MPa, JB.GPa, JB.ppm, JB.prop
EMC_NOTE = JB.EMC_NOTE
URL_BASE = "https://www.emctw.com/upload/website/item/"
LOCAL_DIR = "/data/paper_patent_corpus/standards_appnotes/pcb/"

# `integrity_check.py:bad_verdict_attrs()` 는 이름에 `absent|not_applicable|rejected_printed|
# no_public` 이 든 attribute 를 **전부 판정으로 읽고**, 허용 넷이 아니면 「집계가 모르는 이름」
# 으로 센다. 75차 KB 가 사본 리허설에서 5건을 실제로 만들었다(`*_rows_absent` 세 이름).
# **판정이 아닌 메모에는 `absent` 를 이름에 쓰지 마라** — `vendor_sheet_missing_*` 로 간다.
VERDICT_LIKE = __import__("re").compile(r"absent|not_?applicable|rejected_printed|no_public", 2)
VERDICT_OK = {"core_not_applicable", "core_absent_from_vendor_sheet",
              "core_rejected_printed_value", "core_no_public_document"}

CORE_ABSENT = ["physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
               "thermal.specific_heat", "mechanical.tensile_strength"]

TM = "IPC-TM-650 "

# ─────────────────────────────────────────────────────────────────────────────
# 등급표 — 34장. 전부 `pdftotext -layout` 으로 읽은 인쇄값 verbatim.
#   tg     : [(시험법, ℃)]  — `N/A` 로 인쇄된 DSC 칸은 넣지 않는다
#   cte_z1 : < Tg (alpha1) 구간,  cte_z2 : > Tg (alpha2) 구간
#   t288   : [(시편상태, 분)]  — 전부 부등호 하한(`>`)
#   dk/df  : [(주파수, IPC-TM-650 칸 원문, 시험법, [(수지함량, 값)])]
#   peel   : [(포일, 조건, 값, 단위)]
#   flex   : ("strength"|"modulus", [(방향, 하한, 상한)])  또는 None
# ─────────────────────────────────────────────────────────────────────────────
DK50 = lambda f, v: (f, "2.5.5.9", "—", [("50%", v)])
CAV = "Cavity Resonator"

G = [
 dict(id="EM-285", pair="EM-285B", title="Middle Tg / Lead Free / Halogen Free",
      pdf="EM-285 Datasheet 20240716_24081911650.pdf", local="EMC_EM-285_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 150), ("DMA", 175)], dsc_na=False, dsc_absent=True,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(200, 220), zexp=2.8, td=360,
      t288=[("Clad", 15), ("Etched", 60)], k=0.53, k_method="ASTM D5470",
      dk=[DK50("1MHz", 4.8), DK50("1GHz", 4.2)], df=[DK50("1MHz", 0.007), DK50("1GHz", 0.011)],
      res=True, es=None, db_kv=None, wa=0.11, wa_cond="E-1/105+D24/23",
      peel=[("HTE, H oz", "As Received", 6.5, "lb/in"), ("HTE, H oz", "After Thermal Stress", 6.5, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: LCD, memory module and mobile devices. Halogen, antimony and red phosphorus free. "
           "Low Df with low moisture absorption and excellent CAF resistance. Superior thermal resistance for lead-free "
           "process. FR-4 process friendly and suitable for sequential lamination."),
 dict(id="EM-355(D)", pair="EM-355B(D)", title="Middle Tg / Low Dk / Halogen Free",
      pdf="EM-355(D) Datasheet 20240716_24081911924.pdf", local="EMC_EM-355(D)_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128; IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 155), ("TMA", 150), ("DMA", 175)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(35, 40), cte_z2=(200, 220), zexp=2.8, td=385,
      t288=[("Clad", 60), ("Etched", 60)], k=0.43, k_method="ASTM D5470",
      dk=[("2GHz", CAV, CAV, [("70%", 3.4)])], df=[("2 GHz", CAV, CAV, [("70%", 0.013)])],
      res=True, es=None, db_kv=None, wa=0.10, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.5, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: mobile devices and consumer products. Low Dk for impedance control. "
           "Low moisture absorption. Similar to FR-4 PCB process."),
 dict(id="EM-370(D)", pair="EM-37B(D)", title="High Tg / Upper Mid Loss / Halogen Free",
      pdf="EM-370(D) Datasheet 20240716_24081911319.pdf", local="EMC_EM-370(D)_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 175), ("TMA", 170), ("DMA", 195)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(35, 40), cte_z2=(160, 180), zexp=2.2, td=385,
      t288=[("Clad", 60)], k=0.47, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 4.1)]), ("10 GHz", CAV, CAV, [("50%", 4.0)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.011)]), ("10 GHz", CAV, CAV, [("50%", 0.015)])],
      res=True, es=None, db_kv=None, wa=0.13, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, H oz", "As Received", 4.5, "lb/in"), ("RTF, H oz", "After Thermal Stress", 4.5, "lb/in"),
            ("RTF, 1 oz", "As Received", 5.0, "lb/in"), ("RTF, 1 oz", "After Thermal Stress", 5.0, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: high performance server, network and telecom. Low moisture absorption and excellent "
           "CAF resistance. Standard FR-4 Dk and lower Df. Z-axis CTE: 2.2% (50~260 oC)."),
 dict(id="EM-370(D)-15", pair="EM-37B(D)-15", title="High Tg / Upper Mid Loss / Halogen Free",
      pdf="EM-370(D)-15 Datasheet 20240716_24081911632.pdf", local="EMC_EM-370(D)-15_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 175), ("TMA", 170), ("DMA", 195)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(35, 40), cte_z2=(160, 180), zexp=2.2, td=385,
      t288=[("Clad", 60)], k=0.47, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 4.1)]), ("10 GHz", CAV, CAV, [("50%", 4.0)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.011)]), ("10 GHz", CAV, CAV, [("50%", 0.015)])],
      res=True, es=None, db_kv=None, wa=0.13, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, H oz", "As Received", 4.5, "lb/in"), ("RTF, H oz", "After Thermal Stress", 4.5, "lb/in"),
            ("RTF, 1 oz", "As Received", 5.0, "lb/in"), ("RTF, 1 oz", "After Thermal Stress", 5.0, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: high performance server, network and telecom. Low moisture absorption and excellent "
           "CAF resistance. Standard FR-4 Dk and lower Df. Z-axis CTE: 2.2% (50~260 oC)."),
 dict(id="EM-370(Z)-15", pair="EM-37B(Z)-15", title="High Tg / High Reliability / Halogen Free",
      pdf="EM-370(Z)-15 Datasheet 20240716_24081911740.pdf", local="EMC_EM-370(Z)-15_Datasheet_20240716.pdf",
      slash="IPC-4101 /153, /154; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 190), ("TMA", 180), ("DMA", 210)], dsc_na=False, dsc_absent=False,
      cte_xy=(11, 13), cte_z1=(35, 40), cte_z2=(140, 160), zexp=1.8, td=390,
      t288=[("Clad", 60), ("Etched", 60)], k=0.58, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 4.4), ("70%", 4.0)]),
          ("10 GHz", CAV, CAV, [("50%", 4.2), ("70%", 3.8)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.012), ("70%", 0.014)]),
          ("10 GHz", CAV, CAV, [("50%", 0.015), ("70%", 0.019)])],
      res=True, es=None, db_kv=None, wa=0.14, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.0, "lb/in"), ("HTE, H oz", "After Thermal Stress", 6.0, "lb/in"),
            ("HTE, 1 oz", "As Received", 8.0, "lb/in"), ("HTE, 1 oz", "After Thermal Stress", 8.0, "lb/in")],
      flex=("strength", [("warp", 570, 630), ("fill", 500, 550)]),
      feat="Applications include: automotive, power system, server and heavy copper PCB. Designed for high thermal "
           "reliability with excellent CAF resistance. Very Low Z-axis CTE: 1.8% (50~260 oC). FR-15.1, MOT: 150 oC."),
 dict(id="EM-626", pair="EM-626B", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-626 Datasheet 20240716 (Preliminary)_24081910158.pdf", local="EMC_EM-626_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim="(Preliminary) Datasheet",
      tg=[("TMA", 170), ("DMA", 200)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(35, 40), cte_z2=(140, 160), zexp=1.8, td=430,
      t288=[("Clad", 120), ("Etched", 120)], k=0.49, k_method="ASTM D5470",
      dk=[("1GHz", "2.5.5.9", "—", [("55%", 3.6), ("70%", 3.2)]),
          ("10GHz", CAV, CAV, [("55%", 3.5), ("70%", 3.1)]),
          ("10GHz", "SPC method", "SPC method", [("55%", 3.5), ("70%", 3.1)])],
      df=[("1GHz", "2.5.5.9", "—", [("55%", 0.0034), ("70%", 0.0029)]),
          ("10GHz", CAV, CAV, [("55%", 0.0045), ("70%", 0.0038)]),
          ("10GHz", "SPC method", "SPC method", [("55%", 0.0034), ("70%", 0.0028)])],
      res=True, es=None, db_kv=None, wa=0.09, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, H oz", "As Received", 5.0, "lb/in"), ("HVLP, H oz", "As Received", 4.0, "lb/in")],
      flex=("strength", [("warp", 430, 470), ("fill", 410, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability. Fabrication friendly "
           "resin can be combined with mid-loss resins for \"hybrid\" designs."),
 dict(id="EM-626K", pair="EM-626BK", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-626K Datasheet 20240716 (Preliminary)_24081910784.pdf", local="EMC_EM-626K_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim="(Preliminary) Datasheet",
      tg=[("TMA", 170), ("DMA", 200)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(35, 40), cte_z2=(140, 160), zexp=1.8, td=430,
      t288=[("Clad", 120), ("Etched", 120)], k=0.47, k_method="ASTM D5470",
      dk=[("1GHz", "2.5.5.9", "—", [("55%", 3.2), ("70%", 3.0)]),
          ("10GHz", CAV, CAV, [("55%", 3.1), ("70%", 2.9)]),
          ("10GHz", "SPC method", "SPC method", [("55%", 3.1), ("70%", 2.9)])],
      df=[("1GHz", "2.5.5.9", "—", [("55%", 0.0020), ("70%", 0.0019)]),
          ("10GHz", CAV, CAV, [("55%", 0.0026), ("70%", 0.0025)]),
          ("10GHz", "SPC method", "SPC method", [("55%", 0.0020), ("70%", 0.0019)])],
      res=True, es=None, db_kv=None, wa=0.09, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, H oz", "As Received", 5.0, "lb/in"), ("HVLP, H oz", "As Received", 4.0, "lb/in")],
      flex=("strength", [("warp", 430, 470), ("fill", 410, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability. Fabrication friendly "
           "resin can be combined with mid-loss resins for \"hybrid\" designs."),
 dict(id="EM-825", pair="EM-825B", title="Middle Tg / Low CTE / Lead Free",
      pdf="EM-825 Datasheet 20240716_24081911944.pdf", local="EMC_EM-825_Datasheet_20240716.pdf",
      slash="IPC-4101 /98, /99, /101; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 150), ("TMA", 140), ("DMA", 160)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(240, 250), zexp=3.2, td=340,
      t288=[("Clad", 20), ("Etched", 25)], k=0.46, k_method="ASTM D5470",
      dk=[DK50("1 MHz", 4.9), DK50("1 GHz", 4.4)], df=[DK50("1 MHz", 0.015), DK50("1 GHz", 0.016)],
      res=True, es=40, db_kv=45, wa=0.11, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.5, "lb/in"), ("HTE, H oz", "After Thermal Stress", 6.5, "lb/in"),
            ("HTE, 1 oz", "As Received", 8.5, "lb/in"), ("HTE, 1 oz", "After Thermal Stress", 8.5, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: computer and consumer electronics. Excellent thermal stability for lead-free process. "
           "Low Z-axis CTE: < 3.5% (50~260 oC)."),
 dict(id="EM-825(I)", pair="EM-825B(I)", title="Middle Tg / CAF Resistance / Lead Free",
      pdf="EM-825(I) Datasheet 20240716_24081914837.pdf", local="EMC_EM-825(I)_Datasheet_20240716.pdf",
      slash="IPC-4101 /98, /99, /101; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 150), ("TMA", 140), ("DMA", 160)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(240, 250), zexp=3.2, td=340,
      t288=[("Clad", 20), ("Etched", 25)], k=0.46, k_method="ASTM D5470",
      dk=[DK50("1 MHz", 4.9), DK50("1 GHz", 4.4)], df=[DK50("1 MHz", 0.015), DK50("1 GHz", 0.016)],
      res=True, es=40, db_kv=45, wa=0.11, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.5, "lb/in"), ("HTE, H oz", "After Thermal Stress", 6.5, "lb/in"),
            ("HTE, 1 oz", "As Received", 8.5, "lb/in"), ("HTE, 1 oz", "After Thermal Stress", 8.5, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: automotive, computer and consumer electronics. Designed for high thermal reliability "
           "with excellent CAF resistance. Low Z-axis CTE: < 3.5% (50~260 oC)."),
 dict(id="EM-827", pair="EM-827B", title="High Tg / Low CTE / Lead Free",
      pdf="EM-827 Datasheet 20240716_24081911198.pdf", local="EMC_EM-827_Datasheet_20240716.pdf",
      slash="IPC-4101 /98, /99, /101, /126; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 175), ("TMA", 160), ("DMA", 185)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(200, 220), zexp=2.6, td=350,
      t288=[("Clad", 25), ("Etched", 30)], k=0.44, k_method="ASTM D5470",
      dk=[DK50("1 MHz", 4.8), DK50("1 GHz", 4.3)], df=[DK50("1 MHz", 0.018), DK50("1 GHz", 0.019)],
      res=True, es=40, db_kv=45, wa=0.15, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.5, "lb/in"), ("HTE, H oz", "After Thermal Stress", 6.5, "lb/in"),
            ("HTE, 1 oz", "As Received", 8.5, "lb/in"), ("HTE, 1 oz", "After Thermal Stress", 8.5, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: server, computer, consumer clectronics (원문 오식). Excellent thermal stability for "
           "lead-free process. Low Z-axis CTE < 3.0% (50~260 oC)."),
 dict(id="EM-827(I)", pair="EM-827B(I)", title="High Tg / CAF Resistance / Lead Free",
      pdf="EM-827(I) Datasheet 20240716_24081911720.pdf", local="EMC_EM-827(I)_Datasheet_20240716.pdf",
      slash="IPC-4101 /98, /99, /101, /126; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("DSC", 175), ("TMA", 160), ("DMA", 185)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(200, 220), zexp=2.6, td=350,
      t288=[("Clad", 25), ("Etched", 30)], k=0.44, k_method="ASTM D5470",
      dk=[DK50("1 MHz", 4.8), DK50("1 GHz", 4.3)], df=[DK50("1 MHz", 0.018), DK50("1 GHz", 0.019)],
      res=True, es=40, db_kv=45, wa=0.15, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.5, "lb/in"), ("HTE, H oz", "After Thermal Stress", 6.5, "lb/in"),
            ("HTE, 1 oz", "As Received", 8.5, "lb/in"), ("HTE, 1 oz", "After Thermal Stress", 8.5, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: automotive, server, computer and consumer electronics. Designed for high thermal "
           "reliability with excellent CAF resistance. Low Z-axis CTE: < 3.0% (50~260 oC)."),
 dict(id="EM-828G", pair="EM-828BG", title="High Tg / Lower Mid Loss / Halogen Free",
      pdf="EM-828G Datasheet 20240716_24081911465.pdf", local="EMC_EM-828G_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /240, /540", rev="Rev: 2023 Nov.", year=2023, prelim=None,
      tg=[("DSC", 170), ("TMA", 160), ("DMA", 190)], dsc_na=False, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(220, 240), zexp=2.6, td=380,
      t288=[("Clad", 20)], k=0.48, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 3.9)]), ("10 GHz", CAV, CAV, [("50%", 3.8)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.008)]), ("10 GHz", CAV, CAV, [("50%", 0.011)])],
      res=True, es=None, db_kv=None, wa=0.08, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, H oz", "As Received", 3.5, "lb/in"), ("RTF, H oz", "After Thermal Stress", 3.5, "lb/in"),
            ("RTF, 1 oz", "As Received", 4.0, "lb/in"), ("RTF, 1 oz", "After Thermal Stress", 4.0, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 400, 450)]),
      feat="Applications include: high-speed server, network and telecom. Designed for excellent CAF resistance."),
 dict(id="EM-888K", pair="EM-888BK", title="High Tg / Very Low Loss / Halogen Free",
      pdf="EM-888K Datasheet 20240716_24081911867.pdf", local="EMC_EM-888K_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 170), ("DMA", 210)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(220, 240), zexp=2.4, td=390,
      t288=[("Clad", 60)], k=0.48, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 3.3)]), ("10 GHz", CAV, CAV, [("50%", 3.2)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.0047)]), ("10 GHz", CAV, CAV, [("50%", 0.0062)])],
      res=True, es=None, db_kv=None, wa=0.1, wa_cond="E-1/105+D-24/23",
      peel=[("VLP, H oz", "As Received", 4.8, "lb/in"), ("HVLP, H oz", "As Received", 4.1, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: high-speed server, network and telecom. Designed for excellent CAF resistance."),
 dict(id="EM-888(S)", pair="EM-888B(S)", title="High Tg / Low Loss / Halogen Free",
      pdf="EM-888(S) Datasheet 20240716_24081911419.pdf", local="EMC_EM-888(S)_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 170), ("DMA", 210)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(220, 240), zexp=2.4, td=390,
      t288=[("Clad", 60)], k=0.50, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 3.8)]), ("10 GHz", CAV, CAV, [("50%", 3.7)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.0055)]), ("10 GHz", CAV, CAV, [("50%", 0.0073)])],
      res=True, es=None, db_kv=None, wa=0.1, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.3, "lb/in"), ("VLP, H oz", "As Received", 4.8, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: high-speed server, network and telecom. Designed for excellent CAF resistance."),
 dict(id="EM-888(S)(A)", pair="EM-888B(S)(A)", title="High Tg / Low Loss / Halogen Free",
      pdf="EM-888(S)(A) Datasheet 20240716_24081911319.pdf", local="EMC_EM-888(S)(A)_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 170), ("DMA", 210)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 15), cte_z1=(40, 45), cte_z2=(220, 240), zexp=2.4, td=390,
      t288=[("Clad", 60)], k=0.50, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 3.8)]), ("10 GHz", CAV, CAV, [("50%", 3.7)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.0055)]), ("10 GHz", CAV, CAV, [("50%", 0.0073)])],
      res=True, es=None, db_kv=None, wa=0.1, wa_cond="E-1/105+D-24/23",
      peel=[("HTE, H oz", "As Received", 6.3, "lb/in"), ("VLP, H oz", "As Received", 4.8, "lb/in")],
      flex=("strength", [("warp", 510, 570), ("fill", 450, 500)]),
      feat="Applications include: high-speed server, network and telecom. Designed for excellent CAF resistance."),
 dict(id="EM-890K", pair="EM-89BK", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-890K Datasheet- 20240716_24081910711.pdf", local="EMC_EM-890K_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 170), ("DMA", 205)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(45, 50), cte_z2=(185, 205), zexp=2.2, td=430,
      t288=[("Clad", 60), ("Etched", 60)], k=0.47, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.1), ("70%", 2.9)]),
          ("10 GHz", CAV, CAV, [("55%", 3.0), ("70%", 2.8)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 3.0), ("70%", 2.8)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0019), ("70%", 0.0018)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0025), ("70%", 0.0024)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0019), ("70%", 0.0018)])],
      res=True, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP, H oz", "As Received", 4.5, "lb/in")],
      flex=("strength", [("warp", 430, 470), ("fill", 410, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability."),
 dict(id="EM-890K(A)", pair="EM-89BK(A)", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-890K(A) Datasheet 20240716_24081910828.pdf", local="EMC_EM-890K(A)_Datasheet_20240716.pdf",
      slash="IPC 4101 /134; IPC-4103 /230, /530 (원문이 첫 규격을 하이픈 없이 인쇄한다)",
      rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 170), ("DMA", 205)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(45, 50), cte_z2=(185, 205), zexp=2.2, td=430,
      t288=[("Clad", 60), ("Etched", 60)], k=0.47, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.1), ("70%", 2.9)]),
          ("10 GHz", CAV, CAV, [("55%", 3.0), ("70%", 2.8)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 3.0), ("70%", 2.8)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0019), ("70%", 0.0018)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0025), ("70%", 0.0024)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0019), ("70%", 0.0018)])],
      res=True, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP, H oz", "As Received", 4.5, "lb/in")],
      flex=("strength", [("warp", 430, 470), ("fill", 410, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability."),
 dict(id="EM-891K", pair="EM-891BK", title="High Tg / Ultra Low Loss / Halogenated",
      pdf="EM-891K Datasheet 20240716_24081910428.pdf", local="EMC_EM-891K_Datasheet_20240716.pdf",
      slash="IPC-4101 /102; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 170), ("DMA", 205)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(40, 45), cte_z2=(180, 200), zexp=2.2, td=400,
      t288=[("Clad", 60), ("Etched", 60)], k=0.47, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.2), ("70%", 3.0)]),
          ("10 GHz", CAV, CAV, [("55%", 3.1), ("70%", 3.0)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 3.1), ("70%", 3.0)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0024), ("70%", 0.0025)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0032), ("70%", 0.0033)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0024), ("70%", 0.0025)])],
      res=True, es=None, db_kv=None, wa=0.10, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP, H oz", "As Received", 4.0, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 400, 450)]),
      feat="Applications include: high-speed Ethernet, network and telecom. Designed for high thermal reliability with "
           "excellent CAF resistance. Outstanding multiple lamination capability. **이 등급만 Halogenated 다** — "
           "형제 K 등급들과 달리 할로겐프리가 아니다."),
 dict(id="EM-892K", pair="EM-892BK", title="High Tg / Extreme Low Loss / Halogen Free",
      pdf="EM-892K Datasheet 20240716_24081910361.pdf", local="EMC_EM-892K_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 180), ("DMA", 215)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(40, 45), cte_z2=(185, 205), zexp=1.8, td=420,
      t288=[("Clad", 60), ("Etched", 60)], k=0.46, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.11), ("70%", 2.93)]),
          ("10 GHz", CAV, CAV, [("55%", 3.00), ("70%", 2.84)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 3.00), ("70%", 2.84)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0014), ("70%", 0.0012)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0019), ("70%", 0.0017)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0015), ("70%", 0.0013)])],
      res=True, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP3, H oz", "As Received", 3.5, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 400, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability."),
 dict(id="EM-892K(A)", pair="EM-892BK(A)", title="High Tg / Extreme Low Loss / Halogen Free",
      pdf="EM-892K(A) Datasheet-20240716_24101109565.pdf", local="EMC_EM-892K(A)_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 180), ("DMA", 215)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(40, 45), cte_z2=(185, 205), zexp=1.8, td=420,
      t288=[("Clad", 60), ("Etched", 60)], k=0.46, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.11), ("70%", 2.93)]),
          ("10 GHz", CAV, CAV, [("55%", 3.00), ("70%", 2.84)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 3.00), ("70%", 2.84)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0014), ("70%", 0.0012)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0019), ("70%", 0.0017)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0015), ("70%", 0.0013)])],
      res=True, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP3, H oz", "As Received", 3.5, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 400, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability."),
 dict(id="EM-892K2", pair="EM-892BK2", title="High Tg / Extreme Low Loss / Halogen Free",
      pdf="EM-892K2 Datasheet 20240716_24081910964.pdf", local="EMC_EM-892K2_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 180), ("DMA", 215)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(40, 45), cte_z2=(185, 205), zexp=1.8, td=420,
      t288=[("Clad", 60), ("Etched", 60)], k=0.46, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.00), ("70%", 2.85)]),
          ("10 GHz", CAV, CAV, [("55%", 2.90), ("70%", 2.76)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 2.90), ("70%", 2.76)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0010), ("70%", 0.0010)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0014), ("70%", 0.0013)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0011), ("70%", 0.0010)])],
      res=True, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP3, H oz", "As Received", 3.5, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 400, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability."),
 dict(id="EM-892K2(A)", pair="EM-892BK2(A)", title="High Tg / Extreme Low Loss / Halogen Free",
      pdf="EM-892K2(A) Datasheet 20240716_24081910160.pdf", local="EMC_EM-892K2(A)_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 180), ("DMA", 215)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(40, 45), cte_z2=(185, 205), zexp=1.8, td=420,
      t288=[("Clad", 60), ("Etched", 60)], k=0.46, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.00), ("70%", 2.85)]),
          ("10 GHz", CAV, CAV, [("55%", 2.90), ("70%", 2.76)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 2.90), ("70%", 2.76)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0010), ("70%", 0.0010)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0014), ("70%", 0.0013)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0011), ("70%", 0.0010)])],
      res=False, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP3, H oz", "As Received", 3.5, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 400, 450)]),
      feat="Applications include: high-speed Ethernet, network, HPC, AI, 5G and antenna. Designed for high thermal "
           "reliability with excellent CAF resistance. Outstanding multiple lamination capability."),
 dict(id="EM-A30", pair="EM-A3B", title="High Tg / High Voltage / Halogen Free",
      pdf="EM-A30 Datasheet 20250416_25042814428.pdf", local="EMC_EM-A30_Datasheet_20250416.pdf",
      slash="IPC-4101 /153, /154; IPC-4103 /250, /550", rev="Rev: 2025 April.", year=2025,
      prelim="Preliminary Datasheet",
      tg=[("DSC", 190), ("TMA", 185), ("DMA", 220)], dsc_na=False, dsc_absent=False,
      cte_xy=(11, 13), cte_z1=(30, 35), cte_z2=(140, 160), zexp=1.7, td=405,
      t288=[("Clad", 120), ("Etched", 120)], k=0.58, k_method="ASTM D5470",
      dk=[("1GHz", "2.5.5.9", "—", [("50%", 4.3), ("70%", 3.8)]),
          ("10GHz", CAV, CAV, [("50%", 4.1), ("70%", 3.7)])],
      df=[("1GHz", "2.5.5.9", "—", [("50%", 0.010), ("70%", 0.011)]),
          ("10GHz", CAV, CAV, [("50%", 0.013), ("70%", 0.015)])],
      res=True, es=40, db_kv=45, wa=0.16, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, 1.0 oz", "As Received", 4.5, "lb/in")],
      flex=("strength", [("warp", 450, 510), ("fill", 450, 500)]),
      feat="Applications Include: Automotive ECU, Power System, Heavy Copper. Designed for High Thermal Reliability "
           "with Excellent CAF Resistance (1500V). Very Low Z-axis CTE: 1.7% (50~260 °C). FR-15.1, MOT: 150 °C; "
           "CTI PLC1."),
 dict(id="EM-A50", pair="EM-A5B", title="Low Loss / Very Low CTE / Halogen Free",
      pdf="EM-A50 Datasheet 20240716_24081910273.pdf", local="EMC_EM-A50_Datasheet_20240716.pdf",
      slash="IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 230), ("DMA", 260)], dsc_na=True, dsc_absent=False,
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(120, 140), zexp=1.3, td=430,
      t288=[("Clad", 60), ("Etched", 60)], k=0.60, k_method="ASTM D5470",
      dk=[("10GHz", CAV, CAV, [("50%", 3.9), ("70%", 3.4)])],
      df=[("10GHz", CAV, CAV, [("50%", 0.007), ("70%", 0.008)])],
      res=True, es=40, db_kv=40, wa=0.12, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, 0.5 oz", "As Received", 5.5, "lb/in"), ("RTF, 1.0 oz", "As Received", 6.0, "lb/in")],
      flex=("modulus", [("warp", 24, 26), ("fill", 23, 25)]),
      feat="Applications include: automotive and other higher performance requirements. Designed for high thermal "
           "reliability with excellent CAF resistance. Lower Dk/Df value, excellent electrical performance. "
           "Very low Z-axis CTE: 1.3% (50~260 °C)."),
 dict(id="EM-A56", pair="EM-A56B", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-A56 Datasheet 20250214_25022715405.pdf", local="EMC_EM-A56_Datasheet_20250214.pdf",
      slash="IPC-4101 /134; IPC-4103 /240, /540", rev="Rev: 2025 February", year=2025, prelim=None,
      tg=[("TMA", 170), ("DMA", 200)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(35, 40), cte_z2=(140, 160), zexp=1.8, td=425,
      t288=[("Clad", 120), ("Etched", 120)], k=0.50, k_method="ASTM D5470",
      dk=[("10 GHz", CAV, CAV, [("50%", 3.7), ("70%", 3.2)])],
      df=[("10 GHz", CAV, CAV, [("50%", 0.005), ("70%", 0.004)])],
      res=True, es=40, db_kv=40, wa=0.10, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, 1 oz", "As Received", 4.5, "lb/in")],
      flex=("strength", [("warp", 430, 470), ("fill", 410, 450)]),
      feat="Applications Include: Autonomous Driving System, Networking, and High Speed Applications. Ultra Low "
           "Transmission Loss Material. Designed for High Thermal Reliability with Excellent CAF Resistance. "
           "Outstanding multiple lamination capability."),
 dict(id="EM-A56K", pair="EM-A56BK", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-A56K Datasheet 20250214_25033113269.pdf", local="EMC_EM-A56K_Datasheet_20250214.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2025 February", year=2025, prelim=None,
      tg=[("TMA", 170), ("DMA", 200)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(35, 40), cte_z2=(140, 160), zexp=1.8, td=425,
      t288=[("Clad", 120), ("Etched", 120)], k=0.48, k_method="ASTM D5470",
      dk=[("10 GHz", CAV, CAV, [("50%", 3.2), ("70%", 3.0)])],
      df=[("10 GHz", CAV, CAV, [("50%", 0.0029), ("70%", 0.0027)])],
      res=True, es=40, db_kv=40, wa=0.10, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, 1 oz", "As Received", 4.5, "lb/in")],
      flex=("strength", [("warp", 430, 470), ("fill", 410, 450)]),
      feat="Applications Include: Autonomous Driving System, Networking, and High Speed Applications. Ultra Low "
           "Transmission Loss Material. Designed for High Thermal Reliability with Excellent CAF Resistance. "
           "Outstanding multiple lamination capability."),
 dict(id="EM-A70K", pair=None, title="Radio Frequency / Extreme-low Loss / Halogen Free",
      pdf="EM-A70K Datasheet (Preliminary) 20250225_25033113302.pdf", local="EMC_EM-A70K_Datasheet_20250225.pdf",
      slash="IPC-4103 /240", rev="Rev: 2025 Feb.", year=2025, prelim="Preliminary Datasheet",
      tg=[("TMA", 170), ("DMA", 200)], dsc_na=True, dsc_absent=False,
      cte_xy=(19, 21), cte_xy_note="원문 행이름이 `CTE, X/Y-axis (5 mil)` 이다 — **5 mil 구성 한정 값**이다.",
      cte_z1=(35, 40), cte_z2=(140, 160), zexp=1.8, td=360,
      t288=[("Clad", 120), ("Etched", 120)], k=0.45, k_method="ASTM D5470",
      dk=[("10 GHz", "2.5.5.13", "—", [("5 mil 구성", 3.1)])],
      df=[("10 GHz", "2.5.5.13", "—", [("5 mil 구성", 0.0018)])],
      res=True, es=None, db_kv=None, wa=0.13, wa_cond="E-1/105+D-24/23",
      peel=[("HVLP3, 1 oz", "As Received", 4.5, "lb/in"), ("HVLP3, H oz", "As Received", 3.5, "lb/in")],
      flex=None,
      feat="Applications Include: Base Station and Satellite Antenna, Automotive Radar. Glass-Reinforced with Excellent "
           "Stability over Frequency and Temperature. Extreme-Low Transmission Loss Performance."),
 dict(id="EM-S370(Z)", pair="EM-S37B(Z)", title="High Reliability / Halogen Free",
      pdf="EM-S370(Z) Datasheet 20240716_24081910748.pdf", local="EMC_EM-S370Z_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 180), ("DMA", 210)], dsc_na=True, dsc_absent=False,
      cte_xy=(11, 13), cte_z1=(35, 40), cte_z2=(140, 160), zexp=None, td=390,
      t288=[("Clad", 60), ("Etched", 60)], k=0.58, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 4.4), ("70%", 4.0)]),
          ("10 GHz", CAV, CAV, [("50%", 4.2), ("70%", 3.8)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.012), ("70%", 0.014)]),
          ("10 GHz", CAV, CAV, [("50%", 0.015), ("70%", 0.019)])],
      res=True, es=None, db_kv=None, wa=0.14, wa_cond="E-1/105+D-24/23",
      peel=[("VLP, 12 um", "As Received", 0.9, "kg/cm")],
      flex=("modulus", [("warp", 22, 24), ("fill", 20, 23)]),
      feat="Applications include: W/B, CSP, BGA, FC PKG, SiP, module and coreless. High heat resistance and excellent "
           "CAF resistance. Halogen free for IC packaging."),
 dict(id="EM-S376", pair="EM-S376B", title="Low Loss / Low CTE / Halogen Free",
      pdf="EM-S376 Datasheet 20241231_25022715242.pdf", local="EMC_EM-S376_Datasheet_20241231.pdf",
      slash="IPC-4103 /240, /540", rev="Rev: 2024 Dec.", year=2024, prelim=None,
      tg=[("TMA", 210), ("DMA", 240)], dsc_na=True, dsc_absent=False,
      cte_xy=(11, 12), cte_z1=(30, 35), cte_z2=(130, 150), zexp=None, td=430,
      t288=[("Clad", 60), ("Etched", 60)], k=0.59,
      k_method="ASTM D5470 (원문의 `Test Condition` 칸은 비어 있다)",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 4.0), ("70%", 3.5)]),
          ("10GHz", CAV, CAV, [("50%", 3.9), ("70%", 3.4)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.005), ("70%", 0.006)]),
          ("10GHz", CAV, CAV, [("50%", 0.007), ("70%", 0.008)])],
      res=True, es=None, db_kv=None, wa=0.12, wa_cond="E-1/105+D-24/23",
      peel=[("VLP, 12 um", "As Received", 0.9, "kg/cm")],
      flex=("modulus", [("warp", 23, 25), ("fill", 22, 24)]),
      feat="Applications include: W/B, CSP, BGA, FC PKG, SiP, module and coreless. High heat resistance and excellent "
           "CAF resistance. Low Df for better signal integrity and flexible circuit design. Low CTE for anti-warpage "
           "solution of IC substrate."),
 dict(id="EM-S526", pair="EM-S526B", title="Low Loss / Low CTE / Halogen Free",
      pdf="EM-S526 Datasheet 20240716_24081910195.pdf", local="EMC_EM-S526_Datasheet_20240716.pdf",
      slash="IPC-4103 /240, /540", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 230), ("DMA", 260)], dsc_na=True, dsc_absent=False,
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(120, 140), zexp=None, td=430,
      t288=[("Clad", 60), ("Etched", 60)], k=0.60,
      k_method="ASTM D5470 (원문의 `Test Condition` 칸은 비어 있다)",
      dk=[("1 GHz", "2.5.5.9", "—", [("50%", 4.0), ("70%", 3.5)]),
          ("10GHz", CAV, CAV, [("50%", 3.9), ("70%", 3.4)])],
      df=[("1 GHz", "2.5.5.9", "—", [("50%", 0.005), ("70%", 0.006)]),
          ("10GHz", CAV, CAV, [("50%", 0.007), ("70%", 0.008)])],
      res=True, es=None, db_kv=None, wa=0.12, wa_cond="E-1/105+D-24/23",
      peel=[("VLP, 12 um", "As Received", 0.9, "kg/cm")],
      flex=("modulus", [("warp", 24, 26), ("fill", 23, 25)]),
      feat="Applications include: W/B, CSP, BGA, FC PKG, SiP, module and coreless. High heat resistance and excellent "
           "CAF resistance. Low Df for better signal integrity and flexible circuit design. Low CTE for anti-warpage "
           "solution of IC substrate."),
 dict(id="EM-S530", pair="EM-S53B", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-S530 Datasheet 20240716_24081910796.pdf", local="EMC_EM-S530_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 235), ("DMA", 260)], dsc_na=True, dsc_absent=False,
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(120, 140), zexp=None, td=445,
      t288=[("Clad", 60), ("Etched", 60)], k=0.83, k_method="ASTM D5470",
      dk=[("1GHz", "2.5.5.9", "—", [("50%", 3.78), ("70%", 3.26)]),
          ("10GHz", CAV, CAV, [("50%", 3.65), ("70%", 3.16)])],
      df=[("1GHz", "2.5.5.9", "—", [("50%", 0.0039), ("70%", 0.0032)]),
          ("10GHz", CAV, CAV, [("50%", 0.0052), ("70%", 0.0042)])],
      res=True, es=None, db_kv=None, wa=0.11, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, 18 um", "As Received", 0.8, "kg/cm"), ("3 um plated to 36 um", "As Received", 0.9, "kg/cm")],
      flex=("modulus", [("warp", 22, 24), ("fill", 21, 23)]),
      feat="Suitable for high-speed and high frequency applications like mmWave and AiP. Excellent dielectric "
           "properties. High heat resistance and high thermal reliability capability. High peel strength with low "
           "profile copper foil."),
 dict(id="EM-S530K", pair="EM-S53BK", title="High Tg / Ultra Low Loss / Halogen Free",
      pdf="EM-S530K Datasheet 20240716_24081910807.pdf", local="EMC_EM-S530K_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim=None,
      tg=[("TMA", 235), ("DMA", 260)], dsc_na=True, dsc_absent=False,
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(120, 140), zexp=None, td=445,
      t288=[("Clad", 60), ("Etched", 60)], k=0.83, k_method="ASTM D5470",
      dk=[("1GHz", "2.5.5.9", "—", [("50%", 3.36), ("70%", 3.05)]),
          ("10GHz", CAV, CAV, [("50%", 3.24), ("70%", 2.95)])],
      df=[("1GHz", "2.5.5.9", "—", [("50%", 0.0021), ("70%", 0.0021)]),
          ("10GHz", CAV, CAV, [("50%", 0.0028), ("70%", 0.0027)])],
      res=True, es=None, db_kv=None, wa=0.11, wa_cond="E-1/105+D-24/23",
      peel=[("RTF, 18 um", "As Received", 0.8, "kg/cm"), ("3 um plated to 36 um", "As Received", 0.9, "kg/cm")],
      flex=("modulus", [("warp", 22, 24), ("fill", 21, 23)]),
      feat="Suitable for high-speed and high frequency applications like mmWave and AiP. Excellent dielectric "
           "properties. High heat resistance and high thermal reliability capability. High peel strength with low "
           "profile copper foil."),
 dict(id="EM-S532K", pair="EM-S532BK", title="High Tg / Extreme Low Loss / Halogen Free",
      pdf="EM-S532K Datasheet (Preliminary) 20240716_24100810769.pdf", local="EMC_EM-S532K_Datasheet_20240716.pdf",
      slash="IPC-4101 /134; IPC-4103 /230, /530", rev="Rev: 2024 July", year=2024, prelim="Preliminary Datasheet",
      tg=[("TMA", 180), ("DMA", 215)], dsc_na=True, dsc_absent=False,
      cte_xy=(12, 13), cte_z1=(40, 45), cte_z2=(185, 205), zexp=1.8, td=420,
      t288=[("Clad", 60), ("Etched", 60)], k=0.46, k_method="ASTM D5470",
      dk=[("1 GHz", "2.5.5.9", "—", [("55%", 3.11), ("70%", 2.93)]),
          ("10 GHz", CAV, CAV, [("55%", 3.00), ("70%", 2.84)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 3.00), ("70%", 2.84)])],
      df=[("1 GHz", "2.5.5.9", "—", [("55%", 0.0014), ("70%", 0.0012)]),
          ("10 GHz", CAV, CAV, [("55%", 0.0019), ("70%", 0.0017)]),
          ("10 GHz", "SPC method", "SPC method", [("55%", 0.0015), ("70%", 0.0013)])],
      res=False, es=None, db_kv=None, wa=0.07, wa_cond="E-1/105+D-24/23",
      peel=[("LP, H oz", "As Received", 0.6, "kN/m")],
      flex=None,
      feat="Applications Include: mmWave and package (antenna, Front-end module). Multiple lamination and high thermal "
           "reliability applications. Excellent dielectric properties (extreme low Df and Dk)."),
 dict(id="EM-S570", pair="EM-S57B", title="High Modulus / Ultra Low CTE / Halogen Free",
      pdf="EM-S570 Datasheet (Preliminary) 20240716_24081910822.pdf",
      local="EMC_EM-S570_Datasheet_Preliminary_20240716.pdf",
      slash="IPC-4103 /250, /550", rev="Rev: 2024 July", year=2024, prelim="Preliminary Datasheet",
      tg=[("TMA", 280), ("DMA", 320)], dsc_na=False, dsc_absent=True,
      cte_xy=(4, 6), cte_z1=(8, 13), cte_z2=(70, 90), zexp=None, td=440,
      t288=[("Clad", 120), ("Etched", 120)], k=0.59, k_method="ASTM D5470",
      dk=[("1GHz", "2.5.5.9", "—", [("50%", 4.5)])], df=[("1GHz", "2.5.5.9", "—", [("50%", 0.006)])],
      res=True, es=None, db_kv=None, wa=None, wa_cond=None,
      peel=[("RTF, 18 um", "As Received", 0.9, "kg/cm")],
      flex=("modulus", [("warp", 30, 32)]),
      feat="Applications Include: FC-CSP/BGA, PoP, SiP. Compatible with multiple lamination and high thermal "
           "reliability applications. Ultra low CTE in X/Y direction."),
]

PEEL_CONV = {"lb/in": (LBIN, "175.126835"), "kg/cm": (KGCM, "980.665"), "kN/m": (KNM, "1000")}


def row_list(g):
    """이 등급 시트의 실측 행 구성 — 사유문 덧댐과 카드 attributes 에 같이 쓴다."""
    r = ["Tg(" + ("DSC=N/A · " if g["dsc_na"] else ("" if g["dsc_absent"] else "DSC · ")) + "TMA · DMA)",
         "CTE X/Y", "CTE Z(<Tg, >Tg)"]
    if g["zexp"] is not None:
        r.append("Z-axis Expansion")
    r += ["Td", "T288(" + " · ".join(s for s, _ in g["t288"]) + ")", "Thermal Conductivity", "Dk", "Df"]
    if g["res"]:
        r += ["Volume Resistivity", "Surface Resistivity"]
    if g["es"]:
        r += ["Electric Strength", "Dielectric Breakdown"]
    if g["wa"] is not None:
        r.append("Water Absorption")
    r.append("Peel Strength")
    if g["flex"]:
        r.append("Flexural " + ("Modulus" if g["flex"][0] == "modulus" else "Strength"))
    r.append("Flame Resistance")
    return r


def kb_reason(g, key):
    """74차 JB 의 사유문 생성기를 그대로 부르고, 등급별 실측 행 구성을 KB 가 덧댄다."""
    stub = {"local": LOCAL_DIR + g["local"], "id": g["id"], "pair": g["pair"] or g["id"],
            "flex_mod": g["flex"] and g["flex"][0] == "modulus"}
    base = JB.em_absent_reason(stub, key)
    extra = ("\n\n**[75차 KB 등급별 실측]** 위 행 목록은 74차 JB 가 쓴 **이 벤더의 표준 행 구성**이다. "
             "이 등급 시트의 실제 행은 이렇다 — " + " · ".join(row_list(g)) + ". ")
    if not g["flex"]:
        extra += ("**이 등급은 굽힘 행이 아예 없다**(43장 중 `EM-A70K`·`EM-S532K` 둘뿐이다) — "
                  "JB 사유문의 `Flexural Strength` 서술은 이 등급에 해당하지 않는다. ")
    if g["prelim"]:
        extra += "**원문이 `" + g["prelim"] + "` 로 인쇄된 잠정판이라 개정 시 행이 바뀔 수 있다.** "
    extra += ("75차 KB 가 같은 43장을 다시 낱말 단위로 훑었고 결과가 같다 — "
              "`density` 0장 · `gravity` 0장 · `specific heat` 0장 · `Young` 0장 · `tensile` 0장 · `Poisson` 0장.")
    return base + extra


def build_props(g):
    P = []
    vb = "원문 verbatim"
    L = LOCAL_DIR + g["local"]

    # ── Tg ────────────────────────────────────────────────────────────────
    dsc_note = (" **같은 표의 DSC 칸은 `N/A` 로 인쇄돼 있어 행을 만들지 않았다.**" if g["dsc_na"]
                else (" **이 시트에는 DSC 행 자체가 없다.**" if g["dsc_absent"] else ""))
    for meth, v in g["tg"]:
        std = {"DSC": TM + "2.4.25", "TMA": TM + "2.4.24", "DMA": TM + "2.4.24.4"}[meth]
        P.append(prop("thermal.glass_transition", round(v + C2K, 2), "K", 1,
                      {"method_detail": meth, "test_standard": std, "test_mode": "thermal transition (" + meth + ")"},
                      vb + ": `Tg | " + str(v) + " | oC | " + meth + " | " + std.replace(TM, "") + "`. 환산 " +
                      str(v) + " ℃ + 273.15 = " + str(round(v + C2K, 2)) + " K." + dsc_note +
                      " 시험법이 다른 행은 평균 내지 않고 따로 넣었다."))

    # ── CTE X/Y ───────────────────────────────────────────────────────────
    xy_note = g.get("cte_xy_note") or ""
    for ax, v in (("X", g["cte_xy"][0]), ("Y", g["cte_xy"][1])):
        P.append(prop("thermal.expansion_linear", ppm(v), "1/K", 1,
                      {"axis": "in-plane (" + ax + ")", "regime": "below Tg (alpha1)",
                       "method_detail": "TMA", "test_standard": TM + "2.4.24.5",
                       "test_mode": "thermomechanical analysis"},
                      vb + ": `CTE, X/Y-axis | " + str(g["cte_xy"][0]) + "/" + str(g["cte_xy"][1]) +
                      " | ppm/ oC | < Tg, TMA`. 원문이 `X/Y` 를 슬래시로 갈라 인쇄하므로 두 축을 두 행으로 나눴다. "
                      "환산 " + str(v) + " ppm/℃ x 1e-6 = " + repr(ppm(v)) + " 1/K. " + xy_note))

    # ── CTE Z ─────────────────────────────────────────────────────────────
    for reg, (lo, hi), lbl in (("below Tg (alpha1)", g["cte_z1"], "< Tg, TMA"),
                               ("above Tg (alpha2)", g["cte_z2"], "> Tg, TMA")):
        for b, v in (("lower", lo), ("upper", hi)):
            P.append(prop("thermal.expansion_linear", ppm(v), "1/K", 1,
                          {"axis": "through-thickness (Z)", "regime": reg, "bound": b,
                           "method_detail": "TMA", "test_standard": TM + "2.4.24",
                           "test_mode": "thermomechanical analysis"},
                          vb + ": `CTE, Z-axis | " + str(lo) + "~" + str(hi) + " | ppm/ oC | " + lbl +
                          "`. **인쇄 구간이라 평균 내지 않고 두 행(`bound`)으로 갈랐다.** 환산 " + str(v) +
                          " ppm/℃ x 1e-6 = " + repr(ppm(v)) + " 1/K."))

    # ── Z-axis Expansion ─────────────────────────────────────────────────
    if g["zexp"] is not None:
        P.append(prop("thermal.expansion_total", g["zexp"] / 100.0, "1", 1,
                      {"axis": "through-thickness (Z)", "temperature_range_c": "50-260",
                       "test_standard": TM + "2.4.24", "test_mode": "thermomechanical analysis"},
                      vb + ": `Z-axis Expansion | " + str(g["zexp"]) + " | % | 50~260 oC`. 환산 " +
                      str(g["zexp"]) + " % / 100 = " + repr(g["zexp"] / 100.0) + " (무차원)."))

    # ── Td ───────────────────────────────────────────────────────────────
    P.append(prop("thermal.decomposition_temp", round(g["td"] + C2K, 2), "K", 1,
                  {"method_detail": "TGA, 5% weight loss", "test_standard": TM + "2.4.24.6",
                   "test_mode": "thermogravimetric analysis"},
                  vb + ": `Td | " + str(g["td"]) + " | oC | TGA (5% W.L)`. 환산 " + str(g["td"]) +
                  " ℃ + 273.15 = " + str(round(g["td"] + C2K, 2)) + " K."))

    # ── T288 ─────────────────────────────────────────────────────────────
    for st, mins in g["t288"]:
        P.append(prop("thermal.time_to_delamination", float(mins * 60), "s", 1,
                      {"temperature_c": 288, "specimen_state": st, "bound": "lower",
                       "test_standard": TM + "2.4.24.1", "test_mode": "TMA delamination"},
                      vb + ": `T288 | >" + str(mins) + " | min. | " + st + "`. **원문이 부등호(`>" + str(mins) +
                      "`)로 인쇄한 하한이다** — `bound: lower` 로 넣었고 상한 행은 만들지 않았다. 환산 " +
                      str(mins) + " min x 60 = " + str(float(mins * 60)) + " s."))

    # ── Thermal conductivity ─────────────────────────────────────────────
    P.append(prop("thermal.conductivity", g["k"], "W/(m*K)", 1,
                  {"test_standard": g["k_method"], "test_geometry": "through-thickness (laminate stack)",
                   "test_mode": "steady-state guarded heat flow"},
                  vb + ": `Thermal Conductivity | " + str(g["k"]) + " | W/m.K`. 단위가 이미 W/(m·K) 라 환산이 없다. "
                  "시험법 칸 원문: `" + g["k_method"] + "`."))

    # ── Dk / Df ──────────────────────────────────────────────────────────
    for key, rows, label in (("electrical.dielectric_constant", g["dk"], "Dk"),
                             ("electrical.dissipation_factor", g["df"], "Df")):
        for freq, printed_cell, meth, vals in rows:
            for rc, v in vals:
                cond = {"frequency": freq, "resin_content": rc, "conditioning": "C-24/23/50",
                        "test_standard": (TM + printed_cell) if printed_cell[0].isdigit() else printed_cell,
                        "method_detail": meth if meth != "—" else printed_cell,
                        "test_mode": "dielectric (" + (meth if meth != "—" else "IPC-TM-650 " + printed_cell) + ")"}
                P.append(prop(key, v, "1", 1, cond,
                              vb + ": `" + label + " (" + rc + ") | " + freq + " | " + str(v) +
                              " | C-24/23/50`. 원문 `IPC-TM-650` 칸: `" + printed_cell + "`. " +
                              ("**원문이 수지함량 두 값을 슬래시로 갈라 인쇄한다** — 두 행으로 나누고 "
                               "`resin_content` 에 박았다. 평균 0건." if len(vals) > 1 else
                               "원문이 수지함량 한 열만 인쇄한다.")))

    # ── Volume / Surface resistivity ─────────────────────────────────────
    if g["res"]:
        P.append(prop("electrical.resistivity_volume", 1e14, "ohm*m", 1,
                      {"conditioning": "C-96/35/90", "bound": "lower", "test_standard": TM + "2.5.17.1",
                       "test_mode": "insulation resistance (volume)"},
                      vb + ": `Volume Resistivity | >10^10 | MΩ-cm | C-96/35/90`. "
                      "**주의 — `pdftotext -layout` 이 위첨자를 납작하게 떨어뜨려 `>1010` 으로 뽑는다.** "
                      "75차 KB 가 `pdftotext -bbox-layout` 으로 확인했다: `>10`(yMin 577.9) 다음 `10`(yMin 576.9, "
                      "글자높이 8.0 vs 12.0)이 **위첨자**다. 지수 10 이다. 환산 1e10 MΩ·cm x 1e6 = 1e16 Ω·cm, "
                      "x 1e-2 = 1e14 Ω·m. **부등호 하한이라 `bound: lower`.**"))
        P.append(prop("electrical.surface_resistivity", 1e15, "ohm", 1,
                      {"conditioning": "C-96/35/90", "bound": "lower", "test_standard": TM + "2.5.17.1",
                       "test_mode": "insulation resistance (surface)"},
                      vb + ": `Surface Resistivity | >10^9 | MΩ | C-96/35/90`. 같은 위첨자 함정이다"
                      "(`pdftotext -layout` 이 `>109` 로 뽑는다). 환산 1e9 MΩ x 1e6 = 1e15 Ω. "
                      "**부등호 하한이라 `bound: lower`.**"))

    # ── Electric strength ────────────────────────────────────────────────
    if g["es"]:
        P.append(prop("electrical.dielectric_strength", float(g["es"]) * 1e6, "V/m", 1,
                      {"conditioning": "D-48/50+D-0.5/23", "bound": "lower", "test_standard": TM + "2.5.6.2",
                       "test_mode": "electric strength (short-time AC)"},
                      vb + ": `Electric Strength | >" + str(g["es"]) + " | kV/mm | D-48/50+D-0.5/23`. 환산 " +
                      str(g["es"]) + " kV/mm x 1e6 = " + repr(float(g["es"]) * 1e6) + " V/m. "
                      "**부등호 하한이라 `bound: lower`.** 같은 표의 `Dielectric Breakdown | >" + str(g["db_kv"]) +
                      " | kV`(2.5.6)는 **두께가 없는 절대전압이라 우리 분류에 맞는 키가 없어** 행을 만들지 "
                      "않았고 카드 attributes 에 verbatim 으로 남겼다."))

    # ── Water absorption ─────────────────────────────────────────────────
    if g["wa"] is not None:
        P.append(prop("chemical.water_absorption_24h", g["wa"] / 100.0, "1", 1,
                      {"conditioning": g["wa_cond"], "test_standard": TM + "2.6.2.1",
                       "test_mode": "gravimetric water absorption"},
                      vb + ": `Water Absorption | " + str(g["wa"]) + " | % | " + g["wa_cond"] + "`. 환산 " +
                      str(g["wa"]) + " % / 100 = " + repr(g["wa"] / 100.0) + "."))

    # ── Peel strength ────────────────────────────────────────────────────
    for foil, condn, v, unit in g["peel"]:
        f, fs = PEEL_CONV[unit]
        nv = round(v * f, 2)
        P.append(prop("interface.peel_strength", nv, "N/m", 1,
                      {"foil": foil, "conditioning": condn, "test_standard": TM + "2.4.8",
                       "test_mode": "peel (copper foil from laminate)"},
                      vb + ": `Peel Strength | " + foil + " | " + str(v) + " | " + unit + " | " + condn +
                      "`. 환산 " + str(v) + " " + unit + " x " + fs + " = " + str(nv) + " N/m; 되돌리면 " +
                      str(nv) + " / " + fs + " = " + str(round(nv / f, 4)) + ". " +
                      ("**이 벤더는 IC 기판용 S 계열에서만 `kg/cm` 로 인쇄한다** — kgf 기준이라 9.80665 N / "
                       "0.01 m = 980.665 N/m 을 곱했다." if unit == "kg/cm" else
                       ("**이 등급만 `kN/m` 로 인쇄한다.**" if unit == "kN/m" else ""))))

    # ── Flexural ─────────────────────────────────────────────────────────
    if g["flex"]:
        kind, rows = g["flex"]
        for d, lo, hi in rows:
            for b, v in (("lower", lo), ("upper", hi)):
                if kind == "strength":
                    P.append(prop("mechanical.flexural_strength", MPa(v), "Pa", 1,
                                  {"direction": d, "conditioning": "As Received", "bound": b,
                                   "test_standard": TM + "2.4.4", "test_mode": "flexural (3-point bend)",
                                   "strength_property": "flexural strength"},
                                  vb + ": `Flexural Strength | " + d.capitalize() + " | " + str(lo) + "~" + str(hi) +
                                  " | MPa | As Received`. **인쇄 구간이라 두 행(`bound`)으로 갈랐다.** 환산 " +
                                  str(v) + " MPa x 1e6 = " + repr(MPa(v)) + " Pa. **이 행은 굽힘이다 — "
                                  "`mechanical.tensile_strength` 로 옮기지 마라**(IPC-TM-650 2.4.4)."))
                else:
                    P.append(prop("mechanical.flexural_modulus", GPa(v), "Pa", 1,
                                  {"direction": d, "conditioning": "As Received", "bound": b,
                                   "test_standard": TM + "2.4.4", "test_mode": "flexural (3-point bend)",
                                   "strength_property": "flexural modulus"},
                                  vb + ": `Flexural Modulus | " + d.capitalize() + " | " + str(lo) + "~" + str(hi) +
                                  " | GPa | As Received`. **인쇄 구간이라 두 행(`bound`)으로 갈랐다.** 환산 " +
                                  str(v) + " GPa x 1e9 = " + repr(GPa(v)) + " Pa. **굽힘탄성률이다 — "
                                  "`mechanical.youngs_modulus` 칸에 옮기지 않았다.** 68차 DC 가 Panasonic 여섯 "
                                  "등급에서 굽힘값을 영률 칸에 넣었다가 진짜 인장값과 12~23 % 어긋나는 것을 보고 "
                                  "전부 되돌린 자리다. 시험법이 IPC-TM-650 2.4.4(굽힘)라 영률 부재 판정은 그대로 "
                                  "유지된다."))

    # ── UL-94 ────────────────────────────────────────────────────────────
    P.append(prop("thermal.flammability_ul94", "V-0", None, 1,
                  {"conditioning": "C-48/23/50", "test_standard": "UL-94", "test_mode": "vertical burn"},
                  vb + ": `Flame Resistance | V-0 | C-48/23/50 | UL-94`."))
    return P


def build():
    mats = []
    for g in G:
        pair = g["pair"]
        disp = g["id"] + (" / " + pair if pair else "")
        url = URL_BASE + g["pdf"].replace(" ", "%20").replace("(", "%28").replace(")", "%29")
        title_short = (g["title"].replace(" / ", " ").replace("Halogen Free", "Halogen-Free")
                       .replace("Extreme-low Loss", "Extreme-Low-Loss"))
        name = "Elite Material " + disp + " " + title_short + " Laminate"
        assert len(name) <= 200, (len(name), name)

        src = {"kind": "datasheet",
               "title": "Elite Material Co., Ltd. — " + disp + " Datasheet (" + g["title"] + "), " + g["rev"] +
                        (" [" + g["prelim"] + "]" if g["prelim"] else ""),
               "url": url,
               "publisher": "Elite Material Co., Ltd. (台光電子材料股份有限公司)",
               "year": g["year"],
               "local_path": LOCAL_DIR + g["local"],
               "url_note": "74차 JB 가 2026-09-13 에 벤더 제품목록에서 받아 둔 43장 중 한 장이다. " + EMC_NOTE}

        attrs = {
            "material_class": "copper-clad laminate (glass fabric / " +
                              ("halogenated epoxy" if "Halogenated" in g["title"] else "halogen-free epoxy") + ")",
            "subsystem": "pcb",
            "role": "product",
            "role_reason": "PCB 실부품 동장적층판. 벤더가 등급명으로 인쇄해 파는 제품이다.",
            "role_confidence": "high",
            "manufacturer": "Elite Material Co., Ltd. (EMC, 台光電子材料)",
            "product_series": "EM series copper-clad laminate",
            "product_form": "copper-clad laminate / prepreg",
            "aliases": [g["id"], "EMC " + g["id"], "Elite Material " + g["id"], g["id"].replace("-", "")] +
                       ([pair, pair.replace("-", "")] if pair else []),
            "ipc_slash_sheets": g["slash"],
            "ul_file": "E150504",
            "datasheet_revision": g["rev"],
            "vendor_sheet_rows": row_list(g),
            "locale_note": EMC_NOTE,
            "core_absent_from_vendor_sheet": {k: kb_reason(g, k) for k in CORE_ABSENT},
        }
        if pair:
            attrs["grade_pair_note"] = ("`" + g["id"] + "` 는 동장적층판(laminate), `" + pair +
                                        "` 는 같은 수지계의 프리프레그(B-stage)다. 벤더가 한 시트에 두 품번을 묶어 "
                                        "인쇄하고 **특성값은 한 벌뿐**이라 카드도 하나다.")
        else:
            attrs["grade_pair_note"] = ("**이 등급만 프리프레그 짝 품번이 인쇄돼 있지 않다** — 43장 중 유일하다. "
                                        "표제가 `EM-A70K` 한 줄뿐이다.")
        if g["prelim"]:
            attrs["preliminary_datasheet"] = ("원문 표제에 `" + g["prelim"] + "` 가 인쇄돼 있다. **등급이 흔들릴 수 "
                                              "있다** — 개정판이 나오면 값과 행 구성을 다시 대조해라.")
        if g["db_kv"]:
            attrs["dielectric_breakdown_printed"] = ("이 표는 `Dielectric Breakdown | >" + str(g["db_kv"]) +
                                                     " | kV | D-48/50+D-0.5/23 | IPC-TM-650 2.5.6` 을 인쇄한다. "
                                                     "**두께가 없는 절대 파괴전압이라 우리 분류에 맞는 키가 없어** "
                                                     "행을 만들지 않았다(`electrical.dielectric_strength` 는 V/m, "
                                                     "`electrical.withstand_voltage_surface` 는 다른 측정이다). "
                                                     "값을 버리지 않도록 여기 적어 둔다.")
        if not g["res"]:
            attrs["vendor_sheet_missing_resistivity_rows"] = ("43장 중 `EM-892K2(A)`·`EM-S532K` 두 장만 "
                                                "`Volume Resistivity`·`Surface Resistivity` 행이 **없다.** "
                                                "형제 등급(`EM-892K2`·`EM-892K`)에는 있다 — 형제 값을 이 카드에 "
                                                "옮기지 마라.")
        if not g["flex"]:
            attrs["vendor_sheet_missing_flexural_rows"] = ("43장 중 `EM-A70K`·`EM-S532K` 두 장만 굽힘 행이 **아예 없다.** "
                                             "나머지 41장은 `Flexural Strength`(31장) 또는 "
                                             "`Flexural Modulus`(10장)를 인쇄한다. 이 카드에는 기계축이 "
                                             "`Peel Strength` 하나뿐이다.")
        if g["wa"] is None:
            attrs["vendor_sheet_missing_water_absorption_row"] = ("43장 중 이 등급 시트에만 `Water Absorption` 행이 없다.")

        desc = ("台光電子材料(Elite Material Co., Ltd.) 동장적층판 `" + disp + "` — " + g["title"] + ". "
                "벤더 표기 특징: " + g["feat"] + " 적용 IPC 슬래시시트: " + g["slash"] + ". "
                "**이 카드가 75차 KB 에 선 이유** — 74차 JB 가 이 벤더 데이터시트 43장을 전수로 내려받아 두었는데 "
                "카드가 선 등급은 아홉뿐이었다(68차 DC 의 다섯 + JB 의 넷). 이 등급은 벤더 시트가 "
                "**열전도율과 CTE 를 인쇄**하므로 카드를 세우면 코어7 두 칸이 차고 온다. "
                "밀도·영률·포아송비·비열·인장강도 다섯은 43장 전수에서 0건이라 태어날 때부터 부재판정이 걸려 있다.")
        if g["flex"] and g["flex"][0] == "modulus":
            desc += (" **이 등급은 `Flexural Modulus` 를 GPa 로 인쇄한다**(10장 중 하나) — 68차 DC 의 "
                     "「이 벤더의 강도축은 Flexural Strength 하나다」가 여기서는 성립하지 않는다. 다만 시험법이 "
                     "IPC-TM-650 2.4.4(굽힘)이라 영률 칸은 여전히 못 채운다.")

        for k in attrs:
            if VERDICT_LIKE.search(k) and k not in VERDICT_OK:
                raise SystemExit("판정으로 오인될 attribute 이름: " + k + " (" + name + ")")

        mats.append({"new_material": {"name": name, "category": "composite",
                                      "description": desc, "attributes": attrs},
                     "source": src, "properties": build_props(g)})
    return mats


if __name__ == "__main__":
    doc = {"batch": BATCH, "materials": build()}
    out = os.path.join(OUT, "kb75_01_elite_material_uncarded_grades.json")
    json.dump(doc, open(out, "w"), ensure_ascii=False, indent=1)
    n = sum(len(m["properties"]) for m in doc["materials"])
    core = sum(1 for m in doc["materials"] for p in m["properties"]
               if p["key"] in ("thermal.conductivity", "thermal.expansion_linear"))
    print("카드", len(doc["materials"]), "· 물성행", n,
          "· 코어7 행", core,
          "· 판정칸", sum(len(m["new_material"]["attributes"]["core_absent_from_vendor_sheet"])
                          for m in doc["materials"]))
    print("이름 최대", max(len(m["new_material"]["name"]) for m in doc["materials"]), "자")
