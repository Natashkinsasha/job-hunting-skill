# Login-gated sites: Wellfound, YC, aggregators, contractor marketplaces

Sites that need an account are not a separate kind of work — they are the same applications behind one
human step. This file is the measured mechanics of that step, and of each platform's profile, so a new
session doesn't rediscover them.

## The division of labour that works

You cannot register for someone. But "the candidate registers" is much smaller than it sounds if you
split it correctly:

**You do:** open the exact sign-up URL, pre-fill every field that is a *fact* — name, email, phone with
the right country code, city, links, résumé upload, country of residence.

**They do, and only they:** type a password, tick a legal-consent checkbox ("I agree to the Terms"),
press the final *Create account*, and complete any OAuth consent screen that creates the account.

Then **you do the rest**: the whole candidate profile, preferences, and every application after it.

Why this exact line: a password and a terms checkbox are the two things that are legally theirs, and an
OAuth consent is the moment the account comes into existence in their name. Everything else is
transcription, and transcription is what you are for. Measured: filling a Wellfound/YC/Lemon.io sign-up
form to the last field takes ~2 minutes; the candidate's remaining step takes ~10 seconds.

Announce it in that shape — "form is filled, you need the password and the checkbox" — rather than
handing over a blank page and a sentence about what to type.

## Do not silently change profile-level settings

Application dialogs on these platforms sometimes edit the *profile*, not just this application. The
one that has actually bitten: **YC's apply modal pre-checks "This role doesn't match your location
preferences. Check here if you're open to relocating — we'll update your profile"**. Checked by
default, on every application, and it rewrites the answer the candidate gave you.

Rule: before sending anything on a platform, read the checkboxes in the dialog, and uncheck anything
that asserts a preference the candidate didn't state. A profile that drifts is worse than a missing
application — it silently misrepresents them to every future search.

## Résumé parsers lie — read back every field they filled

Three of these platforms offer "upload your CV and we'll fill the profile". It saves real time and it
gets things wrong in ways that are invisible unless you read the result. Measured on one CV, one night:

- **Company name taken from a parenthetical.** A CV line shaped `<Employer> | Full-stack Engineer /
  AI Systems (Node.js, React)` became employer **"Node.js, React"**.
- **Invented education.** A mention of MCP in the skills section became a degree: school "MCP", type
  "Certification".
- **Truncated institution name** — a word dropped from the middle of the university's name, leaving a
  school that does not exist.
- **Side projects glued onto the last job.** The CV's SIDE PROJECTS block landed inside the 2017–2018
  employer's description, which reads as a false claim about that job.

So: after any parse, dump every field (`[...document.querySelectorAll('input,textarea')].map(e => e.value)`)
and compare against the CV before pressing Continue. Fixing four fields costs a minute; a fabricated
degree in a profile recruiters read is not recoverable by explanation.

## Platform notes (measured 17.09.2026)

### Wellfound (wellfound.com)
- Sign-in: Google OAuth. `/login` may bounce straight into Google if a session exists.
- Profile is five tabs: Profile, Resume/CV, Preferences, Culture, AI Interview. Only the first three matter.
- Fields are `react-select` widgets: focus the input, press ArrowDown to open, then click the option id
  (`#react-select-form-input--<field>-option-N`). Typing + Enter does **not** select.
- Work history: company is a Downshift combobox over their company DB; if the employer isn't there,
  "Create <name>" adds it and then asks for a Company URL.
- Date fields accept typing `MM/YYYY` directly — much faster than clicking through the year arrows.
- **The job search hides postings that don't accept applications from the candidate's city** ("Hiding
  jobs that do not accept applications from your location: <city>"). That is the best geography filter
  on any platform here — set the profile location first, then search.
- Filter "Hide jobs which require me to apply on the company's website" leaves only one-click applies,
  which is also what keeps you out of duplicate-application territory with your ATS log.
- Applying: `Apply now` → modal with "What interests you about working for this company?" Some employers
  add custom questions (last name, visa sponsorship radio, free-text) — they appear as
  `customQuestionAnswers[<id>][answer]`.
- After every send it offers a **15-minute AI video interview** that ranks you higher with recruiters.
  If the candidate's limits exclude video, skip it and tell them it exists — it's one recording reused
  across all applications, so it's their call, not yours.

### Y Combinator — Work at a Startup (workatastartup.com)
- Sign-up is `account.ycombinator.com`: first/last name, email, **username**, password. No OAuth, so the
  candidate must be there for the password.
- Profile is seven steps: Personal Info → Location → Role → Experience → Skills → Career → Share.
- Location step asks the two US questions separately: *authorized to work in the US* and *require
  sponsorship*. For a non-US candidate that's No / Yes.
- Experience step = résumé upload + parse. See the parser warnings above; this is where they were measured.
- Skills: pick up to 10, each gets Beginner/Intermediate/Advanced. Type the exact product name — "Golang"
  matches nothing, "Go" does; the Enter key selects the highlighted option, so check the menu before pressing it.
- Career step: company-size grid, equity importance, and a salary floor with a number field.
- Share step is the one founders actually read: a one-line self description, "what are you looking
  for / what would you avoid", and a proud project. Put the constraints (timezone, contractor vs payroll,
  remote-only) in the "avoid" field — it saves a call on every mismatch.
- Directory filters live in the URL: `?remote=yes&role=eng&usVisaNotRequired=true`. Measured with all
  three: 113 companies, of which maybe a dozen are truly non-US-remote — the catalogue is SF-heavy.
- Applying = a direct message to a named founder, not a form. Write to the person, sign it, and keep
  their stated "how to apply" list in order if they gave one.
- **Uncheck the relocation box** (see above) before Send.

### Aggregators with a match engine (e.g. talent.monopoly-gold.com)
- Google OAuth, then a three-step onboarding: CV upload → four parsed profile blocks → three free-text
  filters ("what are you looking for", "what to cut immediately", "work format", "salary").
- The "what to cut" field is where the candidate's dealbreakers belong verbatim: office/hybrid, required
  residency, US timezones, excluded role types, excluded stacks. It is the filter, not a formality.
- First match pass takes 5–15 minutes over a few hundred postings; come back to it rather than waiting.
- These aggregate **Telegram channels and boards**, so a large share of cards resolve to `lnkd.in`,
  `t.me` or a reposted listing. A card is a *lead*, not an application: find the role on the company's
  own ATS and apply there, and log it with the ATS URL so dedup keeps working.
- Their per-card scoring is worth reading — it flagged, correctly, that a Revolut role conflicts with a
  B2B-contractor candidate because they hire employees into hubs.

### Contractor marketplaces (Lemon.io, Proxify, A.Team, Toptal, Braintrust)
- Different economics from everything else here: one profile plus one vetting interview, then a
  *continuous* project stream at hourly rates. They are the only channel that keeps producing after a
  sweep is exhausted, so raise them early even though they're slow to start.
- Lemon.io sign-up is `me.lemon.io/escape-the-matrix` (the `/apply/` path 404s): name, email, country of
  residence, **LinkedIn URL (required field)**, phone, terms checkbox.
- Country pickers are MUI `<li>` menus, not text inputs — clicking the visible field opens a list you
  must click an item in; typing goes into whatever input is underneath and lands in the wrong field.
  Always read back what each field holds before submitting.
- Phone inputs that prefill a country code (`+31`) treat it as editable text: typing the national number
  after it yields nonsense like `5995 99692814`. Select-all, delete, then type the full `+995…` number.
- The vetting interview and any skills test are the candidate's, not yours. Fill the profile, then stop.

### Telegram (web.telegram.org)
- Login is a **QR code scanned from the candidate's phone** (Telegram → Settings → Devices → Add Device) —
  the one sign-in step where you cannot even pre-fill a field. The session then survives restarts.
- Unlike every other platform here, you end up inside their *personal* messenger: their private chats
  sit in the left column of every screenshot. Keep captures to the message pane.
- Mechanics, channel taxonomy and measured yield live in `references/telegram.md`. Short version:
  most channels relay aggregators you can read over HTTP, and a recruiter DM is an outward-facing
  message that needs the candidate's approval — it is not an application form.

### Excluded by rule, not by yield
- **LinkedIn** — prohibited outright, see "Never touch LinkedIn" in `SKILL.md`.
- Anything the candidate names (one search excluded all Ukrainian services; another excluded a specific
  former employer). Record it in `profile.md` the moment they say it, because the next session will
  otherwise walk straight back into it.

## Record which accounts exist

Write every platform account into `profile.md` (or a line in `session-log.md`) as it is created:
platform, login method, and what state the profile is in. Two failure modes it prevents — a resumed
session trying to register again on a site the candidate already joined, and a half-finished profile
sitting invisible to recruiters because nobody knew the last two tabs were never filled.
