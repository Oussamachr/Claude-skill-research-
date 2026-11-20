#!/usr/bin/env python3
"""Deduplicate records from several search exports.

Matching rules (in order):
  1. identical normalised DOI                          -> duplicate (certain)
  2. identical normalised title and |year diff| <= 1   -> duplicate (certain)
  3. title similarity >= --threshold (default 0.93)
     and |year diff| <= 1 and no conflicting DOIs      -> duplicate (probable, listed for review)

The kept record is the most complete one (has DOI, abstract, longest metadata); missing
fields are filled from its duplicates. Each output record gets a stable id R0001... and a
`sources` column listing every database it was found in.

Usage:
  python dedup.py 02_search/*.csv --out 03_records_dedup.csv --report 03_dedup_report.json
"""
import argparse
import difflib
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FIELDS, eprint, norm_doi, norm_title, read_csv, write_csv  # noqa: E402


def completeness(r):
    return (bool(r.get("doi")) * 4 + bool(r.get("abstract")) * 2
            + sum(bool(r.get(k)) for k in FIELDS) + len(r.get("abstract", "")) / 1e5)


def _year(r):
    try:
        return int(str(r.get("year", ""))[:4])
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--threshold", type=float, default=0.93)
    a = ap.parse_args()

    recs, per_file = [], {}
    for p in a.inputs:
        rows = read_csv(p)
        for r in rows:
            r["doi"] = norm_doi(r.get("doi"))
            r["_nt"] = norm_title(r.get("title"))
            r["source"] = r.get("source") or os.path.splitext(os.path.basename(p))[0]
            per_file[r["source"]] = per_file.get(r["source"], 0) + 1
            recs.append(r)
    n_in = len(recs)
    missing_title = [r for r in recs if not r["_nt"]]
    recs = [r for r in recs if r["_nt"]]

    parent = list(range(len(recs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        parent[find(j)] = find(i)

    by_doi, by_title = defaultdict(list), defaultdict(list)
    for i, r in enumerate(recs):
        if r["doi"]:
            by_doi[r["doi"]].append(i)
        by_title[r["_nt"]].append(i)
    for idxs in by_doi.values():
        for j in idxs[1:]:
            union(idxs[0], j)
    for idxs in by_title.values():
        for j in idxs[1:]:
            yi, yj = _year(recs[idxs[0]]), _year(recs[j])
            di, dj = recs[idxs[0]]["doi"], recs[j]["doi"]
            if (yi is None or yj is None or abs(yi - yj) <= 1) and not (di and dj and di != dj):
                union(idxs[0], j)

    # fuzzy pass: block on first 3 title words to keep it fast
    probable = []
    blocks = defaultdict(list)
    for i, r in enumerate(recs):
        blocks[" ".join(r["_nt"].split()[:3])].append(i)
    for idxs in blocks.values():
        for x in range(len(idxs)):
            for y in range(x + 1, len(idxs)):
                i, j = idxs[x], idxs[y]
                if find(i) == find(j):
                    continue
                ri, rj = recs[i], recs[j]
                if ri["doi"] and rj["doi"] and ri["doi"] != rj["doi"]:
                    continue
                yi, yj = _year(ri), _year(rj)
                if yi and yj and abs(yi - yj) > 1:
                    continue
                s = difflib.SequenceMatcher(None, ri["_nt"], rj["_nt"]).ratio()
                if s >= a.threshold:
                    union(i, j)
                    probable.append({"title_a": ri["title"], "title_b": rj["title"],
                                     "similarity": round(s, 3)})

    groups = defaultdict(list)
    for i in range(len(recs)):
        groups[find(i)].append(i)

    out = []
    for n, (_, idxs) in enumerate(sorted(groups.items(), key=lambda kv: min(kv[1])), start=1):
        members = sorted((recs[i] for i in idxs), key=completeness, reverse=True)
        keep = dict(members[0])
        for m in members[1:]:
            for k in FIELDS:
                if not keep.get(k) and m.get(k):
                    keep[k] = m[k]
        keep["orig_id"] = keep.get("id", "")
        keep["id"] = f"R{n:04d}"
        keep["sources"] = "; ".join(sorted({m["source"] for m in members}))
        keep["n_merged"] = len(members)
        out.append(keep)

    write_csv(a.out, out, FIELDS + ["orig_id", "sources", "n_merged"])
    report = {
        "records_in": n_in,
        "records_per_source": per_file,
        "records_without_title_removed": len(missing_title),
        "duplicates_removed": n_in - len(missing_title) - len(out),
        "records_out": len(out),
        "probable_duplicates_merged_check_these": probable,
    }
    with open(a.report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    eprint(f"{n_in} in -> {len(out)} unique ({report['duplicates_removed']} duplicates, "
           f"{len(missing_title)} without title, {len(probable)} fuzzy merges to check)")


if __name__ == "__main__":
    main()
