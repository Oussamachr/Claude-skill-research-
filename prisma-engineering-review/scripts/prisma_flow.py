#!/usr/bin/env python3
"""Draw the PRISMA 2020 flow diagram (new reviews; databases/registers + optional other methods).

Input: prisma_counts.json produced by `screening.py counts` (or written by hand, same keys).
Output: <out>.svg (standalone vector figure) and <out>.tex (TikZ picture for \\input{} in LaTeX;
needs \\usepackage{tikz}).

The script checks the arithmetic of the flow before drawing and refuses (exit 3) if numbers
don't add up, unless --force is given. Inconsistent PRISMA numbers are a common reviewer
complaint, so fix the logs rather than forcing.

Usage:
  python prisma_flow.py prisma_counts.json --out prisma_flow [--force]
"""
import argparse
import json
import sys
import textwrap

BOX_W = 270
GAP_X = 40
LINE_H = 15
PAD = 10
GAP_Y = 34
LEFT = 40
WRAP = 40


def check(c):
    errs = []
    ident = sum(c["identification"]["databases"].values()) + c["identification"].get("registers", 0)
    removed = sum(c["removed_before_screening"].values())
    if ident - removed != c["records_screened"]:
        errs.append(f"identified ({ident}) - removed ({removed}) != screened ({c['records_screened']})")
    if c["records_screened"] - c["records_excluded"] != c["reports_sought"]:
        errs.append(f"screened ({c['records_screened']}) - excluded ({c['records_excluded']}) "
                    f"!= sought ({c['reports_sought']})")
    if c["reports_sought"] - c["reports_not_retrieved"] != c["reports_assessed"]:
        errs.append("sought - not retrieved != assessed")
    inc_db = c.get("reports_included_databases",
                   c["reports_assessed"] - sum(c["reports_excluded"].values()))
    if c["reports_assessed"] - sum(c["reports_excluded"].values()) != inc_db:
        errs.append(f"assessed ({c['reports_assessed']}) - excluded "
                    f"({sum(c['reports_excluded'].values())}) != included from databases ({inc_db})")
    om = c.get("other_methods")
    if om:
        ident_o = sum(om.get("identified", {}).values())
        if om.get("sought", ident_o) - om.get("not_retrieved", 0) != om.get("assessed"):
            errs.append("other methods: sought - not retrieved != assessed")
        if om["assessed"] - sum(om.get("excluded", {}).values()) != om.get("included"):
            errs.append("other methods: assessed - excluded != included")
    total = inc_db + (om.get("included", 0) if om else 0)
    if c.get("reports_included", total) != total:
        errs.append(f"reports_included ({c.get('reports_included')}) != database + other includes ({total})")
    return errs


def fmt_list(d):
    return [f"{k} (n = {v})" for k, v in d.items()]


def boxes(c):
    """Return list of (key, col, row, lines). col 0/1 = databases main/side, 2/3 = other methods."""
    B = []
    ident = ["Records identified from:"]
    ident += [f"  {k} (n = {v})" for k, v in c["identification"]["databases"].items()]
    if c["identification"].get("registers"):
        ident.append(f"  Registers (n = {c['identification']['registers']})")
    B.append(("ident", 0, 0, ident))
    r = c["removed_before_screening"]
    B.append(("removed", 1, 0, ["Records removed before screening:",
                                f"  Duplicate records removed (n = {r.get('duplicates', 0)})",
                                f"  Records marked as ineligible by automation tools (n = {r.get('automation', 0)})",
                                f"  Records removed for other reasons (n = {r.get('other', 0)})"]))
    B.append(("screened", 0, 1, [f"Records screened", f"(n = {c['records_screened']})"]))
    B.append(("excluded", 1, 1, [f"Records excluded", f"(n = {c['records_excluded']})"]))
    B.append(("sought", 0, 2, ["Reports sought for retrieval", f"(n = {c['reports_sought']})"]))
    B.append(("notret", 1, 2, ["Reports not retrieved", f"(n = {c['reports_not_retrieved']})"]))
    B.append(("assessed", 0, 3, ["Reports assessed for eligibility", f"(n = {c['reports_assessed']})"]))
    B.append(("ftexcl", 1, 3, ["Reports excluded:"] + ["  " + s for s in fmt_list(c["reports_excluded"])]))
    B.append(("included", 0, 4, [f"Studies included in review (n = {c['studies_included']})",
                                 f"Reports of included studies (n = {c['reports_included']})"]))
    om = c.get("other_methods")
    if om:
        B.append(("o_ident", 2, 0, ["Records identified from:"] +
                  ["  " + s for s in fmt_list(om.get("identified", {}))]))
        B.append(("o_sought", 2, 2, ["Reports sought for retrieval", f"(n = {om.get('sought')})"]))
        B.append(("o_notret", 3, 2, ["Reports not retrieved", f"(n = {om.get('not_retrieved', 0)})"]))
        B.append(("o_assessed", 2, 3, ["Reports assessed for eligibility", f"(n = {om.get('assessed')})"]))
        B.append(("o_excl", 3, 3, ["Reports excluded:"] + ["  " + s for s in fmt_list(om.get("excluded", {}))]))
    return B


def layout(B):
    wrapped = {}
    for key, col, row, lines in B:
        wl = []
        for ln in lines:
            indent = "  " if ln.startswith("  ") else ""
            ln = ln.replace("(n = ", "(n\u00a0=\u00a0")  # keep "(n = x)" on one line
            wl += textwrap.wrap(ln.strip(), WRAP, initial_indent=indent, subsequent_indent=indent + "  ") or [""]
        wrapped[key] = (col, row, wl)
    nrows = 1 + max(r for _, r, _ in wrapped.values())
    row_h = [0] * nrows
    for col, row, wl in wrapped.values():
        row_h[row] = max(row_h[row], len(wl) * LINE_H + 2 * PAD)
    row_y = [30]
    for h in row_h[:-1]:
        row_y.append(row_y[-1] + h + GAP_Y)
    pos = {}
    for key, (col, row, wl) in wrapped.items():
        x = LEFT + col * (BOX_W + GAP_X) + (GAP_X if col >= 2 else 0)
        pos[key] = (x, row_y[row], BOX_W, row_h[row], wl)
    width = LEFT + (4 if any(k.startswith("o_") for k in pos) else 2) * (BOX_W + GAP_X) + GAP_X
    height = row_y[-1] + row_h[-1] + 20
    return pos, row_y, row_h, width, height


ARROWS = [("ident", "removed", "h"), ("ident", "screened", "v"), ("screened", "excluded", "h"),
          ("screened", "sought", "v"), ("sought", "notret", "h"), ("sought", "assessed", "v"),
          ("assessed", "ftexcl", "h"), ("assessed", "included", "v"),
          ("o_ident", "o_sought", "v"), ("o_sought", "o_notret", "h"),
          ("o_sought", "o_assessed", "v"), ("o_assessed", "o_excl", "h"), ("o_assessed", "included", "elbow")]


def esc_xml(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(pos, row_y, row_h, W, H, has_other):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
         f'font-family="Helvetica, Arial, sans-serif" font-size="11">',
         '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
         '<path d="M0,0 L8,4 L0,8 z" fill="#000"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/>']
    # header bars
    hdr_w = 2 * BOX_W + GAP_X
    o.append(f'<text x="{LEFT + hdr_w/2}" y="18" text-anchor="middle" font-weight="bold">'
             f'Identification of studies via databases and registers</text>')
    if has_other:
        x0 = LEFT + 2 * (BOX_W + GAP_X) + GAP_X
        o.append(f'<text x="{x0 + hdr_w/2}" y="18" text-anchor="middle" font-weight="bold">'
                 f'Identification of studies via other methods</text>')
    # phase labels
    phases = [("Identification", 0, 0), ("Screening", 1, 3), ("Included", 4, 4)]
    for name, r0, r1 in phases:
        y0, y1 = row_y[r0], row_y[r1] + row_h[r1]
        o.append(f'<rect x="4" y="{y0}" width="24" height="{y1-y0}" fill="#cfe2f3" stroke="#000" rx="3"/>')
        cy = (y0 + y1) / 2
        o.append(f'<text x="16" y="{cy}" transform="rotate(-90 16 {cy})" text-anchor="middle" '
                 f'dominant-baseline="middle" font-weight="bold">{name}</text>')
    for key, (x, y, w, h, wl) in pos.items():
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff" stroke="#000"/>')
        centered = key in ("screened", "excluded", "sought", "notret", "assessed", "included",
                           "o_sought", "o_notret", "o_assessed") and len(wl) <= 2
        for i, ln in enumerate(wl):
            ty = y + PAD + (i + 0.8) * LINE_H
            if centered:
                o.append(f'<text x="{x + w/2}" y="{ty}" text-anchor="middle">{esc_xml(ln.strip())}</text>')
            else:
                o.append(f'<text x="{x + 8}" y="{ty}" xml:space="preserve">{esc_xml(ln)}</text>')
    for a, b, kind in ARROWS:
        if a not in pos or b not in pos:
            continue
        xa, ya, wa, ha, _ = pos[a]
        xb, yb, wb, hb, _ = pos[b]
        if kind == "h":
            y = ya + ha / 2
            o.append(f'<line x1="{xa+wa}" y1="{y}" x2="{xb}" y2="{y}" stroke="#000" marker-end="url(#ar)"/>')
        elif kind == "v":
            x = xa + wa / 2
            o.append(f'<line x1="{x}" y1="{ya+ha}" x2="{x}" y2="{yb}" stroke="#000" marker-end="url(#ar)"/>')
        else:  # elbow: down from other-methods box, then left into included box
            x = xa + wa / 2
            ym = yb + hb / 2
            o.append(f'<polyline points="{x},{ya+ha} {x},{ym} {xb+wb},{ym}" fill="none" stroke="#000" '
                     f'marker-end="url(#ar)"/>')
    o.append("</svg>")
    return "\n".join(o)


def esc_tex(s):
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"),
                 ("_", r"\_"), ("$", r"\$"), ("{", r"\{"), ("}", r"\}"), ("\u00a0", "~")):
        s = s.replace(a, b)
    return s


def tikz(pos, row_y, row_h, has_other):
    s = 1 / 40.0  # px -> cm
    L = ["% PRISMA 2020 flow diagram -- generated by prisma_flow.py",
         "% Requires \\usepackage{tikz} and \\usetikzlibrary{arrows.meta}",
         "\\begin{tikzpicture}[x=1cm,y=-1cm,font=\\scriptsize,",
         "  box/.style={draw,align=left,anchor=north west,inner sep=3pt},",
         "  arr/.style={-{Stealth[length=2mm]}}]"]
    hdr_w = 2 * BOX_W + GAP_X
    L.append(f"\\node[font=\\scriptsize\\bfseries] at ({(LEFT + hdr_w/2)*s:.2f},{12*s:.2f}) "
             f"{{Identification of studies via databases and registers}};")
    if has_other:
        x0 = LEFT + 2 * (BOX_W + GAP_X) + GAP_X
        L.append(f"\\node[font=\\scriptsize\\bfseries] at ({(x0 + hdr_w/2)*s:.2f},{12*s:.2f}) "
                 f"{{Identification of studies via other methods}};")
    for name, r0, r1 in [("Identification", 0, 0), ("Screening", 1, 3), ("Included", 4, 4)]:
        y0, y1 = row_y[r0], row_y[r1] + row_h[r1]
        L.append(f"\\draw[fill=blue!12,rounded corners=2pt] ({4*s:.2f},{y0*s:.2f}) rectangle "
                 f"({28*s:.2f},{y1*s:.2f});")
        L.append(f"\\node[rotate=90,font=\\scriptsize\\bfseries] at ({16*s:.2f},{(y0+y1)/2*s:.2f}) {{{name}}};")
    for key, (x, y, w, h, wl) in pos.items():
        text = "\\\\ ".join(esc_tex(ln).replace("  ", "\\quad ", 1) if ln.startswith("  ") else esc_tex(ln)
                            for ln in wl)
        L.append(f"\\node[box,text width={w*s - 0.2:.2f}cm,minimum height={h*s:.2f}cm] ({key}) at "
                 f"({x*s:.2f},{y*s:.2f}) {{{text}}};")
    for a, b, kind in ARROWS:
        if a not in pos or b not in pos:
            continue
        if kind == "h":
            L.append(f"\\draw[arr] ({a}.east) -- ({b}.west |- {a}.east);")
        elif kind == "v":
            L.append(f"\\draw[arr] ({a}.south) -- ({a}.south |- {b}.north);")
        else:
            L.append(f"\\draw[arr] ({a}.south) |- ({b}.east);")
    L.append("\\end{tikzpicture}")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("counts")
    ap.add_argument("--out", default="prisma_flow")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    c = json.load(open(a.counts, encoding="utf-8"))
    c.setdefault("reports_included_databases",
                 c["reports_assessed"] - sum(c["reports_excluded"].values()))
    c.setdefault("reports_included", c["reports_included_databases"] +
                 c.get("other_methods", {}).get("included", 0))
    c.setdefault("studies_included", c["reports_included"])
    errs = check(c)
    if errs:
        print("PRISMA arithmetic errors:\n  - " + "\n  - ".join(errs), file=sys.stderr)
        if not a.force:
            sys.exit(3)
    pos, row_y, row_h, W, H = layout(boxes(c))
    has_other = "other_methods" in c
    with open(a.out + ".svg", "w", encoding="utf-8") as f:
        f.write(svg(pos, row_y, row_h, W, H, has_other))
    with open(a.out + ".tex", "w", encoding="utf-8") as f:
        f.write(tikz(pos, row_y, row_h, has_other))
    print(f"Wrote {a.out}.svg and {a.out}.tex" + (" (WITH ARITHMETIC ERRORS)" if errs else " (arithmetic OK)"))


if __name__ == "__main__":
    main()
