#!/usr/bin/env python3
"""Generate profile/stats.svg and profile/top-langs.svg (dark, tokyonight-style).
Uses the public GitHub REST API (GITHUB_TOKEN env var is used if present).
Usage: python scripts/profile_cards.py <username> <out_dir>
"""
import json, os, re, sys, urllib.request
from html import escape

user, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)


def api(url):
    headers = {"User-Agent": "profile-cards", "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    req = urllib.request.Request(url, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=30))


profile = api(f"https://api.github.com/users/{user}")
repos = api(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner")
stars = sum(r["stargazers_count"] for r in repos)
prs = api(f"https://api.github.com/search/issues?q=author:{user}+type:pr&per_page=1")["total_count"]
issues = api(f"https://api.github.com/search/issues?q=author:{user}+type:issue&per_page=1")["total_count"]

# contributions in the last year (public calendar)
req = urllib.request.Request(f"https://github.com/users/{user}/contributions", headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode()
contribs = sum(int(n) for n in re.findall(r'>\s*(\d+) contributions?\s+on', html))

# languages (bytes) over non-fork repos
langs = {}
for r in repos:
    if r["fork"]:
        continue
    try:
        for k, v in api(r["languages_url"]).items():
            langs[k] = langs.get(k, 0) + v
    except Exception:
        pass

BG, STROKE = "#1a1b27", "#2a2e45"
TITLE, TEXT, ACCENT, ICON = "#70a5fd", "#38bdae", "#70a5fd", "#bf91f3"
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"

# ---------------- stats card ----------------
ICONS = {
    "star": "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z",
    "clock": "M1.643 3.143L.427 1.927A.25.25 0 000 2.104V5.75c0 .138.112.25.25.25h3.646a.25.25 0 00.177-.427L2.715 4.215a6.5 6.5 0 11-1.18 4.458.75.75 0 10-1.493.154 8.001 8.001 0 101.6-5.684zM7.75 4a.75.75 0 01.75.75v2.992l2.028.812a.75.75 0 01-.557 1.392l-2.5-1A.75.75 0 017 8.25v-3.5A.75.75 0 017.75 4z",
    "pr": "M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z",
    "issue": "M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm9 3a1 1 0 11-2 0 1 1 0 012 0zm-.25-6.25a.75.75 0 00-1.5 0v3.5a.75.75 0 001.5 0v-3.5z",
    "book": "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z",
}
rows = [
    ("star", "Total Stars Earned", stars),
    ("clock", "Contributions (last year)", contribs),
    ("pr", "Total PRs", prs),
    ("issue", "Total Issues", issues),
    ("book", "Public Repositories", profile["public_repos"]),
]
W, H = 495, 195
s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(user)} GitHub stats">',
     f"<title>{escape(profile.get('name') or user)}'s GitHub Stats</title>",
     f"<style>text{{font-family:{FONT}}}.h{{font-size:18px;font-weight:600;fill:{TITLE}}}"
     f".st{{font-size:14px;font-weight:600;fill:{TEXT}}}.ic{{fill:{ICON}}}"
     "@keyframes f{from{opacity:0}to{opacity:1}}.g{opacity:0;animation:f .4s ease-out forwards}</style>",
     f'<rect x=".5" y=".5" rx="6" width="{W-1}" height="{H-1}" fill="{BG}" stroke="{STROKE}"/>',
     f'<text class="h" x="25" y="35">{escape(profile.get("name") or user)}&#39;s GitHub Stats</text>']
for i, (ic, label, val) in enumerate(rows):
    y = 62 + i * 25
    s.append(f'<g class="g" style="animation-delay:{i*120}ms" transform="translate(25,{y})">'
             f'<svg class="ic" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="{ICONS[ic]}"/></svg>'
             f'<text class="st" x="26" y="12.5">{label}:</text>'
             f'<text class="st" x="236" y="12.5">{val}</text></g>')
# followers ring
cx, cy = 408, 112
s.append(f'<circle cx="{cx}" cy="{cy}" r="40" stroke="{ACCENT}" stroke-width="6" opacity=".2"/>')
s.append(f'<circle cx="{cx}" cy="{cy}" r="40" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round" opacity=".8" stroke-dasharray="190 251" transform="rotate(-90 {cx} {cy})"/>')
s.append(f'<text x="{cx}" y="{cy+2}" text-anchor="middle" dominant-baseline="central" style="font-size:24px;font-weight:800;fill:{TEXT}">{profile["followers"]}</text>')
s.append(f'<text x="{cx}" y="{cy+58}" text-anchor="middle" style="font-size:12px;font-weight:600;fill:{TITLE}">Followers</text>')
s.append("</svg>")
open(os.path.join(out_dir, "stats.svg"), "w", encoding="utf-8").write("\n".join(s))

# ---------------- top languages card ----------------
COLORS = {"JavaScript": "#f1e05a", "TypeScript": "#3178c6", "CSS": "#a371f7", "HTML": "#e34c26", "Python": "#3572A5",
          "Java": "#b07219", "C++": "#f34b7d", "C": "#8a8a8a", "PHP": "#4F5D95", "Shell": "#89e051", "SCSS": "#c6538c"}
PAL = ["#58a6ff", "#38bdae", "#bf91f3", "#ffb86c", "#ff7b9c", "#9ece6a"]
tot = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
LW = 340
l = [f'<svg width="{LW}" height="{H}" viewBox="0 0 {LW} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Most used languages">',
     "<title>Most Used Languages</title>",
     f"<style>text{{font-family:{FONT}}}.h{{font-size:18px;font-weight:600;fill:{TITLE}}}.n{{font-size:12px;font-weight:600;fill:#c0caf5}}.p{{font-size:12px;fill:#7a82a8}}</style>",
     f'<rect x=".5" y=".5" rx="6" width="{LW-1}" height="{H-1}" fill="{BG}" stroke="{STROKE}"/>',
     '<text class="h" x="25" y="35">Most Used Languages</text>',
     '<clipPath id="bar"><rect x="25" y="55" width="290" height="10" rx="5"/></clipPath>',
     f'<rect x="25" y="55" width="290" height="10" rx="5" fill="#252a40"/>', '<g clip-path="url(#bar)">']
x = 25.0
for i, (name, b) in enumerate(top):
    w = 290 * b / sum(v for _, v in top)
    col = COLORS.get(name, PAL[i % len(PAL)])
    l.append(f'<rect x="{x:.2f}" y="55" width="{w:.2f}" height="10" fill="{col}"/>')
    x += w
l.append("</g>")
for i, (name, b) in enumerate(top):
    col = COLORS.get(name, PAL[i % len(PAL)])
    cxp = 25 + (i % 2) * 150
    cyp = 96 + (i // 2) * 26
    l.append(f'<circle cx="{cxp+5}" cy="{cyp}" r="5" fill="{col}"/>'
             f'<text class="n" x="{cxp+16}" y="{cyp+4}">{escape(name)}</text>'
             f'<text class="p" x="{cxp+128}" y="{cyp+4}" text-anchor="end">{100*b/tot:.1f}%</text>')
l.append("</svg>")
open(os.path.join(out_dir, "top-langs.svg"), "w", encoding="utf-8").write("\n".join(l))
print("OK", dict(stars=stars, prs=prs, issues=issues, contribs=contribs, repos=profile["public_repos"], followers=profile["followers"]), top)
