# 71차 정정 — 70차 FC 가 감사에서 찾은 결함 둘을 고친다. 값을 지우지는 않는다.
#
#   FC-D1  structure.particle_diameter(정의: 입자 직경) 칸에 **반지름**이 앉은 2행.
#          원문(Liebig 2019)이 같은 기호 r 을 Table 3 은 `Particle Size r`,
#          Table 6 은 `Particle Radius r (출처: Table 3)` 로 부른다 — 문서 자신의 모순이다.
#          같은 표가 그 r 로 비표면적을 계산한다: a = 3·eps_s/R.
#          음극 3*0.548/172730 = 9.518 um (인쇄 9.89 의 0.962배)
#          양극 3*0.457/825880 = 1.660 um (인쇄 1.72 의 0.965배)
#          지름으로 읽으면 두 전극 다 1.93 배로 어긋난다. 두 어긋남이 같으므로 eps_s
#          반올림이고 저자는 r 을 반지름으로 썼다. 직경 = 2r 로 고친다(정의 환산이지
#          다른 물성에서의 역산이 아니다). method 를 computed 로 바꾸고 근거를 notes 에 박는다.
#
#   FC-O1  출처 2371(Eclipse 페라이트 시트)의 등급표는 온도를 한 줄도 인쇄하지 않는다.
#          `20 °C` 는 같은 장의 **감자곡선 축 이름**에만 나온다. 그런데 이 출처에서 나온
#          339행이 `temperature_c: 20` 을 인쇄값처럼 달고 있다(여섯 파동 누적).
#          값은 아마 맞다 — 자석 시트의 Typical Values 는 관례상 상온이다. 그러나
#          **관례는 인쇄가 아니다.** 조건에서 빼고 무엇을 근거로 20 이라 적었는지 남긴다.
#          `*_before_correction` 감사 흔적은 건드리지 않는다.
import argparse, json, os, sqlite3

BASIS = ("이 시트의 등급표는 온도를 인쇄하지 않는다(표 머리가 `Typical Values` 뿐이다). "
         "`20 °C` 는 같은 장의 감자곡선 패널 축 이름(`20°C Normal`·`20°C Intrinsic`)에만 나온다. "
         "자석 데이터시트의 Typical Values 가 관례상 상온인 것은 맞으나 관례는 인쇄가 아니므로 "
         "조건에서 뺀다(71차, 70차 FC 의 FC-O1 감사).")

D1 = {  # pv_id: (기존 반지름 m, 고칠 직경 m, 출처 표기)
    40339: (9.89e-6, 19.78e-6, "Table 3 `Particle Size r (µm) 9.89 ± 3.31`"),
    40343: (1.72e-6, 3.44e-6, "Table 3 `Particle Size r (µm) 1.72 ± 0.54`"),
}
D1_NOTE = (
    " || [71차 정정 — 직경 칸에 반지름이 앉아 있었다] 원문이 같은 기호 r 을 Table 3 에서는 "
    "`Particle Size r`, Table 6 에서는 `Particle Radius r (출처: Table 3)` 로 부른다 — 문서 "
    "자신의 모순이다. Table 6 이 같은 r 로 비표면적을 계산하므로 그 식으로 갈랐다: a = 3·eps_s/R. "
    "음극 3×0.548/172730 = 9.518 µm(인쇄 9.89 의 0.962배), 양극 3×0.457/825880 = 1.660 µm"
    "(인쇄 1.72 의 0.965배). **지름으로 읽으면 두 전극 다 1.93 배로 어긋난다.** 두 어긋남이 "
    "0.962·0.965 로 같으므로 eps_s 반올림이고 저자는 r 을 반지름으로 썼다. 우리 키는 직경이라 "
    "2r 로 환산했다 — 정의 환산이지 다른 물성에서의 역산이 아니다. 원 인쇄값(반지름)은 "
    "conditions.radius_printed_m 에 보존했다."
)

ap = argparse.ArgumentParser()
ap.add_argument("--db", default=os.environ.get("MATERIALTWIN_DATA_DIR", "") + "/materialtwin.db")
ap.add_argument("--apply", action="store_true")
a = ap.parse_args()
c = sqlite3.connect(a.db)
print(f"[DB] {a.db}\n")

# ── FC-D1
print("=== FC-D1 · 반지름 → 직경 ===")
n1 = 0
for vid, (old, new, cite) in D1.items():
    row = c.execute("select value_num, conditions, notes, method from property_value where id=?", (vid,)).fetchone()
    if not row:
        print(f"  {vid} 행 없음 — 건너뜀"); continue
    if abs(row[0] - old) > 1e-12:
        print(f"  {vid} 값이 {row[0]} 로 예상({old})과 달라 건드리지 않는다"); continue
    cond = json.loads(row[1] or "{}")
    cond["radius_printed_m"] = old
    cond["definition"] = ("입자 **직경** = 2r. 원문 인쇄값 r 은 반지름이며 그 판정 근거는 notes 에 있다. "
                          + str(cond.get("definition", "")))[:900]
    print(f"  {vid}: {old:.4g} → {new:.4g} m  ({cite})")
    if a.apply:
        c.execute("update property_value set value_num=?, conditions=?, notes=?, method='computed' where id=?",
                  (new, json.dumps(cond, ensure_ascii=False), (row[2] or "") + D1_NOTE, vid))
    n1 += 1

# ── FC-O1
print("\n=== FC-O1 · 인쇄되지 않은 20 °C 를 조건에서 뺀다 (출처 2371) ===")
rows = c.execute("select id, conditions from property_value where source_id=2371").fetchall()
n2 = 0
for vid, cd in rows:
    d = json.loads(cd or "{}")
    if str(d.get("temperature_c")) != "20":
        continue
    d.pop("temperature_c", None)
    d["temperature_not_printed"] = True
    d["temperature_basis"] = BASIS
    if a.apply:
        c.execute("update property_value set conditions=? where id=?", (json.dumps(d, ensure_ascii=False), vid))
    n2 += 1
print(f"  대상 {n2}행 / 이 출처 전체 {len(rows)}행")

if a.apply:
    c.commit(); print(f"\n[적용] FC-D1 {n1}행 · FC-O1 {n2}행")
else:
    print(f"\n[예행] --apply 를 붙이면 쓴다 — FC-D1 {n1}행 · FC-O1 {n2}행")
