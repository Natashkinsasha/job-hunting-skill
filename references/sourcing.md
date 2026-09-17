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

Public dataset, kept current, one JSON array of tokens per ATS:

```
https://raw.githubusercontent.com/Feashliaa/job-board-aggregator/HEAD/data/<ats>_companies.json
```
`<ats>` ∈ `ashby`, `greenhouse`, `lever`, `workday`, `bamboohr`, `icims`.

Sizes as measured 2026-09-17: ashby 3,161 · greenhouse 8,333 · lever 4,368 · bamboohr 11,316 · workday 12,884.

Other ways to discover tokens, in rough order of yield:
- Company careers pages: the board is in an `<iframe src>` or a `fetch()` to one of the hosts above.
- `site:jobs.ashbyhq.com` / `site:job-boards.greenhouse.io` in a search engine that answers you.
- Aggregators that expose JSON: `remoteok.com/api`, `remotive.com/api/remote-jobs`,
  `himalayas.app/jobs/api`, `arbeitnow.com/api/job-board-api`, `weworkremotely.com/remote-jobs.rss`.
  Small (hundreds), but they surface companies not in the token dataset — harvest **company names**
  from them, then find each company's board.

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
TITLE_OUT = r'devops|sre|site reliab|platform|infrastructur|security|release|manager|director|sales|recruit'
GEO_OUT   = r'\b(us|u\.s\.|united states|usa|canada|emea only|uk only)\b.{0,40}(only|based|resident|eligib)'
GEO_IN    = r'georgia|tbilisi|worldwide|anywhere|global|asia|any timezone'
```

Then read the body. A body that never names a country, and never names a timezone band narrower
than the candidate's, is the good case.

## What a sweep actually yields

From ~130,000 postings, after filtering for one specific candidate (backend/fullstack, Tbilisi,
worldwide remote, $100k), roughly **60–120 applyable roles**. That is the real size of the
worldwide-remote market at a given moment — not thousands. Plan for depth per application, not volume.
