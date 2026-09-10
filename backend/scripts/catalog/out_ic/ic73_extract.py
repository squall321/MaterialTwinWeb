# Kenner 1995 Fig.2 마스터커브 3벌을 정수 log t 격자에서 뽑는다
import numpy as np, json

d = np.load('ic73_tracks.npy', allow_pickle=True).item()
cal = np.load('ic73_cal.npy', allow_pickle=True).item()
pt, pb = cal['pt'], cal['pb']
A = np.array([61.2286, 880.929])
def x_of(lt): return A[0]*lt + A[1]
def logt_of(x): return (x - A[1]) / A[0]
def logE(x, y):
    t = np.polyval(pt, x); bo = np.polyval(pb, x)
    return 5.0 - 2.5 * (y - t) / (bo - t)

def sep_ok(x):
    v = {k: d[k].get(x) for k in ('c025', 'c05', 'c10')}
    ks = [k for k in v if v[k] is not None]
    bad = set()
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            if abs(v[ks[i]][0] - v[ks[j]][0]) < 25:
                bad.add(ks[i]); bad.add(ks[j])
    return {k: (v[k] is not None and k not in bad) for k in v}

RANGE = {}
for k in ('c025', 'c05', 'c10'):
    xs = [x for x in range(311, 1761) if sep_ok(x).get(k)]
    RANGE[k] = (xs[0], xs[-1])
    print(k, 'valid x', xs[0], xs[-1], 'logt', round(logt_of(xs[0]), 2), round(logt_of(xs[-1]), 2),
          'gaps', sum(1 for i in range(len(xs)-1) if xs[i+1] != xs[i]+1))

STRAIN = {'c025': 0.25, 'c05': 0.5, 'c10': 1.0}
out = {}
for k in ('c025', 'c05', 'c10'):
    x0, x1 = RANGE[k]
    rows = []
    for lt in range(-10, 16):
        xc = x_of(lt)
        if xc < x0 + 2 or xc > x1 - 2: continue
        ys = [d[k][x][0] for x in range(int(round(xc)) - 3, int(round(xc)) + 4)
              if d[k].get(x) is not None]
        if len(ys) < 5: continue
        y = float(np.median(ys))
        le = float(logE(xc, y))
        rows.append({'log_t': lt, 'time_s': 10.0**lt, 'log_E_MPa': round(le, 4),
                     'E_MPa': 10**le, 'E_Pa': 10**le * 1e6})
    out[k] = rows
    print(k, 'strain', STRAIN[k], 'rows', len(rows), 'logt', rows[0]['log_t'], '..', rows[-1]['log_t'])

# 단조감소 검사
for k, rows in out.items():
    v = [r['log_E_MPa'] for r in rows]
    bad = [(rows[i]['log_t'], v[i], v[i+1]) for i in range(len(v)-1) if v[i+1] > v[i] + 1e-9]
    print(k, '단조감소 위반', len(bad), bad[:5])

json.dump(out, open('ic73_kenner_fig2_points.json', 'w'), indent=1)
for k, rows in out.items():
    print('---', k, STRAIN[k], '%')
    for r in rows: print(f"  logt={r['log_t']:+3d}  logE={r['log_E_MPa']:.4f}  E={r['E_MPa']:9.1f} MPa")
