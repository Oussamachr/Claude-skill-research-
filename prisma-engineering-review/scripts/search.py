#!/usr/bin/env python3
"""Literature search + import/export in a common CSV schema.

Modes (choose one):
  --source openalex|crossref|arxiv|semanticscholar --query "..."   live API search
  --source openalex --cites W123 | --references W123               citation snowballing
  --import FILE [FILE ...]                                         convert RIS/BibTeX/CSV/TXT exports
  --to-bibtex CSV                                                   write BibTeX from a records CSV

Output columns: id,title,authors,year,venue,doi,abstract,keywords,type,source,url
Authors are separated by '; '.

Examples:
  python search.py --source openalex --from-year 2014 --max 2000 \
      --query '("digital twin") AND (manufacturing OR production)' --out 02_search/openalex.csv
  python search.py --import scopus.csv wos.txt ieee.csv --out 02_search/imported.csv
  python search.py --to-bibtex 07_extraction.csv --out manuscript/references.bib

Network note: OpenAlex/Crossref/arXiv/Semantic Scholar need outbound HTTPS. If a request
fails, the script exits non-zero with the reason -- never substitute invented records.
Set POLITE_MAILTO=you@example.org (optional) to join the OpenAlex/Crossref polite pools.
"""
import argparse
import csv
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FIELDS, eprint, http_get, http_json, norm_doi, read_csv, split_author, write_csv  # noqa: E402


# ----------------------------------------------------------------------------- OpenAlex
def _oa_abstract(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def _oa_record(w):
    loc = (w.get("primary_location") or {})
    src = (loc.get("source") or {})
    return {
        "id": (w.get("id") or "").rsplit("/", 1)[-1],
        "title": w.get("display_name") or w.get("title") or "",
        "authors": "; ".join((a.get("author") or {}).get("display_name", "")
                             for a in w.get("authorships", [])),
        "year": w.get("publication_year") or "",
        "venue": src.get("display_name") or "",
        "doi": norm_doi(w.get("doi")),
        "abstract": _oa_abstract(w.get("abstract_inverted_index")),
        "keywords": "; ".join(k.get("display_name", "") for k in (w.get("keywords") or [])),
        "type": w.get("type") or "",
        "source": "OpenAlex",
        "url": loc.get("landing_page_url") or w.get("id") or "",
    }


def search_openalex(query=None, from_year=None, to_year=None, max_n=1000, cites=None,
                    references=None, types=None):
    base = "https://api.openalex.org/works"
    if references:
        w = http_json(f"{base}/{references}")
        ids = [r.rsplit("/", 1)[-1] for r in w.get("referenced_works", [])]
        out = []
        for i in range(0, len(ids), 50):
            chunk = "|".join(ids[i:i + 50])
            data = http_json(base, {"filter": f"openalex:{chunk}", "per-page": 50})
            out += [_oa_record(x) for x in data.get("results", [])]
        return out
    filters = []
    if query:
        filters.append(f"title_and_abstract.search:{query}")
    if cites:
        filters.append(f"cites:{cites}")
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")
    if types:
        filters.append("type:" + "|".join(types))
    params = {"filter": ",".join(filters), "per-page": 200, "cursor": "*"}
    out, total = [], None
    while len(out) < max_n:
        data = http_json(base, params)
        if total is None:
            total = data.get("meta", {}).get("count")
            eprint(f"OpenAlex reports {total} matching records")
        res = data.get("results", [])
        if not res:
            break
        out += [_oa_record(x) for x in res]
        nxt = data.get("meta", {}).get("next_cursor")
        if not nxt:
            break
        params["cursor"] = nxt
        time.sleep(0.2)
    return out[:max_n]


# ----------------------------------------------------------------------------- Crossref
def search_crossref(query, from_year=None, to_year=None, max_n=1000):
    base = "https://api.crossref.org/works"
    flt = []
    if from_year:
        flt.append(f"from-pub-date:{from_year}")
    if to_year:
        flt.append(f"until-pub-date:{to_year}")
    params = {"query.bibliographic": query, "rows": 100, "cursor": "*"}
    if flt:
        params["filter"] = ",".join(flt)
    out = []
    while len(out) < max_n:
        msg = http_json(base, params)["message"]
        items = msg.get("items", [])
        if not items:
            break
        for it in items:
            year = ""
            for k in ("published-print", "published-online", "issued"):
                dp = (it.get(k) or {}).get("date-parts")
                if dp and dp[0] and dp[0][0]:
                    year = dp[0][0]
                    break
            abstract = re.sub(r"<[^>]+>", " ", it.get("abstract", "") or "")
            out.append({
                "id": it.get("DOI", ""),
                "title": (it.get("title") or [""])[0],
                "authors": "; ".join(" ".join(filter(None, [a.get("given"), a.get("family")]))
                                     for a in it.get("author", [])),
                "year": year,
                "venue": (it.get("container-title") or [""])[0],
                "doi": norm_doi(it.get("DOI")),
                "abstract": re.sub(r"\s+", " ", abstract).strip(),
                "keywords": "; ".join(it.get("subject", []) or []),
                "type": it.get("type", ""),
                "source": "Crossref",
                "url": it.get("URL", ""),
            })
        params["cursor"] = msg.get("next-cursor")
        if not params["cursor"]:
            break
        time.sleep(0.2)
    return out[:max_n]


# ----------------------------------------------------------------------------- arXiv
def search_arxiv(query, from_year=None, to_year=None, max_n=1000):
    """query uses arXiv syntax, e.g. 'abs:"digital twin" AND abs:manufacturing'.
    Plain text is wrapped as all:(...)."""
    if not re.search(r"\b(ti|abs|all|au|cat):", query):
        query = f"all:({query})"
    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    out, start = [], 0
    while len(out) < max_n:
        xml = http_get("https://export.arxiv.org/api/query",
                       {"search_query": query, "start": start, "max_results": 200,
                        "sortBy": "submittedDate", "sortOrder": "descending"},
                       accept="application/atom+xml")
        root = ET.fromstring(xml)
        entries = root.findall("a:entry", ns)
        if not entries:
            break
        for e in entries:
            year = (e.findtext("a:published", "", ns) or "")[:4]
            if from_year and year and int(year) < int(from_year):
                return out
            if to_year and year and int(year) > int(to_year):
                continue
            aid = (e.findtext("a:id", "", ns) or "").rsplit("/abs/", 1)[-1]
            out.append({
                "id": "arXiv:" + aid,
                "title": re.sub(r"\s+", " ", e.findtext("a:title", "", ns)).strip(),
                "authors": "; ".join(a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)),
                "year": year,
                "venue": e.findtext("arxiv:journal_ref", "", ns) or "arXiv (preprint)",
                "doi": norm_doi(e.findtext("arxiv:doi", "", ns)),
                "abstract": re.sub(r"\s+", " ", e.findtext("a:summary", "", ns)).strip(),
                "keywords": "; ".join(c.get("term", "") for c in e.findall("a:category", ns)),
                "type": "preprint",
                "source": "arXiv",
                "url": e.findtext("a:id", "", ns),
            })
        start += 200
        time.sleep(3)  # arXiv API etiquette
    return out[:max_n]


# ----------------------------------------------------------------------------- Semantic Scholar
def search_s2(query, from_year=None, to_year=None, max_n=1000):
    base = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
    params = {"query": query,
              "fields": "title,authors,year,venue,externalIds,abstract,url,publicationTypes"}
    if from_year or to_year:
        params["year"] = f"{from_year or ''}-{to_year or ''}"
    out = []
    while len(out) < max_n:
        data = http_json(base, params)
        for p in data.get("data", []):
            ext = p.get("externalIds") or {}
            out.append({
                "id": "S2:" + (p.get("paperId") or ""),
                "title": p.get("title") or "",
                "authors": "; ".join(a.get("name", "") for a in p.get("authors") or []),
                "year": p.get("year") or "",
                "venue": p.get("venue") or "",
                "doi": norm_doi(ext.get("DOI")),
                "abstract": p.get("abstract") or "",
                "keywords": "",
                "type": "; ".join(p.get("publicationTypes") or []),
                "source": "SemanticScholar",
                "url": p.get("url") or "",
            })
        tok = data.get("token")
        if not tok:
            break
        params["token"] = tok
        time.sleep(1.1)
    return out[:max_n]


# ----------------------------------------------------------------------------- Importers
RIS_MAP = {"TI": "title", "T1": "title", "PY": "year", "Y1": "year", "DA": "year",
           "JO": "venue", "JF": "venue", "T2": "venue", "BT": "venue", "DO": "doi",
           "AB": "abstract", "N2": "abstract", "UR": "url", "TY": "type"}


def import_ris(path, label):
    recs, cur = [], None
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            m = re.match(r"^([A-Z][A-Z0-9])  -\s?(.*)$", line.rstrip("\n"))
            if not m:
                continue
            tag, val = m.group(1), m.group(2).strip()
            if tag == "TY":
                cur = {"authors": [], "keywords": [], "type": val}
            elif cur is None:
                continue
            elif tag == "ER":
                cur["authors"] = "; ".join(cur["authors"])
                cur["keywords"] = "; ".join(cur["keywords"])
                cur["year"] = (re.search(r"\d{4}", str(cur.get("year", ""))) or [""])[0] \
                    if cur.get("year") else ""
                cur["doi"] = norm_doi(cur.get("doi"))
                cur["source"] = label
                recs.append(cur)
                cur = None
            elif tag in ("AU", "A1", "A2") and tag != "A2":
                cur["authors"].append(val)
            elif tag == "KW":
                cur["keywords"].append(val)
            elif tag in RIS_MAP and not cur.get(RIS_MAP[tag]):
                cur[RIS_MAP[tag]] = val
    return recs


def _bib_entries(text):
    i = 0
    while True:
        m = re.compile(r"@(\w+)\s*\{\s*([^,\s]*)\s*,", re.S).search(text, i)
        if not m:
            return
        depth, j = 1, m.end()
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        yield m.group(1).lower(), m.group(2), text[m.end():j - 1]
        i = j


def _bib_fields(body):
    fields, i = {}, 0
    pat = re.compile(r"\s*,?\s*(\w[\w-]*)\s*=\s*", re.S)
    while True:
        m = pat.match(body, i)
        if not m:
            break
        key, j = m.group(1).lower(), m.end()
        if j < len(body) and body[j] == "{":
            depth, k = 1, j + 1
            while k < len(body) and depth:
                depth += {"{": 1, "}": -1}.get(body[k], 0)
                k += 1
            val, i = body[j + 1:k - 1], k
        elif j < len(body) and body[j] == '"':
            k = body.index('"', j + 1)
            val, i = body[j + 1:k], k + 1
        else:
            mm = re.match(r"[^,]*", body[j:])
            val, i = mm.group(0), j + mm.end()
        val = re.sub(r"\\([&%#_$])", r"\1", val.replace("{", "").replace("}", ""))
        fields[key] = re.sub(r"\s+", " ", val).strip()
    return fields


def import_bib(path, label):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    recs = []
    for etype, key, body in _bib_entries(text):
        if etype in ("comment", "string", "preamble"):
            continue
        fl = _bib_fields(body)
        recs.append({
            "id": key, "title": fl.get("title", ""),
            "authors": "; ".join(a.strip() for a in fl.get("author", "").split(" and ") if a.strip()),
            "year": fl.get("year", ""),
            "venue": fl.get("journal") or fl.get("booktitle") or fl.get("publisher", ""),
            "doi": norm_doi(fl.get("doi")), "abstract": fl.get("abstract", ""),
            "keywords": fl.get("keywords", "").replace(",", ";"),
            "type": etype, "source": label, "url": fl.get("url", ""),
        })
    return recs


# column aliases for Scopus CSV, Web of Science (tab-delimited), IEEE Xplore CSV, ACM, generic
CSV_ALIASES = {
    "title": ["title", "document title", "ti", "article title"],
    "authors": ["authors", "author full names", "au", "af", "author"],
    "year": ["year", "publication year", "py", "pubyear"],
    "venue": ["source title", "publication title", "so", "journal", "venue", "source"],
    "doi": ["doi", "di"],
    "abstract": ["abstract", "ab"],
    "keywords": ["author keywords", "keywords", "de", "index keywords", "ieee terms"],
    "type": ["document type", "dt", "type", "document identifier"],
    "url": ["link", "pdf link", "url"],
    "id": ["eid", "ut", "ut (unique wos id)", "id"],
}


def import_table(path, label):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        sample = f.read(4096)
        f.seek(0)
        delim = "\t" if sample.count("\t") > sample.count(",") else ","
        rows = list(csv.DictReader(f, delimiter=delim))
    if not rows:
        return []
    lower = {c.lower().strip(): c for c in rows[0].keys() if c}
    colmap = {}
    for field, aliases in CSV_ALIASES.items():
        for a in aliases:
            if a in lower:
                colmap[field] = lower[a]
                break
    recs = []
    for r in rows:
        rec = {k: (r.get(c) or "").strip() for k, c in colmap.items()}
        rec["authors"] = re.sub(r"\s*;\s*", "; ", rec.get("authors", ""))
        rec["doi"] = norm_doi(rec.get("doi"))
        rec["source"] = label
        recs.append(rec)
    return recs


def import_file(path):
    label = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1].lower()
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        head = f.read(2000)
    if ext == ".ris" or re.search(r"^TY  - ", head, re.M):
        return import_ris(path, label)
    if ext == ".bib" or head.lstrip().startswith("@"):
        return import_bib(path, label)
    return import_table(path, label)


# ----------------------------------------------------------------------------- BibTeX export
def _bib_escape(s):
    s = str(s or "")
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")):
        s = s.replace(a, b)
    return s


def to_bibtex(rows):
    used, out = set(), []
    for r in rows:
        first = (r.get("authors") or "anon").split(";")[0].strip()
        last = split_author(first)[0] or "anon"
        last = re.sub(r"[^A-Za-z]", "", last.encode("ascii", "ignore").decode()) or "anon"
        word = next((w for w in re.findall(r"[A-Za-z]{4,}", r.get("title", ""))
                     if w.lower() not in {"with", "from", "using", "towards", "toward", "based"}), "x")
        key = f"{last.lower()}{r.get('year', '')}{word.lower()}"
        base, n = key, 1
        while key in used:
            n += 1
            key = f"{base}{chr(96 + n)}"
        used.add(key)
        r["bibkey"] = key
        venue = r.get("venue", "")
        is_conf = bool(re.search(r"conference|proceedings|symposium|workshop|congress", venue, re.I)) \
            or "proceedings" in (r.get("type") or "").lower()
        etype = "inproceedings" if is_conf else ("misc" if "preprint" in (r.get("type") or "") else "article")
        authors = " and ".join(
            (lambda sg: f"{sg[0]}, {sg[1]}" if sg[1] else sg[0])(split_author(a))
            for a in (r.get("authors") or "").split(";") if a.strip())
        fields = [("author", authors), ("title", "{" + _bib_escape(r.get("title")) + "}"),
                  ("booktitle" if is_conf else "journal", _bib_escape(venue)),
                  ("year", r.get("year")), ("doi", r.get("doi")),
                  ("url", "" if r.get("doi") else r.get("url"))]
        body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields if v)
        out.append(f"@{etype}{{{key},\n{body}\n}}\n")
    return "\n".join(out)


# ----------------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", choices=["openalex", "crossref", "arxiv", "semanticscholar"])
    ap.add_argument("--query")
    ap.add_argument("--from-year", type=int)
    ap.add_argument("--to-year", type=int)
    ap.add_argument("--max", type=int, default=2000, help="max records to fetch (default 2000)")
    ap.add_argument("--types", nargs="*", help="OpenAlex work types, e.g. article review proceedings-article")
    ap.add_argument("--cites", help="OpenAlex work ID: fetch works citing it (forward snowballing)")
    ap.add_argument("--references", help="OpenAlex work ID: fetch its reference list (backward snowballing)")
    ap.add_argument("--import", dest="imports", nargs="+", help="RIS/BibTeX/CSV/TSV export files")
    ap.add_argument("--to-bibtex", help="records CSV -> BibTeX")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.to_bibtex:
        rows = read_csv(a.to_bibtex)
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(to_bibtex(rows))
        eprint(f"Wrote {len(rows)} BibTeX entries -> {a.out}")
        return

    if a.imports:
        recs = []
        for p in a.imports:
            got = import_file(p)
            eprint(f"{p}: {len(got)} records")
            recs += got
    elif a.source:
        if not (a.query or a.cites or a.references):
            ap.error("--query (or --cites/--references for openalex) is required")
        try:
            if a.source == "openalex":
                recs = search_openalex(a.query, a.from_year, a.to_year, a.max, a.cites, a.references, a.types)
            elif a.source == "crossref":
                recs = search_crossref(a.query, a.from_year, a.to_year, a.max)
            elif a.source == "arxiv":
                recs = search_arxiv(a.query, a.from_year, a.to_year, a.max)
            else:
                recs = search_s2(a.query, a.from_year, a.to_year, a.max)
        except RuntimeError as e:
            eprint(f"ERROR: {e}\nNo records written. Check network access, or run the search in the "
                   f"database UI and use --import on the export.")
            sys.exit(2)
    else:
        ap.error("choose --source, --import or --to-bibtex")

    write_csv(a.out, recs, FIELDS)
    eprint(f"Wrote {len(recs)} records -> {a.out}")


if __name__ == "__main__":
    main()
