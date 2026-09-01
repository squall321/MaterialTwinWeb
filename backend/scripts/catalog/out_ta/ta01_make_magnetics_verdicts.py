# 58차 TA — magnetics 하드페라이트 25등급의 자유 키 판정을 집계가 읽는 자리로 옮기는 JSON 을 만든다.
import json
import sqlite3

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"

# Eclipse `Ferrite Magnets/Ceramic Magnets Datasheet`(출처 2371) p.3
# `Physical Characteristics (Typical)` 표에서 인쇄되는 코어 7칸 — 58차 TA 가 PDF 전문을 열어 옮겼다.
PRINTED = {
    "physical.density": "`Density  D  g/cc  4.9 to 5.1`",
    "mechanical.youngs_modulus": "`Modulus of Elasticity  λ/E  Pa  1.8x10^11`",
    "mechanical.poisson_ratio": "`Poisson's Ratio  ν  0.28`",
    "thermal.expansion_linear": "`Coefficient of Thermal Expansion  C∥  10^-6/°C  15` / `C⊥  10^-6/°C  10`",
    "thermal.conductivity": "`Thermal Conductivity  k  W/cm°C  0.029`",
    "thermal.specific_heat": "`Specific Heat Capacity  c  J/kg°C  795−855`",
    "mechanical.tensile_strength": "`Tensile Strength  σUTS or S U  Pa  34x10^6`",
}

TAIL = (
    " — 원문에 값이 **인쇄돼 있는데 안 넣은 칸**이다(V2 가 아니다). Eclipse Magnetics "
    "`Ferrite Magnets/Ceramic Magnets Datasheet`(출처 2371, Rev.2021) p.3 의 "
    "`Physical Characteristics (Typical)` 표는 **등급별이 아니라 소결 하드페라이트 공통값**이라 "
    "이 등급에 귀속시키지 않았다. 58차 TA 가 PDF 전문을 열어 확인했다 — 같은 문서의 등급표"
    "(Chinese Standard 27등급 · European IEC 60404-8-1 18등급 · American Standard)는 "
    "Br·Hc(Hcb)·Hci(Hcj)·(BH)max **자기특성만** 인쇄하고 물리특성 열이 하나도 없다. "
    "⚠ **규약이 갈려 있다**(브리프 612) — 같은 표의 같은 값이 재료 424(Y30)·425(Y35)·"
    "2533(C8/C8A)에는 `grade_scope: class value — sintered hard ferrite, not grade-specific` "
    "t3 규약으로 **이미 복제돼 있다**(2026-08-04·08-19 적재, 이 25등급 생성 2026-08-28 보다 앞선다). "
    "계보를 따를지 안 따를지는 다음 파동의 판단이고, 여기서는 이 칸이 V5(진짜 남은 것)로 세어져 "
    "**다음 파동이 또 표적으로 집는 것**만 멈춘다(브리프 593·609). — 58차 TA"
)

ORPHAN = (
    " ※ 이 재료(2675 C1)만 `grade_table_scope` 자유 키가 없어 24 형제와 달리 V5 로 세어지고 있었다 — "
    "같은 문서·같은 표·같은 클래스인데 판정만 빠진 것이다(브리프 600 의 역방향). — 58차 TA"
)


def main() -> int:
    c = sqlite3.connect(DB)
    rows = []
    for mid, name, attrs in c.execute("select id,name,attributes from material order by id"):
        a = json.loads(attrs or "{}")
        if not isinstance(a, dict):
            continue
        if a.get("subsystem") != "magnetics" or a.get("role") != "product":
            continue
        if not name.startswith("Hard Ferrite Magnet"):
            continue
        if mid < 2600:                      # 424·425 는 이미 값이 차 있다
            continue
        tail = TAIL + (ORPHAN if mid == 2675 else "")
        rows.append({"material_id": mid, "name": name,
                     "core_rejected_printed_value": {k: v + tail for k, v in PRINTED.items()}})
    doc = {"batch": "58차 TA",
           "무엇": "magnetics 하드페라이트 25등급 175칸 — 자유 키 `grade_table_scope` 에 있던 판정을 "
                   "집계가 읽는 `core_rejected_printed_value` 로 옮긴다(브리프 593·608·609).",
           "선언 칸 수": sum(len(r["core_rejected_printed_value"]) for r in rows),
           "verdicts": rows}
    out = "ta01_magnetics_core_verdicts.json"
    with open(out, "w") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"{out} — 재료 {len(rows)}종 · 선언 {doc['선언 칸 수']}칸")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
