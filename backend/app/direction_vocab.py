# `conditions.direction` 자유서술을 최소 정규어휘로 접고, 그 정규값의 '면'을 돌려주는 어휘표.
"""방향 조건의 정규 어휘(52차 NA).

라이브 `direction` 값이 자유형식 **351종**이고 86종이 40자를 넘는 산문이라
`'MD'` 와 `'in-plane (biaxially oriented film; MD/TD not distinguished by the source)'` 가
따로 살고 있었다(브리프 550·551). 값을 지우지 않고 **정규값과 원문을 갈라** 둔다 —
`direction` 은 정규값, `direction_verbatim` 은 원문이다. 정규값 자리를 `direction` 으로
둔 이유는 **코드가 읽는 쪽이 거기**이기 때문이다(`dyna_export._direction`·`_COND_SHOW`,
taxonomy 의 `condition_axes`).

**정규 어휘는 최소다.** 원문이 실제로 인쇄한 축만 받는다. 모르면 `None` 을 돌려
정규값을 비운다 — 억지로 배정하지 않는다(브리프 537). 야금 축(L/LT/ST)·자성 배향축
(C∥/C⊥)·결정축(‖c/⊥c)처럼 **이 여덟 어휘로 표현되지 않는 축은 배정하지 않는다.**

판정 순서가 규율이다.
  ① 머리절(첫 괄호·엠대시·세미콜론 앞)이 "미기재" 면 그것이 그 행의 주장이다 → None.
  ② 머리절이 "isotropic" 이고 방향 낱말이 없으면 → isotropic.
  ③ 면(면내/두께방향)은 **먼저 나온 낱말**이 정한다 — `"in-plane (nu12) — 두께방향 nu13은
     값이 다르다"` 처럼 뒤쪽 서술이 **다른 행**을 가리키는 경우가 실재한다.
  ④ 면내 안의 MD/TD 도 먼저 나온 낱말이 정한다. 단 원문이 **일부러 안 갈랐다고 적었으면**
     (MD/TD · warp/fill · not distinguished) 면내로 둔다.

`plane()` 은 그 정규값이 **어느 면인가**만 돌려준다. `_direction_clash`(§462)가 쓰는 축이다 —
등방 카드가 물리적으로 깨지는 것은 `면내 E` 에 `두께방향 ν` 를 짝지었을 때이고,
`MD` 와 `면내(미분해)` 는 같은 면이라 깨지지 않는다(브리프 551 의 오탐 38종이 그 부류다).
"""
from __future__ import annotations

import re

IN_PLANE = "in-plane"
THROUGH = "through-thickness"
MD = "MD"
TD = "TD"
AXIAL = "axial"
RADIAL = "radial"
CIRCUM = "circumferential"
ISOTROPIC = "isotropic"
CANONICAL = (IN_PLANE, THROUGH, MD, TD, AXIAL, RADIAL, CIRCUM, ISOTROPIC)

# 면 — 이것이 같으면 `_direction_clash` 는 뜨지 않는다.
# 등방·축대칭·미상은 `None` 이라 **비교 자체를 하지 않는다.**
_PLANE = {IN_PLANE: IN_PLANE, MD: IN_PLANE, TD: IN_PLANE, THROUGH: THROUGH}


def plane(value) -> str | None:
    """정규값(또는 아직 정규화 전 원문) → 면. 정할 수 없으면 None.

    **원문도 받는다** — 정정이 막힌 군(§548)은 `direction` 이 아직 자유서술이라
    정규값만 받으면 그 행에서 검사가 통째로 꺼진다. 참 양성을 잃지 않으려면
    여기서 한 번 더 접어야 한다.
    """
    if not value:
        return None
    if value in _PLANE:
        return _PLANE[value]
    return _PLANE.get(normalize(value) or "")


_HEAD_SPLIT = re.compile(r"\(|—|;|\s--\s|\s-\s")
_UNKNOWN = re.compile(
    r"not stated|not printed|not specified|unspecified|not directional|"
    r"orientation-averaged|미인쇄|미표기|미기재|미상", re.I)
_ISO = re.compile(r"\bisotropic\b|등방", re.I)

# 이 여덟 어휘로 표현되지 않는 축 — 배정하지 않는다.
_OUT_OF_VOCAB = re.compile(
    r"short transverse|long transverse|\bL-T\b|\b[SL]T-\d|with the grain|"
    r"diagonal|45 ?deg|30 ?deg|60 ?deg|and 90 ?deg|"
    r"orientation \(easy\)|to orientation|c-axis \(E|anisotropic", re.I)
_UNRESOLVED = re.compile(
    r"MD ?/ ?TD|warp ?/ ?fill|warp=fill|not distinguished|identical by symmetry|"
    r"prints the identical value|single value given for both|"
    r"구분 없|구분 미|구분이 없|동일값|차이 없|방향차가 없", re.I)

_INPLANE = re.compile(
    r"in-?plane|면내|basal plane|c-plane|\bx-y\b|\bx/y\b|\bx,\s*y\b|\bx\s+and\s+y\b|"
    r"film plane|wafer plane|membrane plane|coating layer|1-2 plane", re.I)
_THROUGH = re.compile(
    r"through-?thickness|through-?plane|through plate thickness|cross-?plane|out-?of-?plane|"
    r"두께방향|thickness direction|flat-?wise", re.I)
_MD = re.compile(
    r"\bMD\b|machine direction|lengthwise|length-wise|\blength\b|\bLW\b|\bwarp\b|경사|"
    r"\bflow\b|\b0 ?deg to mold flow|\bRD\b|rolling direction", re.I)
_TD = re.compile(
    r"\bTD\b|\bCD\b|\bCMD\b|\bCW\b|transverse|cross-?wise|cross-?machine|cross direction|"
    r"\bcross\b|\bfill\b|\bweft\b|위사|90 ?deg to mold flow|across fib", re.I)
_AXIAL = re.compile(r"\baxial\b|fibre axis|fiber axis|along fib|fibre direction|fiber direction|"
                    r"tube axis|extrusion direction|growth axis|longitudinal|ribbon length", re.I)
_RADIAL = re.compile(r"\bradial\b", re.I)
_CIRCUM = re.compile(r"\bcircumferential\b", re.I)

_BARE_XY = re.compile(r"^\s*[XxYy]\s*(-|_| )?(axis)?\s*$")
_BARE_Z = re.compile(r"^\s*[Zz]\s*(-|_| )?(axis)?\s*$")


def _first(rx, s):
    m = rx.search(s)
    return m.start() if m else 10**6


def normalize(raw) -> str | None:
    """원문 → 정규값. 배정할 수 없으면 None(정규값을 비운다)."""
    if raw is None:
        return None
    s = " ".join(str(raw).split())
    if not s:
        return None
    if _BARE_XY.match(s):
        return IN_PLANE
    if _BARE_Z.match(s):
        return THROUGH
    head = _HEAD_SPLIT.split(s, 1)[0].strip()
    if _UNKNOWN.search(head):
        return None
    if _ISO.search(head) and not (_INPLANE.search(head) or _THROUGH.search(head)
                                 or _MD.search(head) or _TD.search(head)):
        return ISOTROPIC
    if _OUT_OF_VOCAB.search(s):
        return None
    ip, th = _first(_INPLANE, s), _first(_THROUGH, s)
    if th < ip:
        return THROUGH
    if _UNRESOLVED.search(s):
        return IN_PLANE if min(ip, th) < 10**6 or _MD.search(s) or _TD.search(s) else None
    if _RADIAL.search(s):
        return RADIAL
    if _CIRCUM.search(s):
        return CIRCUM
    md, td = _first(_MD, s), _first(_TD, s)
    if min(md, td) < 10**6:
        return MD if md < td else TD
    if ip < 10**6:
        return IN_PLANE
    if _AXIAL.search(s):
        return AXIAL
    if _ISO.search(s):
        return ISOTROPIC
    return None
