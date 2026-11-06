#!/usr/bin/env python3
"""Generate a dark-themed contribution heatmap SVG from the public GitHub calendar.
No token needed. Usage: python scripts/contrib_graph.py <username> <out.svg> [input.html]
"""
import re, sys, urllib.request
from datetime import date, timedelta

user = sys.argv[1]
out = sys.argv[2]
if len(sys.argv) > 3:
    html = open(sys.argv[3], encoding="utf-8").read()
else:
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

# cells: <td ... data-date="YYYY-MM-DD" id="contribution-day-component-D-W" data-level="N">
cells = {}
for m in re.finditer(
    r'data-date="(\d{4}-\d{2}-\d{2})"\s+id="contribution-day-component-(\d)-(\d+)"\s+data-level="(\d)"', html
):
    d, wd, wk, lvl = m.groups()
    cells[f"{wd}-{wk}"] = {"date": date.fromisoformat(d), "wd": int(wd), "wk": int(wk), "lvl": int(lvl), "n": 0}

# counts from tooltips
for m in re.finditer(
    r'for="contribution-day-component-(\d)-(\d+)"[^>]*>\s*(No|\d+) contributions?\s+on', html
):
    wd, wk, n = m.groups()
    key = f"{wd}-{wk}"
    if key in cells:
        cells[key]["n"] = 0 if n == "No" else int(n)

if not cells:
    sys.exit("No contribution cells found - GitHub markup may have changed.")

days = sorted(cells.values(), key=lambda c: c["date"])
today = date.today()
days = [c for c in days if c["date"] <= today] or days

total = sum(c["n"] for c in days)
best = max(days, key=lambda c: c["n"])

longest = run = 0
for c in days:
    run = run + 1 if c["n"] > 0 else 0
    longest = max(longest, run)

cur = 0
seq = list(reversed(days))
start = 1 if seq and seq[0]["n"] == 0 else 0  # today may not have contributions yet
for c in seq[start:]:
    if c["n"] > 0:
        cur += 1
    else:
        break

# ---------- SVG ----------
BG, CARD_STROKE = "#1a1b27", "#2a2e45"
TITLE, TEXT, MUTED = "#70a5fd", "#c0caf5", "#7a82a8"
LEVELS = ["#252a40", "#1e4a7a", "#2f78c9", "#58a6ff", "#a5d1ff"]
SZ, GAP = 11, 3
STEP = SZ + GAP
weeks = max(c["wk"] for c in cells.values()) + 1
GX, GY = 52, 118
W = GX + weeks * STEP + 26
H = GY + 7 * STEP + 52

p = []
p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{user} contribution activity">')
p.append(f'<title>{user} contribution activity: {total} contributions in the last year</title>')
p.append("<style>text{font-family:'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif}"
         ".t{font-size:18px;font-weight:600}.v{font-size:22px;font-weight:700}"
         ".l{font-size:11px}.s{font-size:10px}"
         "@keyframes pop{from{opacity:0}to{opacity:1}}"
         ".c{opacity:0;animation:pop .35s ease-out forwards}</style>")
p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8" fill="{BG}" stroke="{CARD_STROKE}"/>')
p.append(f'<text class="t" x="26" y="36" fill="{TITLE}">Contribution Activity</text>')
p.append(f'<text class="l" x="{W-26}" y="36" fill="{MUTED}" text-anchor="end">last 12 months · @{user}</text>')

stats = [
    (str(total), "total contributions"),
    (f"{longest} days", "longest streak"),
    (f"{cur} days", "current streak"),
    (f"{best['n']}", f"best day · {best['date'].strftime('%b %d')}"),
]
colw = (W - 52) / len(stats)
for i, (v, lab) in enumerate(stats):
    x = 26 + i * colw
    p.append(f'<text class="v" x="{x:.0f}" y="72" fill="{TEXT}">{v}</text>')
    p.append(f'<text class="l" x="{x:.0f}" y="90" fill="{MUTED}">{lab}</text>')

# weekday labels (rows 1,3,5 = Mon, Wed, Fri; GitHub rows are Sun=0)
for wd, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    p.append(f'<text class="s" x="{GX-8}" y="{GY + wd*STEP + SZ - 1}" fill="{MUTED}" text-anchor="end">{lab}</text>')

# month labels
last_month = None
for wk in range(weeks):
    top = cells.get(f"0-{wk}")
    if not top:
        continue
    mo = top["date"].month
    if mo != last_month and (wk == 0 or top["date"].day <= 7):
        if not (wk == 0 and top["date"].day > 20):
            p.append(f'<text class="s" x="{GX + wk*STEP}" y="{GY-8}" fill="{MUTED}">{top["date"].strftime("%b")}</text>')
        last_month = mo

# cells
for c in cells.values():
    if c["date"] > today:
        continue
    x = GX + c["wk"] * STEP
    y = GY + c["wd"] * STEP
    delay = c["wk"] * 12
    tip = f'{c["n"]} contribution{"s" if c["n"] != 1 else ""} on {c["date"].strftime("%b %d, %Y")}'
    p.append(f'<rect class="c" style="animation-delay:{delay}ms" x="{x}" y="{y}" width="{SZ}" height="{SZ}" rx="2.5" fill="{LEVELS[c["lvl"]]}"><title>{tip}</title></rect>')

# legend
ly = GY + 7 * STEP + 24
lx = W - 26 - (5 * STEP) - 62
p.append(f'<text class="s" x="{lx}" y="{ly+9}" fill="{MUTED}" text-anchor="end">Less</text>')
for i, col in enumerate(LEVELS):
    p.append(f'<rect x="{lx + 8 + i*STEP}" y="{ly}" width="{SZ}" height="{SZ}" rx="2.5" fill="{col}"/>')
p.append(f'<text class="s" x="{lx + 8 + 5*STEP + 4}" y="{ly+9}" fill="{MUTED}">More</text>')
p.append("</svg>")

open(out, "w", encoding="utf-8").write("\n".join(p))
print(f"OK: {total} contributions, longest {longest}, current {cur}, wrote {out}")
