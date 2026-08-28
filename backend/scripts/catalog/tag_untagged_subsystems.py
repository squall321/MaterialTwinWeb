#!/usr/bin/env python3
# role=product 인데 계통 태그가 없던 203종(+role 판정으로 늘어난 넷)에 subsystem 을 붙이고, 못 붙인 것은 사유를 남긴다 — 49차 KA.
#
# 왜 필요한가
#   43차 EA 가 계통 태깅을 한 뒤 파동들이 재료를 계속 늘렸다. 실측으로 role=product 860종 중
#   203종(물성 5,863행)에 `subsystem` 이 없었다. 계통 패싯에서 이들은 전부 `기타`(1,958종)에
#   섞여, 화면으로 조사하면 "그 계통에 N 종" 을 실제보다 작게 센다(브리프 528 — 48차 JC 가
#   OLED 소분자를 8종으로 세고 넘어간 배치 둘을 잡았다. 실제 172종).
#
# 무엇을 근거로 붙였나 — 넷뿐이다. 이 밖은 붙이지 않았다.
#   ① 재료 자신의 description 이 부품을 말한다 (KooRemapper 폰 모델 라이브러리 47~61)
#   ② 출처가 용도를 말한다 (NOA/Dymax/ThreeBond 는 전부 'Cemented Doublets' 렌즈 접합 문서다)
#   ③ 이미 태그된 형제가 있다 (브리프 465 — 같은 부품의 짝이 다른 값에 들어가면 필터가 죽는다)
#   ④ `docs/drop_materials.k` 가 낙하 모델 부품으로 쓴다
#
# 어휘를 늘리지 않았다. 기존 16개 값만 쓴다(브리프 466 — 옛 값 speaker/audio/fpcb/soc 는
# 43차에 acoustics/pcb/wlp 로 합쳐졌고 되살리지 않는다).
#
# 못 붙인 것은 `subsystem` 을 비워 두고 `subsystem_basis` 에 사유를, `verdict_subsystem` 에
# 판정(not_applicable / undetermined)을 남긴다. 둘 다 병합기가 운영으로 전파하는 키다
# (`CURATION_KEYS` · `CURATION_PREFIXES` 의 `verdict_`). 다음 파동이 같은 203종을 다시 세지 않게 하는 것이 목적이다.
#
# 한 번 더 돌려도 안전하다(멱등). `--apply` 없이는 미리보기만 한다.
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys

DB = os.environ.get(
    "MATERIALTWIN_DB",
    os.path.join(os.environ["MATERIALTWIN_DATA_DIR"], "materialtwin.db")
    if os.environ.get("MATERIALTWIN_DATA_DIR")
    else "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db")

# 지금 쓰이는 계통 어휘 — 조회로 확인했다(2026-08-28). 새 값을 만들지 않는다.
VOCAB = {"pcb", "packaging", "display", "thermal", "housing", "magnetics", "camera",
         "battery", "rf", "passive", "acoustics", "semiconductor", "wlp", "coating",
         "sensor", "emi"}

# ── ① 붙인다 ────────────────────────────────────────────────────────────────
B_ALLOY = ("구조 금속 — 미들프레임·브래킷·판금·스프링판 계열이다. "
           "2·3(SUS301/304)·17·19(Al5052/6061)·2369(ZAMAK) 와 같은 축이다. "
           "스마트폰 전용 등급은 아니나 구조 부품 축에 걸린다(2369 선례 문구).")
B_MGDIE = ("다이캐스트 Mg 합금 — 34 AZ91D·2557 AM60B·2558 AM50A 와 같은 계통이다. "
           "1785~1788 은 같은 AE44 의 시효 시간점 넷이라 계통이 같다.")
B_TAPE = ("기구 조립·실링용 양면/전사 접착 테이프다. 특정 모듈을 지목하는 근거가 없고 "
          "58·59 방수 실링 부재와 같은 하우징 조립 축에 걸린다. "
          "모듈이 지목된 것은 따로 갈랐다(47 pcb · 48·52 battery · 49 camera · 50·54 display).")
B_FOAM = ("완충·가스켓 폼 — 65 PORON 4701 가스켓·66 PORON SR-S 와 같은 제품군(Rogers PORON)이다.")
B_EPLAS = ("엔지니어링 열가소성 구조재 — 133·264~317·1161·2267 등 하우징 수지와 같은 축이다.")

TAG: dict[int, tuple[str, str]] = {}


def _put(ids, sub, basis):
    for i in ids:
        TAG[i] = (sub, basis)


# 구조 금속 라이브러리(KooRemapper Bilinear + 논문 금속). 43차 EA 가 같은 블록의
# SUS301/304·Al5052/6061/6063/7075·Ti6Al4V·ADC12·Mg 를 housing 으로 이미 골랐고,
# 나머지가 남아 있었다 — 기준이 아니라 범위가 덜 돈 것이다(23 Al7075-T6 는 있는데 22 Al7050 은 없다).
_put([1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 22, 25, 26, 30, 31, 32, 36,
      1364, 2261, 2262, 2290, 2432], "housing", B_ALLOY)
_put([28], "housing", B_ALLOY + " 28 'M-Film' 은 Ti 합금 판재(tag Ti_MetalFilm_EP)이나 제품 식별은 안 된다.")
_put([1785, 1786, 1787, 1788], "housing", B_MGDIE)

# 폰 모델 라이브러리 — description 이 부품을 말한다(근거 ①).
_put([47], "pcb", "재료 description 이 'General acrylic PSA for FPC-mainboard' 다 — FPCB·메인보드 조립 접착이다.")
_put([48], "battery", "재료 description 이 'Silicone PSA for battery-adjacent high-temp' 다.")
_put([52], "battery", "재료 description 이 '3M VHB 5952, battery mounting' 다(55·56 배터리 고정 접착 선례).")
_put([49], "camera", "재료 description 이 'High-shear PSA for camera module' 다.")
_put([50], "display", "재료 description 이 'Removable PSA for screen protector' 다.")
_put([54], "display", "재료 description 이 'PU foam tape, display cushion/impact protection' 다.")
_put([51], "housing", "재료 description 이 '3M VHB 4905, back cover bonding' 다.")
_put([53], "housing", "재료 description 이 'PE foam tape, frame-back cover bonding' 다.")
_put([61], "magnetics", "재료 description 이 'Haptic motor isolation tape' 다 — 계통 라벨이 '자성/모터'다.")

# 구리 스프링·접점 합금 → 179 Beryllium Copper (spring/contact) 가 이미 pcb 다(근거 ③).
# 37·39 는 `docs/drop_materials.k` 의 Cu-Alloy·C7701_1_2H 카드 근거이기도 하다(근거 ④).
_put([37, 38, 39], "pcb",
     "구리 스프링·접점 합금 — 179 Beryllium Copper (spring/contact) 와 같은 계통이다. "
     "37·39 는 docs/drop_materials.k 의 Cu-Alloy·C7701_1_2H 카드 근거다.")

# 접착 테이프·폼·실링(근거 ③ — 58·59·65·66 선례).
_put([65, 66, 69, 235, 236, 237,
      322, 323, 324, 325, 326, 327, 328, 329,
      330, 331, 332, 333, 334, 335,
      336, 337, 338, 339, 340,
      341, 342, 343, 344, 345, 346, 347, 348,
      352, 353, 354, 355, 356, 357, 358, 359,
      360, 361, 362, 363, 366, 367, 368, 369, 382, 740], "housing", B_TAPE)
_put([384, 385], "housing", B_FOAM)
_put([394], "housing", "이름이 부품 기능을 말한다 — 'rubber bumper'. 기구 완충 부재다.")
_put([401], "housing", "이름이 부품 기능을 말한다 — 'seal rubber'. 58·59 방수 실링과 같은 축이다.")

# 광학 접착제 — 출처가 용도를 말한다(근거 ②).
_put([370, 373, 374, 380], "camera",
     "출처가 렌즈 접합 문서다 — 'Design Guidelines for Predicting Stress in Cemented Doublets'(SPIE). "
     "네 재료가 같은 시트를 공유한다.")

# COP — 1292 ZEONEX→camera · 1293 ZEONOR→display 로 이미 갈려 있다(근거 ③).
_put([1294, 1295], "display",
     "ZEONOR 계열 — 1293 ZEONOR 1020R 이 display(백라이트 도광판·확산판)다. ZEONEX(1292·2540~) 는 camera 로 갈려 있다.")

# 광학등급 배리어 기재 필름 — 플렉시블 디스플레이 봉지 기재다.
_put([2223, 2224, 2225, 2254], "display",
     "이름이 '광학등급(optical-grade)' 을 못박은 배리어 기재 필름(Teijin·Melinex)이다 — "
     "플렉시블 디스플레이 봉지 기재 계열(90 TFE·155 UTG 축). "
     "광학등급이 안 적힌 배리어 대조 필름(2230·2233·2283·1347·461)은 붙이지 않았다.")

# 스핀코팅 폴리이미드 — 출처가 UPILEX 필름 카탈로그다. 195 Upilex-S 가 이미 pcb 다(근거 ③).
_put([294], "pcb",
     "출처가 UBE UPILEX/UPIA 필름 카탈로그다 — 195 'PI Base Film — Upilex-S (UBE)' 와 같은 PI 다. "
     "같은 재료가 pcb 와 다른 값으로 갈리면 필터가 죽는다(브리프 465).")

# GPO-3 — 낙하 모델의 Glastic 부품이다(근거 ④). 전기절연 적층판이라 FR-4·BT 와 같은 축이다.
_put([2377, 2378, 2379], "pcb",
     "docs/drop_materials.k 298~309 의 Glastic 부품 근거다(2377). "
     "NEMA LI-1 GPO-3 전기절연 적층판이라 94 FR-4·97 BT 적층판과 같은 축이다.")

# 전자 포팅·봉지 수지.
_put([438], "packaging", "이름이 용도를 말한다 — 'electronic potting and encapsulation compound'.")
_put([616], "packaging", "PWA(인쇄배선조립) 포팅 실리콘이다 — 봉지재 축(92 EMC·93 언더필)에 걸린다.")
_put([774], "packaging",
     "같은 논문(Nguyen 2011)의 776 'ICA-2 EPO-TEK H20E' 가 이미 packaging 이다 — 그 접착제의 매트릭스다.")

# 엔지니어링 열가소성 구조재.
_put([1083, 2316, 2317, 2318, 2319], "housing", B_EPLAS)
_put([2274], "housing", B_EPLAS + " Noryl(변성 PPE) 은 하우징급 수지다.")

# ── ①' role 판정으로 새로 product 가 된 넷 ──────────────────────────────────
# `apply_material_role.py` 로 2417·2446·2447·2448 을 product 로 판정했다. 판정만 하고
# 계통을 안 붙이면 **그 넷이 곧바로 새 사각지대**가 된다(브리프 115 의 지표 왜곡과 같은 지문).
_put([2448], "sensor",
     "130 'Piezo MEMS (AlN thin-film)' 이 이미 sensor 다 — 같은 스퍼터 AlN 압전 박막이다. "
     "105 AlN BAW·181 ScAlN 은 rf 인데, Stoeckel 2014 는 BAW 필터가 아니라 MEMS 압전 박막이라 sensor 로 간다.")

# ── ② 못 붙인 것 — 사유를 남긴다 ────────────────────────────────────────────
# ("not_applicable" = 계통이 있을 수 없다 · "undetermined" = 가를 근거가 없다)
SKIP: dict[int, tuple[str, str]] = {}


def _skip(ids, verdict, basis):
    for i in ids:
        SKIP[i] = (verdict, basis)


_skip([2381, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2419, 2420, 2421, 2422, 2423],
      "not_applicable",
      "Uddeholm 금형·공구강 13종 — 부품이 아니라 그 부품을 만드는 금형이다(45차 GD 판정). "
      "계통이 있을 수 없다. 다시 세지 마라.")
_skip([364], "not_applicable",
      "웹 가공용 스플라이싱 테이프 — 제품에 남는 부재가 아니라 제조 공정 소모재다.")
_skip([387, 388, 389], "not_applicable",
      "EPE 발포PE 완충 포장재다. **카탈로그의 `packaging` 은 반도체 패키지를 뜻하므로 붙이면 안 된다** — "
      "이 오해가 다음 파동에서 재발할 자리다.")
_skip([27, 40], "undetermined",
      "Inconel 초내열합금 — 범용 합금 라이브러리에 있으나 스마트폰 구조 부품 축에 대응물이 없다.")
_skip([41], "undetermined",
      "순텅스텐 — 진동모터 웨이트로 쓰인다는 추정은 있으나 이 레코드에 근거가 없다. 비워 둔다.")
_skip([2266], "undetermined",
      "GlidCop 분산강화동 — 저항용접 전극·고열부하 부품용이다. 스마트폰 부품 근거가 없다.")
_skip([67, 70], "undetermined",
      "제진재이나 용도를 말하는 description 이 없다(60 은 'Speaker Mount'·61 은 'Haptic' 이라 갈렸다). "
      "70 'visco-6' 은 내부 코드라 제품 식별도 안 된다.")
_skip([295, 639], "undetermined",
      "295 소다석회유리는 출처가 'Indentation creep of window glass' 인 창유리이고, 639 용융석영은 광학 석영이다. "
      "스마트폰 커버유리(77·274·275·2604~)·디스플레이 기판유리(2618~)와 다른 재료다 — 기준 유리로 둔다.")
_skip([371, 372], "undetermined",
      "DELO KATIOBOND 광경화 접착제 — 카메라 모듈용으로 알려져 있으나 이 레코드의 출처는 벤더 TDS 뿐이고 "
      "광학 물성도 없다(370·373·374·380 은 렌즈 접합 문서를 공유해 camera 로 갈렸다).")
_skip([381, 383], "undetermined",
      "범용 전자용 RTV 실리콘 접착·실런트. 실링(housing)·기판 본딩(pcb)·포팅(packaging) 어디에나 쓰여 못 가른다.")
_skip([405, 412], "undetermined",
      "Sylgard 184·RTV615 는 실험실 표준 PDMS/실리콘이다. 인계 요약은 이 둘을 '스마트폰 재료' 로 적었으나 "
      "생산 부품 근거가 이 레코드에 없다(브리프 505 — 인계의 주의는 검증 대상이다).")
_skip([390, 391, 392, 393], "undetermined",
      "충격흡수 폼 — 390 은 attributes 가 스스로 '스마트폰 도메인 밖' 이라 적었고(자동차 시트폼), "
      "392 D3O·393 폴리우레아는 스포츠·보호구 브랜드다. 384·385(Rogers PORON) 와 달리 전자 부품 계열이 아니다.")
_skip([395, 396, 397, 398, 399, 400], "undetermined",
      "NBR/PUR/EVA/SBR/CB충전 NR — 이름이 부품이 아니라 고분자 계열명이다. "
      "같은 블록에서 이름이 기능을 말한 394(bumper)·401(seal)만 갈랐다.")
_skip([442, 461, 2230, 2233, 2283, 1347], "undetermined",
      "배리어 기재·절연 필름 — 플렉시블 디스플레이 봉지와 식품·PV 포장 양쪽에 쓰여 못 가른다. "
      "이름이 '광학등급' 을 못박은 2223·2224·2225·2254 만 display 로 갈랐다. "
      "442 Lexan FR25A 는 43차에 PV 백시트로 범위 밖에 넣을 뻔했다가 남긴 재료다(난연 PC 필름은 전자 절연재).")
_skip([587, 591, 1109, 1110], "undetermined",
      "항공 구조용 필름접착제 4종 — 브리프 193 이 '스마트폰에 직접 대응물이 있어' 범위 안에 남긴 것이지 "
      "특정 계통 부품이라는 뜻이 아니다.")
_skip([618, 619, 756, 1643, 1644], "undetermined",
      "비스말레이미드(BMI) 수지·복합재 — 고온 구조재라 스마트폰 계통에 대응물이 없다.")
_skip([641, 1380, 1652, 1653], "undetermined", "구조용 섬유강화 복합재 라미나 — 스마트폰 부품 근거가 없다.")
_skip([1299, 1300, 1502, 1503, 2398], "undetermined",
      "복합재 원료(탄소섬유·에폭시 수지·상용화제 왁스) — 부품이 아니라 배합 원료다.")
_skip([1345, 1462, 1509, 1525, 1542, 2380, 2397, 2271, 2272], "undetermined",
      "범용 사출·압출 수지(HDPE·PP·PVC·PCL·주조 PMMA·충전 PP) — 하우징급 엔지니어링 수지와 달리 "
      "스마트폰 부품 축에 대응물이 없다.")
_skip([1422, 1430, 2128], "undetermined",
      "에폭시·불포화폴리에스터 수지 원료 — 용도를 말하는 근거가 레코드에 없다.")
_skip([1658, 2389, 2418], "undetermined", "범용 2액형·1액형 구조 접착제. 특정 모듈 근거가 없다.")
_skip([2341, 2342], "undetermined", "Kraton SBS/SIS — PSA 배합용 기재 고분자이지 완성 부재가 아니다.")
_skip([2417], "undetermined",
      "PP-GF30 사출 컴파운드 — 2271·2272 충전 PP 와 같은 축이다. 스마트폰 부품 근거가 없다.")
_skip([2446, 2447], "undetermined",
      "PZN·PZN-8%PT 릴랙서 강유전 단결정 — 의료 초음파·정밀 액추에이터용이다. "
      "107 PZT·130 AlN MEMS 와 달리 스마트폰 부품 근거가 이 레코드에 없다.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    bad = {v[0] for v in TAG.values()} - VOCAB
    if bad:
        print(f"어휘 밖 계통값: {bad}", file=sys.stderr)
        return 1
    dup = set(TAG) & set(SKIP)
    if dup:
        print(f"TAG·SKIP 중복: {sorted(dup)}", file=sys.stderr)
        return 1

    if not os.path.exists(DB):
        print(f"DB 가 없다: {DB}", file=sys.stderr)
        return 1
    c = sqlite3.connect(DB, timeout=60)
    c.execute("pragma busy_timeout=60000")
    print(f"[DB] {DB}")

    # 지금 DB 에 실제로 쓰이는 어휘를 찍는다 — 옛 값이 되살아나지 않았는지 눈으로 본다(브리프 466).
    live = {s for (s,) in c.execute(
        "select distinct json_extract(attributes,'$.subsystem') from material "
        "where coalesce(json_extract(attributes,'$.subsystem'),'')<>''")}
    print(f"[어휘] DB 사용중 {len(live)}개: {' '.join(sorted(live))}")
    if live - VOCAB:
        print(f"  ✗ 스크립트가 모르는 값이 DB 에 있다: {live - VOCAB}", file=sys.stderr)
        return 1

    stat = {"tag": 0, "skip": 0, "이미 같음": 0, "없는 id": 0, "이미 태그됨": 0}
    per_sub: dict[str, int] = {}

    def patch(mid: int, **kw) -> None:
        row = c.execute("select attributes,name from material where id=?", (mid,)).fetchone()
        if row is None:
            stat["없는 id"] += 1
            print(f"  ✗ id {mid} 없음")
            return
        at = json.loads(row[0] or "{}") or {}
        # **기존 키를 보존한다** — role·core_*·merge_* 가 들어 있다. 통째로 덮지 않는다.
        if at.get("subsystem") and kw.get("subsystem") and at["subsystem"] != kw["subsystem"]:
            stat["이미 태그됨"] += 1
            print(f"  ! id {mid} 는 이미 {at['subsystem']} 이다 — 건드리지 않는다 ({row[1][:50]})")
            return
        if all(at.get(k) == v for k, v in kw.items()):
            stat["이미 같음"] += 1
            return
        at.update(kw)
        if a.apply:
            c.execute("update material set attributes=? where id=?",
                      (json.dumps(at, ensure_ascii=False), mid))
        if "subsystem" in kw:
            stat["tag"] += 1
            per_sub[kw["subsystem"]] = per_sub.get(kw["subsystem"], 0) + 1
        else:
            stat["skip"] += 1

    for mid, (sub, basis) in sorted(TAG.items()):
        patch(mid, subsystem=sub, subsystem_basis=basis)
    for mid, (verdict, basis) in sorted(SKIP.items()):
        patch(mid, verdict_subsystem=verdict, subsystem_basis=basis)

    if a.apply:
        c.commit()
    c.close()

    print(f"\n계통 붙임 {stat['tag']}종 · 사유만 남김 {stat['skip']}종 "
          f"· 이미 같음 {stat['이미 같음']} · 이미 태그됨 {stat['이미 태그됨']} · 없는 id {stat['없는 id']}")
    for s, n in sorted(per_sub.items(), key=lambda kv: -kv[1]):
        print(f"  {s}: {n}")
    print("(미리보기다 — 반영하려면 --apply)" if not a.apply else "반영했다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
