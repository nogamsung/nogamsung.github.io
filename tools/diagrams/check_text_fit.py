"""SVG 다이어그램 글자 넘침 검사기 (영어판 다이어그램처럼 글이 길어졌을 때 확인용).

각 <text> 의 실제 폭을 Pillow 폰트 측정으로 어림해서
  1) 캔버스 밖으로 나가는 글자
  2) 글자의 기준점이 들어 있는 가장 작은 <rect> 를 좌우로 넘는 글자
  3) 서로 겹치는 글자 (애니메이션용 class="anim" 글자는 제외)
를 보고한다. 문제가 없으면 아무것도 출력하지 않고 종료 코드 0.

사용: python3 tools/diagrams/check_text_fit.py assets/img/en/2026/11/*.svg
"""
import re, sys
import xml.etree.ElementTree as ET
from PIL import ImageFont

NS = '{http://www.w3.org/2000/svg}'
SANS = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
MONO = '/System/Library/Fonts/Menlo.ttc'
_cache = {}


def font(size, weight, mono):
    key = (round(size), int(weight) >= 600, mono)
    if key in _cache:
        return _cache[key]
    if mono:
        f = ImageFont.truetype(MONO, key[0], index=1 if key[1] else 0)
    else:
        want = 'bold' if key[1] else 'regular'
        f = None
        for idx in range(20):
            try:
                cand = ImageFont.truetype(SANS, key[0], index=idx)
            except Exception:
                break
            if cand.getname()[1].lower() == want:
                f = cand
                break
        f = f or ImageFont.truetype(SANS, key[0])
    _cache[key] = f
    return f


def num(v, d=0.0):
    try:
        return float(re.sub(r'[^0-9.\-]', '', v)) if v is not None else d
    except ValueError:
        return d


def check(path):
    root = ET.parse(path).getroot()
    W, H = num(root.get('width')), num(root.get('height'))
    rects, texts = [], []
    for el in root.iter():
        tag = el.tag.replace(NS, '')
        if tag == 'rect' and el.get('width') not in (None, '100%'):
            if 'anim' in (el.get('class') or ''):
                continue
            rects.append((num(el.get('x')), num(el.get('y')), num(el.get('width')), num(el.get('height'))))
        elif tag == 'text':
            s = ''.join(el.itertext()).strip()
            if not s or el.get('transform'):  # 회전한 축 라벨 등은 건너뛴다
                continue
            size = num(el.get('font-size'), 15)
            weight = el.get('font-weight') or '400'
            mono = 'mono' in (el.get('font-family') or '').lower() or 'menlo' in (el.get('font-family') or '').lower()
            w = font(size, weight, mono).getlength(s)
            x, y = num(el.get('x')), num(el.get('y'))
            anchor = el.get('text-anchor') or 'start'
            x0 = x - w / 2 if anchor == 'middle' else (x - w if anchor == 'end' else x)
            texts.append(dict(s=s, x=x, y=y, x0=x0, x1=x0 + w, y0=y - size * 0.6, y1=y + size * 0.6,
                              anim='anim' in (el.get('class') or '')))
    problems = []
    for t in texts:
        if t['x0'] < 2 or t['x1'] > W - 2:
            problems.append(f"canvas  {t['x0']:.0f}..{t['x1']:.0f} (W={W:.0f}) : {t['s']}")
        inside = [r for r in rects if r[0] <= t['x'] <= r[0] + r[2] and r[1] <= t['y'] <= r[1] + r[3]]
        if inside and not t['anim']:
            r = min(inside, key=lambda r: r[2] * r[3])
            if t['x0'] < r[0] + 1 or t['x1'] > r[0] + r[2] - 1:
                problems.append(f"box     text {t['x0']:.0f}..{t['x1']:.0f} vs box {r[0]:.0f}..{r[0] + r[2]:.0f} : {t['s']}")
    static = [t for t in texts if not t['anim']]
    for i, a in enumerate(static):
        for b in static[i + 1:]:
            if a['x0'] < b['x1'] - 2 and b['x0'] < a['x1'] - 2 and a['y0'] < b['y1'] - 2 and b['y0'] < a['y1'] - 2:
                problems.append(f"overlap '{a['s']}'  <->  '{b['s']}'")
    return problems


if __name__ == '__main__':
    bad = 0
    for p in sys.argv[1:]:
        probs = check(p)
        if probs:
            bad += 1
            print(f'== {p}')
            for x in probs:
                print('   ' + x)
    sys.exit(1 if bad else 0)
