# -*- coding: utf-8 -*-
"""『才能を見落とさない七つの関門』の表紙——タイトルから起こした3案。

- gates : 「七つの関門」を、くぐるたびに減っていく門の列にする
- spill : 「才能は、こぼれている」を、漏斗からこぼれ落ちる点で見せる
- sheet : 「見落とさない仕組み」を、一枚の観察票そのもので見せる
"""

import hashlib


def jitter(seed, i, spread):
    """同じ本なら毎回同じ散らばりになる、決め打ちの乱数。"""
    h = hashlib.md5(("%s-%d" % (seed, i)).encode()).digest()
    return (h[0] / 255.0 - 0.5) * spread


def gates(cfg, P, S):
    """門を7つ。通るたびに開口が狭まり、通った点の数が減る。"""
    ink, accent = P["ink"], P["accent"]
    counts = [26, 20, 15, 11, 8, 6, 4]
    labels = [l for l in (cfg.get("diagram_labels") or []) if l][:7]
    top, step, post = 168, 138, 66
    out = []
    for i in range(7):
        w = 1340 - i * 164
        x1, x2, y = 800 - w / 2, 800 + w / 2, top + i * step
        op = 1.0 - i * 0.04
        out.append('<g stroke="%s" stroke-width="%d" opacity="%.2f">' % (ink, 9, op))
        out.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d"/>' % (x1, y, x2, y))
        out.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d"/>'
                   % (x1, y, x1, y + post))
        out.append('<line x1="%.0f" y1="%d" x2="%.0f" y2="%d"/>'
                   % (x2, y, x2, y + post))
        out.append("</g>")
        if i < len(labels):
            out.append('<text x="%.0f" y="%d" fill="%s" font-size="34" '
                       'font-family="NSJP" font-weight="700" opacity=".85">%s'
                       '</text>' % (x1 + 8, y - 16, ink, labels[i]))
        n = counts[i]
        last = i == 6
        for k in range(n):
            cx = x1 + 44 + (w - 88) * (k / float(n - 1) if n > 1 else .5)
            out.append('<circle cx="%.0f" cy="%d" r="%d" fill="%s" '
                       'opacity="%.2f"/>'
                       % (cx, y + 44, 14 if last else 11,
                          accent if last else ink, 1.0 if last else .85))
    nums = cfg.get("diagram_numbers") or ["", ""]
    # 段階名は開口の左肩に出るので、人数は右肩に置く（重なる）
    out.append('<text x="1470" y="132" fill="%s" font-size="60" '
               'font-family="NSJP" font-weight="900" text-anchor="end">%s</text>'
               % (accent, nums[0]))
    out.append('<text x="800" y="%d" fill="%s" font-size="60" font-family="NSJP" '
               'font-weight="900" text-anchor="middle">%s</text>'
               % (top + 6 * step + post + 96, accent,
                  nums[1] if len(nums) > 1 else ""))
    return "".join(out)


def spill(cfg, P, S):
    """漏斗。中に残る点と、壁の外を滑り落ちていく点。抜けるのは8人だけ。"""
    art, accent = S["art"], P["accent"]
    ink = art(P, .9)
    top, neck_y, lx0, rx0, nx1, nx2 = 200, 980, 120, 1480, 700, 900

    def wall(y):
        t = (y - top) / float(neck_y - top)
        return lx0 + (nx1 - lx0) * t, rx0 - (rx0 - nx2) * t

    out = ['<path d="M%d %d L%d %d M%d %d L%d %d" stroke="%s" '
           'stroke-width="10" fill="none"/>'
           % (lx0, top, nx1, neck_y, rx0, top, nx2, neck_y, ink)]
    out.append('<path d="M%d %d V1160 M%d %d V1160" stroke="%s" '
               'stroke-width="10" fill="none"/>' % (nx1, neck_y, nx2, neck_y, ink))

    for k in range(46):                              # 漏斗の中
        y = top + 40 + abs(jitter("sy", k, 1.0)) * 1160
        y = min(y, neck_y - 60)
        l, r = wall(y)
        f = 0.5 + jitter("sx", k, 1.7)
        x = l + 46 + max(0.0, min(1.0, f)) * (r - l - 92)
        out.append('<circle cx="%.0f" cy="%.0f" r="13" fill="%s" opacity=".9"/>'
                   % (x, y, ink))

    for k in range(16):                              # 壁の外を落ちていく
        y = top + 180 + abs(jitter("oy", k, 1.0)) * 1500
        y = min(y, 1140)
        l, r = wall(min(y, neck_y))
        side = -1 if k % 2 == 0 else 1
        x = (l - 54 if side < 0 else r + 54) + jitter("ox", k, 90)
        out.append('<circle cx="%.0f" cy="%.0f" r="12" fill="%s" opacity="%.2f"/>'
                   % (x, y, ink, max(.18, .5 - (y - top) / 2400.0)))

    for k in range(8):                               # 通り抜けた8人
        out.append('<circle cx="%d" cy="%d" r="17" fill="%s"/>'
                   % (752 + (k % 4) * 32, 1046 + (k // 4) * 52, accent))
    nums = cfg.get("diagram_numbers") or ["", ""]
    out.append('<text x="120" y="150" fill="%s" font-size="60" font-family="NSJP" '
               'font-weight="900">%s</text>' % (ink, nums[0]))
    out.append('<text x="960" y="1110" fill="%s" font-size="60" '
               'font-family="NSJP" font-weight="900">%s</text>'
               % (accent, nums[1] if len(nums) > 1 else ""))
    return "".join(out)


def sheet(cfg, P, S):
    art, accent = S["art"], P["accent"]
    ink = art(P, .88)
    card = 'fill="#FFFFFF"'
    out = ['<rect x="150" y="110" width="1300" height="960" %s stroke="%s" '
           'stroke-width="4"/>' % (card, ink)]
    out.append('<rect x="150" y="110" width="1300" height="104" fill="%s"/>'
               % accent)
    out.append('<text x="190" y="180" fill="#FFFFFF" font-size="52" '
               'font-family="NSJP" font-weight="900">一枚の観察票</text>')
    out.append('<text x="1410" y="180" fill="#FFFFFF" font-size="34" '
               'font-family="NSJP" font-weight="700" text-anchor="end" '
               'opacity=".85">背番号　　月　　日</text>')
    rows = ["いま何ができるか", "1年後に何ができそうか", "体はいまどの段階か",
            "この日に見た場面", "次に注目する点", "もう一度観るべきか"]
    for i, label in enumerate(rows):
        y = 296 + i * 138
        hot = i == len(rows) - 1
        if hot:
            out.append('<rect x="170" y="%d" width="1260" height="104" '
                       'fill="%s" opacity=".12"/>' % (y - 62, accent))
        out.append('<line x1="190" y1="%d" x2="1410" y2="%d" stroke="%s" '
                   'stroke-width="3" opacity=".35"/>' % (y + 30, y + 30, ink))
        out.append('<text x="196" y="%d" fill="%s" font-size="40" '
                   'font-family="NSJP" font-weight="700">%s</text>'
                   % (y, ink, label))
        for k in range(4):                        # 4段階の評価欄
            cx = 1010 + k * 100
            filled = hot and k == 2
            out.append('<rect x="%d" y="%d" width="56" height="56" fill="%s" '
                       'stroke="%s" stroke-width="3"/>'
                       % (cx, y - 42, accent if filled else "#FFFFFF", ink))
    return "".join(out)


ARTS = [
    {"name": "gates", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#10233A", "#0A1626", "#FFFFFF", "#F08A24", "#FFFFFF",
                 "#0A1626", "#C0392B", None),
     "svg": gates},
    {"name": "spill", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#F5F2EC", "#123B6D", "#FFFFFF", "#C0392B", "#123B6D",
                 "#F5F2EC", "#F08A24", "#DCD6C8"),
     "svg": spill},
    {"name": "sheet", "text": "lower", "panel": 1180,
     "badge": (1300, 2072, 148), "obi_y": 2300,
     "palette": ("#E9E4D8", "#16161A", "#FFFFFF", "#1B5FA8", "#1B5FA8",
                 "#FFFFFF", "#C0392B", "#D6CFBE"),
     "svg": sheet},
]
