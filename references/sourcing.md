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

## Channels that need the candidate's own account

You cannot register on someone's behalf. Flag these early so the candidate can decide whether to
open them, because a couple are the only channels with a *continuous* flow rather than a snapshot:

- **LinkedIn Easy Apply** — hundreds of one-click applications, needs their logged-in profile.
- **Djinni** (`djinni.co/jobs/?primary_keyword=Node.js&exp_level=5y&employment=remote`) — RU/UA-speaking
  market, many B2B contracts. Browser-rendered; applying needs their account.
- **Contractor marketplaces** — Lemon.io, Proxify, A.Team, Toptal, Braintrust. One profile plus their
  interview, then a project stream. The only channel that keeps producing after the sweep is exhausted.
- **Telegram job channels** — not readable without their account.
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
- **LinkedIn / Indeed** — hostile to automation and mostly reposts of the above. Not worth the fight.

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
