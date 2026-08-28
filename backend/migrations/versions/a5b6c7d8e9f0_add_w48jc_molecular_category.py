"""`category` 어휘에 `molecular` 를 더하고, 순수 탄소를 `ceramic` 으로 옮긴다.

45차 GD·46차 HD 가 두 파동 연속으로 보고만 하고 못 고친 어휘 결함 둘이다.
**인계는 "OLED 소분자 8종 · fac-Ir(ppy)3 1종 · 순수 탄소 7종" 이었는데
전수 조사하니 분자 172종 · 탄소 24종**이다(§479·480 — 인계는 언제나 검증 대상).

## ① `molecular` 를 연다 — 어휘가 못 담는 부류가 실재한다

`category` 여섯(metal·polymer·rubber·composite·ceramic·foam)은 Ashby 의 구조재
계통수다. **분자로 특성화되는 기능재는 이 나무에 집이 없다** — OLED 발광체·호스트·
전하수송체, 사이클로메탈화 Ir/Pt/Pd/Cu 착체, 포르피린 색소, 분자결정.
이들의 물성은 HOMO/LUMO·삼중항에너지·PLQY·발광파장이지 E·σ 가 아니다.

지금은 164종이 `polymer`, 10종이 `composite` 다. **소분자는 고분자가 아니고
유기금속 착체는 복합재가 아니다.** `polymer` 필터 960종 중 17%가 고분자가 아니었다.

**무엇이 달라지나**(어휘를 늘리는 유일한 근거다) —
`category` 는 ⓐ 카탈로그 facet 필터 ⓑ Ashby 산점도의 **기본 색상축** ⓒ taxonomy
지식그래프의 최상위 노드다. 셋 다 DB 파생이라 새 값이 자동으로 뜬다.
**축이 아니라 색이고, `dyna_export` 카드 생성은 category 를 읽지 않는다** —
그래서 카드도 커버리지(그건 `attributes.role` 이 가른다)도 바뀌지 않는다.
바뀌는 것은 필터의 정직성과 그래프의 최상위 노드다.

## ② 순수 탄소는 `composite` 가 아니라 `ceramic` 이다 — 이미 갈려 있었다

§465 의 지문 그대로다 — **같은 것이 두 어휘에 나뉘어 있다.**
`ceramic` 에 6종(DLC · TPG · 열분해흑연 2 · 흑연전극 4), `composite` 에 24종
(PGS 시트 · 카본블랙 · 그래핀필름 · PAN 탄소섬유 · MWNT/SWNT · MCMB · Timcal 흑연 · 코크스).

**단상 원소 탄소는 어느 정의로도 복합재가 아니다.** `ceramic`(비금속 무기 고체)은
Ashby 계통수가 탄소를 두는 자리이고 이미 이 DB 의 6종이 그렇게 들어 있다.
→ **새 어휘를 열지 않고 `ceramic` 으로 합친다.** §419 — 파동마다 어휘가 늘면 못 쓴다.

**안 옮긴 것과 사유**(애매하면 바꾸지 마라 — 45차 EA 규율) —
  · `Graphite Anode`(시드 항목) · `Li-ion graphite anode coating layer` ·
    `Li-ion graphite composite anode electrode` — 전극은 흑연+바인더+도전재라 복합재다
  · `Kaneka Multilayer Graphite Sheet Thermal Strap` — 다층 조립 스트랩
  · `graphene oxide (GO …)` — 산화흑연이라 순수 탄소가 아니다
  · pyrrole 처리 SWNT 4종 · GnP-bispyrene 나노페이퍼 5종 — 유기 사슬이 붙어 있다

## ③ 소자는 `role` 을 늘리지 않는다 — 1911 MLCC 칩 판정을 닫는다

45차 GD 가 `1911 BaTiO3/Ni MLCC 칩`(3x2x1.6 mm, 활성층 150장)을 판정 보류했다.
근거는 *"낙하·보드휨 해석은 칩을 균질체로 보고 유효 밀도·E·CTE 를 쓴다"* 였다.
**DB 를 쳐 보니 1911 에는 밀도도 E 도 CTE 도 없다** — 있는 것은 연마 단면에서 잰
비커스 경도 3행과 전극 기준 방향별 잔류응력 6행뿐이다. 경도는 유전체의 값이고
잔류응력은 적층체의 정직한 응력상태다. **Ashby 기본축(rho-E)에도 안 오르고
`dyna_export` 카드(rho+E 또는 rho+Cp+k)도 못 만든다** — 즉 소자 표시가 바꿀 것이 없다.

그리고 `attributes.role` 을 읽는 코드는 **온 시스템에 둘뿐**이다 —
`coverage_report.py`(evidence·out_of_scope 를 격자에서 뺀다)와 `apply_material_role.py`
(어휘 게이트). 앱 계층(`dyna_export`·`catalog_compare`·`insights`·catalog 라우터)도
프런트도 `role` 을 안 읽는다. **`device` 를 더해도 격자 말고는 아무것도 안 바뀌는데,
소자 유효물성은 §475 가 못박은 대로 소자 해석의 정당한 입력이라 격자에서 뺄 이유가 없다.**
→ **`role` 어휘는 셋 그대로 둔다.** 판정만 재료에 남긴다(`verdict_device`).

진짜 위험(베이퍼챔버·히트파이프의 유효 열전도율)은 이미 검사기가 `[주의]` 로 넷을
드러낸다. 그건 값이 재료 상한을 넘는다는 물리로 걸리는 것이지 어휘로 걸리는 것이 아니다.

**id 가 아니라 이름·지문으로 찾는다**(§466·480). 병합이 id 를 다시 매기고,
인계된 id 목록은 언제나 실제보다 작다.

Revision ID: a5b6c7d8e9f0
Revises: a4b5c6d7e8f9
"""
from __future__ import annotations

import json
import re

import sqlalchemy as sa
from alembic import op

revision = "a5b6c7d8e9f0"
down_revision = "a4b5c6d7e8f9"
branch_labels = None
depends_on = None

# ── ① molecular 지문 ─────────────────────────────────────────────────────────
# **두 매처를 합집합으로 쓴다.** 어느 하나도 혼자서는 못 잡는다(§480) —
#   · 분자궤도/발광 물성키 — 이름이 어떻든 "분자로 특성화됐다" 는 구조적 증거다.
#     다만 발광 고분자(Ir-폴리노보넨)와 무기 나노결정(양자점)도 같이 걸린다.
#   · 이름 지문 — 물성키가 optical 하나뿐인 재료(23종)를 잡는다. 대신 오탐이 있다.
# 그래서 **제외 지문을 반드시 함께 건다.**
_MO_KEYS = (
    "electrical.homo_level", "electrical.lumo_level",
    "optical.triplet_energy_t1", "optical.singlet_energy_s1",
    "optical.photoluminescence_quantum_yield", "optical.emission_peak_wavelength",
    "optical.singlet_oxygen_quantum_yield",
)
_NAME_SIG = re.compile(
    r"OLED|TADF|인광체|발광체|형광 발광|phosphorescent|phosphor\b|emitter|dopant|도판트"
    r"|전자수송|정공수송|charge-transport|multi-resonance|TTA-UC|O2 sensor|porphyrin"
    r"|호스트|host\b|dye\b|착체|iridium\(III\)|이리듐|Ir\(|\[Ir|Ir-[0-9]|Pt\(II\)|\[Pt"
    r"|Pt\(BPI|Pt\(mpp|PdOEP|PdTPP|Cu\(pop\)|센시타이저|sensitizer", re.I)
# 제외 — 고분자 · 무기 나노결정 · **연속체로 모델링되는 층/필름** · 오탐.
# **경계를 여기서 못박는다** — 레코드가 *분자*를 말하면 `molecular`, *층*을 말하면
# 그 층의 벌크 어휘다. `OLED Emitter Layer` 셋은 E·인장·밀도를 가진 균질층 대표값이라
# 남긴다(그 값으로 해석에 들어간다). §475 의 소자/부품 가르기와 같은 자다.
_NAME_EXC = re.compile(
    r"polynorbornene|copolymer|homopolymer|폴리|poly\(|polyimide|PSA|resin|epoxy|OCA\b"
    r"|acrylic|Cathode|austenitic|steel|Quantum dot|양자점|PDMS|silicone|film\b|layer\b"
    r"|필름|coating|Perylenediimide|nanocrystal|nanoparticle"
    r"|^OLED (Emitter Layer|Host/Transport|ETL/HTL)", re.I)
_MOL_FROM = ("polymer", "composite")

# ── ② ceramic 으로 옮길 순수 탄소 ────────────────────────────────────────────
# **이름 전수 스윕(탄소 토큰 208종)을 눈으로 벳한 결과다.** 정규식으로 쓸면
# `Epoxy + Graphite 40 wt%` 같은 진짜 복합재를 죽인다(§480 — 매처를 넓히면 값을 죽인다).
# 그래서 여기만은 이름 목록이다. 목록은 전수 조사에서 나왔지 인계에서 나오지 않았다.
_CARBON_NAMES = (
    "Graphite PGS (Pyrolytic Sheet)",
    "Carbon Black (conductive additive)",
    "Graphene Film (thermal)",
    "PGS Graphite Sheet 100 um (Panasonic)",
    "T300-type plain-weave carbon fibre, Wei-hai Development Fiber (Ding 2021 raw-material spec)",
    "Toho Tenax Fortafil 243 PAN carbon fibre (chopped/pelletised, 3.2 mm)",
    "Zoltek Panex 30 MF milled high-purity PAN carbon fibre (150 um)",
    "Catalytic MWNT A/CoSi700 (acetylene / Co-silica 700 C, HF+HNO3 purified) — Frackowiak 2002",
    "Catalytic MWNT A/CoSi900 (acetylene / Co-silica 900 C, fishbone, HF+HNO3 purified) — Frackowiak 2002",
    "Catalytic MWNT A/CoSi900 annealed 2400 C / 1 h in Ar — Frackowiak 2002",
    "Catalytic MWNT A/CoNaY600 (acetylene / Co-NaY zeolite 600 C, HF purified) — Frackowiak 2002",
    "Catalytic MWNT from acetylene/Co-silica, heat-treated 900 C (Frackowiak 1999)",
    "Catalytic MWNT from acetylene/Co-silica, heat-treated 2000 C (Frackowiak 1999)",
    "Catalytic MWNT from acetylene/Co-silica, heat-treated 2800 C (Frackowiak 1999)",
    "Hyperion Graphite Fibrils H23008 catalytic MWNT (Hyperion Catalysis International) — Frackowiak 2002 측정",
    "MCMB mesocarbon microbead graphite (Osaka Gas, heat-treated) — MacNeil 1999",
    "Timcal SFG-75 synthetic flake graphite — MacNeil 1999",
    "Timcal SFG-44 synthetic flake graphite — MacNeil 1999",
    "Timcal KS-75 synthetic flake graphite — MacNeil 1999",
    "Conoco XP-3 petroleum coke (turbostratic, HTT ~1200 C) — MacNeil 1999",
    "BP-Amoco pitch-based carbon fiber (heat-treated) — MacNeil 1999",
    "SWNT buckypaper electrode, untreated HiPco SWNT (control) — Zhou 2005",
    "GnP nanopaper (unfunctionalized graphite nanoplate heat spreader foil, vacuum filtration) — Ferraro 2021",
)
# 템플릿 성장 MWNT 는 이름에 `alumina membrane` 이 들어가 위 목록과 따로 적는다 —
# 주형은 제거되고 남는 것은 탄소다(원문 verbatim: `template-grown … in alumina membrane`).
_CARBON_LIKE = ("Template-grown bamboo-like MWNT P/Al800%",)

# ── ③ 1911 MLCC 칩 판정 ─────────────────────────────────────────────────────
_MLCC_LIKE = "BaTiO3/Ni MLCC chip, Y5V%"
_MLCC_VERDICT = (
    "45차 GD 의 판정 보류를 닫는다 — **소자 표시를 만들지 않는다.** 완제 소자(3x2x1.6 mm, "
    "활성층 150장)인 것은 맞지만 이 레코드가 담은 값은 소자 유효물성이 아니다. "
    "경도 3행은 연마 단면(유전체)의 비커스, 잔류응력 6행은 전극 기준 방향별 값이다. "
    "밀도·E·CTE 가 없어 Ashby 기본축에도 못 오르고 카드도 못 만든다 — 표시가 바꿀 것이 없다. "
    "유효 밀도·E·CTE 를 나중에 넣게 되면 그때는 소자값이므로 `role`/`attributes` 를 다시 판정해라."
)


def _rows(conn):
    return conn.execute(sa.text(
        "select id, name, category from material")).fetchall()


def _mo_ids(conn) -> set[int]:
    q = "select distinct material_id from property_value where property_key in :k"
    return {r[0] for r in conn.execute(sa.text(q).bindparams(
        sa.bindparam("k", expanding=True)), {"k": list(_MO_KEYS)})}


def _molecular_ids(conn) -> list[int]:
    mo = _mo_ids(conn)
    out = []
    for mid, name, cat in _rows(conn):
        if cat not in _MOL_FROM:
            continue
        nm = name or ""
        if not (mid in mo or _NAME_SIG.search(nm)):
            continue
        if _NAME_EXC.search(nm):
            continue
        out.append(mid)
    return out


def _set_verdict(conn, key: str, value: str | None) -> None:
    rows = conn.execute(sa.text(
        "select id, attributes from material where name like :p"), {"p": _MLCC_LIKE}).fetchall()
    for mid, attrs in rows:
        try:
            a = json.loads(attrs) if attrs else {}
        except (TypeError, ValueError):
            continue
        if not isinstance(a, dict):
            continue
        if value is None:
            a.pop(key, None)
        else:
            a[key] = value
        conn.execute(sa.text("update material set attributes=:a where id=:i"),
                     {"a": json.dumps(a, ensure_ascii=False), "i": mid})


def upgrade() -> None:
    conn = op.get_bind()
    ids = _molecular_ids(conn)
    if ids:
        conn.execute(sa.text("update material set category='molecular' where id in :i")
                     .bindparams(sa.bindparam("i", expanding=True)), {"i": ids})
    conn.execute(sa.text(
        "update material set category='ceramic' where category='composite' and name in :n")
        .bindparams(sa.bindparam("n", expanding=True)), {"n": list(_CARBON_NAMES)})
    for pat in _CARBON_LIKE:
        conn.execute(sa.text(
            "update material set category='ceramic' where category='composite' and name like :p"),
            {"p": pat})
    _set_verdict(conn, "verdict_device", _MLCC_VERDICT)


def downgrade() -> None:
    conn = op.get_bind()
    # 되돌리면 **전부 polymer 로 간다** — 원래 10종은 composite 였다. 어느 쪽이었는지
    # 되찾을 방법이 없어서(그게 결함이었다) 다수 쪽으로 되돌린다. 이 다운그레이드는
    # 마이그레이션 검증용이지 운영 롤백용이 아니다.
    conn.execute(sa.text("update material set category='polymer' where category='molecular'"))
    conn.execute(sa.text(
        "update material set category='composite' where category='ceramic' and name in :n")
        .bindparams(sa.bindparam("n", expanding=True)), {"n": list(_CARBON_NAMES)})
    for pat in _CARBON_LIKE:
        conn.execute(sa.text(
            "update material set category='composite' where category='ceramic' and name like :p"),
            {"p": pat})
    _set_verdict(conn, "verdict_device", None)
