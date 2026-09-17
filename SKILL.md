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

1. **Intake** — read the résumé, build `profile.md`, ask for what's missing (see below).
2. **Source** — get postings. See `references/sourcing.md`.
3. **Filter** — cut before opening any form. See "Filter before you open" below.
4. **Apply** — per-ATS mechanics in `references/ats-playbook.md`.
5. **Log** — every outcome, including rejections with reasons.

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
- Never restate the job description back at them.

## Logging

Two files, appended as you go:

- `applied-list.md` — one row per posting: number, company, role, geography, URL, status. Rejections get a **reason**: "❌ Java/Spring required", not "❌ not a fit".
- `session-log.md` — sourcing numbers, new gotchas, blocked applications and what unblocks them.

The log is how a resumed session knows what's already been tried. Never skip it to save time.

## Red flags — stop and ask

- A required field has no truthful option
- The employer bans AI assistance
- A video or AI interview is required
- The form wants an address, ID number, or salary history you weren't given
- You're about to answer "yes" to a work-authorisation question you can't verify

## References

- `references/sourcing.md` — where postings come from, with API endpoints and what's worthless
- `references/ats-playbook.md` — per-ATS form mechanics and the bugs that silently eat submissions
- `scripts/sweep_boards.py` — bulk board sweep
- `scripts/fetch_postings.py` — resolve arbitrary job links to title/location/body
