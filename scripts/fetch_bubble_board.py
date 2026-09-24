#!/usr/bin/env python3
"""Read a Bubble-built job board through its Data API, in one pass.

  python3 fetch_bubble_board.py choicy.work --out rows.json --bodies bodies.json
  python3 fetch_bubble_board.py example.com --probe          # is the API open, what's the type?
  python3 fetch_bubble_board.py example.com --type positions --title Role --body Details

Bubble sites (custom domains included — look for `window._bubble_page_load_data` or
`/package/run_js/` in the HTML) render postings client-side, so `curl` on the page
returns an empty shell and the obvious move is to drive a browser. Very often you
don't have to: the owner never turned the Data API off, and one request returns the
whole table, including fields the rendered page omits.

Two things make this worth a script rather than a one-liner.

**It emits rows AND bodies from the same call.** The board's description field is
already in the response, so there is nothing left to fetch — the bodies file is
written in fetch_postings.py's format and filter_postings.py accepts it directly.

**It leaves `location` empty when the board has no location field**, instead of
writing "Remote". filter_postings.py keeps a row whose location is empty and judges
it on the body; a row that says "Remote" is tested against geo_in, matches nothing,
and is dropped with a reason that reads as if it were correct. Boards like this one
keep geography in prose only, so the empty string is the honest value.

Known boards live in ../data/bubble_boards.json. Anything not listed there can be
read with --type plus the field flags once --probe tells you the type name.

Only read what the board already publishes. A Bubble app that also exposes `user` is
misconfigured, not inviting you in; this script will not fetch that type.
"""
import argparse, json, os, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
REGISTRY = os.path.join(DATA, "bubble_boards.json")

# Ordered by how often each one is the answer. Deliberately no `user`, `account`,
# `profile`, `application`: those are people, not postings.
TYPE_GUESSES = ["jobs", "job", "vacancy", "vacancies", "position", "positions",
                "listing", "listings", "opening", "openings", "role", "roles",
                "post", "posts", "offer", "offers"]

PRIVATE_TYPES = {"user", "users", "account", "accounts", "profile", "profiles",
                 "candidate", "candidates", "application", "applications",
                 "message", "messages", "payment", "payments"}


# Bubble stores rich text as BBCode. Both patterns are bounded and non-nested on
# purpose — an unbounded `.*?` between brackets backtracks badly on a long description.
BB_LINK = re.compile(r"\[url=([^\]\s]{1,400})\]([^\[]{0,200})\[/url\]", re.I)
BB_TAG = re.compile(r"\[/?[a-z][^\]\n]{0,60}\]", re.I)


# Where these boards actually state geography. Measured: on an agency board the only
# sentence naming it ("100% remote, work from anywhere … overlap with Asian and European
# time zones") sat at character 6394, and filter_postings.py reads the first 3000 — so the
# one genuinely worldwide role on the board was rejected for "no geo_in term". Hoisting the
# line into the header fixes that without widening the filter's window for every board.
GEO_HINT = re.compile(
    r"work from anywhere|anywhere in the world|worldwide|globally|fully remote|100% remote"
    r"|remote[- ]first|time ?zone|\bGMT\b|\bUTC\b|\bCET\b|\bEST\b|relocation"
    r"|based (in|anywhere)|located (in|anywhere)|eligible to work", re.I)


def hoist_geo(text, limit=240):
    """Return the first line that states where the job may be done, if any."""
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 4 and GEO_HINT.search(line):
            return line[:limit]
    return ""


def untag(text):
    """Strip Bubble's BBCode, but keep the href — the apply link often lives in one."""
    if not text:
        return ""
    # "[url=https://x]click here[/url]" -> "click here (https://x)"; a bare label keeps the URL.
    text = BB_LINK.sub(lambda m: f"{m.group(2).strip()} ({m.group(1)})".strip(), text)
    text = BB_TAG.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def get(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:                       # 404 carries the useful message
        try:
            return e.read().decode("utf-8", "ignore")
        except Exception:
            return None
    except Exception:
        return None


def api(host, type_name, limit=100, cursor=0):
    q = urllib.parse.urlencode({"limit": limit, "cursor": cursor})
    return f"https://{host}/api/1.1/obj/{urllib.parse.quote(type_name)}?{q}"


def probe(host, guesses=TYPE_GUESSES):
    """Return (type_name, note). A 'Type not found' reply means the API is ON."""
    api_is_on = False
    for name in guesses:
        body = get(api(host, name, limit=1))
        if body is None:
            continue
        try:
            data = json.loads(body)
        except ValueError:
            continue
        if isinstance(data.get("response"), dict) and "results" in data["response"]:
            return name, f"Data API open, type '{name}'"
        if data.get("body", {}).get("status") == "NOT_FOUND":
            api_is_on = True                 # right door, wrong name — keep trying
    if api_is_on:
        return None, ("Data API is ON but none of the guessed type names matched. "
                      "Find the real name in the page's JS bundle and pass --type.")
    return None, "No Data API here — this one needs a browser."


def fetch_all(host, type_name, page=100, cap=10000):
    rows, cursor = [], 0
    while len(rows) < cap:
        body = get(api(host, type_name, limit=page, cursor=cursor))
        if not body:
            sys.exit(f"FATAL: request failed at cursor {cursor}; partial data not written")
        try:
            resp = json.loads(body)["response"]
        except (ValueError, KeyError):
            sys.exit(f"FATAL: unexpected response at cursor {cursor}; partial data not written")
        results = resp.get("results") or []
        rows += results
        if not results or not resp.get("remaining"):
            break
        cursor += resp.get("count", len(results))
    return rows


def load_board(host):
    try:
        with open(REGISTRY) as fh:
            boards = json.load(fh)["boards"]
    except Exception:
        return None
    for b in boards:
        if b.get("host") == host:
            return b
    return None


def visible(rec, rules):
    return all(rec.get(k) == v for k, v in (rules or {}).items())


def salary_line(rec, spec):
    if not spec:
        return ""
    rng = rec.get(spec.get("range") or "")
    if not isinstance(rng, list) or not rng:
        return ""
    lo, hi = (rng + [None, None])[:2]
    if not lo and not hi:            # [0, 0] and [None, None] carry no information
        return ""
    amount = f"{lo}–{hi}" if lo and hi and lo != hi else f"{hi or lo}"
    unit = " ".join(x for x in (rec.get(spec.get("currency") or ""),
                                rec.get(spec.get("period") or "")) if x)
    return f"Salary: {amount} {unit}".strip()


def to_rows(records, board):
    org = board.get("org") or board["host"]
    rows, bodies = [], []
    for rec in records:
        if not visible(rec, board.get("visible_if")):
            continue
        title = str(rec.get(board.get("title") or "title", "") or "").strip()
        url = (board.get("url") or f"https://{board['host']}/{{_id}}").format(**{
            k: rec.get(k, "") for k in ("_id",)})
        if not title or not url:
            continue
        # Empty, not "Remote": see the module docstring.
        loc_field = board.get("location")
        location = str(rec.get(loc_field, "") or "").strip() if loc_field else ""
        body = untag(str(rec.get(board.get("body") or "description", "") or ""))
        # Fields the rendered page usually hides go in front of the description, so
        # the filter's stack/geography checks and a human both see them.
        head = [f"{k}: {rec[k]}" for k in board.get("extras", []) if rec.get(k) not in (None, "")]
        pay = salary_line(rec, board.get("salary"))
        if pay:
            head.insert(0, pay)
        geo = hoist_geo(body)
        if geo:
            head.insert(0, f"Location note: {geo}")
        text = ("\n".join(head) + "\n\n" + body).strip() if head else body.strip()
        rows.append(["bubble", org, title, location, url])
        bodies.append([url, title, location, text, "verified" if text else "failed"])
    return rows, bodies


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host", help="e.g. choicy.work")
    ap.add_argument("--probe", action="store_true", help="only report whether the API is open")
    ap.add_argument("--type", help="Bubble data type; overrides the registry")
    ap.add_argument("--org", help="employer name to log these under")
    ap.add_argument("--title", help="field holding the job title")
    ap.add_argument("--location", help="field holding the location, if the board has one")
    ap.add_argument("--body", help="field holding the description")
    ap.add_argument("--out", default="bubble_rows.json")
    ap.add_argument("--bodies", help="also write a fetch_postings.py-shaped bodies file")
    args = ap.parse_args()

    host = args.host.replace("https://", "").replace("http://", "").strip("/")
    board = load_board(host) or {"host": host}
    for key, val in (("type", args.type), ("org", args.org), ("title", args.title),
                     ("location", args.location), ("body", args.body)):
        if val:
            board[key] = val

    if args.probe or not board.get("type"):
        found, note = probe(host)
        print(f"{host}: {note}")
        if args.probe:
            return
        if not found:
            sys.exit(1)
        board["type"] = found

    if board["type"].lower() in PRIVATE_TYPES:
        sys.exit(f"Refusing to read '{board['type']}' — that is people, not postings.")

    records = fetch_all(host, board["type"])
    rows, bodies = to_rows(records, board)
    with open(args.out, "w") as fh:
        json.dump(rows, fh)
    print(f"{len(records)} records -> {len(rows)} live postings -> {args.out}")
    if args.bodies:
        with open(args.bodies, "w") as fh:
            json.dump(bodies, fh)
        print(f"descriptions -> {args.bodies} (pass to filter_postings.py --bodies)")
    if records and not rows:
        print("! every record was filtered out — check `visible_if` against a record's real fields",
              file=sys.stderr)


if __name__ == "__main__":
    main()
