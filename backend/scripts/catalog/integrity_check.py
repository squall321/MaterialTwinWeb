# 카탈로그 정합성 20항목 일괄 점검 — 0이 아니면 결함이다. 배포 전 반드시 통과시킬 것.
import sqlite3
import sys

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
OPT = "('optical.refractive_index','optical.reflectance','optical.extinction_coefficient','optical.birefringence')"
# 값 자체가 온도인 물성 — 여기에 temperature_C 조건이 붙으면 대표값 선택이 무너진다(문서 19장).
TEMP_VALUED = ("('thermal.melting_point','thermal.glass_transition','thermal.max_service_temp',"
               "'thermal.min_service_temp','thermal.decomposition_temp','thermal.heat_deflection_temp',"
               "'thermal.vicat_softening')")

CHECKS = [
    ("출처 없는 값", "select count(*) from property_value where source_id is null"),
    ("끊어진 출처 참조", """select count(*) from property_value pv left join source s on s.id=pv.source_id
        where pv.source_id is not null and s.id is null"""),
    ("정의 없는 물성키", """select count(*) from property_value pv
        left join property_definition pd on pd.key=pv.property_key where pd.key is null"""),
    ("고아 시편", "select count(*) from specimen sp left join material m on m.id=sp.material_id where m.id is null"),
    ("값·텍스트 모두 없음", "select count(*) from property_value where value_num is null and coalesce(value_text,'')=''"),
    ("단위가 정의와 다름", """select count(*) from property_value pv join property_definition pd on pd.key=pv.property_key
        where pv.value_num is not null and pd.si_unit is not null and coalesce(pv.unit,'')<>pd.si_unit"""),
    ("tier 범위 밖", "select count(*) from property_value where quality_tier not between 1 and 5"),
    ("method 어휘 밖", "select count(*) from property_value where method not in ('measured','handbook','computed','estimated')"),
    ("출처 kind 어휘 밖", """select count(*) from source where kind not in
        ('journal','book','database','datasheet','computed','standard','web','other')"""),
    ("category 어휘 밖", """select count(*) from material where category not in
        ('metal','polymer','rubber','composite','ceramic','foam')"""),
    ("물성값 0인 재료", "select count(*) from material m where not exists(select 1 from property_value where material_id=m.id)"),
    ("추정만 있는 재료", """select count(*) from (select m.id from material m join property_value pv on pv.material_id=m.id
        group by m.id having min(pv.quality_tier)>=4)"""),
    ("제목 없는 출처", "select count(*) from source where coalesce(title,'')=''"),
    ("journal인데 DOI 없음", "select count(*) from source where kind='journal' and coalesce(doi,'')=''"),
    ("조건이 dict 아님", "select count(*) from property_value where conditions is not null and conditions not like '{%'"),
    ("초탄성인데 model 조건 없음", """select count(*) from property_value where property_key like 'mechanical.hyperelastic%'
        and (conditions is null or conditions not like '%model%')"""),
    ("파장 없는 광학값(tier<4)", f"""select count(*) from property_value where property_key in {OPT}
        and quality_tier<4 and (conditions is null or (conditions not like '%wavelength%' and conditions not like '%line%'))"""),
    ("온도가 값인데 온도 조건", f"select count(*) from property_value where property_key in {TEMP_VALUED} and conditions like '%temperature_C%'"),
    ("Prony 항에 항번호 없음", """select count(*) from property_value where property_key like 'mechanical.prony_%'
        and (conditions is null or conditions not like '%term%')"""),
    ("파장 조건이 가시광 밖(오타 의심)", f"""select count(*) from property_value where property_key in {OPT}
        and conditions like '%wavelength_nm%' and (
            cast(replace(substr(conditions, instr(conditions,'wavelength_nm')+15), '}}', '') as real) <= 0)"""),
]

c = sqlite3.connect(DB)
bad = 0
for label, sql in CHECKS:
    v = c.execute(sql).fetchone()[0]
    if v:
        bad += 1
    print(f"  {label:28s} {v}{'  ←' if v else ''}")
q = lambda s: c.execute(s).fetchone()[0]
print(f"\n재료 {q('select count(*) from material')} · 물성값 {q('select count(*) from property_value')}"
      f" · 출처 {q('select count(*) from source')}"
      f" · 정의 {q('select count(*) from property_definition')}/{q('select count(distinct property_key) from property_value')}")
print(f"이상 {bad}개")
sys.exit(1 if bad else 0)
