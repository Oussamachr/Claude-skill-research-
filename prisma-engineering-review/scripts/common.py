"""Shared helpers: common record schema, CSV I/O, normalisation, HTTP."""
import csv
import json
import os
import re
import ssl
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

FIELDS = ["id", "title", "authors", "year", "venue", "doi", "abstract",
          "keywords", "type", "source", "url"]

USER_AGENT = "prisma-engineering-review/1.0 (systematic-review tool)"


def norm_doi(doi):
    if not doi:
        return ""
    d = doi.strip().lower()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d.strip().rstrip(".")


def norm_title(title):
    if not title:
        return ""
    t = unicodedata.normalize("NFKD", title)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"<[^>]+>", " ", t)          # strip HTML/MathML tags
    t = re.sub(r"[^a-z0-9 ]", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    fields = fields or FIELDS
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def _ssl_context():
    cafile = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if not cafile and os.path.exists("/root/.ccr/ca-bundle.crt"):
        cafile = "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()


def http_get(url, params=None, accept="application/json", retries=4, timeout=60):
    """GET with retries/backoff. Raises RuntimeError with a clear message on failure."""
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    mailto = os.environ.get("POLITE_MAILTO")  # optional, user-supplied only
    if mailto:
        headers["User-Agent"] += f" mailto:{mailto}"
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            last = e
            code = getattr(e, "code", None)
            if code in (400, 401, 403, 404):
                break
            time.sleep(2 ** attempt)
    raise RuntimeError(f"HTTP request failed for {url[:120]}...: {last}")


def http_json(url, params=None):
    return json.loads(http_get(url, params))


def eprint(*a):
    print(*a, file=sys.stderr)


_INITIALS = __import__("re").compile(r"^(?:[A-Z]\.?-?){1,4}$")


def split_author(name):
    """Return (surname, given) for 'Smith, John', 'John Smith' or Scopus-style 'Smith J.'."""
    name = (name or "").strip()
    if "," in name:
        last, given = name.split(",", 1)
        return last.strip(), given.strip()
    toks = name.split()
    if not toks:
        return "", ""
    if len(toks) > 1 and _INITIALS.match(toks[-1]):
        return " ".join(toks[:-1]), toks[-1]
    return toks[-1], " ".join(toks[:-1])
