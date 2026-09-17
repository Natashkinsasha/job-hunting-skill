#!/usr/bin/env python3
"""Sweep every Ashby / Greenhouse / Lever board and dump one row per posting.

  python3 sweep_boards.py --out rows.json            # all three ATS, ~16k boards, ~20 min
  python3 sweep_boards.py --ats ashby --workers 8

Output: JSON array of [ats, org, title, location, url].
Descriptions are NOT fetched (that is 130k extra requests) — filter on title and
location first, then pull bodies for the survivors with fetch_postings.py.

Keep --workers at 8-12. Higher saturates the connection and starts failing the
browser session you are applying through, which looks exactly like a broken form.
"""
import argparse, concurrent.futures, json, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0"}
TOKENS = "https://raw.githubusercontent.com/Feashliaa/job-board-aggregator/HEAD/data/{ats}_companies.json"


def get(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers=UA)
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except Exception:
        return None


def parse_ashby(org, body):
    for j in json.loads(body).get("jobs", []):
        secondary = " | ".join(
            (l.get("location", "") if isinstance(l, dict) else str(l))
            for l in (j.get("secondaryLocations") or [])
        )
        yield ("ashby", org, j.get("title", ""),
               f"{j.get('location', '')} {secondary}".strip(), j.get("jobUrl", ""))


def parse_greenhouse(org, body):
    for j in json.loads(body).get("jobs", []):
        # absolute_url is often the company's own careers page (…?gh_jid=123), which no
        # API resolves. The canonical board URL always works — rebuild it from the id.
        url = f"https://job-boards.greenhouse.io/{org}/jobs/{j.get('id')}"
        yield ("greenhouse", org, j.get("title", ""),
               (j.get("location") or {}).get("name", ""), url)


def parse_lever(org, body):
    arr = json.loads(body)
    if not isinstance(arr, list):
        return
    for j in arr:
        cat = j.get("categories") or {}
        yield ("lever", org, j.get("text", ""),
               f"{cat.get('location', '')} {j.get('workplaceType', '')}".strip(),
               j.get("hostedUrl", ""))


ATS = {
    "ashby":      ("https://api.ashbyhq.com/posting-api/job-board/{org}", parse_ashby),
    "greenhouse": ("https://boards-api.greenhouse.io/v1/boards/{org}/jobs", parse_greenhouse),
    "lever":      ("https://api.lever.co/v0/postings/{org}?mode=json", parse_lever),
}


def fetch(task):
    ats, org = task
    url_tpl, parse = ATS[ats]
    body = get(url_tpl.format(org=org))
    if not body:
        return []
    try:
        return list(parse(org, body))
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ats", nargs="*", default=list(ATS), choices=list(ATS))
    ap.add_argument("--out", default="rows.json")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    tasks = []
    for ats in args.ats:
        tokens = get(TOKENS.format(ats=ats))
        if not tokens:
            print(f"! could not fetch token list for {ats}", file=sys.stderr)
            continue
        tasks += [(ats, t) for t in json.loads(tokens)]
    print(f"{len(tasks)} boards", flush=True)

    rows, done = [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for got in ex.map(fetch, tasks):
            rows += got
            done += 1
            if done % 1000 == 0:
                print(f"  {done}/{len(tasks)} boards, {len(rows)} postings", flush=True)

    with open(args.out, "w") as fh:
        json.dump(rows, fh)
    print(f"{len(rows)} postings -> {args.out}")


if __name__ == "__main__":
    main()
