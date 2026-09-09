# Chen 2006 그림(벡터 SVG)에서 경로 좌표를 PDF 사용자공간으로 되돌려 뽑는 파서
import re, sys, json

NUM = r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'

def parse_paths(svgfile):
    s = open(svgfile).read()
    body = s.split('</defs>', 1)[1]
    out = []
    for m in re.finditer(r'<path\s+([^>]*?)/>', body):
        attrs = m.group(1)
        dm = re.search(r'\sd="([^"]*)"', attrs)
        if not dm: continue
        d = dm.group(1)
        st = re.search(r'style="([^"]*)"', attrs)
        style = st.group(1) if st else ''
        has_tf = 'transform=' in attrs
        sw = re.search(r'stroke-width:(' + NUM + ')', style)
        sw = float(sw.group(1)) if sw else None
        filled = 'fill-rule' in style and 'fill:none' not in style
        # d 를 서브패스로 쪼갠다 (M ... L ... 반복)
        subs = []
        cur = []
        toks = re.findall(r'([MLZmlz])|(' + NUM + ')', d)
        i = 0
        vals = []
        cmd = None
        for t in re.finditer(r'([MLZCz])\s*((?:' + NUM + r'[\s,]*)*)', d):
            c = t.group(1); nums = [float(x) for x in re.findall(NUM, t.group(2))]
            if c == 'M':
                if cur: subs.append(cur)
                cur = [(nums[0], nums[1])]
                for k in range(2, len(nums), 2): cur.append((nums[k], nums[k+1]))
            elif c == 'L':
                for k in range(0, len(nums), 2): cur.append((nums[k], nums[k+1]))
            elif c == 'C':
                for k in range(0, len(nums), 6): cur.append((nums[k+4], nums[k+5]))
            elif c in 'Zz':
                pass
        if cur: subs.append(cur)
        out.append(dict(style=style, sw=sw, filled=filled, tf=has_tf, subs=subs))
    return out

if __name__ == '__main__':
    ps = parse_paths(sys.argv[1])
    for i, p in enumerate(ps):
        pts = [pt for s in p['subs'] for pt in s]
        if not pts: continue
        xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
        print(f"{i:3d} sw={p['sw']} fill={p['filled']} tf={p['tf']} nsub={len(p['subs'])} npt={len(pts)} "
              f"x[{min(xs):.1f},{max(xs):.1f}] y[{min(ys):.1f},{max(ys):.1f}]")


def parse_paths_abs(svgfile):
    """경로별 transform="matrix(...)" 를 실제로 적용해 페이지 좌표로 돌려준다.
    (한 페이지에 서로 다른 transform 이 섞인 SVG 용 — Chen 2006 은 단일 transform 이라 불필요했다)"""
    import re
    s = open(svgfile).read()
    body = s.split('</defs>', 1)[1]
    out = []
    for m in re.finditer(r'<path\s+([^>]*?)/>', body):
        attrs = m.group(1)
        tf = re.search(r'transform="matrix\(([^)]*)\)"', attrs)
        if tf:
            a, b, c, d, e, f = [float(v) for v in re.split(r'[,\s]+', tf.group(1).strip())]
        else:
            a, b, c, d, e, f = 1, 0, 0, 1, 0, 0
        one = parse_paths_from_attrs(attrs)
        if one is None: continue
        one['subs'] = [[(a*x + c*y + e, b*x + d*y + f) for x, y in sub] for sub in one['subs']]
        one['tf_matrix'] = (a, b, c, d, e, f)
        out.append(one)
    return out


def parse_paths_from_attrs(attrs):
    import re
    dm = re.search(r'\sd="([^"]*)"', attrs)
    if not dm: return None
    d = dm.group(1)
    st = re.search(r'style="([^"]*)"', attrs)
    style = st.group(1) if st else ''
    sw = re.search(r'stroke-width:(' + NUM + ')', style)
    sw = float(sw.group(1)) if sw else None
    filled = 'fill-rule' in style and 'fill:none' not in style
    subs, cur = [], []
    for t in re.finditer(r'([MLZCz])\s*((?:' + NUM + r'[\s,]*)*)', d):
        c = t.group(1); nums = [float(x) for x in re.findall(NUM, t.group(2))]
        if c == 'M':
            if cur: subs.append(cur)
            cur = [(nums[0], nums[1])]
            for k in range(2, len(nums), 2): cur.append((nums[k], nums[k+1]))
        elif c == 'L':
            for k in range(0, len(nums), 2): cur.append((nums[k], nums[k+1]))
        elif c == 'C':
            for k in range(0, len(nums), 6): cur.append((nums[k+4], nums[k+5]))
    if cur: subs.append(cur)
    return dict(style=style, sw=sw, filled=filled, subs=subs)
