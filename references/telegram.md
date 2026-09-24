# Telegram job channels

Telegram looks like a huge untapped channel and mostly isn't. This file exists so a later session
can decide in one minute whether to spend an hour here, and — if it does — drive the client without
rediscovering its quirks.

## Measured yield before you start

One candidate (senior full-stack, remote-only, floor $7k/month), five sweeps in one session:
**99 live channels found and all 99 read, 1 application sent, 2 DM-only postings, 1 ATS catalogue**.
An earlier partial pass of the same list (8 feeds read, chosen by name and size) found
**1 vacancy that matched the stack** — and that one was posted at
Middle+ level with no salary range and a DM-only application. The same evening, the no-account
channels (Wellfound, YC, an ATS sweep) produced **16 sent applications**.

So: Telegram is a background channel. Run it when the candidate asks for it, time-box it, and do not
let it displace the ATS sweep. Say the ratio out loud rather than quietly producing nothing.

## Access

`https://web.telegram.org/a/` — login is a **QR code the candidate scans from their phone**
(Telegram → Settings → Devices → Add Device). You cannot do this step for them. The session persists
across browser restarts, so it is a one-time cost.

Everything below assumes their account. That has a consequence worth stating to them: you are reading
their personal Telegram, and their private chats are visible in the left column of every screenshot
you take. Keep screenshots to the message pane when you can.

## Driving the client

- **Search box is `#telegram-search-input`. Click it before typing.** Typing into it unfocused eats
  the first characters — measured: `remotegeekjob` arrived as `motegeekjob` and returned "No Results",
  which reads exactly like "channel doesn't exist".
- **For batches, set the value programmatically** (`HTMLInputElement.prototype.value` setter +
  `input` event) — React picks it up and it's much faster than typing four queries by hand.
- **Short queries only.** Long multi-word strings silently fall back to the candidate's own chat list
  instead of Global Search. Measured failures: `Вакансии JavaScript, Node.js, TypeScript`,
  `Golang Jobs Вакансии`, `Remote_Software_Developer_Jobs` (underscored handles fail too).
  The same searches work as `golang вакансии`, `Remote Software Developer Jobs`, `crypto вакансии`.
- **Throttling is real.** Sleep ~1.2 s after clearing and ~3 s after setting the query; several rapid
  searches in a row start returning empty results that are indistinguishable from "nothing found".
- **Opening a channel:** click the result's `h3`. A channel and its bot often share a title, so
  `h3:has-text("…")` hits strict-mode violations — take `.first()`, and verify by the page title.
- **Search results are `div.ListItem.chat-item-clickable`, not `<button>`** — the accessibility tree
  reports them as buttons, so `querySelectorAll('button')` finds nothing. Match on the result's
  `.handle` (it renders as `handle` + subscriber count with no `@` and no comma in `innerText`, e.g.
  `DeJob_Global16,573 subscribers`), and dispatch pointerdown/mousedown/pointerup/mouseup/click on
  its `.ListItem-button` child — a bare `.click()` on the wrapper does not open the chat.
  Guard the handle match with `(?![A-Za-z0-9_])` or `@foo` also matches `@foo_group`, its chat.
- **Wrap the whole search→click→read cycle in one `window.__tgRead(handle)` function** defined once,
  then call it in batches of five or six per evaluate. Whole-list sweeps become minutes, not hours.
- **Reading a feed:** `#MiddleColumn .message-content-wrapper`. Every message appears **twice** in the
  DOM — dedupe before counting. Don't slice the text of a candidate posting; pull the full `innerText`
  of the matching messages, because the stack list and the salary live at the bottom of a long post.

## Read the feed. Do not triage by name and subscriber count.

The tempting shortcut is to catalogue a hundred channels from search results and then read only
the ones whose name and size look promising. It was tried, and measured against a full read of
all 99: **the shortcut was wrong about one channel in four, in both directions.**

- It discarded **@nodejs_vakansii (708 subscribers)** — the smallest channel on the list — which
  was carrying a $72–90k/yr fully-remote role paid through Deel, with a timezone band (GMT-1 to
  GMT+8) that actually included the candidate.
- It kept **@golangjob**, **@it_jobs_remote**, **@nrgjobs**, **@remoters**, **@revacancy_raw** and
  six others that turn out to be dead — last posts from 2022, 2023 and 2024.
- It dismissed **@careers_crypto** as a duplicate of a sibling channel; it was cross-posting the
  same recruiter but also carried a second vacancy that existed nowhere else in the sweep.

Reading a feed costs 2–4 minutes with the loop below. Guessing costs the one posting that matched.
If the candidate has asked for the channel to be worked, work all of it.

## Always capture the date of the newest message

`#MiddleColumn .sticky-date` — take the **last** one. Without it you will read the bottom of a dead
channel and report its contents as current. Measured: `@golangjob` presents a *Senior Backend
(Golang), Singapore, remote, $7000–10000/month* post at the foot of its feed. It is from **February
2023**. Everything above it in the same viewport looks equally fresh and is equally stale.

A channel whose newest message is older than ~2 months is a finding in itself — record the date and
move on.

## Channel taxonomy — what each class is actually worth

1. **Aggregator relays.** Post the same feed you can read over HTTP, wrapped in "Unlock 33,000 hidden
   remote jobs". Measured: `@Remote_Software_Developer_Jobs` relays Remotive, `@evacuatejobs` relays
   its own remocate.app, `@cryptojobslist` relays its own site. Postings are country-tied
   (USA / Germany / LATAM). Read the source site instead — it has filters.
2. **Marketing and arbitrage.** The entire Russian-language iGaming cluster (`@iGaming_work`,
   `@opento_igaming`, `@talentgrator`) is media buyers, affiliate managers, CRM and sales. Engineering
   appears once in a hundred posts and tends to be AppSec. iGaming *companies* hire engineers through
   their own ATS — go there.
3. **Spam feeds.** Some large stack channels are ad dumps. Measured: a 12,600-subscriber Go channel
   whose visible history was repeated military-recruitment ads plus one "Backend Tech Lead (Go),
   salary negotiable" with no company name.
4. **Structured recruiter channels — the only class worth reading.** Hashtag-tagged posts
   (`#Вакансия #Developer #Fullstack #Remote`), full stack list, level, conditions and a contact.
   Measured example: `@workingincrypto` (Blockchain Hunter). This is where the single matching
   vacancy came from.
5. **Geography channels.** Tbilisi/Batumi/Cyprus boards are general labour — couriers, waiters,
   sales. The IT-specific ones are small (`@it_jobs_cyprus`, `@it_jobs_armenia`, ~2k each).

## Rules

- **A DM to a recruiter is outward-facing.** Many posts have no form, only `@handle`. Draft the
  message, show it to the candidate, wait for approval — same rule as booking an interview. Never
  send from their account on your own initiative.
- **Posts that link to LinkedIn are blocked** by "Never touch LinkedIn" in `SKILL.md`. Find the role
  on the company's own ATS; if it exists nowhere else, log it as blocked with the reason.
- **Deduplicate hard.** One vacancy is cross-posted across five sibling channels — the recruiter
  networks list their other channels in the post footer. Dedupe by company + title, not by channel.
- **Record subscriber counts with the date.** They age, and a later session needs to know whether
  "2,892 subscribers" was measured or guessed.
- **Never claim a handle from memory.** Handles churn. Verify each one through search and write down
  what the search returned; a guessed `@handle` in a report is worse than no list.

## What a full sweep of 99 channels actually produced

One candidate, one evening, every channel read: **1 application sent through a real ATS (Zerion,
found in `@job_web3`), 2 postings that require a DM to a recruiter, 1 catalogue of direct ATS links.**
The same evening's no-account channels produced 20 applications. So the conclusion about relative
yield survives the full read — but "the rest aren't worth reading" did not, and should not be
asserted without having read them.

## Where the signal is, for an English-market senior engineer

- `@remotegeekjob` — the only channel found with a genuine English-language engineering flow
  (Senior Go, Go/Networking, Applied AI roles at real companies).
- `@workingincrypto` and `@careers_crypto` — structured crypto/Web3 recruiting, full stack details.
- For the Russian-speaking market specifically: **getmatch** (`@g_job` + its bot) is the only source
  with moderation and a mandatory salary range — but it serves the RU market with relocation, so it
  collides with a "no residency requirement" constraint.
- `@job_web3` — English crypto/Web3 postings with **direct Ashby and Lever links**, remote scope
  stated per role ("work from wherever you have work authorization", "fully remote, team worldwide").
  The single best channel found across the whole sweep.
- `@nodejs_vakansii` (tiny) and `@notificaJobs_nodeJS` — structured Node/TypeScript postings that
  quote salary and timezone bands. Small channels, real content.
- `@Jobs_global_startups` — the only aggregator that links to companies' own ATS rather than its own
  site. Roughly half its posts are LinkedIn links and therefore blocked.
