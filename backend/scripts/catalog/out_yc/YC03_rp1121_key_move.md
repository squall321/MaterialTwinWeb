# 63차 YC — 표적 (3) NASA RP-1121 `ε_n` 5행 키 오분류 — 원문 확인과 이동

**결론 — 신고가 맞다. 5행을 옮겼다.** 마이그레이션 `b3c4d5e6f7a8_move_w63yc_rp1121_normal_emittance.py`.

## 1. 원문을 직접 열었다

`/data/paper_patent_corpus/standards_appnotes/mech/NASA_RP-1121_Henninger_1984_SolarAbsorptanceThermalEmittance.pdf`
(1.8 MB · 디스크에 있다 · `source.local_path` 도 채워져 있다) · `pdftotext -layout` 1,999줄.

`DESCRIPTION OF MEASUREMENTS` 절 `Normal Emittance (ε_n)` 이 그대로 정의한다.

> verbatim `Spectral reflectance measurements were made over the wavelength region from 5 to 35
> micrometers. This region contains approximately 90 percent of the energy of a 300 K blackbody radiator`
>
> verbatim `The following formulas are used for computing **total normal emittance**, ε_n (reference 4):`
>
> 기호표 verbatim `ε_n (T) = **Total normal emittance** at T` · `J_λ(T) = Planckian blackbody function`
> 식은 `∫(5..35 µm) ρ_λ(λ)·J_λ(T) dλ / ∫(5..35 µm) J_λ(T) dλ` 다 — **λ 가 적분으로 사라진다.**
>
> `INSTRUMENTATION` 절 verbatim `The Gier-Dunkle portable emissometer, model DB-100 (Figure 22) is used
> to make normal emittance measurements at room temperature. This instrument **gives a single integrated
> value of emittance**.`

**우리 DB 가 심판이다**(62차 XB 의 규율) — `property_definition` 이 `optical.emissivity_total` 의
`test_standard` 를 **ASTM E408**(*Total Normal Emittance of Surfaces Using Inspection-Meter Techniques*)
로 적어 두었고, DB-100 inspection emissometer 가 정확히 그 규격의 기기다.

**구조도 같은 답을 낸다.** `optical.emissivity_spectral` 의 선언된 `condition_axes` 는
`["wavelength_nm","temperature_k"]` 인데 **이 5행에는 파장 축이 한 칸도 없다** — 대신
`band_um: "5-35"`(적분 대역)와 `temperature_k: 300` 이 있다. 대상 키의 축은 `["temperature_k"]` 이고
다섯 행 모두 그 축을 이미 갖고 있다.

## 2. 값도 원문과 글자까지 대조했다

| 행 | 재료 | 원문 표 · 행 라벨 | ε_n |
|---|---|---|---|
| pv6686 | 194 PI Base Film — Kapton HN | `FILMS AND TAPES` · `Kapton Film (Aluminum Backing)` `1.0 mil` | 0.67 |
| pv6688 | 151 Anodized Aluminum Layer | `ANODIZED ALUMINUM SAMPLES` · `Sulphuric` | 0.87 |
| pv6690 | 179 Beryllium Copper | `METALS AND CONVERSION COATINGS` · `Plain Beryllium Copper` | 0.03 |
| pv6692 | 41 Tungsten_99pct | 같은 표 · `Tungsten Polished` | 0.03 |
| pv6694 | 3 SUS304_annealed | 같은 표 `Stainless Steel` 블록 · `1-mil 304 Foil` | 0.05 |

## 3. 조건은 어떻게 했나

- **`band_um: "5-35"` 를 지우지 않았다.** 그것이 이 값의 정의(적분 대역)다. 지우면 다음 파동이
  "대역 없는 전방사율" 로 읽는다. `emissivity_total` 에서 이 칸은 축이 아니라 **정의의 기술**이다.
- **`quantity` 를 붙였다** — 62차 XB 가 같은 표에서 옳은 키로 넣은 행(pv43892·pv43893)과
  **글자까지 같은 문구**(`total normal emittance (Planck-weighted 300 K)`)로 달아 두 행이 같은 물리량임을 드러냈다.
- **되돌리기 표시는 `conditions.migrated_from = "optical.emissivity_spectral"`** 이다
  (47차 IA `a4b5c6d7e8f9` 가 세운 규약과 같은 모양 · §594).
- **값·단위·등급·`method`·출처는 한 칸도 안 바꿨다.**

## 4. 중복 한 쌍 — 지우지 않고 표시했다

62차 XB 가 같은 표의 같은 행(`Plain Beryllium Copper` 0.03)을 **옳은 키로 이미 넣었다**(pv43892).
옮기면 재료 179 에만 같은 측정이 두 행이 된다. 52차 NB 의 규약대로 **중복 쪽(pv6690)에만**
`verdict_duplicate_of`(정본의 **원문 조건 지문**)·`verdict_duplicate_note` 를 달았다.

**표시가 필요한 이유는 순위다.** `_rep_rank` 다섯째 자리가 조건 수 **오름차순**이라, 표시가 없으면
조건이 성긴 옛 행(pv6690, 5칸)이 XB 의 잘 적힌 행(pv43892, 7칸)을 **이겨서 대표가 된다.**
표시 두 칸을 얹으니 정본이 그대로 대표다(아래 §5 실측).

## 5. 성과는 총계가 아니라 내가 손댄 행으로 쟀다(§640·647)

스냅샷은 `VACUUM INTO` 로 떴다(§647 — `cp` 는 WAL 을 안 가져온다).

```
적용 직전 스냅샷 42,185행 → 적용 후 라이브 42,185행
내 적용으로 바뀐 행 5 · 추가 0 · 삭제 0
(스냅샷을 처음 뜬 22:06 의 42,164행과 22:5x 의 42,185행 차 21행은 **옆 파동의 것**이다)
```

**대표값 변동 — 선언과 집계를 대조했다(§610).**

| (재료, 키) | 전 | 후 | 판단 |
|---|---|---|---|
| 194·151·179·3 `emissivity_total` | 대표 그대로 | 대표 그대로 (행 수만 +1) | 무해 |
| **41 Tungsten `emissivity_total`** | pv43785 **0.024**(t3, Mikron 편찬표 클래스값) | **pv6692 0.03**(t2, RP-1121) | **값이 바뀐다.** t3 클래스 편찬표를 t2 GSFC 실측 보고서가 밀어낸 것이라 방향이 옳다. 둘 다 `polished/unoxidized tungsten` 이고 25% 차다 |
| **3 SUS304 `emissivity_spectral`** | pv6694 **0.05**(대역적분값이 분광 대표였다) | pv10967 **0.27**(λ=2.0 µm, Richmond & Stewart) | **이동이 고친 것이다.** 잘못된 키에 앉은 t2 가 등급 순위로 t4 분광값들을 이기고 있었다 |
| 194·151·179·41 `emissivity_spectral` | 각 1행 | **0행** | 옳다 — 이 재료들은 분광 방사율을 가진 적이 없다 |

**검사 — 사본에 먼저 걸고 diff 를 봤다.**

```
integrity_check   스냅샷 대 적용후 diff **0줄** (총계 "이상 1개" 는 기존 잔재)
verdicts_check    ✔ 이상 0개
pytest -q         512 passed, 1 skipped (기준선 366 보다 많은 것은 옆 파동이 넣은 시험 때문이다)
downgrade 왕복    원본과 다른 행 **0** (조건·notes 까지 글자 그대로 복원)
```

## 6. 신고 — 이 이동은 운영까지 안 간다. 병합기에 키 이동 분기가 없다

`_materialtwin_merge.py` 의 `property_value` 자연키에 **`property_key` 가 들어 있고**,
세 우회 분기가 **전부** 그 칸으로 좁힌다.

```
③ find_corrected_row   WHERE material_id IS ? AND property_key IS ? AND source_id IS ? …
④ find_moved_row       WHERE material_id=?  AND property_key IS ? AND source_id IS ? …   (moved_from_material)
⑤ find_source_moved_row WHERE material_id IS ? AND property_key IS ? AND source_id IS ? … (moved_from_source)
```

**`migrated_from` 을 보는 분기는 없다.** 그래서 옮긴 5행은 운영에서 대응행을 못 찾고 **새 행으로
들어가고**, 그 뒤 운영에서 이 마이그레이션이 돌아 옛 행까지 옮기면 **두 벌이 된다** —
§536 이 재료 이동에서 이미 겪은 그 모양이다(배포 순서상 **병합이 앱 기동보다 먼저**이므로
병합 시점의 운영 DB 는 아직 옛 리비전이고 행이 옛 키 밑에 있다).

**이 배치는 공유 도구를 안 고쳤다**(§468). **고칠 자리를 적어 둔다** — `MOVE_MARKER` 옆에
한 줄이면 된다.

```python
# _materialtwin_merge.py — ④ 옆에 같은 모양으로
KEY_MOVE_MARKER = "migrated_from"      # 적재기·마이그레이션이 남기는 옛 **물성키**

def key_move_prior(cond_text):         # move_prior 와 같은 모양
    ...  # d.get(KEY_MOVE_MARKER) 가 문자열이면 그것이 옛 키다

def find_key_moved_row(dc, vals, old_key):
    """**옛 키 밑에서** 운영행을 찾는다. 좁히는 축은 이동이 바꾸지 않는 것 — 재료·출처·값."""
    rows = dc.execute(
        "SELECT id FROM property_value WHERE material_id IS ? AND property_key IS ? "
        "AND source_id IS ? AND value_num IS ? AND value_text IS ?",
        (vals.get("material_id"), old_key, vals.get("source_id"),
         vals.get("value_num"), vals.get("value_text"))).fetchall()
    ...  # 유일하지 않으면 옮기지 않고 key_move_misses 로 보고한다(④·⑤ 와 같은 규율)
```

**47차 IA(`a4b5c6d7e8f9`, 영률 336행) 도 같은 자리다** — 그 이동도 운영에 전파되지 않았을 공산이 크다.
분기를 넣는 배치는 **그 336행을 같이 세라**(§599 — 분류기를 고쳤으면 이미 박힌 것을 다시 세라).
