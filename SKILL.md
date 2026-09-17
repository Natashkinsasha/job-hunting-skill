---
name: job-hunting
description: Use when asked to find jobs, apply to jobs, or run a job search on someone's behalf — including "apply for me", "find me vacancies", "submit these job links", or resuming a long-running search across many applications.
---

# Job Hunting

Run a job search end to end: intake a résumé, source openings, filter them, fill application forms, and keep an auditable log. Optimised for volume without lying.

**Core principle: the candidate's truth is the hard constraint.** Everything else — speed, volume, clever sourcing — is negotiable. A form you cannot answer truthfully is a form you stop and ask about.

## What you need before you start

**A driveable browser — in practice the Playwright MCP server — is a hard requirement for applying.**
Sourcing and filtering are plain HTTP and need nothing but `curl` and the scripts here. Submitting is
not: every ATS form in `references/ats-playbook.md` is a React app that rejects text you inject, so you
need to click, type character by character, read back what the widget actually committed, attach a file
through a real file chooser, and watch the network response. `curl`-ing a form POST does not work and is
not worth attempting. Without a browser, run the search and hand the candidate a ranked queue of links.

Three things to set up on day one, each of which has cost a wasted hour: copy the résumé into the
working directory (the file chooser is sandboxed and can't reach `~/Documents`); have the candidate log
into their mail in that browser (Greenhouse gates submission behind an emailed code — `references/email.md`);
and never navigate away from a half-filled form while waiting, it loses its state. Details in
`references/ats-playbook.md`.

## Run autonomously

The candidate hired you to do this instead of doing it themselves. Applying to 100 roles means ~100 decisions; if each one becomes a question, you have saved them nothing.

**Default to acting.** Source, filter, fill, submit, log, move to the next one. Do not ask permission per application, do not present a shortlist for approval, do not report after each submission. Work through the queue and report in batches.

**Batch every question.** When you genuinely need input, collect the open questions and ask them together at a natural break, then keep working on everything that doesn't depend on the answer. A blocked application goes on a blocked list; it does not stop the run.

**Only the "Red flags" list below stops you.** Everything else — an ambiguous title, a location you have to reason about, a cover letter to write — you decide.

**Session breaks are normal.** The candidate will go to sleep mid-run. Keep going, and make the log good enough that the next session can resume from it cold.

## Workflow

0. **If resuming** — read `applied-list.md` and `profile.md` first, then sweep the mail. The log is the
   only record of what has already been sent; a session that skips it re-applies to the same jobs. And
   replies have deadlines while postings don't — a scheduling link that expired while you swept 16,000
   boards is a worse outcome than ten applications not sent. See `references/after-submitting.md`.
1. **Intake** — fill `templates/profile.md`: what we're looking for, then who the candidate is.
2. **Source** — `scripts/sweep_boards.py`. Channels and measured yields in `references/sourcing.md`.
3. **Filter** — `scripts/filter_postings.py` on titles and locations, fetch bodies for the survivors,
   filter again. Then check the form itself for gates before filling it.
4. **Apply** — per-ATS mechanics in `references/ats-playbook.md`, wording in `references/answering.md`.
5. **Log** — every outcome, including rejections with reasons. Write the row as each one lands.

```sh
python3 scripts/sweep_boards.py --out rows.json
python3 scripts/filter_postings.py rows.json --profile profile.md --applied applied-list.md --out pass1.json
python3 -c "import json;print('\n'.join(r['url'] for r in json.load(open('pass1.json'))))" > links.txt
python3 scripts/fetch_postings.py links.txt --out bodies.json
python3 scripts/filter_postings.py rows.json --profile profile.md --applied applied-list.md \
        --bodies bodies.json --out shortlist.json --rejects rejects.json
```

## Step 1: Intake

Copy `templates/profile.md` into the working directory and fill it. It has two halves and you need both before applying to anything.

### Half one — what we're looking for

Ask this **first**. Every hour of sourcing against the wrong criteria is wasted, and these constraints are discovered painfully if you don't ask: in one run "remote only", "no US-timezone overlap", "not DevOps", "no client-facing roles", "exclude this specific employer" and "no video interviews" each surfaced *after* applications had already gone out to roles that violated them.

Roles and titles wanted · titles refused · stack · stacks they won't work in · remote / hybrid / on-site · acceptable timezones · countries they can actually be hired in · employers to exclude outright · salary floor.

This half lives in a fenced ```criteria``` block that `filter_postings.py` parses directly, so it is both the brief and the filter. One trap worth repeating: **never put the word `remote` in `geo_in`** — several boards append the workplace type to the location string, so it matches everything and silently disables the geography check.

### Half two — who the candidate is

Ask **once, as a single batch**, for what forms demand and résumés never contain. Don't dribble these out one at a time.

Phone and city · citizenship, residence and work authorisation · legal form (employee / sole proprietor / company) · salary with currency and period · notice period · links · EEO answers · pronouns · relocation · hard limits · whether to answer "reason for leaving" · street address (**never invent one without asking**). The full questionnaire, with the facts worth collecting once for essays, is the second half of `templates/profile.md`.

Write answers to `profile.md` and re-read it at the start of every session. Its last section is append-only: every constraint the candidate reveals mid-run goes there, dated, because that is what a resumed session reads instead of asking the same question again.

**The résumé itself.** Get the actual file and attach that same file everywhere. Don't rewrite it per application — a tailored cover letter earns its time, a tailored CV doesn't, and two CVs that disagree become a problem in an interview. Name it `<Firstname>_<Lastname>_CV.pdf`; some ATS show the filename to the reviewer. If they have no PDF, ask for one rather than generating a document that claims to be their CV.

## Step 2: Filter before you open

Opening a form costs ~10 minutes. Filtering costs seconds. Check in this order and stop at the first failure:

1. **Title** — is it the role type they want? Reject infra/QA/sales/design titles unless asked for.
2. **Geography** — does the location admit where they live?
3. **Stack** — fetch the posting body and grep for their actual stack. A posting that never names their language is not their job, however good the title looks.
4. **Gates inside the form** — see below.

Steps 1–3 are `scripts/filter_postings.py`, run twice: once on the sweep (title and location only, which removes ~99% of a 130k corpus) and again with `--bodies` once you've fetched the survivors. It writes every rejection **with its reason** — a rejection log you can't audit is how a good role gets dropped for the wrong reason and nobody notices.

Two things it gets right that a hand-rolled filter gets wrong. It **dedups after the geography checks, never before**: one role is often posted once per office plus once as remote, and deduping first keeps the New York row and throws away "Remote, Worldwide" for the same job. And it **keeps postings whose body came back empty** — an empty body is a fetch failure, not a posting without a description. Measured once: 31 of 244 links came back empty and every single one was a fetch problem.

Roughly half of postings that look perfect by title and location still fail on stack or a hidden gate.

## Step 3: Hidden gates

**The disqualifying question is usually not in the job description. It is in the form.** Load the form and scan its field labels *before* writing any answers. Recurring gates:

- "Do you have the legal right to work in \<country\>?"
- "Are you located in \<region\>? We hire only there."
- "This role requires overlap with \<US timezone\>. Are you comfortable?"
- "How many years with \<technology\>?" — with **no zero option**
- A video interview or AI-interview step disclosed only in a consent checkbox
- Compensation as a bare number field with no stated period

When a required field has **no truthful answer**, stop. Report the exact wording to the candidate and let them decide. Do not pick the least-bad option on their behalf.

## Honesty rules

These are not style preferences. Breaking them produces a candidate who gets caught in an interview.

- **Never claim a technology, year count, or credential that isn't in `profile.md`.** If the minimum option overstates them, that's a gate — ask.
- **State gaps plainly in free-text answers.** "My Python is working-level, not primary" costs nothing and buys credibility.
- **Never invent personal data** — address, employer, education, immigration status.
- **Ambiguous geography** ("are you in a European timezone?"): answering "yes" to a defensible reading is fine *only if* the exact city and timezone go into a free-text field on the same form. A question that states its range or its auto-reject ("resident in GMT+0…GMT+3?") is a gate, not a puzzle — stop.
- If the employer forbids AI-written applications, **stop and hand it to the candidate** with a facts sheet. Don't paraphrase your way around it.

## Writing answers

Free-text answers are where applications are won. Aim for specific, verifiable, and unflattering-where-true.

- Lead with the concrete thing that matches their posting's hardest sentence.
- Use numbers from the candidate's real work.
- Name one real limitation. It makes everything else credible.
- State location, timezone in *their* frame, work-authorisation reality and salary as plain facts — even unprompted.
- Never restate the job description back at them.

Draft cover letters as files under `cover-letters/`, never in the browser: some "Cover Letter" fields are file inputs, and typing into one opens a file dialog per keystroke.

Full guidance — letter structure, essay questions, "years of X" with no zero option, geography wording, salary, AI-ban forms: `references/answering.md`.

## Logging

Two files, appended as you go:

- `applied-list.md` — one row per posting: number, company, role, geography, URL, status. Rejections get a **reason**: "❌ Java/Spring required", not "❌ not a fit".
- `session-log.md` — sourcing numbers, new gotchas, blocked applications and what unblocks them.

The log is how a resumed session knows what's already been tried. Never skip it to save time.

### Never apply to the same posting twice

A duplicate application is not a harmless retry. It reaches a human as evidence the candidate
is not paying attention, some ATSes treat it as spam (Ashby blocks the whole board after a few),
and one employer — RevenueCat — bars re-application to the same role for **365 days**. You cannot
un-send it.

So the log is not documentation, it is the deduplication index, and it is the only memory you have:
a new session starts with none of the last one's context.

**Before sourcing and before every application, check the log.** `filter_postings.py --applied
applied-list.md` matches on **company + role title**, not URL — the same role is reachable at several
URLs and boards rewrite them — and compares company names by containment, because the log holds a
human name ("Holepunch (Tether)") while the sweep holds an ATS token ("holepunch").

- **Already in the log → skip it.** No re-reading the posting, no "maybe it changed".
- **Same company, different role → allowed, but space it out.** Several roles at one company are
  normal and often smart; several *in a row on one Ashby board* trip the spam filter. Interleave
  other employers between them.
- Dedup *before* fetching bodies — deduplication is free, fetching is not.

Write the row the moment a submission confirms, not at the end of the batch. A crash, a context
limit or a closed laptop between submit and log turns a sent application into an invisible one,
and the next session re-sends it.

## Red flags — stop and ask

This is the complete list. Nothing else stops the run.

- A required field has no truthful option — including an address, ID number or salary history you weren't given
- The employer bans AI assistance
- A video or AI interview is required, or any other stated hard limit is triggered
- You're about to answer "yes" to a work-authorisation or residency question you can't verify
- Anything outward-facing in the candidate's name *beyond the application itself*: sending an email, booking an interview slot, accepting a take-home. Draft it, show it, wait.

## References

- `references/sourcing.md` — every channel with measured yield: ATS endpoints, aggregator feeds, what's account-gated, what's dead
- `references/ats-playbook.md` — per-ATS form mechanics and the bugs that silently eat submissions
- `references/answering.md` — cover letters, essay questions, geography and salary wording, AI-ban forms
- `references/email.md` — verification codes, applying by email, driving Gmail, and the privacy line
- `references/after-submitting.md` — replies, statuses, the blocked pile, and what to do when the channel runs out
- `templates/profile.md` — the intake questionnaire and the criteria block the filter reads
- `data/*_companies.json` — ~27,000 board tokens, shipped with the skill so a sweep needs no third party
- `scripts/sweep_boards.py` — sweep every Ashby/Greenhouse/Lever board (`--refresh` to merge newer tokens)
- `scripts/filter_postings.py` — cut a sweep to a shortlist using the profile, with audited rejections
- `scripts/fetch_postings.py` — resolve arbitrary job links to title/location/body
- `scripts/discover_boards.py` — find boards no token list has, by probing slugified company names

All scripts are stdlib-only Python 3.
