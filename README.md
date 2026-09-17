# job-hunting

An [Agent Skill](https://agentskills.io/specification) that lets a coding agent run a job search
end to end on your behalf: intake your résumé, source openings straight from applicant-tracking
systems, filter them, fill in the application forms, and keep an auditable log of everything it did.

It is not tied to a role, a stack, or a country. You drop in a résumé; the agent asks once for the
handful of things forms demand and résumés never contain, and then works through the queue.

## Why

Job boards are a stale, deduplicated-badly slice of the market and most of them fight scraping.
The applicant-tracking systems underneath them — Ashby, Greenhouse, Lever and friends — expose
**public, unauthenticated JSON** listing every open role at every company that uses them. A full
sweep is ~16,000 boards and ~130,000 postings in about twenty minutes.

Everything in here was written from actually doing it: ~150 applications over two days, including
the submissions that silently failed and why.

## Install

Skills live in your agent's skills directory — `~/.claude/skills/` for Claude Code,
`~/.agents/skills/` works as a cross-runtime alias for Codex, Copilot CLI and Gemini CLI.

```sh
git clone https://github.com/Natashkinsasha/job-hunting-skill ~/.claude/skills/job-hunting
```

Then just ask: *"find me remote backend roles and apply"*.

## What's in it

| File | Contents |
|---|---|
| `SKILL.md` | The workflow: intake, autonomy rules, filtering order, hidden gates, honesty rules, logging |
| `references/sourcing.md` | Every ATS endpoint, where to get the org tokens, and measured verdicts on which channels are worth running |
| `references/ats-playbook.md` | Per-ATS form mechanics and the bugs that silently eat submissions |
| `scripts/sweep_boards.py` | Sweep every Ashby/Greenhouse/Lever board → one row per posting |
| `scripts/fetch_postings.py` | Resolve arbitrary job links to title / location / body text |

Both scripts are stdlib-only Python 3 — no dependencies.

```sh
python3 scripts/sweep_boards.py --out rows.json
python3 scripts/fetch_postings.py links.txt --out postings.json
```

## A few things it knows that cost a failed submission to learn

- On **Ashby**, setting an input's `.value` from JavaScript does not reach React state. The form
  looks filled and reports "Missing entry for required field". You have to actually type.
- On **Lever**, the email input carries a `pattern` attribute whose regex is invalid in current
  browsers. `checkValidity()` throws, submit silently does nothing, and **no error appears**.
- **Greenhouse** answering HTTP 428 means it wants an emailed verification code — which is why the
  skill asks for mail access up front rather than round-tripping to you for every code.
- "Remote" on a posting nearly always means "remote *within* the country we can employ you in".
  The only geography signal that holds up is your country appearing in the list of hiring locations.

## Honesty

The skill's hard constraint is that it never invents anything about you — no technology you haven't
used, no year counts, no address, no work-authorisation status. Where a required field has no
truthful answer, it stops and asks instead of picking the least-bad option. Where an employer bans
AI-written applications, it hands the application back to you with a facts sheet.

## License

MIT
