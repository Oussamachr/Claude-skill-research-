#!/usr/bin/env python3
"""Descriptive bibliometrics for the included set -> CSV tables + simple SVG bar charts.

Reads a records/extraction CSV with columns year, venue, keywords (';'-separated), and
optionally any categorical column you name with --by (e.g. method_family, evidence_type).

Usage:
  python bibliometrics.py 07_extraction.csv --outdir figures/ [--by method_family evidence_type]
Outputs:
  pubs_per_year.csv/.svg, top_venues.csv/.svg, top_keywords.csv/.svg,
  keyword_cooccurrence.csv, <col>_counts.csv/.svg, year_by_<col>.csv
"""
import argparse
import csv
import itertools
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_csv  # noqa: E402


def write_table(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def bar_svg(path, items, title, vertical=True):
    """Minimal, greyscale-safe bar chart. items: list of (label, value)."""
    if not items:
        return
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;")  # noqa: E731
    vmax = max(v for _, v in items) or 1
    if vertical:
        bw, gap, H, top, bottom, left = 26, 8, 260, 40, 60, 40
        W = left + len(items) * (bw + gap) + 20
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+top+bottom}" '
             f'font-family="Helvetica, Arial, sans-serif" font-size="11">',
             f'<rect width="100%" height="100%" fill="#fff"/>',
             f'<text x="{W/2}" y="22" text-anchor="middle" font-weight="bold">{esc(title)}</text>',
             f'<line x1="{left}" y1="{top+H}" x2="{W-10}" y2="{top+H}" stroke="#333"/>']
        for i, (lab, v) in enumerate(items):
            h = H * v / vmax
            x = left + i * (bw + gap)
            o.append(f'<rect x="{x}" y="{top+H-h}" width="{bw}" height="{h}" fill="#3b6ea5"/>')
            o.append(f'<text x="{x+bw/2}" y="{top+H-h-4}" text-anchor="middle">{v}</text>')
            o.append(f'<text x="{x+bw/2}" y="{top+H+14}" text-anchor="end" '
                     f'transform="rotate(-45 {x+bw/2} {top+H+14})">{esc(lab)}</text>')
    else:
        bh, gap, left, top, Wb = 18, 6, 260, 40, 320
        H = top + len(items) * (bh + gap) + 20
        W = left + Wb + 60
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'font-family="Helvetica, Arial, sans-serif" font-size="11">',
             f'<rect width="100%" height="100%" fill="#fff"/>',
             f'<text x="{W/2}" y="22" text-anchor="middle" font-weight="bold">{esc(title)}</text>']
        for i, (lab, v) in enumerate(items):
            y = top + i * (bh + gap)
            w = Wb * v / vmax
            lab = lab if len(lab) <= 42 else lab[:40] + "…"
            o.append(f'<text x="{left-6}" y="{y+bh*0.7}" text-anchor="end">{esc(lab)}</text>')
            o.append(f'<rect x="{left}" y="{y}" width="{w}" height="{bh}" fill="#3b6ea5"/>')
            o.append(f'<text x="{left+w+4}" y="{y+bh*0.7}">{v}</text>')
    o.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(o))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--outdir", default="figures")
    ap.add_argument("--by", nargs="*", default=[], help="extra categorical columns to count")
    ap.add_argument("--top", type=int, default=15)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    rows = read_csv(a.csv)
    P = lambda n: os.path.join(a.outdir, n)  # noqa: E731

    years = Counter(str(r.get("year", "")).strip()[:4] for r in rows if str(r.get("year", "")).strip())
    if years:
        ys = sorted(int(y) for y in years if y.isdigit())
        series = [(str(y), years.get(str(y), 0)) for y in range(ys[0], ys[-1] + 1)] if ys else []
        write_table(P("pubs_per_year.csv"), ["year", "n"], series)
        bar_svg(P("pubs_per_year.svg"), series, "Publications per year")

    venues = Counter(r.get("venue", "").strip() for r in rows if r.get("venue", "").strip())
    top_v = venues.most_common(a.top)
    write_table(P("top_venues.csv"), ["venue", "n"], top_v)
    bar_svg(P("top_venues.svg"), top_v, "Top publication venues", vertical=False)

    kw_sets = []
    for r in rows:
        ks = {k.strip().lower() for k in (r.get("keywords") or "").split(";") if k.strip()}
        kw_sets.append(ks)
    kws = Counter(k for s in kw_sets for k in s)
    top_k = kws.most_common(a.top)
    write_table(P("top_keywords.csv"), ["keyword", "n"], top_k)
    bar_svg(P("top_keywords.svg"), top_k, "Most frequent keywords", vertical=False)
    topset = {k for k, _ in kws.most_common(40)}
    co = Counter()
    for s in kw_sets:
        for x, y in itertools.combinations(sorted(s & topset), 2):
            co[(x, y)] += 1
    write_table(P("keyword_cooccurrence.csv"), ["kw1", "kw2", "n"],
                [(x, y, n) for (x, y), n in co.most_common()])

    for col in a.by:
        cnt = Counter()
        yb = defaultdict(Counter)
        for r in rows:
            for v in (r.get(col) or "").split(";"):
                v = v.strip()
                if v:
                    cnt[v] += 1
                    yb[str(r.get("year", ""))[:4]][v] += 1
        write_table(P(f"{col}_counts.csv"), [col, "n"], cnt.most_common())
        bar_svg(P(f"{col}_counts.svg"), cnt.most_common(a.top), f"Studies by {col}", vertical=False)
        cats = [c for c, _ in cnt.most_common()]
        write_table(P(f"year_by_{col}.csv"), ["year"] + cats,
                    [[y] + [yb[y][c] for c in cats] for y in sorted(yb)])
    print(f"Bibliometric tables and charts written to {a.outdir}/ ({len(rows)} records)")


if __name__ == "__main__":
    main()
