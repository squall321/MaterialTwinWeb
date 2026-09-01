# Cai 2010 Fig.27 대 Cai 2012 Fig.12 의 **비시효(0일) 응력-변형 곡선**을 같은 좌표로 겹쳐 본다.
import numpy as np
import sd05_svgpaths as svgpaths

def curve(svgf, box, cal, rgb, legend_box):
    lx0, lx1, ly0, ly1 = legend_box
    pts = []
    for p in svgpaths.paths(open(svgf, encoding='utf-8').read()):
        if p['rgb'] != rgb or p['n'] < 8:
            continue
        xs = [q[0] for q in p['pts']]; ys = [q[1] for q in p['pts']]
        if not (min(xs) > box[0]-6 and max(xs) < box[1]+6
                and min(ys) > box[2]-6 and max(ys) < box[3]+6):
            continue
        pts += [q for q in p['pts'] if not (lx0 <= q[0] <= lx1 and ly0 <= q[1] <= ly1)]
    A = np.array([cal(x, y) for x, y in sorted(set(pts))])
    A = A[np.argsort(A[:, 0])]
    keep = np.concatenate([[True], np.diff(A[:, 0]) > 0])
    return A[keep]

C10 = curve('cai2010_p14.svg', (335, 548, 300, 448),
            lambda px, py: ((px-340.95)*0.020/200.865, (442.43-py)*35.0/122.81),
            (100, 0, 0), (478, 500, 393, 442))
C12 = curve('cai2012_p07.svg', (345, 545, 45, 192),
            lambda px, py: ((px-354.23)*0.020/181.13, (185.58-py)*30.0/126.49),
            (100, 0, 0), (498, 516, 122, 186))
