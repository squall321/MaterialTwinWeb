#!/usr/bin/env python3
# 대표값 **동률**(선택기가 못 가른 것)을 세고, 왜 갈렸는지 축으로 분류하고, 판정을 선언으로 낸다.
#
# 왜 있나(51차 MA). 50차 LA 가 라이브 41,368행에서 잰 대로, 후보가 둘 이상인 (재료,물성키)
# 6,306쌍 중 3,975쌍이 **적재 순서(id)로만** 갈린다(§545). LA 는 그것을 `representative_ties()`
# 로 **드러냈고**, 이 도구는 그 다음 칸이다 — **왜 갈렸는지를 분류해 값에 적는다.**
#
# **값을 고치지도 버리지도 않는다.** `conditions` 에 `verdict_tie_axis`·`verdict_tie_note`
# 두 칸만 더한다. 그 두 칸은 적재기의 `corrections` 경로(§521)로 들어가고, 병합기의 정정
# 전파 분기(§522)를 타 운영까지 간다.
#
# 규율 둘 — 이걸 어기면 값이 조용히 바뀐다.
#   ① **한 군의 모든 행에 같은 수의 칸**을 더해라. `_rep_rank` 5번째 자리가 `len(conditions)`
#      라서 일부 행에만 더하면 대표값이 뒤집힌다(`tests/test_rep_rank.py` 가 양방향으로 못박았다).
#   ② **전파 불가능한 군은 건너뛰어라**(`gen` 이 자동으로 뺀다). 병합기는 (재료·키·출처·옛 값)
#      으로 운영행을 찾는데 그게 유일하지 않으면 **운영에 새 행을 만든다.**
#
# 사용:
#   MATERIALTWIN_DATA_DIR=<라이브> python3 tie_verdicts.py census
#   … classify                      부류별 집계
#   … dump <부류> [n] [card]        손확인용 덤프
#   … gen <out.json> [all]          `corrections` 선언 생성(기본은 카드 8키·격차 10% 초과)
import argparse
import json
import os
import random
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.catalog_compare import _rep_rank, _temp_distance, _tie_key  # noqa: E402

# 해석 카드가 바로 읽는 여덟 키 — 동률 판정의 최우선 표적이다.
CARD_KEYS = {"physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
             "mechanical.yield_strength", "mechanical.tensile_strength",
             "thermal.conductivity", "thermal.specific_heat", "thermal.expansion_linear"}
BY = os.environ.get("TIE_VERDICT_BY", "51차 MA")


def db_path() -> str:
    d = os.environ.get("MATERIALTWIN_DATA_DIR")
    if not d:
        sys.exit("MATERIALTWIN_DATA_DIR 를 지정해라 — 어느 DB 를 치는지 밝히지 않으면 "
                 "낡은 개발 DB 를 본다(브리프 30·49).")
    return str(Path(d) / "materialtwin.db")


class PV:
    __slots__ = ("id", "material_id", "property_key", "value_num", "value_text", "unit",
                 "conditions", "method", "quality_tier", "source_id", "notes")

    def __init__(self, r):
        (self.id, self.material_id, self.property_key, self.value_num, self.value_text,
         self.unit, c, self.method, self.quality_tier, self.source_id, self.notes) = r
        self.conditions = json.loads(c) if c else None


def load(db, numeric_only=True):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute("select id,material_id,property_key,value_num,value_text,unit,"
                       "conditions,method,quality_tier,source_id,notes "
                       "from property_value").fetchall()
    con.close()
    pvs = [PV(r) for r in rows]
    return [p for p in pvs if p.value_num is not None] if numeric_only else pvs


def groups(pvs):
    g = defaultdict(list)
    for pv in pvs:
        g[(pv.material_id, pv.property_key)].append(pv)
    return g


def tie_groups(db, numeric_only=True):
    """[((재료,키), 1위행, [순위가 완전히 같은 경쟁행…])] — 즉 적재 순서로 갈린 것들."""
    out = []
    for k, rows in groups(load(db, numeric_only)).items():
        if len(rows) < 2:
            continue
        rows.sort(key=_rep_rank)
        tk = _tie_key(rows[0])
        riv = [p for p in rows[1:] if _tie_key(p) == tk]
        if riv:
            out.append((k, rows[0], riv))
    return out


def gap(a, riv):
    m = [abs(a.value_num - b.value_num) / max(abs(a.value_num), abs(b.value_num))
         for b in riv if max(abs(a.value_num), abs(b.value_num)) > 0]
    return max(m) if m else 0.0


# ① 다른 물리량·다른 세트·다른 정의 — 대표값을 다투는 것 자체가 잘못이다
TERM = {"term","prony_term","term_index","set_id","unit_of_term","model","model_form",
        "component","quantity","parameter","symbol","property","strength_property",
        "polynomial_degree_term","definition","measure",
        "constitutive_model","transition","transition_label","phase_boundary","stress_definition",
        "criterion","failure_criterion","mechanism","normalization","estimator","distribution_stat",
        "alpha","tau_s","relaxation_time_s","paired_tau_s","paired_exponent_n","paired_coefficient_a",
        "paired_relaxation_time_term","paired_activation_energy_kj_per_mol","diffusing_species",
        "permeant","life_basis","value_basis","stress_basis","specimen_basis","temperature_basis",
        "sign_convention","stress_reference_area","printed_form","fit_mode","fit_method",
        "gap_kind",
        # 손확인에서 나온 것들 — `basis` 는 shear 대 tensile · T5% 대 T50% 였다(51차 MA)
        "basis","determination","gage_basis","strength_property","measure"}

# ② 산포·범위의 양끝 — 한 값의 두 얼굴이다(브리프 76·110)
SPREAD = {"bound","range","range_C","temp_range","scatter","std_dev","variance_k2",
          "uncertainty","uncertainty_pm","uncertainty_mpa","uncertainty_gpa","uncertainty_sd_j_m2",
          "uncertainty_printed","reading_uncertainty","coefficient_of_variation",
          "ci95_upper","ci95_lower","confidence_interval_90pct","confidence_interval_90pct_mpa",
          "distribution","distribution_min_mpa","distribution_max_mpa",
          "r_squared","r_squared_range_reported_in_text","fit_correlation_r",
          "range_over_crosshead_speeds_mpa","reproducibility_pct","life_range_cycles",
          "strain_rate_range_s","pore_size_range","Mw_range_Da","frequency_range_hz",
          "spectral_range_nm","stress_range_pa","evaluation_range_C","depth_range_um",
          "applicable_temperature_range_c","printed_value","tolerance",
          # 손확인 — average/min/max·typical/minimum 은 한 값의 통계량이다(51차 MA)
          "statistic","value_type"}

# ③ 같은 조건의 반복 시편 — 값의 산포지 의견 차가 아니다
REPLICATE = {"run","replicate","replicates","sample_id","sample_code","sample_label","sample",
             "specimen_number","specimen_no","specimen_id","specimen_group","group","series",
             "test_batch","n_specimens","n_samples","measurement_sequence","measurement"}
# 손확인(51차 MA) — `specimen` 은 '3-1' 같은 시편 번호도 되지만 'clad/etched'·'3.2 mm disc' 도
# 된다. 반복이 아니라 조건이므로 시편축으로 보낸다. `cycle(s)` 도 하중이력이지 반복이 아니다.

# ④ 자유서술 — 축이 여기 숨는다(51차 MA 손확인: 방향·파장·Tg영역·제품명이 detail 안에 있었다)
FREE = {"detail","note","notes","remark","context","condition_note","description",
        "temperature_note","comment"}
# `method_detail` 은 서술이 아니라 시험법 축이다 — 값이 TMA 대 DMA 였다(51차 MA 손확인).

# ⑤ 순수 기록 — 물리 조건이 아니다
BOOK = {"figure","source_figure","table","source_table","source_page","line","dataset",
        "provenance","document_conflict","correction","converted_from","fitted_from","baseline",
        "scope_limit","regression","missing_partner_constants","sign_check","cooling_curve_no",
        "printed_companion","printed_strain_rate","assumed_stress_strain_set",
        "steady_state_same_row","phase_angle_deg_same_row","shear_stress_status","averaging",
        "midpoint_of_range","temperature_independent","reference_state","not_printed",
        "ansys_version","fe_model_config","simulation_method","time_step_scheme",
        "temperature_change_command","package_effect","class_value"}

# ⑥ 구조화된 조건축 — 정규식으로 받는다(꼬리가 550키다)
AXIS_PATTERNS = [
    (r"^(direction|axis|orientation|plane|crystal_orientation|side|angle|angle_deg|"
     r"orientation_deg_to_RD|ray|reflection|fracture_plane|crack_direction|incident_angle_deg|"
     r"peel_arm|measurement_region|measured_layer|location|hole)$", "방향"),
    (r"(strain_rate|shear_rate|rate_mm|crosshead_speed|loading_speed|test_speed|peel_rate|"
     r"stress_rate|cycles_per_hour|frequency|angular_frequency|speed_rpm|conveyor_speed|"
     r"force_ramp_rate|impact_velocity|loading_velocity|slow_shot_speed|fast_shot_speed|"
     r"^sweep$|waveform|frequency_factor|wavelength)", "율속·주파수·파장"),
    (r"(^temperature|_temperature|temperature_|^temp_|^Tg|below_Tg|_k$|_c$|_C$|_f$|"
     r"final_temperature|^regime$)", "온도·상태영역"),
    (r"(aging|ageing|anneal|temper$|tempering|heat_treatment|cure|sinter|calcination|soaking|"
     r"austenitizing|post_treatment|post_anneal|processing|^process$|consolidation|milling|"
     r"holding_time|dwell|weathering|irradiation_time|exposure|preconditioning|pretreatment|"
     r"surface_pretreatment|bcb_cure|degree_of_cure|aging_protocol|idle_time|"
     r"cooling_rate|t800_500_s|welding_energy|aging_after_welding|hold_time|contact_time|"
     r"recovery_time|creep_time|duration|exposure_window|exchange_time|ion_exchange)",
     "열이력·공정"),
    (r"(humid|moisture|atmosphere|environment|weather|medium|liquid|solvent|^ph$|ph_range|"
     r"msl_condition|oxygen_partial_pressure|vacuum|conditioning|soc|state_of_charge|"
     r"state_of_health)", "환경·조습"),
    (r"(thickness|^layer|layers|geometry|gauge|notch|span_mm|bond_area|"
     r"^die|package|chip_size|block_size|wafer|bar_diameter|ball_diameter|drop_size|drop_volume|"
     r"particle|D50|grain_size|porosity|relative_density|tap_density|microstructure|composition|"
     r"filler|matrix|clay|crosslinker|coupling_agent|resin_content|silver_content|carbon_coating|"
     r"li_content|lipf6|purity|space_group|form$|specimen_form|construction|"
     r"wire_diameter|weight_oz|number_of_|heat_pipe|roughness|depth_um|effective_pore_radius|"
     r"carrier_concentration|voids_inside_grains|surface_residual_stress|solidus_c|liquidus_c|"
     r"^phase$|phase_at_test_temperature|_wt_pct|_vol_pct|_content|weight_loss_pct|"
     r"specimen_purpose|specimen_dimensions_mm|blend|enr_content|^fraction$|^polydispersity$|"
     r"^specimen$)", "시편·조성"),
    (r"(substrate|adherend|backing|interface|surface|primer|interlayer|metall|plasma_clean|"
     r"carrier_substrate|die_type|stress_balance_layer|ald_layer|parylene_type|"
     r"sputtering_power|ultrasonic|bondline)", "계면·표면"),
    (r"(^load|_load|stress|pressure|compress|^strain|stretch|bending|bend_radius|deflection|"
     r"impact|control_mode|loading|^mode$|stress_ratio|transition_life|"
     r"cyclic_elastic|amplitude|failure_mode|fracture_type|crack_onset|crack_pattern|^cycle$|^cycles$|"
     r"darveaux_index|reversibility|^stage$|thermal_cycle|^profile|^branch$)", "하중·이력"),
    (r"(standard|test_method|^test$|^method|measurement_method|technique|"
     r"test_geometry|test_voltage|voltage_V|indenter|hardness_hrc|instrument|"
     r"viscosity_log10_poise|calibration_strain_rate|reference_strain_rate|"
     r"reference_temperature|lamp|intensity|chromaticity|^application$|^angle_type$|^analysis$)", "시험법"),
    (r"(grade|brand|alloy|foil_grade|formulation|^powder$|^filler$|"
     r"mixing_ratio|solution_concentration|^condition$|_state$|^state$|"
     r"product_form|^product)", "등급·상태"),
]
_AX = [(re.compile(p), lab) for p, lab in AXIS_PATTERNS]

# 자유서술 안에서 축을 읽는다. **원문에 없는 축을 지어내지 않는다** — 서술이 그 낱말을
# 실제로 인쇄했을 때만 잡는다(브리프 537 의 규율).
TEXT_AXES = [
    (r"(lengthwise|crosswise|warp|fill\b|in-?plane|through-?plane|through-?thickness|"
     r"machine direction|transverse|\bMD\b|\bTD\b|axial|radial|basal|x-?axis|y-?axis|z-?axis|"
     r"parallel to|perpendicular to)", "방향"),
    (r"(alpha ?1|alpha ?2|below tg|above tg|glassy|rubbery|α1|α2)", "온도·상태영역"),
    (r"(\d+\s*nm\b|wavelength|passband|stop-?band)", "율속·주파수·파장"),
    (r"(\d+\s*(°|deg)?\s*C\b|room temperature|\bK\b)", "온도·상태영역"),
    # 52차 NC 고침 — `wt%\b` 는 **한 번도 안 걸린다.** `%` 뒤에 오는 것이 공백이라
    # 둘 다 비단어 문자여서 `\b` 가 성립하지 않는다(`'15 wt% CB'` → 0건, 실측).
    # 그리고 몰농도 `M` 이 `re.I` 라 `'1270 m^2/g'`·`'50 min'` 을 조성으로 오인했다.
    # 전수 대조 — 이 둘을 고치니 2군이 서술차이 → 서술축으로 옮겨갔고(재료138 AgNW 1.9 대
    # 1.1 vol%, 재료147 카본블랙 15 대 3 wt%) 다른 군은 하나도 안 바뀌었다.
    (r"(\d+(\.\d+)?\s*(?:wt\.?\s?%|vol\.?\s?%|mol\s?%|at\.?\s?%|phr\b)"
     r"|\d+(\.\d+)?\s*M(?![A-Za-z]))", "시편·조성"),
    (r"(\d+(\.\d+)?\s*(mil|um|µm|mm)\b)", "시편·조성"),
    (r"(\d+(\.\d+)?\s*(Hz|kHz|MHz|GHz)\b|/min\b|mm/min)", "율속·주파수·파장"),
    # 52차 NC 추가 — 서술 안의 **공정 시간**. 재료191 NiCr 은 RTA 가 60 s 대 600 s 인데
    # 그것이 `detail` 안에만 있어 "서술만 다르다" 로 분류됐다. 전수 대조 1군 이동·0군 부작용.
    (r"(\d+(\.\d+)?\s*(?:s|sec|seconds?|min|minutes?|h|hr|hours?|d|days?)\b)", "열이력·공정"),
]
_TX = [(re.compile(p, re.I), lab) for p, lab in TEXT_AXES]


def axis_label(k: str):
    for rx, lab in _AX:
        if rx.search(k):
            return lab
    return None


def _text_axis(vals):
    """두 서술이 **다르게 인쇄한** 축 낱말만 잡는다. 한쪽에만 있으면 그것이 갈린 축이다."""
    labs = []
    for rx, lab in _TX:
        hits = [set(m.group(0).lower() for m in rx.finditer(str(v or ""))) for v in vals]
        if any(h != hits[0] for h in hits[1:]) and any(hits):
            labs.append(lab)
    return sorted(set(labs))


# 같은 축을 **다른 키 이름으로** 적은 경우. 51차 MA 손확인에서 조건미기재 199군 중 91군이
# 이것이었다 — `standard` 대 `test_standard` · `axis` 대 `direction` · `temperature_c` 대
# `temperature_C` · `frequency_Hz` 대 `frequency_hz`. 축이 갈린 게 아니라 **표기가 갈렸다.**
SYN = {"axis": "direction", "conditioning": "condition", "test": "method",
       "measurement_method": "method", "test_method": "method", "method_detail": "method",
       "test_standard": "standard", "technique": "method", "test_geometry": "geometry",
       "test_voltage": "voltage", "test_speed": "speed", "test_mode": "mode",
       "test_temperature": "temperature", "test_frequency": "frequency"}
_UNIT_SUFFIX = re.compile(
    r"_(hz|k|c|f|v|mm|um|nm|mpa|pa|s|deg|degc|celsius|kelvin|percent|pct|wt|in|mil)$")


def norm_key(k: str) -> str:
    k = _UNIT_SUFFIX.sub("", k.lower())
    k = k[5:] if k.startswith("test_") else k
    return SYN.get(k, k)


def synonym_pairs(head, rivals):
    """한쪽에만 있는 키가 **정규화하면 상대쪽 키와 같아지는** 짝들. 없으면 빈 리스트."""
    out = []
    ca = head.conditions or {}
    for b in rivals:
        cb = b.conditions or {}
        oa, ob = set(ca) - set(cb), set(cb) - set(ca)
        for x in sorted(oa):
            for y in sorted(ob):
                if norm_key(x) != norm_key(y):
                    continue
                # 온도는 단위 접미어가 **표기 흔들림이 아닐 수 있다** — 51차 MA 손확인에서
                # 재료 508/510 의 `temperature_C 20` 대 `temperature_K 77` 이 걸렸다.
                # 그건 다른 온도다(광학 키라 선택기가 온도를 안 봐서 동률이 됐을 뿐이다).
                # 상온 거리가 같을 때만 같은 축의 표기 차이로 본다.
                if norm_key(x).startswith("temperature") and \
                        _temp_distance(ca) != _temp_distance(cb):
                    continue
                out.append((x, y))
    return sorted(set(out))


# 52차 NC — MA 의 온도 가드는 **짝을 버리기만 하고 그 다음을 정하지 않았다.**
# `temperature_C 20` 대 `temperature_K 77` 은 짝에서 빠진 뒤 "한쪽에만 있는 축" 으로 남아
# **조건미기재**로 판정됐다. 그런데 두 행 모두 온도를 인쇄했다 — 축은 닫혀 있고 값이 다르다.
# 판정문이 *"이 축이 한쪽에만 적혀 있다"* 라고 말하는데 그것이 사실이 아니다(브리프 505 —
# 틀린 주의는 표적이 틀린 것보다 나쁘다). 라이브 전수에서 5군(재료508~512 Pt(II) 인광체,
# 20 °C 톨루엔 용액 대 77 K 2-MeTHF 유리)이 여기 걸렸고 다른 군은 하나도 안 움직였다.
_TEMP_IN_TEXT = re.compile(r"(-?\d+(?:\.\d+)?)\s*(?:°|deg\s*)?\s*([CKF])\b", re.I)


def temp_c(key, val):
    """(조건키, 값) 에서 °C 를 읽는다. **못 읽으면 None** — 지어내지 않는다."""
    kl = key.lower()
    if isinstance(val, bool) or val is None:
        return None
    if isinstance(val, (int, float)):
        if kl.endswith(("_k", "_kelvin")):
            return float(val) - 273.15
        if kl.endswith(("_c", "_celsius")):
            return float(val)
        if kl.endswith("_f"):
            return (float(val) - 32) / 1.8
        return None
    if isinstance(val, str):
        m = _TEMP_IN_TEXT.search(val)
        if m:
            v, u = float(m.group(1)), m.group(2).upper()
            return v if u == "C" else v - 273.15 if u == "K" else (v - 32) / 1.8
    return None


def norm_pairs(head, rivals):
    """`synonym_pairs` 와 같은 짝인데 **값 비교 없이 전부** 돌려준다. (키, 값, 키, 값)."""
    out = []
    ca = head.conditions or {}
    for b in rivals:
        cb = b.conditions or {}
        oa, ob = set(ca) - set(cb), set(cb) - set(ca)
        for x in sorted(oa):
            for y in sorted(ob):
                if norm_key(x) == norm_key(y):
                    out.append((x, ca.get(x), y, cb.get(y)))
    return out


def _axis_closed_by_other_name(head, rivals, only_axis):
    """한쪽에만 있는 축 키가 **상대쪽의 다른 이름 같은 축**과 전부 짝이 되는가.

    돌려주는 것 — (같은 값 짝, 다른 값 짝). 둘 다 비면 축이 안 닫혔다는 뜻이다.
    온도는 실제로 읽어서 비교한다. **못 읽는 온도는 판단을 미룬다**(짝으로 안 센다).
    """
    same, diff = [], []
    for x, vx, y, vy in norm_pairs(head, rivals):
        tx, ty = temp_c(x, vx), temp_c(y, vy)
        if tx is not None and ty is not None:
            (same if abs(tx - ty) <= 1.0 else diff).append((x, y))
        elif norm_key(x).startswith("temperature"):
            continue
        else:
            same.append((x, y))
    covered = {x for x, y in same + diff} | {y for x, y in same + diff}
    if only_axis - covered:
        return [], []          # 안 닫힌 축이 남아 있다
    return sorted(set(same)), sorted(set(diff))


# 우리가 조건에 적는 살림살이 — **조건이 아니다.** 분류에서 빼지 않으면 이 도구가
# 자기가 적은 판정을 "갈린 축" 으로 다시 읽는다(51차 MA 가 두 번째 실행에서 확인했다).
def _is_bookkeeping(k: str) -> bool:
    return (k.startswith("verdict_") or k.endswith("_before_correction")
            or k in ("correction_reason", "corrected_by", "correction_evidence"))


def facets(head, rivals):
    """갈린 조건키를 **면(facet)별로** 모은다. 한 군이 여러 면에서 갈릴 수 있다."""
    only, common = set(), set()
    same_src = True
    for b in rivals:
        ca, cb = head.conditions or {}, b.conditions or {}
        only |= (set(ca) ^ set(cb))
        common |= {x for x in set(ca) & set(cb) if ca[x] != cb[x]}
        if head.source_id != b.source_id:
            same_src = False
    only = {k for k in only if not _is_bookkeeping(k)}
    common = {k for k in common if not _is_bookkeeping(k)}
    d = only | common
    ax = {k: axis_label(k) for k in d if k not in (BOOK | FREE | REPLICATE | TERM | SPREAD)}
    ax = {k: v for k, v in ax.items() if v}
    txt = []
    for k in sorted(d & FREE):
        txt += _text_axis([(pv.conditions or {}).get(k) for pv in [head] + rivals])
    return {"term": sorted(d & TERM), "spread": sorted(d & SPREAD), "axis": ax,
            "replicate": sorted(d & REPLICATE), "free": sorted(d & FREE),
            "text_axis": sorted(set(txt)), "book": sorted(d & BOOK),
            "only": sorted(only), "all": sorted(d), "same_src": same_src}


def classify(head, rivals):
    """(부류, 라벨들, 갈린 조건키들). 부류는 **가장 앞선 면**이 정하고, 라벨은 면을 전부 싣는다.

    우선순위 — 다른항 > 다른조건/조건미기재 > 산포범위 > 반복시편 > 서술축 > 서술차이 > 의견차.
    **다른항이 앞인 이유**는 그 군의 대표값 자체가 뜻이 없기 때문이고(브리프 545),
    **조건축이 산포보다 앞인 이유**는 51차 MA 손확인이다 — NP-155FR 은 `bound` 와 `below_Tg` 가
    같이 갈리는데 값을 85% 벌리는 것은 α1/α2 이지 min/max 가 아니다.
    """
    f = facets(head, rivals)
    labs = list(f["term"]) + sorted(set(f["axis"].values())) + f["text_axis"] \
        + f["spread"] + f["replicate"]
    labs = sorted(set(labs))
    if f["term"]:
        return "다른항", labs, f["all"]
    if f["axis"]:
        only_axis = set(f["axis"]) & set(f["only"])
        if only_axis:
            # 52차 NC — 표기가 달라 한쪽에만 있는 것처럼 보이는 축을 먼저 닫는다.
            same, diff = _axis_closed_by_other_name(head, rivals, only_axis)
            if diff:
                return "다른조건", labs, f["all"]      # 축은 양쪽에 있고 **값이 다르다**
            if same:
                return "키표기흔들림", [f"{x}↔{y}" for x, y in same] + labs, f["all"]
            syn = synonym_pairs(head, rivals)
            if syn:
                return "키표기흔들림", [f"{x}↔{y}" for x, y in syn] + labs, f["all"]
            return "조건미기재", labs, f["all"]
        return "다른조건", labs, f["all"]
    if f["spread"]:
        return "산포범위", labs, f["all"]
    if f["replicate"]:
        return "반복시편", labs, f["all"]
    if f["text_axis"]:
        return "서술축", labs, f["all"]
    if f["free"]:
        return "서술차이", sorted(f["free"]), f["all"]
    if not f["all"]:
        return ("같은출처중복" if f["same_src"] else "의견차"), [], []
    return "의견차", ["기록만 다르다"], f["all"]


HEAD = {
 "다른조건": "축이 다르므로 **둘 다 대표다** — 어느 쪽을 쓸지는 해석자가 정한다.",
 "조건미기재": "이 축이 한쪽에만 적혀 있다 — 축이 닫히지 않았다. "
               "**원문에 없는 조건을 채우지 않았다**(브리프 537).",
 "키표기흔들림": "같은 축을 **다른 키 이름**으로 적었다 — 축이 갈린 게 아니라 표기가 갈렸다. "
                 "키를 통일하면 이 동률은 사라진다.",
 "다른항": "한 키에 **여러 항·세트**가 산다 — 이 (재료,키)의 대표값 자체가 뜻이 없다"
           "(브리프 545). `set_id`·`term` 으로 묶어 읽어라.",
 "산포범위": "한 값의 **하한·상한(또는 통계량)**이다 — 한쪽을 대표로 고르면 범위를 버리는 것이다"
             "(브리프 76·110).",
 "반복시편": "**같은 조건의 반복 시편**이다 — 대표값은 임의의 한 시편이고, 산포를 보려면 전부 봐라.",
 "서술축": "축이 `conditions` 에 없고 **자유서술 안에** 있다 — 서술을 읽어야 갈린다.",
 "서술차이": "조건 축은 같고 **서술만 다르다** — 한 재료에 다른 제품·등급이 섞였을 수 있다"
             "(브리프 123). 서술을 읽어야 갈린다.",
 "의견차": "**인쇄된 조건이 같은데 값이 다르다 — 진짜 의견 차다.** 값을 버리지 않았다. "
           "어느 출처를 쓸지는 해석자가 정한다.",
 "같은출처중복": "조건도 출처도 같다 — **중복 적재로 보인다.** 값은 지우지 않았다.",
}


def fmt(pv):
    v = pv.value_num
    s = f"{v:.6g}" if v is not None else "-"
    return f"{s} {pv.unit or ''}".strip()


def axis_bits(pv, keys, limit=5):
    c = pv.conditions or {}
    out = [f"{k}={json.dumps(c[k], ensure_ascii=False)[:70]}" for k in keys if k in c]
    return " · ".join(out[:limit]) or "(이 행에는 그 축이 없다)"


# 판정을 **남길 수 없는 군**을 뺀다. 병합기(§522)는 `(재료·키·출처·옛 값)` 으로 운영행을 찾는데
# 그것이 유일하지 않으면 갱신하지 못하고 **운영에 새 행을 넣는다** — 같은 측정이 두 벌이 된다.
# 실측(라이브 41,368행 대 운영 사본 예행) — 거르지 않고 2,587행에 달았더니 **509건이 못 갔다.**
# 막는 것은 둘이다.
#   ① 한 군 안에 `(출처, 값)` 이 같은 행이 둘 이상 — 키표기흔들림이 만든 중복 적재다(51차 MA).
#   ② 그 행이 이미 `method_before_correction` 같은 옛 표시를 달고 있다 — 병합기가 그것으로
#      **정정 전 값을 잘못 복원**한다(§451·455 의 중앙값 가드 표시다. 정정이 아니다).
PRIOR_MARKERS = ("value_before_correction", "value_text_before_correction",
                 "unit_before_correction", "method_before_correction")


def blocked_rows(G, k, cnt):
    out = []
    for p in G[k]:
        c = p.conditions or {}
        why = []
        if cnt[(p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)] > 1:
            why.append("같은 (출처,값) 행이 둘 이상")
        if any(x in c for x in PRIOR_MARKERS):
            why.append("옛 *_before_correction 표시")
        if why:
            out.append((p.id, " · ".join(why)))
    return out


def gen(out_path, only_priority=True):
    DB = db_path()
    G = groups(load(DB))
    _all = load(DB, numeric_only=False)
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in _all)
    ties = tie_groups(DB)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    MAT = {r[0]: r[1] for r in con.execute("select id,name from material")}
    SRC = {r[0]: (r[1] or "") for r in con.execute("select id,title from source")}

    sel = [(k, a, riv) for k, a, riv in ties
           if (not only_priority) or (k[1] in CARD_KEYS and gap(a, riv) > 0.10)]
    corr, skipped = [], []
    for k, a, riv in sel:
        blk = blocked_rows(G, k, cnt)
        if blk:
            skipped.append({"material_id": k[0], "material_name": MAT.get(k[0]),
                            "property_key": k[1], "부류": classify(a, riv)[0],
                            "막은 행": blk})
            continue
        c, labs, diff = classify(a, riv)
        f = facets(a, riv)
        axis_keys = sorted(set(f["axis"]) | set(f["term"]) | set(f["spread"])
                           | set(f["replicate"]) | set(f["free"])) or diff
        tied = {a.id} | {b.id for b in riv}
        rows = sorted(G[k], key=_rep_rank)
        axis_txt = f"{c} — {'·'.join(labs)[:120]}" if labs else c
        for pv in rows:
            others = [o for o in rows if o.id != pv.id and o.id in tied]
            rival = " · ".join(f"{fmt(o)} [{axis_bits(o, axis_keys, 3)}]" for o in others[:4])
            if len(others) > 4:
                rival += f" · 외 {len(others)-4}건"
            pos = ("이 행이 대표로 뽑혀 있다" if pv.id == rows[0].id
                   else "이 행은 대표와 순위가 같다(적재 순서로 밀렸다)" if pv.id in tied
                   else "이 행은 순위에서 뒤에 있다(동률이 아니다)")
            note = (f"[{BY} 동률 판정] {HEAD[c]} {pos}. "
                    f"이 행 = {fmt(pv)} [{axis_bits(pv, axis_keys)}]. "
                    f"동률 경쟁행 = {rival or '(없다)'}. "
                    f"갈린 조건키 = {', '.join(diff[:12]) or '(없다 — 조건이 같다)'}.")
            if c == "의견차":
                note += f" 이 행의 출처 = {SRC.get(pv.source_id,'(없다)')[:90]}."
            corr.append({
                "target": {"property_value_id": pv.id,
                           "material_id": pv.material_id,
                           "material_name": MAT.get(pv.material_id),
                           "property_key": pv.property_key},
                "by": BY,
                "reason": (f"대표값 동률 판정 — 값·등급·method·출처를 하나도 바꾸지 않고 "
                           f"**왜 갈렸는지**만 조건에 적는다(브리프 545). 부류 {axis_txt}."),
                "set": {"conditions": dict(pv.conditions or {},
                                           verdict_tie_axis=f"{BY} — {axis_txt}",
                                           verdict_tie_note=note)},
            })
    doc = {"_skipped": skipped, "_comment": (
        "51차 MA — 대표값 동률의 **판정**이다. 값·등급·method·출처를 하나도 바꾸지 않는다. "
        "`conditions` 에 `verdict_tie_axis`·`verdict_tie_note` 두 칸만 더한다. "
        "한 (재료,키) 군의 **모든 행**에 같은 수의 칸을 더해 `_rep_rank` 의 `len(conditions)` "
        "자리가 군 안의 순서를 바꾸지 않게 했다. "
        "`_skipped` 는 판정을 **남기지 못한** 군이다 — 운영 전파가 불가능해 중복을 만든다."),
        "corrections": corr}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"{out_path}: 군 {len(sel)} → 판정 {len(sel)-len(skipped)}군 "
          f"· 정정 선언 {len(corr)}건 · 전파 불가로 뺀 군 {len(skipped)}")




# ── 세기 ────────────────────────────────────────────────────────────────────
def census():
    """인계 수치를 직접 센다(§479·505 — 인계는 언제나 검증 대상이다)."""
    db = db_path()
    print(f"[DB] {db}")
    for label, num in (("수치값 있는 행만(50차 LA 의 모수)", True), ("전 행", False)):
        g = groups(load(db, num))
        multi = {k: v for k, v in g.items() if len(v) > 1}
        sep, ido, gt10 = Counter(), 0, 0
        names = ("비고체", "tier", "수치보유", "지배조건", "조건수", "id")
        for k, rows in multi.items():
            rows.sort(key=_rep_rank)
            a, b = rows[0], rows[1]
            ra, rb = _rep_rank(a), _rep_rank(b)
            for i, nm in enumerate(names):
                if ra[i] != rb[i]:
                    sep[nm] += 1
                    break
            if _tie_key(a) == _tie_key(b):
                ido += 1
                if None not in (a.value_num, b.value_num):
                    m = max(abs(a.value_num), abs(b.value_num))
                    if m > 0 and abs(a.value_num - b.value_num) / m > 0.10:
                        gt10 += 1
        print(f"\n{label} — (재료,키) 쌍 {len(g)} · 후보 둘 이상 {len(multi)}")
        print(f"  1·2위가 id 로만 갈림 {ido} · 그중 1·2위 값이 10% 초과 {gt10}")
        print(f"  1·2위를 가른 자리 {dict(sep)}")
    ties = tie_groups(db)
    print(f"\n동률군(1위와 순위가 완전히 같은 경쟁행 보유) {len(ties)} "
          f"· 1위 대 **모든** 경쟁행 중 하나라도 10% 초과 "
          f"{sum(1 for k, a, r in ties if gap(a, r) > 0.10)}")


def classify_report():
    db = db_path()
    ties = tie_groups(db)
    tot, big, card = Counter(), Counter(), Counter()
    for k, a, riv in ties:
        c = classify(a, riv)[0]
        tot[c] += 1
        if gap(a, riv) > 0.10:
            big[c] += 1
            if k[1] in CARD_KEYS:
                card[c] += 1
    order = ["다른항", "다른조건", "조건미기재", "키표기흔들림", "산포범위", "반복시편",
             "서술축", "서술차이", "의견차", "같은출처중복", "미분류"]
    print(f"[DB] {db}\n{'부류':<13}{'전체':>7}{'10%초과':>9}{'카드8키&10%':>12}")
    for c in order:
        print(f"{c:<13}{tot[c]:>7}{big[c]:>9}{card[c]:>12}")
    print(f"{'합':<13}{sum(tot.values()):>7}{sum(big.values()):>9}{sum(card.values()):>12}")


def dump(want, n, only_card):
    db = db_path()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    MAT = {r[0]: r[1] for r in con.execute("select id,name from material")}
    sel = []
    for k, a, riv in tie_groups(db):
        c, labs, d = classify(a, riv)
        if c != want or (only_card and (k[1] not in CARD_KEYS or gap(a, riv) <= 0.10)):
            continue
        sel.append((k, a, riv, labs, d))
    random.seed(510)
    random.shuffle(sel)
    print(f"### {want} — {len(sel)}군 중 {min(n, len(sel))}군")
    for k, a, riv, labs, d in sel[:n]:
        print(f"\n· 재료{k[0]} {MAT.get(k[0],'')[:44]} | {k[1]} | 격차 {gap(a,riv)*100:.0f}% "
              f"| 라벨 {'·'.join(labs)[:70]}")
        for pv in [a] + riv[:4]:
            vals = {x: (pv.conditions or {}).get(x) for x in d}
            print(f"    pv{pv.id} {pv.value_num:.4g} :: "
                  f"{json.dumps(vals, ensure_ascii=False)[:180]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("census")
    sub.add_parser("classify")
    d = sub.add_parser("dump")
    d.add_argument("kind")
    d.add_argument("n", nargs="?", type=int, default=15)
    d.add_argument("--card", action="store_true")
    g = sub.add_parser("gen")
    g.add_argument("out")
    g.add_argument("--all", action="store_true",
                   help="카드 8키·격차 10% 초과 제한을 풀고 동률군 전부를 낸다")
    a = ap.parse_args()
    if a.cmd == "census":
        census()
    elif a.cmd == "classify":
        classify_report()
    elif a.cmd == "dump":
        dump(a.kind, a.n, a.card)
    else:
        gen(a.out, only_priority=not a.all)


if __name__ == "__main__":
    main()
