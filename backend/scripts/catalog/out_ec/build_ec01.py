# 69차 EC — Chen 2006 Fig.6·8·10 디지타이즈 결과를 카탈로그 JSON 과 좌표 CSV 로 낸다
import json, os
from crossmatch import PANELS, curves

W_M = 0.0074          # 박리 전선 폭 7.4 mm (원문 인쇄 + Fig.1 실측)
MAT = ('Hitachi ANISOLM AC-7106-25 anisotropic conductive film '
       '(Au/Ni-coated polymer particles in epoxy, LCD FPC-to-ITO)')
SRC = dict(kind='journal',
           title='Effects of different bonding parameters on the electrical performance and peeling strengths of ACF interconnection',
           doi='10.1016/j.microrel.2005.07.115',
           url='https://doi.org/10.1016/j.microrel.2005.07.115', year=2006,
           local_path='/data/paper_patent_corpus/structured/snowball_papers/from_pkg/Chen - 2006 - Effects of different bonding parameters on the electrical performance and peeling strengths of ACF interconnection/Chen - 2006 - Effects of different bonding parameters on the electrical performance and peeling strengths of ACF interconnection.md')

FIGNAME = {'6a':'Fig. 6(a)','6b':'Fig. 6(b)','6c':'Fig. 6(c)',
           '8a':'Fig. 8(a)','8b':'Fig. 8(b)','8c':'Fig. 8(c)',
           '10a':'Fig. 10(a)','10b':'Fig. 10(b)','10c':'Fig. 10(c)'}
AGING = {'a': dict(key='none', text='원시(신뢰성시험 전)'),
         'b': dict(key='TCT -40~125 C, 60 min/cycle, 1000 h', text='열주기시험 1000 h'),
         'c': dict(key='HTHT 85 C / 85 %RH, 500 h', text='고온고습 500 h')}
# 축 캘리브레이션 잔차(extract 결과) — 그림별 최대 잔차
CALRES = {'6a':(0.00002,0.00172),'6b':(0.00002,0.00014),'6c':(0.00001,0.00191),
          '8a':(0.00001,0.00013),'8b':(0.00020,0.00200),'8c':(0.00001,0.00200),
          '10a':(0.00001,0.00196),'10b':(0.00001,0.00217),'10c':(0.00001,0.00217)}
XTICK = {'6a':'0 / 0.4 / 0.8 / 1.2 mm','6b':'0 / 0.2 / 0.4 / 0.6 / 0.8 / 1 mm','6c':'0 / 0.2 / 0.4 / 0.6 / 0.8 mm',
         '8a':'0 / 0.2 / 0.4 / 0.6 / 0.8 / 1 mm','8b':'0 / 0.2 / 0.4 / 0.6 / 0.8 / 1 mm','8c':'0 / 0.2 / 0.4 / 0.6 / 0.8 mm',
         '10a':'0 / 0.2 / 0.4 / 0.6 / 0.8 mm','10b':'0 / 0.2 / 0.4 / 0.6 / 0.8 mm','10c':'0 / 0.2 / 0.4 / 0.6 / 0.8 mm'}
YTICK = {'6a':'0 / 4 / 8 / 12 N','6b':'0 / 4 / 8 / 12 N','6c':'0 / 4 / 8 / 12 N',
         '8a':'0 / 4 / 8 / 12 N','8b':'0 / 2 / 4 / 6 / 8 / 10 / 12 N','8c':'0 / 2 / 4 / 6 / 8 / 10 / 12 N',
         '10a':'0 / 4 / 8 / 12 N','10b':'0 / 2 / 4 / 6 / 8 / 10 / 12 N','10c':'0 / 2 / 4 / 6 / 8 / 10 / 12 N'}
MARKER = {'6':{'160 °C':'△ 삼각','170 °C':'◇ 마름모','180 °C':'★ 별','190 °C':'○ 원'},
          '8':{'9.9 s':'△ 삼각','15 s':'◇ 마름모','18 s':'★ 별','29.7 s':'○ 원'},
          '10':{'0.15 MPa':'△ 삼각','0.2 MPa':'◇ 마름모','0.25 MPa':'★ 별'}}
# 버린 패널
DROP = {'10a': '원시 패널 3계열 전부', '8b': 'TCT 패널 4계열 전부'}
STD = {'6':'180 °C', '8':'18 s', '10':'0.15 MPa'}   # 표준조건(180 °C/18 s/0.15 MPa) 라벨

BASE = dict(peel_angle_deg=90, peel_rate_mm_min=1.0, temperature_c=25, humidity_rh=50,
            substrate='ITO glass (In2O3 90 % / SnO2 10 %)',
            adherend='polyamide FPC — 35 um Cu + 2 um electrolytic Sn pads',
            test_machine='Testometric Materials Testing Machine 350 AX, 40 mm polyethylene flexible strip on the peel arm (Fig. 4)',
            test_standard='원문 미기재 — 규격명을 찍지 않고 시험조건만 인쇄한다(90도, 1 mm/min, 25 C / 50 %RH)',
            specimen_width_mm=7.4, specimen_width_status='printed',
            specimen_width_note=('원문 2.1절 verbatim: `The bonding width of the specimen is 2.1 mm and the length is 7.4 mm`. '
                                 '**박리 전선의 폭은 7.4 mm 쪽이다** — Fig. 1 에서 FPC 리드가 접합 밴드를 세로로 관통해 아래 꼬리로 이어지므로 '
                                 '박리 전진 방향이 세로(2.1 mm)이고 전선은 가로(7.4 mm)다. Fig. 1 을 인쇄된 26 mm 폭으로 스케일링해 실측하면 '
                                 '해칭 접합 밴드가 가로 7.52 mm x 세로 2.15 mm 라 두 인쇄값과 각각 1.6 % · 2.4 % 안에서 맞는다(같은 도면의 '
                                 '10.9 · 12.1 · 20.2 · 4.1 mm 치수도 1.5 % 안에서 맞아 도면이 축척임을 확인했다). '
                                 '보조근거 — 최대하중 변위 0.6~1.0 mm 가 접합 겹침 2.1 mm 보다 짧아 앞뒤가 맞고, 7.4 mm 로 나눈 12 N/cm 가 '
                                 'ACF 벤더 규격대(6~12 N/cm)에 들어가는 반면 2.1 mm 로 나눈 43 N/cm 는 어떤 ACF 시트에도 없는 값이다. '
                                 '**폭은 우리가 고른 숫자가 아니라 원문이 인쇄한 숫자다.**'),
            bond_overlap_mm=2.1,
            quantity=('90도 박리 하중-변위 곡선의 최대하중. 본문이 비교에 쓰는 `the average peeling force` 가 이 값이다 — '
                      '정상상태 박리력이 아니다(접합 겹침이 2.1 mm 뿐이라 정상상태에 못 든다).'),
            teflon_thickness_um=50, post_processing_c=25,
            prebond='80 +/- 10 C / 5 s / 0.1 MPa (Table 1)')

rows = []
readings = {}   # (state, physical-condition) -> [(panel,label,peak,npts,xmin,xmax)]
csv_rows = []
for tag, (pg, xi, yi, xlab, ylab, ser) in PANELS.items():
    fig = tag[:-1]; st = tag[-1]
    for lab, c in curves(tag):
        pk = max(c, key=lambda q: q[1])
        xs = [q[0] for q in c]
        rec = dict(panel=tag, label=lab, peak=pk[1], xpk=pk[0], n=len(c), xmin=min(xs), xmax=max(xs))
        # 물리조건 키 — 표준조건은 그림이 달라도 같은 조건이다
        cond = 'STANDARD' if lab == STD[fig] else f'{fig}:{lab}'
        readings.setdefault((st, cond), []).append(rec)
        used = 'no' if tag in DROP else 'yes'
        for x, y in c:
            csv_rows.append((FIGNAME[tag], lab, f'{x:.5f}', f'{y:.5f}', used))

with open('ec_curves_digitized.csv', 'w') as f:
    f.write('figure,series_legend_verbatim,displacement_mm,force_N,used_in_catalog\n')
    for r in csv_rows: f.write(','.join(r) + '\n')

def cond_fields(fig, lab):
    d = {}
    if fig == '6':
        d.update(bonding_temperature_c=float(lab.split()[0]), curing_time_s=18.0, bonding_pressure_mpa=0.15)
    elif fig == '8':
        d.update(bonding_temperature_c=180.0, curing_time_s=float(lab.split()[0]), bonding_pressure_mpa=0.15)
    else:
        d.update(bonding_temperature_c=180.0, curing_time_s=18.0, bonding_pressure_mpa=float(lab.split()[0]))
    return d

props = []
for (st, cond), recs in sorted(readings.items()):
    recs = [r for r in recs if r['panel'] not in DROP]
    if not recs: continue
    if cond == 'STANDARD':
        fig = '6'; lab = '180 °C'
        cf = dict(bonding_temperature_c=180.0, curing_time_s=18.0, bonding_pressure_mpa=0.15)
        cond_name = '표준조건 180 °C / 18 s / 0.15 MPa'
    else:
        fig, lab = cond.split(':'); cf = cond_fields(fig, lab); cond_name = lab
    F = sum(r['peak'] for r in recs) / len(recs)
    spread = max(r['peak'] for r in recs) - min(r['peak'] for r in recs)
    val = F / W_M
    src_desc = ' · '.join(f"{FIGNAME[r['panel']]} `{lab if cond!='STANDARD' else STD[r['panel'][:-1]]}` {r['peak']:.3f} N ({r['n']}점, x {r['xmin']:.3f}~{r['xmax']:.3f} mm)"
                          for r in recs)
    p0 = recs[0]['panel']
    xr, yr = CALRES[p0]
    marker = MARKER[p0[:-1]][lab if cond != 'STANDARD' else STD[p0[:-1]]]
    c = dict(BASE)
    c.update(cf)
    c.update(aging=AGING[st]['key'],
             peel_force_N=round(F, 4),
             digitized_from=' + '.join(FIGNAME[r['panel']] for r in recs),
             digitized_points=sum(r['n'] for r in recs),
             x_range_mm=[round(min(r['xmin'] for r in recs), 3), round(max(r['xmax'] for r in recs), 3)],
             displacement_at_peak_mm=round(sum(r['xpk'] for r in recs)/len(recs), 3),
             independent_readings=len(recs),
             independent_reading_spread_N=round(spread, 4),
             axis_type='둘 다 선형(로그축 아님) — x 변위 mm, y 하중 N',
             x_ticks=XTICK[p0], y_ticks=YTICK[p0],
             n_samples=(1 if st == 'a' else 2),
             n_samples_note=('원문 2.3절: 조건마다 시편 5개 — 원시 1 · TCT 2 · HTHT 2. '
                             '본문 평균은 두 시편 평균이지만 그림에 그려진 하중-변위 곡선은 단일 트레이스다.'))
    if fig != '6' or cond == 'STANDARD':
        pass
    notes = (
        f"**그림에서 읽은 값이지 인쇄된 값이 아니다.** 출처: {', '.join(FIGNAME[r['panel']] for r in recs)} 의 계열 "
        f"범례 verbatim `{lab if cond!='STANDARD' else '/'.join(STD[r['panel'][:-1]] for r in recs)}` (마커 {marker}). "
        f"계열 동정은 색이 아니라 **범례 드로잉 순서와 마커 모양**으로 했다 — PDF 가 벡터라 곡선 경로 바로 뒤에 그 계열의 마커 경로가 "
        f"이어 나오고, 범례도 같은 순서로 위에서 아래로 그려진다(흑백이라 색 단서는 애초에 없다). "
        f"좌표계는 축 경로의 major tick 픽셀좌표를 최소제곱으로 맞춰 세웠다 — x {XTICK[p0]} / y {YTICK[p0]}. "
        f"**검산: tick 두 개로 세운 직선에 나머지 tick 을 되먹여 최대 잔차 x {xr:.5f} mm · y {yr:.5f} N** "
        f"(전폭 대비 각각 {100*xr/1.2:.3f} % · {100*yr/12:.3f} %). 벡터 좌표라 래스터 디지타이즈의 화소오차가 없다. "
        f"읽은 점 {sum(r['n'] for r in recs)}개. 값은 {src_desc}. "
        + (f"**같은 물리조건이 서로 다른 그림 {len(recs)}장에 나와 독립으로 {len(recs)}번 읽었고 편차는 {spread:.4f} N "
           f"({100*spread/F:.2f} %)다** — 이 배치의 가장 강한 검산이다. " if len(recs) > 1 else "")
        + f"원 하중 {F:.4f} N 을 박리 전선 폭 7.4 mm 로 나눠 {val:.1f} N/m 로 적었다 "
          f"(= {F:.3f} / 0.0074). 폭 근거는 conditions.specimen_width_note 에 있다. "
        + f"시험상태: {AGING[st]['text']}.")
    props.append(dict(key='interface.peel_strength', value=round(val, 1), unit='N/m',
                      method='digitized', tier=1, conditions=c, notes=notes))

out = dict(batch='69차 EC', materials=[dict(match_name=MAT, source=SRC, properties=props)])
json.dump(out, open('ec01_anisolm_peel.json', 'w'), ensure_ascii=False, indent=1)
print(f"행 {len(props)}개 · CSV 좌표 {len(csv_rows)}점")
for p in props:
    c = p['conditions']
    print(f"  {c['aging'][:12]:12s} T={c['bonding_temperature_c']:5.1f} t={c['curing_time_s']:4.1f} P={c['bonding_pressure_mpa']:.2f} "
          f"| F={c['peel_force_N']:6.3f} N -> {p['value']:7.1f} N/m | {c['digitized_from']} | n읽기={c['independent_readings']} 편차={c['independent_reading_spread_N']}")
