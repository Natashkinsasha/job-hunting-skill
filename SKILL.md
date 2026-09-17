---
name: job-hunting
description: Use when asked to find jobs, apply to jobs, or run a job search on someone's behalf — including "apply for me", "find me vacancies", "submit these job links", or resuming a long-running search across many applications.
---

# Job Hunting

Run a job search end to end: intake a résumé, source openings, filter them, fill application forms, and keep an auditable log. Optimised for volume without lying.

**Core principle: the candidate's truth is the hard constraint.** Everything else — speed, volume, clever sourcing — is negotiable. A form you cannot answer truthfully is a form you stop and ask about.

## Run autonomously

The candidate hired you to do this instead of doing it themselves. Applying to 100 roles means ~100 decisions; if each one becomes a question, you have saved them nothing.

**Default to acting.** Source, filter, fill, submit, log, move to the next one. Do not ask permission per application, do not present a shortlist for approval, do not report after each submission. Work through the queue and report in batches.

**Batch every question.** When you genuinely need input, collect the open questions and ask them together at a natural break, then keep working on everything that doesn't depend on the answer. A blocked application goes on a blocked list; it does not stop the run.

**Only these stop you** (the full list is in "Red flags" below): no truthful answer exists, the employer bans AI assistance, or the candidate's stated hard limits are triggered. Everything else — an ambiguous title, a location you have to reason about, a cover letter to write — you decide.

**Session breaks are normal.** The candidate will go to sleep mid-run. Keep going, and make the log good enough that the next session can resume from it cold.

## Workflow

0. **Resume** — read `applied-list.md` first. It is the only record of what has already been sent;
   everything below filters against it. A fresh session that skips this re-applies to the same jobs.
1. **Intake** — read the résumé, build `profile.md`, ask for what's missing (see below).
2. **Source** — get postings. See `references/sourcing.md`.
3. **Filter** — drop anything already in `applied-list.md`, then cut before opening any form.
   See "Filter before you open" below.
4. **Apply** — per-ATS mechanics in `references/ats-playbook.md`.
5. **Log** — every outcome, including rejections with reasons. Write the row as each one lands.

## Step 1: Intake

Read the résumé, then ask **once, as a single batch**, for what forms demand and résumés never contain. Don't dribble these out one at a time.

| Field | Why it's needed |
|---|---|
| Phone, city, country, timezone | Every form |
| Citizenship + residence + work-authorisation status | Gating question on most forms |
| Legal form (employee / sole proprietor / company) | Contractor arrangements |
| Salary expectation + currency + period | Required, often as a number field |
| Notice period | Required |
| LinkedIn, GitHub, portfolio, X | Link fields |
| Gender, race/ethnicity, veteran status | EEO sections (voluntary, but asked constantly) |
| Pronouns | Increasingly required |
| Willing to relocate? Which countries? | Narrows geography |
| Hard limits | e.g. "no video interviews", "no client-facing roles" |
| Reason for leaving — answer or skip? | If they say skip, skip when optional |
| Street address + postcode | Some forms require it; **never invent one without asking** |

Write answers to `profile.md` and re-read it at the start of every session. Add to it whenever the candidate reveals a new constraint mid-run.

**Ask for email access early.** Greenhouse and others gate submission behind an emailed code. Say plainly: "log into your mail in the browser I'm driving, and I'll pull verification codes myself." Without it, every code costs a round-trip to the candidate.

## Step 2: Filter before you open

Opening a form costs ~10 minutes. Filtering costs seconds. Check in this order and stop at the first failure:

1. **Title** — is it the role type they want? Reject infra/QA/sales/design titles unless asked for.
2. **Stack** — fetch the posting body and grep for their actual stack. A posting that never names their language is not their job, however good the title looks.
3. **Geography** — does the location admit where they live?
4. **Gates inside the form** — see below.

Roughly half of postings that look perfect by title and location fail on stack or a hidden gate.

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
- **Transcontinental and ambiguous geography**: answering "yes" to a defensible reading is fine *only if* the exact city and timezone appear in a free-text field on the same form.
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

**Before every application, and before sourcing, load `applied-list.md` and build two sets from it:**

```bash
grep -oE 'https?://[^ |]+' applied-list.md | sed 's#/$##' | sort -u > applied_urls.txt   # exact postings
# and the ATS org tokens inside those URLs -> applied_orgs.txt   (ashby:railway, greenhouse/okx, …)
```

- **URL already in the set → skip it.** No re-reading the posting, no "maybe it changed".
- **Org already in the set → still allowed, but space it out.** Several roles at one company are
  normal and often smart; several *in a row on one Ashby board* trip the spam filter. Interleave
  other employers between them.
- Filter on these sets *before* fetching bodies — deduplication is free, fetching is not.

Write the row the moment a submission confirms, not at the end of the batch. A crash, a context
limit or a closed laptop between submit and log turns a sent application into an invisible one,
and the next session re-sends it.

## Red flags — stop and ask

- A required field has no truthful option
- The employer bans AI assistance
- A video or AI interview is required
- The form wants an address, ID number, or salary history you weren't given
- You're about to answer "yes" to a work-authorisation question you can't verify

## References

- `references/sourcing.md` — every channel with measured yield: ATS endpoints, aggregator feeds, what's account-gated, what's dead
- `references/ats-playbook.md` — per-ATS form mechanics and the bugs that silently eat submissions
- `references/answering.md` — cover letters, essay questions, geography and salary wording, AI-ban forms
- `data/*_companies.json` — ~27,000 board tokens, shipped with the skill so a sweep needs no third party
- `scripts/sweep_boards.py` — sweep every Ashby/Greenhouse/Lever board (`--refresh` to merge newer tokens)
- `scripts/fetch_postings.py` — resolve arbitrary job links to title/location/body
- `scripts/discover_boards.py` — find boards no token list has, by probing slugified company names

All scripts are stdlib-only Python 3.
