"""Commit Runner: draws runner.svg, a pixel-art markhor hopping across pillars built from a year of weekly commits.
Usage: GH_TOKEN=... python runner.py <github login>   (stdlib only; run daily by .github/workflows/runner.yml)
"""
import json
import math
import os
import sys
import urllib.request

QUERY = "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"
W, H, BASE = 900, 236, 196          # canvas and the ground line
X0, STEP, PW, MAXH = 32, 16, 14, 108  # first pillar x, pillar pitch, pillar width, tallest pillar
RUN, HOLD = 24.0, 3.0                # seconds running, seconds standing at the flag
GREENS = ["#0e4429", "#006d32", "#26a641", "#39d353"]
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()

# 14 x 12 pixel markhor facing right. H/h horn, B coat, D shade, W ruff, E eye, K hoof.
BODY = ["........H...h.", "........h..H..", ".........Hh...", ".........BBB..", ".........BEBB.", ".BBBBBBBBBWW..",
        "DBBBBBBBBBW...", ".BBBBBBBBBW...", ".BBDDDDDBB...."]
LEGS = [[".B.B...B.B....", ".B.B...B.B....", ".K.K...K.K...."], [".B..B.B..B....", "B....B....B...", "K....K....K..."]]
COLORS = {"H": "#f1e6c8", "h": "#a08c68", "B": "#c8a165", "D": "#8a6a3b", "W": "#ffffff", "E": "#14091f", "K": "#3a2a1a"}


def fetch(login):
    req = urllib.request.Request("https://api.github.com/graphql", json.dumps({"query": QUERY, "variables": {"u": login}}).encode(),
                                 {"Authorization": "bearer " + os.environ["GH_TOKEN"], "User-Agent": "commit-runner"})
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [(w["contributionDays"][0]["date"], sum(d["contributionCount"] for d in w["contributionDays"])) for w in cal["weeks"]]
    return cal["totalContributions"], weeks


def sprite(rows, y0=0):
    return "".join(f'<rect x="{x * 3}" y="{(y + y0) * 3}" width="3" height="3" fill="{COLORS[c]}"/>'
                   for y, row in enumerate(rows) for x, c in enumerate(row) if c != ".")


def arc_len(p0, c, p1, n=24):
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1])
           for t in (i / n for i in range(n + 1))]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def build(total, weeks):
    top = max(c for _, c in weeks) or 1
    ranked = sorted(c for _, c in weeks if c)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" shape-rendering="crispEdges" role="img" '
           f'aria-label="Commit Runner: a pixel markhor hops across {total} contributions from the last year">',
           '<defs><linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#2b0a4a"/></linearGradient></defs>',
           f'<rect width="{W}" height="{H}" fill="url(#s)"/>',
           '<path d="M0 196L70 120L120 160L200 84L270 150L330 110L420 176L500 100L560 140L640 70L720 150L790 112L900 196Z" fill="#1d0b3a"/>',
           f'<rect y="{BASE}" width="{W}" height="{H - BASE}" fill="#12032b"/><rect y="{BASE}" width="{W}" height="2" fill="#ff2e88"/>']
    stops, month = [(16, BASE - 28)], None          # the start ledge, then every active week
    out.append(f'<rect x="4" y="{BASE - 28}" width="24" height="28" fill="#3b1d6e"/><rect x="4" y="{BASE - 28}" width="24" height="4" fill="#7df9ff"/>')
    for i, (date, count) in enumerate(weeks):
        x = X0 + i * STEP
        if int(date[5:7]) != month and int(date[8:10]) <= 7:
            month = int(date[5:7])
            out.append(f'<text x="{x}" y="{BASE + 18}" font-family="Courier New, monospace" font-size="10" font-weight="bold" fill="#7df9ff">{MONTHS[month - 1]}</text>')
        if not count:
            continue
        h = 12 + 4 * round((MAXH - 12) * count / top / 4)
        y = BASE - h
        green = GREENS[min(3, 4 * ranked.index(count) // len(ranked))]
        out.append(f'<rect x="{x}" y="{y}" width="{PW}" height="{h}" fill="#3b1d6e"/><rect x="{x + PW - 4}" y="{y}" width="4" height="{h}" fill="#2a1352"/>'
                   f'<rect x="{x}" y="{y}" width="{PW}" height="4" fill="{green}"/>')
        stops.append((x + PW // 2, y, count))
    fx = X0 + len(weeks) * STEP + 2
    out.append(f'<rect x="{fx}" y="{BASE - 36}" width="16" height="36" fill="#3b1d6e"/><rect x="{fx}" y="{BASE - 36}" width="16" height="4" fill="#7df9ff"/>'
               f'<rect x="{fx + 10}" y="{BASE - 62}" width="2" height="26" fill="#fff"/><rect x="{fx}" y="{BASE - 62}" width="10" height="8" fill="#ff2e88"/>')
    stops.append((fx + 5, BASE - 36))

    path, lengths = f"M{stops[0][0]} {stops[0][1]}", [0.0]
    for a, b in zip(stops, stops[1:]):
        ctrl = ((a[0] + b[0]) / 2, min(a[1], b[1]) - 14 - 0.25 * (b[0] - a[0]))
        path += f" Q{ctrl[0]:.0f} {ctrl[1]:.0f} {b[0]} {b[1]}"
        lengths.append(lengths[-1] + arc_len(a[:2], ctrl, b[:2]))
    dur, frac = RUN + HOLD, RUN / (RUN + HOLD)
    times = [frac * length / lengths[-1] for length in lengths]   # when the goat lands on each stop, as a share of the loop
    assert all(a < b for a, b in zip(times, times[1:])) and times[-1] <= frac + 1e-9

    def show(t0, t1):  # visible only between two moments of the loop
        keys = sorted({0.0, round(t0, 4), round(t1, 4)} - {1.0})
        vals = ["visible" if round(t0, 4) <= k < round(t1, 4) else "hidden" for k in keys]
        return f'<animate attributeName="visibility" calcMode="discrete" dur="{dur}s" repeatCount="indefinite" keyTimes="{";".join(map(str, keys))}" values="{";".join(vals)}"/>'

    score, text = 0, 'font-family="Courier New, monospace" font-weight="bold"'
    out.append(f'<text x="12" y="24" {text} font-size="14" fill="#ffd60a">SCORE</text><text x="{W - 12}" y="24" text-anchor="end" {text} font-size="14" fill="#ff5fd2">COMMIT RUNNER</text>')
    for k, stop in enumerate(stops):
        if len(stop) == 3:  # a coin that disappears when the goat lands
            out.append(f'<rect x="{stop[0] - 3}" y="{stop[1] - 14}" width="6" height="6" fill="#ffd60a" visibility="hidden">{show(0, times[k])}</rect>')
            score += stop[2]
        end = times[k + 1] if k + 1 < len(stops) else 1.0
        if end > times[k] or k == 0:
            out.append(f'<text x="70" y="24" {text} font-size="14" fill="#fff" visibility="hidden">{score:05d}{show(times[k], end)}</text>')
    out.append(f'<text x="{W / 2}" y="46" text-anchor="middle" {text} font-size="13" fill="#7df9ff" visibility="hidden">{total} CONTRIBUTIONS IN THE LAST YEAR{show(frac, 1.0)}</text>')
    legs = "".join(f'<g visibility="hidden">{sprite(frame, len(BODY))}<animate attributeName="visibility" calcMode="discrete" dur="0.3s" repeatCount="indefinite" '
                   f'values="{"visible;hidden" if n == 0 else "hidden;visible"}"/></g>' for n, frame in enumerate(LEGS))
    out.append(f'<g><animateMotion dur="{dur}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;1;1" keyTimes="0;{frac:.4f};1" path="{path}"/>'
               f'<g transform="translate(-21 -36)">{sprite(BODY)}{legs}</g></g></svg>')
    return "\n".join(out)


if __name__ == "__main__":
    total, weeks = fetch(sys.argv[1])
    with open("runner.svg", "w", encoding="utf-8") as f:
        f.write(build(total, weeks))
    print("runner.svg:", total, "contributions,", sum(1 for _, c in weeks if c), "active weeks of", len(weeks))
