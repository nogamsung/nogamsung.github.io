"""Tiny SVG diagram helper matching the blog's existing animated-SVG style.

- white background, rounded boxes, arrows with triangle markers
- `flow([...])` animates packets travelling along paths stage by stage (SMIL),
  hidden under prefers-reduced-motion via the `.anim` class.
"""
from xml.sax.saxutils import escape

FONT = "'Apple SD Gothic Neo','Noto Sans KR',sans-serif"
PAL = {  # name: (stroke/text, bg)
    'gray':   ('#1f2937', '#ffffff'),
    'muted':  ('#6b7280', '#f9fafb'),
    'blue':   ('#2563eb', '#eff6ff'),
    'green':  ('#059669', '#ecfdf5'),
    'red':    ('#dc2626', '#fef2f2'),
    'amber':  ('#d97706', '#fffbeb'),
    'purple': ('#7c3aed', '#f5f3ff'),
}
INK = '#1f2937'
MUTED = '#6b7280'


def _pts(points):
    return ' '.join(('M' if i == 0 else 'L') + f' {x} {y}' for i, (x, y) in enumerate(points))


class Diagram:
    def __init__(self, w, h, title=None, subtitle=None):
        self.w, self.h = w, h
        self.parts = []
        self.markers = set()
        if title:
            self.text(w / 2, 36, title, size=18, weight=700, anchor='middle')
        if subtitle:
            self.text(w / 2, 62, subtitle, size=14, weight=600, color=MUTED, anchor='middle')

    # ---- primitives -------------------------------------------------
    def text(self, x, y, s, size=15, weight=700, color=INK, anchor='middle', mono=False):
        ff = "'SF Mono','JetBrains Mono',Menlo,monospace" if mono else FONT
        self.parts.append(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}" dominant-baseline="middle" font-family="{ff}">{escape(s)}</text>')

    def lines(self, x, y, items, size=13, weight=600, color=INK, anchor='middle', gap=18, mono=False):
        for i, s in enumerate(items):
            self.text(x, y + i * gap, s, size=size, weight=weight, color=color, anchor=anchor, mono=mono)

    def box(self, x, y, w, h, label=None, sub=None, color='gray', dashed=False, label_size=15, sub_size=12,
            weight=700, fill=None):
        stroke, bg = PAL[color]
        dash = ' stroke-dasharray="6 4"' if dashed else ''
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill or bg}" stroke="{stroke}" '
            f'stroke-width="2"{dash}/>')
        cx = x + w / 2
        if label and sub:
            if isinstance(sub, str):
                sub = [sub]
            total = label_size + 6 + len(sub) * (sub_size + 4)
            ty = y + h / 2 - total / 2 + label_size / 2
            self.text(cx, ty, label, size=label_size, weight=weight, color=INK)
            for i, s in enumerate(sub):
                self.text(cx, ty + label_size / 2 + 8 + i * (sub_size + 4) + sub_size / 2, s,
                          size=sub_size, weight=600, color=MUTED)
        elif label:
            self.text(cx, y + h / 2, label, size=label_size, weight=weight, color=INK)
        return (x, y, w, h)

    def group(self, x, y, w, h, label, color='muted'):
        stroke, _ = PAL[color]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="none" stroke="{stroke}" '
            f'stroke-width="1.5" stroke-dasharray="6 5"/>')
        self.text(x + 14, y + 16, label, size=13, weight=700, color=stroke, anchor='start')

    def note(self, x, y, w, h, text, color='amber', size=14):
        self.box(x, y, w, h, color=color)
        if isinstance(text, str):
            text = [text]
        n = len(text)
        for i, s in enumerate(text):
            self.text(x + w / 2, y + h / 2 + (i - (n - 1) / 2) * (size + 6), s, size=size, weight=700, color=INK)

    def arrow(self, points, color='gray', label=None, dashed=False, width=2, head=True, label_dy=-10,
              label_size=12, label_color=None):
        stroke, _ = PAL[color]
        self.markers.add(color)
        dash = ' stroke-dasharray="6 5"' if dashed else ''
        mk = f' marker-end="url(#a-{color})"' if head else ''
        self.parts.append(
            f'<path d="{_pts(points)}" fill="none" stroke="{stroke}" stroke-width="{width}"{dash}{mk}/>')
        if label:
            (x1, y1), (x2, y2) = points[0], points[-1]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            if len(points) > 2:  # use the middle segment's midpoint
                a, b = points[len(points) // 2 - 1], points[len(points) // 2]
                mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            self.text(mx, my + label_dy, label, size=label_size, weight=700, color=label_color or stroke)

    def flow(self, stages, loop_pause=1.0):
        """stages: list of dicts {path:[(x,y),...], color:'blue', dur:1.0, hold:0.3}
        Packets travel stage by stage; the current stage's line is highlighted."""
        durs = [s.get('dur', 1.0) for s in stages]
        holds = [s.get('hold', 0.25) for s in stages]
        total = sum(durs) + sum(holds) + loop_pause
        t = 0.0
        for s, d, hold in zip(stages, durs, holds):
            stroke, _ = PAL[s.get('color', 'gray')]
            path = _pts(s['path'])
            t0, t1 = t / total, (t + d) / total
            t2 = min((t + d + hold) / total, 1.0)
            # highlighted line
            self.parts.append(
                f'<path class="anim" d="{path}" fill="none" stroke="{stroke}" stroke-width="5" '
                f'stroke-linecap="round" stroke-linejoin="round" opacity="0">'
                f'<animate attributeName="opacity" dur="{total:.2f}s" repeatCount="indefinite" '
                f'keyTimes="0;{t0:.4f};{min(t0 + 0.01, 1):.4f};{t1:.4f};{t2:.4f};1" values="0;0;0.35;0.35;0;0"/></path>')
            # moving packet
            self.parts.append(
                f'<circle class="anim" r="7" fill="{stroke}" stroke="#ffffff" stroke-width="2.5" opacity="0">'
                f'<animate attributeName="opacity" dur="{total:.2f}s" repeatCount="indefinite" '
                f'keyTimes="0;{t0:.4f};{min(t0 + 0.005, 1):.4f};{t1:.4f};{min(t1 + 0.005, 1):.4f};1" values="0;0;1;1;0;0"/>'
                f'<animateMotion dur="{total:.2f}s" repeatCount="indefinite" calcMode="linear" '
                f'keyPoints="0;0;1;1" keyTimes="0;{t0:.4f};{t1:.4f};1" path="{path}"/></circle>')
            if s.get('label'):
                lx, ly = s['label_at'] if 'label_at' in s else s['path'][-1]
                self.parts.append(
                    f'<text class="anim" x="{lx}" y="{ly}" font-size="13" font-weight="700" fill="{stroke}" '
                    f'text-anchor="middle" dominant-baseline="middle" font-family="{FONT}" opacity="0">{escape(s["label"])}'
                    f'<animate attributeName="opacity" dur="{total:.2f}s" repeatCount="indefinite" '
                    f'keyTimes="0;{t0:.4f};{min(t0 + 0.01, 1):.4f};{t2:.4f};{min(t2 + 0.01, 1):.4f};1" values="0;0;1;1;0;0"/></text>')
            t += d + hold

    def pulse(self, x, y, w, h, color='red', start=0.0, end=1.0, total=4.0):
        """A box outline that pulses in during [start,end] of a `total` loop (pair with flow timing)."""
        stroke, bg = PAL[color]
        self.parts.append(
            f'<rect class="anim" x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{bg}" stroke="{stroke}" '
            f'stroke-width="3" opacity="0"><animate attributeName="opacity" dur="{total:.2f}s" repeatCount="indefinite" '
            f'keyTimes="0;{start:.4f};{min(start + 0.02, 1):.4f};{end:.4f};{min(end + 0.02, 1):.4f};1" values="0;0;0.9;0.9;0;0"/></rect>')

    # ---- output -----------------------------------------------------
    def save(self, path):
        defs = []
        for c in sorted(self.markers):
            stroke, _ = PAL[c]
            defs.append(
                f'<marker id="a-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
                f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{stroke}"/></marker>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">'
               f'<defs>{"".join(defs)}</defs>'
               '<style>@media (prefers-reduced-motion: reduce){.anim{display:none}}</style>'
               '<rect width="100%" height="100%" fill="#ffffff"/>'
               + ''.join(self.parts) + '</svg>')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        return path
