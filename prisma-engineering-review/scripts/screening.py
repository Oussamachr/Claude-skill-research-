#!/usr/bin/env python3
"""Screening utilities: PRISMA counts, inter-rater agreement, audit samples.

Subcommands
  counts  Compute every PRISMA 2020 flow-diagram number from the logs.
          python screening.py counts --records 03_records_dedup.csv \
              --dedup-report 03_dedup_report.json --ta 04_screening_ta.csv \
              --ft 05_screening_ft.csv [--search-log 02_search/search_log.csv] \
              [--other-methods other_methods.json] [--automation-removed 0] --out prisma_counts.json

          other_methods.json (optional; citation searching, websites, experts...):
          {"identified": {"Citation searching": 57, "Websites": 4},
           "not_retrieved": 2, "excluded": {"EC1-off-topic": 30, "EC3-no-metrics": 9},
           "included": 20}

  kappa   Cohen's kappa between two screening logs (joined on record_id; maybe -> include).
          python screening.py kappa rater_ai.csv rater_human.csv

  sample  Random audit sample for blind human double-screening.
          python screening.py sample 04_screening_ta.csv --records 03_records_dedup.csv \
              --frac 0.2 --seed 42 --out human_check.csv
"""
import argparse
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import eprint, read_csv, write_csv  # noqa: E402

PASS_TA = {"include", "maybe"}


def _dec(r):
    return (r.get("decision") or "").strip().lower()


def cmd_counts(a):
    records = read_csv(a.records)
    rep = json.load(open(a.dedup_report, encoding="utf-8"))
    ta = {r["record_id"]: r for r in read_csv(a.ta)}
    ft = {r["record_id"]: r for r in read_csv(a.ft)} if a.ft else {}
    warnings = []

    if a.search_log:
        dbs = Counter()
        for r in read_csv(a.search_log):
            dbs[r["source"].strip()] += int(float(r.get("records_found") or 0))
        if sum(dbs.values()) != rep["records_in"]:
            warnings.append(
                f"search_log total ({sum(dbs.values())}) != records imported into dedup "
                f"({rep['records_in']}). Explain the difference (e.g. export caps) in Methods, "
                f"or fix the log.")
    else:
        dbs = Counter(rep.get("records_per_source") or rep.get("records_per_file") or {})

    ids = [r["id"] for r in records]
    unscreened = [i for i in ids if i not in ta]
    if unscreened:
        warnings.append(f"{len(unscreened)} records have no title/abstract decision "
                        f"(first: {unscreened[:5]}). Screening is incomplete.")
    bad = [i for i, r in ta.items() if _dec(r) == "exclude" and not (r.get("reason") or "").strip()]
    if bad:
        warnings.append(f"{len(bad)} TA exclusions without a reason code (first: {bad[:5]}).")

    screened = len(ids)
    ta_excl = sum(1 for i in ids if i in ta and _dec(ta[i]) == "exclude")
    sought_ids = [i for i in ids if i in ta and _dec(ta[i]) in PASS_TA]
    missing_ft = [i for i in sought_ids if i not in ft]
    if ft and missing_ft:
        warnings.append(f"{len(missing_ft)} records passed TA but have no full-text decision "
                        f"(first: {missing_ft[:5]}).")
    not_retr = sum(1 for i in sought_ids if i in ft and _dec(ft[i]) == "not_retrieved")
    ft_reasons = Counter((ft[i].get("reason") or "unspecified").strip()
                         for i in sought_ids if i in ft and _dec(ft[i]) == "exclude")
    included_db = sum(1 for i in sought_ids if i in ft and _dec(ft[i]) == "include")

    out = {
        "identification": {"databases": dict(dbs), "registers": 0},
        "removed_before_screening": {
            "duplicates": rep["duplicates_removed"],
            "automation": a.automation_removed,
            "other": rep.get("records_without_title_removed", 0),
        },
        "records_screened": screened - a.automation_removed,
        "records_excluded": ta_excl,
        "reports_sought": len(sought_ids),
        "reports_not_retrieved": not_retr,
        "reports_assessed": len(sought_ids) - not_retr,
        "reports_excluded": dict(ft_reasons.most_common()),
        "reports_included_databases": included_db,
    }
    if a.automation_removed:
        warnings.append("automation_removed is subtracted from records screened; describe the tool "
                        "in Methods (PRISMA item 8).")
    if a.other_methods:
        om = json.load(open(a.other_methods, encoding="utf-8"))
        ident = sum(om.get("identified", {}).values())
        om.setdefault("sought", ident)
        om.setdefault("not_retrieved", 0)
        om["assessed"] = om["sought"] - om["not_retrieved"]
        om.setdefault("excluded", {})
        om.setdefault("included", om["assessed"] - sum(om["excluded"].values()))
        out["other_methods"] = om
    total_inc = included_db + (out.get("other_methods", {}).get("included", 0))
    out["studies_included"] = a.studies_included if a.studies_included is not None else total_inc
    out["reports_included"] = total_inc
    out["warnings"] = warnings
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    for w in warnings:
        eprint("WARNING:", w)
    eprint(json.dumps({k: v for k, v in out.items() if k != "warnings"}, indent=2))


def _bin(d):
    d = d.strip().lower()
    if d in PASS_TA:
        return 1
    if d == "exclude":
        return 0
    return None


def cmd_kappa(a):
    r1 = {r["record_id"]: _bin(r.get("decision", "")) for r in read_csv(a.rater1)}
    r2 = {r["record_id"]: _bin(r.get("decision", "")) for r in read_csv(a.rater2)}
    common = [k for k in r1 if k in r2 and r1[k] is not None and r2[k] is not None]
    if not common:
        sys.exit("No overlapping record_ids with include/exclude/maybe decisions.")
    t = Counter((r1[k], r2[k]) for k in common)
    n = len(common)
    po = (t[(1, 1)] + t[(0, 0)]) / n
    p1 = (t[(1, 1)] + t[(1, 0)]) / n
    p2 = (t[(1, 1)] + t[(0, 1)]) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    kappa = 1.0 if pe == 1 else (po - pe) / (1 - pe)
    label = ("slight" if kappa <= .2 else "fair" if kappa <= .4 else "moderate" if kappa <= .6
             else "substantial" if kappa <= .8 else "almost perfect")
    res = {"n": n, "agreement_pct": round(100 * po, 1), "cohen_kappa": round(kappa, 3),
           "interpretation_landis_koch": label,
           "table": {"both_include": t[(1, 1)], "both_exclude": t[(0, 0)],
                     "r1_include_r2_exclude": t[(1, 0)], "r1_exclude_r2_include": t[(0, 1)]},
           "disagreements": [k for k in common if r1[k] != r2[k]]}
    print(json.dumps(res, indent=2))


def cmd_sample(a):
    rows = read_csv(a.log)
    rng = random.Random(a.seed)
    k = max(1, round(len(rows) * a.frac))
    pick = rng.sample(rows, k)
    meta = {r["id"]: r for r in read_csv(a.records)} if a.records else {}
    out = [{"record_id": r["record_id"], "title": meta.get(r["record_id"], {}).get("title", ""),
            "abstract": meta.get(r["record_id"], {}).get("abstract", ""),
            "decision": "", "reason": "", "reviewer": "HUMAN", "notes": ""} for r in pick]
    write_csv(a.out, out, ["record_id", "title", "abstract", "decision", "reason", "reviewer", "notes"])
    eprint(f"Wrote {k} records (seed {a.seed}) -> {a.out}. Reviewer should fill 'decision' blind.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("counts")
    c.add_argument("--records", required=True)
    c.add_argument("--dedup-report", required=True)
    c.add_argument("--ta", required=True)
    c.add_argument("--ft")
    c.add_argument("--search-log")
    c.add_argument("--other-methods")
    c.add_argument("--automation-removed", type=int, default=0)
    c.add_argument("--studies-included", type=int,
                   help="if several reports describe one study, give the number of unique studies")
    c.add_argument("--out", required=True)
    k = sub.add_parser("kappa")
    k.add_argument("rater1")
    k.add_argument("rater2")
    s = sub.add_parser("sample")
    s.add_argument("log")
    s.add_argument("--records")
    s.add_argument("--frac", type=float, default=0.2)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    {"counts": cmd_counts, "kappa": cmd_kappa, "sample": cmd_sample}[a.cmd](a)


if __name__ == "__main__":
    main()
