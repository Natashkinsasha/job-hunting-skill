# Sourcing

Where postings actually come from, and which channels are a waste of a day.

## The shape of the problem

Job boards (LinkedIn, Indeed, Wellfound, RemoteOK…) are a search interface over a small,
stale, heavily-duplicated slice of the market, and most of them fight scraping. The
applicant-tracking systems underneath them expose **public, unauthenticated JSON** listing
every open role at every company that uses them. Go to the source.

A full sweep of Ashby + Greenhouse + Lever is ~16,000 boards / ~130,000 postings and takes
about 20 minutes with 8–12 workers. That is the entire addressable market for
internationally-remote engineering roles. Run it once, filter it repeatedly.

## ATS endpoints

All GET, all public, all return JSON.

| ATS | Listings | Single job |
|---|---|---|
| Ashby | `api.ashbyhq.com/posting-api/job-board/<org>?includeCompensation=true` | in the list (`descriptionHtml`) |
| Greenhouse | `boards-api.greenhouse.io/v1/boards/<org>/jobs` | `…/jobs/<id>` → `content` |
| Lever | `api.lever.co/v0/postings/<org>?mode=json` | in the list (`description` + `lists[]`) |
| Workable | `apply.workable.com/api/v1/widget/accounts/<token>?details=true` | in the list |
| Recruitee | `<org>.recruitee.com/api/offers/` | `…/offers/<id>` |
| Teamtailor | `<org>.teamtailor.com/jobs.json` | in the list |
| SmartRecruiters | `api.smartrecruiters.com/v1/companies/<org>/postings` | `…/postings/<id>` |
| BambooHR | `<org>.bamboohr.com/careers/list` | `…/careers/<id>/detail` |
| Workday | `POST <tenant>.wd<N>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs` | `…/job/<path>` |

Greenhouse and Lever have EU-hosted boards (`job-boards.eu.greenhouse.io`, `jobs.eu.lever.co`).
Lever's EU API host is `api.eu.lever.co`; **Greenhouse has no EU API host** — `boards-api.greenhouse.io`
already serves EU boards.

## Getting the list of org tokens

**The skill ships with them.** `data/<ats>_companies.json` holds ~27,000 board tokens
(ashby 3,175 · greenhouse 8,335 · lever 4,370 · bamboohr 11,316), so a sweep needs nothing but
the ATS APIs themselves. Two ways to grow the list, neither of which can shrink it:

- `sweep_boards.py --refresh` merges the upstream dataset
  (`raw.githubusercontent.com/Feashliaa/job-board-aggregator/HEAD/data/<ats>_companies.json`)
  into the local file. If that repo moves or dies you lose *new* companies, not your list.
- `discover_boards.py` finds boards no dataset has. Remote-job aggregators publish company
  **names** freely even when they publish nothing else useful, and a board token is almost always
  the company name lowercased with punctuation stripped. Harvest names → slugify → probe the three
  board APIs → keep the 200s. Measured: 296 harvested names → 120 live boards → 18 that the
  vendored lists didn't have, including Bybit, Kraken, Qonto and Doctolib.

A third way, by hand: a company's careers page always reveals its board, in an `<iframe src>` or a
`fetch()` to one of the hosts above. Worth doing for a specific company you want.

## Aggregator feeds worth reading directly

Small compared to a sweep (hundreds, not 130k), but they surface *companies* that no token list has,
and a few carry a genuine worldwide flag. Feed them to `discover_boards.py --names` or read directly.

| Feed | Endpoint | Notes |
|---|---|---|
| We Work Remotely | `weworkremotely.com/categories/<cat>.rss` | The RSS carries a `<region>` tag — `Anywhere in the World` is a real filter, not a hope. Categories: `remote-programming-jobs`, `remote-back-end-programming-jobs`, `remote-front-end-programming-jobs`, `remote-full-stack-programming-jobs` |
| Hacker News "Who is hiring" | `hnhiring.com/locations/remote` | Small, but these are direct-to-founder and often reply by email |
| Jobicy | `jobicy.com/api/v2/remote-jobs?count=50&geo=europe&industry=dev` | `geo` filter actually works |
| Remotive | `remotive.com/api/remote-jobs?category=software-dev` | Thin but live |
| Himalayas | `himalayas.app/jobs/api?limit=100` + cursor | Fresh, few senior worldwide |
| Working Nomads | `workingnomads.com/api/exposed_jobs/` | Mostly contractor marketplaces |
| Arbeitnow | `arbeitnow.com/api/job-board-api` | EU, mostly on-site |
| RemoteOK | `remoteok.com/api` | Noisy, but a good source of company names |
| NoDesk | `nodesk.co/remote-jobs/index.xml` | ~10 postings |

**Measured on a second full run, months later, with the four API feeds above:** 516 rows in, 16 past
the title/geography filter, **0 genuinely new**. Everything that survived was either already in the log,
already blocked for a known reason, or misfiled by title — a "FullStack Engineer" that turned out to be
Laravel/PHP once the body was fetched. Aggregators are a cheap top-up on a fresh search and close to
worthless on a repeat one; budget minutes, not hours, and never let them delay the board sweep.

## One-off boards: check for an accidental public API first

A single link from a recruiter or an aggregator often lands on a small board built with a no-code tool,
where the posting text is rendered client-side and `curl` returns an empty shell. Before driving a
browser, check whether the platform is answering questions for free.

**Bubble** (`*.bubbleapps.io` and custom domains on it — look for `window._bubble_page_load_data` or
`/package/run_js/` in the HTML) exposes a Data API at `https://<host>/api/1.1/obj/<type>`. Many owners
never turn it off. Probing costs one request and the error message is the hint you need:

```sh
curl -s https://<host>/api/1.1/obj/jobs            # guess the type name
# {"statusCode":404,"body":{"status":"NOT_FOUND","message":"Type not found jobs"}}
#   → the API is ON, the type name is wrong. Try: jobs, job, vacancies, positions, listings, user
# a JSON body with response.results → you have the whole table
curl -s "https://<host>/api/1.1/obj/jobs?limit=100&cursor=0"   # page via response.remaining
```

Measured on one agency board: 945 records, 37 of them visible and approved, with fields the rendered
page never shows — in that case a `Salary range` the posting itself omitted, which decided whether five
of the roles were worth opening at all. It also turns "is there more work here?" into one command
instead of a browsing session.

Two cautions. Only read what the site already publishes — a board that exposes `user` is a
misconfiguration, not an invitation. And the API reflects raw rows, so filter on the site's own
visibility fields (`Visible`, a status like `Approved`) or you will read drafts and expired postings.

## Channels that need the candidate's own account

You cannot register on someone's behalf. Flag these early so the candidate can decide whether to
open them, because a couple are the only channels with a *continuous* flow rather than a snapshot:

- **LinkedIn — OFF LIMITS.** Not "needs their account": do not open it at all. LinkedIn bans accounts
  for automated access, and the candidate's profile is what recruiters check after every application
  elsewhere, so a ban damages the whole search. See "Never touch LinkedIn" in `SKILL.md`. A role that
  exists only behind a `linkedin.com` / `lnkd.in` link is blocked, not a to-do.
- **Djinni** (`djinni.co/jobs/?primary_keyword=Node.js&exp_level=5y&employment=remote`) — RU/UA-speaking
  market, many B2B contracts. Browser-rendered; applying needs their account.
- **Contractor marketplaces** — Lemon.io, Proxify, A.Team, Toptal, Braintrust. One profile plus their
  interview, then a project stream. The only channel that keeps producing after the sweep is exhausted.
- **Telegram job channels** — need their account (QR login from their phone). Measured on one senior
  remote candidate: ~60 channels, 8 feeds read, **1 matching vacancy** against 16 applications sent the
  same evening through Wellfound/YC/Proxify. Treat as background, time-box it, and read
  `references/telegram.md` first — most channels are aggregator relays, marketing/arbitrage, or ad dumps.
- **YC Work at a Startup**, **Otta / Welcome to the Jungle**, **Wellfound** — login-gated.

## Channels confirmed dead or not worth it

- **hh.ru API** — 403 without a Russian-facing IP.
- **Getro** (a16z / Sequoia portfolio talent boards) — public API closed, 404.
- **Wellfound (AngelList)** — 403 unauthenticated.
- **remote3.co, cryptocurrencyjobs.co, arc.dev, aijobs.net, justremote** — HTML only, needs browser
  scraping for a small yield.
- **Guessing Workable tokens** — 60 guessed company tokens produced 2 live boards and 0 matches.
  Slug-probing pays off on Ashby/Greenhouse/Lever; it does not on Workable.

## Channel verdicts (measured, not guessed)

- **Ashby / Greenhouse / Lever** — where internationally-remote engineering actually lives. Apply directly, no account.
- **Workday** — 12,884 boards → 24,300 postings → **0 usable**. Two reasons: applying requires
  creating an account per company, and the location field lies (a posting tagged "Worldwide" said
  "must reside in the United States" in the body). Use for discovery only, if at all.
- **BambooHR** — 11,316 boards → 46,363 postings → **1 usable**. It is the ATS of small domestic
  employers. Almost no international remote.
- **iCIMS** — same profile as the two above. Skip unless you have a specific company in mind.
- **hiring.cafe** — good filters, no usable API (405/404). Only reachable through a browser:
  `https://hiring.cafe/?searchState={"workplaceTypes":["Remote"],"searchQuery":"..."}`,
  wait ~6 s, read `document.body.innerText`. Rate-limits into a Cloudflare challenge quickly.
- **Indeed** — hostile to automation and mostly reposts of the above. Not worth the fight. (LinkedIn is not
  a "verdict" at all — it is prohibited; see above.)

## Filtering: the geography test that works

The naive filter — "posting says Remote" — is wrong more often than right. "Remote" almost
always means "remote *within* the country or bloc we can employ you in".

**Search for the candidate's country or city inside the posting's list of hiring locations.**
That list is the only place a company commits to a geography. Phrases like "remote (non-EU)" are
usually about *tax residence in a specific country*, not about you.

Cheap pre-filters that cost nothing and remove most of the corpus:

```python
# substitute the candidate's own exclusions and their country/city into these
TITLE_OUT = r'devops|sre|site reliab|platform|infrastructur|security|release|manager|director|sales|recruit'
GEO_OUT   = r'\b(us|u\.s\.|united states|usa|canada|emea only|uk only)\b.{0,40}(only|based|resident|eligib)'
GEO_IN    = r'<their country>|<their city>|worldwide|anywhere|global|any timezone'
```

Then read the body. A body that never names a country, and never names a timezone band narrower
than the candidate's, is the good case.

## What a sweep actually yields

Measured on one real run: 15,880 boards → ~130,000 postings (Lever alone: 4,368 boards →
59,103 postings). After filtering for one specific candidate — senior backend/fullstack,
non-EU resident, worldwide remote, $100k — that came down to roughly **60–120 applyable roles**.

That is the real size of the worldwide-remote market at a given moment: not thousands. Two
consequences. First, plan for depth per application rather than volume; there aren't enough
roles to spray. Second, the channel genuinely does get exhausted after a couple of days, and
when it does, further yield comes only from the account-gated channels above — not from
sweeping harder.

**A repeat sweep, same candidate, about a week later**, gives you the shape of the steady state:
15,880 boards → **264,698 postings** → 260 past title+geography → **185** after bodies → roughly
15 worth opening → **7 sent**. The drop from 185 to 15 is not the filter being weak; it is what the
filter cannot see from a title and a location — the stack named only in the body, the residency
requirement stated in the form, the AI ban in a consent checkbox, the role already applied to under a
different URL. Expect single digits of new applications per sweep once the first pass is done, and
tell the candidate that number up front, because "find me more" sounds like it should return dozens.

Two related reflexes worth having at that point. Sweep totals swing a lot between runs (~130k vs
~265k postings on the same board list) — that is board availability and transient failures, not the
market moving, so do not read a trend into it. And when a sweep returns little, the honest report is
the funnel, not an apology: a filter that drops 99.99% is doing its job, and the constraint is the
market rather than the search.
