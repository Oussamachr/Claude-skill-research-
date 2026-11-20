#!/usr/bin/env python3
"""Verify BibTeX entries against Crossref (by DOI) -- catches fabricated or corrupted references.

For each entry:
  * DOI present -> fetch Crossref metadata; compare title (similarity), first-author surname, year.
  * DOI missing -> search Crossref by title+author; report the best match and its DOI as a
    suggestion (never auto-inserted).
Status: OK | MISMATCH | NOT_FOUND | NO_DOI_MATCH_SUGGESTED | NO_DOI_UNVERIFIED | NETWORK_ERROR

Also checks (with --tex) that every \\cite key used in the manuscript exists in the .bib and
lists .bib entries never cited.

Usage:
  python verify_refs.py manuscript/references.bib [--tex manuscript/main.tex] [--out 10_ref_check.csv]
"""
import argparse
import difflib
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import http_json, norm_doi, norm_title, split_author, write_csv  # noqa: E402
from search import _bib_entries, _bib_fields  # noqa: E402


def surname(author_field):
    return split_author(author_field.split(" and ")[0])[0]


def crossref_year(m):
    for k in ("published-print", "published-online", "issued"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            return str(dp[0][0])
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib")
    ap.add_argument("--tex", nargs="*")
    ap.add_argument("--out", default="10_ref_check.csv")
    ap.add_argument("--min-sim", type=float, default=0.85)
    a = ap.parse_args()

    text = open(a.bib, encoding="utf-8", errors="replace").read()
    entries = [(k, _bib_fields(b)) for t, k, b in _bib_entries(text) if t not in ("comment", "string")]
    results, net_fail = [], 0
    for key, f in entries:
        title, doi = f.get("title", ""), norm_doi(f.get("doi"))
        row = {"key": key, "title": title, "doi": doi, "status": "", "detail": ""}
        try:
            if doi:
                m = http_json("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
                ct = (m.get("title") or [""])[0]
                sim = difflib.SequenceMatcher(None, norm_title(title), norm_title(ct)).ratio()
                cs = ((m.get("author") or [{}])[0].get("family") or "")
                cy = crossref_year(m)
                issues = []
                if sim < a.min_sim:
                    issues.append(f"title sim {sim:.2f} vs Crossref '{ct[:80]}'")
                if cs and surname(f.get("author", "")) and norm_title(cs) != norm_title(surname(f.get("author", ""))):
                    issues.append(f"first author '{surname(f.get('author', ''))}' vs '{cs}'")
                if cy and f.get("year") and abs(int(cy) - int(re.sub(r"\D", "", f["year"])[:4] or cy)) > 1:
                    issues.append(f"year {f.get('year')} vs {cy}")
                row["status"] = "MISMATCH" if issues else "OK"
                row["detail"] = "; ".join(issues)
            else:
                q = {"query.bibliographic": f"{title} {surname(f.get('author', ''))}", "rows": 1}
                items = http_json("https://api.crossref.org/works", q)["message"].get("items", [])
                if items:
                    ct = (items[0].get("title") or [""])[0]
                    sim = difflib.SequenceMatcher(None, norm_title(title), norm_title(ct)).ratio()
                    if sim >= a.min_sim:
                        row["status"] = "NO_DOI_MATCH_SUGGESTED"
                        row["detail"] = f"suggested DOI {items[0].get('DOI')} (sim {sim:.2f}); verify then add"
                    else:
                        row["status"] = "NO_DOI_UNVERIFIED"
                        row["detail"] = f"no confident Crossref match (best sim {sim:.2f})"
                else:
                    row["status"] = "NO_DOI_UNVERIFIED"
        except RuntimeError as e:
            msg = str(e)
            if "404" in msg:
                row["status"], row["detail"] = "NOT_FOUND", "DOI does not resolve in Crossref"
            else:
                row["status"], row["detail"] = "NETWORK_ERROR", msg[:150]
                net_fail += 1
        results.append(row)
        print(f"[{row['status']:>22}] {key}: {row['detail']}")

    if a.tex:
        keys = {k for k, _ in entries}
        cited = set()
        for t in a.tex:
            for m in re.finditer(r"\\(?:cite|citep|citet|parencite|textcite|autocite)\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}",
                                 open(t, encoding="utf-8", errors="replace").read()):
                cited |= {c.strip() for c in m.group(1).split(",") if c.strip()}
        for k in sorted(cited - keys):
            results.append({"key": k, "status": "CITED_BUT_MISSING", "detail": "cited in .tex, absent from .bib"})
            print(f"[{'CITED_BUT_MISSING':>22}] {k}")
        for k in sorted(keys - cited):
            results.append({"key": k, "status": "UNCITED", "detail": "in .bib but never cited"})
            print(f"[{'UNCITED':>22}] {k}")

    write_csv(a.out, results, ["key", "title", "doi", "status", "detail"])
    bad = [r for r in results if r["status"] not in ("OK", "UNCITED")]
    print(f"\n{len(entries)} entries checked; {len(bad)} need attention -> {a.out}")
    if net_fail:
        print(f"{net_fail} entries could not be checked (network). They remain UNVERIFIED -- tell the user.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
