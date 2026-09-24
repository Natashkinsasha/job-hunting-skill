# ATS playbook

Per-platform form mechanics. Every entry here cost a failed submission to learn.

## Universal rules

**Three things to set up before the first form**, each of which has cost a wasted hour:

- **The file chooser is sandboxed to the workspace.** Uploading the résumé from `~/Documents` or
  `~/Downloads` fails with "outside allowed roots". Copy it into the working directory once, at the
  start of the run, and attach it from there.
- **Mail logged in, in the same browser.** Greenhouse gates submission behind an 8-character emailed
  code, and each failed submit invalidates the previous one — see `email.md`. Not logged in, every
  code is a round-trip and the application sits half-done until the candidate answers.
- **Keep the tab open while you wait for anything.** A Greenhouse form holds its state, including
  the uploaded résumé and every essay; navigating away means filling it all in again.

**Check the form for gates before filling it.** Dump every field label first:

```js
Array.from(document.querySelectorAll('input,textarea,select')).map(e => {
  const l = (document.querySelector(`label[for="${e.id}"]`)||{}).innerText || '';
  return `${e.type||e.tagName}|${e.id||e.name}|${l.replace(/\n/g,' ').slice(0,50)}`;
}).join('\n')
```

**When a submit does nothing and no error is visible**, the answer is one of four things, in order of likelihood:

```js
// 1. what does the browser think is invalid?
[...document.querySelectorAll(':invalid')].map(e => e.name || e.id)
// 2. is the button mid-flight?
document.querySelector('button[type=submit]')?.disabled
// 3. what did the POST actually return?  (428 = e-mail code required)
//    use the network-request tool, filter on the ATS host
// 4. is there a captcha that never loaded?
document.querySelectorAll('iframe[src*="recaptcha"],iframe[src*="cloudflare"]').length
```

## Ashby

`https://jobs.ashbyhq.com/<org>/<job-uuid>/application`

- **Setting `.value` from JavaScript does not register.** React keeps its own state; the DOM shows your text and the form reports "Missing entry for required field". You must type: Playwright `fill()` or `pressSequentially()`. This is the single most expensive mistake on Ashby.
- Location is a combobox — type, wait ~1.5 s, then `Enter` to take the first suggestion.
- Resume upload: `button.ashby-application-form-input-file-dropzone-upload` opens the file chooser.
- Success text: `Success` / `Your application was successfully submitted`. **Boards can customise it** —
  WunderGraph answers "Your application just landed! 🎉", which matches neither phrase. Check for the
  `Success` step marker or the absence of the form, not for one sentence, or you will re-submit a
  successful application.
- **`Location` is sometimes a COUNTRY picker, not a city one.** On some boards the autocomplete only
  offers countries ("Georgia", "South Georgia and the South Sandwich Islands" — no cities at all). A
  typed city stays in the box looking filled and is silently not counted; submit answers "Missing entry
  for required field: Location". Verify the value matches an option you actually selected, not that the
  box has text in it.
- **The Yes/No control does not respond to a programmatic `.click()`** from injected JS — `aria-pressed`
  stays `false` and the field submits as empty. Click it with the browser tool, then read back
  `aria-pressed` to confirm.
- **When a submit is rejected for un-registered fields, it names only some of them.** Three essays filled
  the same (broken) way came back as two errors. Re-enter *every* field you filled that way, not just the
  ones it complained about — otherwise you burn a second submit discovering the third.
- **A field id that starts with a digit breaks `#id` selectors.** Ashby ids are UUIDs, so about half of
  them begin with a number and `#6e488bac-…` is not a valid CSS selector — Playwright raises
  `SyntaxError: … is not a valid selector` and it reads like a missing element rather than a bad
  selector. Address them as `textarea[id="…"]` / `input[id="…"]` and the problem disappears.
- **`type="tel"` is the one field `fill()` cannot set.** Every other text input on Ashby accepts
  `fill()`; the phone field takes the value in the DOM and still submits as empty — "Missing entry for
  required field: Phone" on a box that visibly contains a number. Use `pressSequentially()` for phone,
  always. (Same failure mode as Greenhouse's phone widget, different cause.)
- **The "Autofill from resume" parser is a draft, not an answer.** Uploading the CV fills name, email,
  phone, current title and location for you — and it fills them from the CV's *headline*, so the title
  can be a self-description rather than the employer's job title, and the location can be the word
  "Remote". Read back every field it touched before submitting.
- **Anti-spam**: a board may answer "Your application submission was flagged as possible spam". Two
  separate things produce it, and they need different responses:
  - **First submission of the session, on a board you have never touched.** Then it is not volume — it is
    the exit IP. Measured: a run whose traffic left through a commercial VPN on a *hosting* ASN was
    flagged on the very first submit; the identical form went through on the immediate retry. **Retry
    once before concluding anything.** If retries keep failing, check the public IP
    (`curl -s https://ipinfo.io/json`) — a datacenter/VPN `org` is the likely cause, and asking the
    candidate to drop the VPN for the session fixes it in a way no amount of retrying will.
  - **Several submissions to the same board in a row.** That is the volume rule: it is per-board, not
    global, other Ashby boards keep working the same hour, and retrying rarely helps. Interleave other
    employers between roles at one company.

  **Either way, do not navigate away to "start fresh".** Ashby keeps the whole form after a rejected
  submit — every essay, the uploaded résumé, the resolved location — and loses all of it on reload.
  The retry is one click; the reload costs you the entire form again.

Public API for listings:
`https://api.ashbyhq.com/posting-api/job-board/<org>?includeCompensation=true`
→ `jobs[]` with `title`, `location`, `secondaryLocations[]`, `descriptionHtml`, `jobUrl`, `compensation.compensationTierSummary`.

## Greenhouse

Direct form URL, bypassing the iframe:
`https://job-boards.greenhouse.io/embed/job_app?for=<org>&token=<jobId>`
EU boards exist at `job-boards.eu.greenhouse.io` but the **API host is the same** — `boards-api.greenhouse.io` serves both. There is no separate EU API.

- JavaScript `.value` injection **works** on the plain text inputs — but not on the phone/country pair or any react-select (see the two sections below).
- `#country` is the phone country picker, not residence.
- `#candidate-location` is a geocoded autocomplete: type, wait, `Enter`.
- Resume: the visible button is a sibling of the hidden `#resume` input — `div:has(> #resume) button`.
- react-select dropdowns: click the input, then read `#react-select-<fieldId>-listbox` for options.

**HTTP 428 on submit = e-mail verification code.** The page grows eight `#security-input-N` boxes. Paste the whole 8-character code into `#security-input-0` — it distributes itself. Get the code from the candidate's mail: search `from:greenhouse-mail.io`, subject "Security code for your application to \<Company\>". Codes are **per company**: once verified, other roles at that company submit freely. Each failed submit issues a *new* code, so always use the newest mail.

API: `https://boards-api.greenhouse.io/v1/boards/<org>/jobs` and `.../jobs/<id>` for the body.

## Greenhouse: the phone widget is not a text input

`#phone` and its country picker `#country` are a React/`intl-tel-input` pair. Injecting `.value` into
`#phone` leaves the number visible in the DOM and invisible to the form: submit comes back with
**"Phone is required"** and **"Select a country"** on a field that plainly shows a number. Type both:
`#country` character by character, take the option out of `react-select-country-listbox` (the
`iti-0__country-listbox` next to it is dead markup), then `#phone` **without the dialling code**.

The rest of Greenhouse's plain text inputs do accept `.value` injection — this widget is the exception,
so a form can fail on two fields while the other eight went in fine.

## Greenhouse: never pick a react-select option with arrow keys

`ArrowDown` ×N + `Enter` does **not** land on the Nth option — the first `ArrowDown` opens the menu and
highlights option 1, so the count is off by one and there is no error when it lands somewhere wrong. On a
"How many years of professional experience" field that silently submits a **false answer about the
candidate**. Type the option's text instead, confirm the listbox has narrowed to it, then `Enter`.

Verify every dropdown before submitting — they all render into the same class:

```js
[...document.querySelectorAll('.select__single-value')].map(e => e.innerText)
```

Read that list as a sentence about the candidate. If any entry is wrong, fix it before you submit; after
submission there is no edit.

## Lever

`https://jobs.lever.co/<org>/<job-uuid>/apply` (EU: `jobs.eu.lever.co`)

- Plain HTML — JavaScript `.value` injection works.
- **The email field carries a `pattern` attribute whose regex is invalid in current browsers.** `checkValidity()` throws a SyntaxError, the submit silently does nothing, and **no error appears on the page**. Fix before submitting:
  `document.querySelectorAll('input[pattern]').forEach(e => e.removeAttribute('pattern'))`
- `consent[store]` — a required consent checkbox, separate from everything else.
- `opportunityLocationId` — a hidden required `<select>` on some postings, listing the regions the company hires in.
- **Fill location LAST.** A rejected submit clears the location, résumé and link fields.
- Location must be *chosen from the dropdown*, not typed: click the suggestion, then verify `[name=selectedLocation]` holds JSON.
- Success: URL ends in `/thanks`.

API: `https://api.lever.co/v0/postings/<org>?mode=json` (EU: `api.eu.lever.co`).

## Workable

- Listings: `https://apply.workable.com/api/v1/widget/accounts/<token>?details=true`
- On `jobs.workable.com` a cookie backdrop blocks the Apply button — accept cookies first.
- The résumé `<input type=file>` is hidden behind `div[data-role="dropzone"]`; click the dropzone, not the input.
- Submission runs through **Cloudflare Turnstile**. If the challenge endpoints return 400 the form hangs on "Submitting…" forever with no error. Nothing you can do in-page; hand it over.

## BambooHR

`https://<org>.bamboohr.com/careers/<id>` — listings at `/careers/list`, detail at `/careers/<id>/detail`.

- **Changing Country resets the Province field and changes its element id.** Fill country first, then the address fields.
- Résumé: a real button labelled "Choose File" sits next to the hidden input.
- reCAPTCHA here is the **v2 checkbox**. It must be clicked or submit does nothing and shows no error:
  `iframe[title="reCAPTCHA"]` → `#recaptcha-anchor`, click through the frame. Then verify `[name="g-recaptcha-response"]` has a value before submitting.

## Workday

`POST https://<tenant>.wd<N>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs`
body `{"appliedFacets":{},"limit":20,"offset":0,"searchText":"..."}` — public, no auth.

**Discovery only.** Applying requires creating an account per company, which you should not do on someone's behalf. Also: the location label on a Workday posting frequently contradicts the body text — a job tagged "Worldwide" can say "must be located within the U.S." three paragraphs in. Read the body.

## Regional and long-tail ATSes

You will meet one every few dozen applications, usually because an aggregator or a recruiting agency
links out to it. Two habits cover most of them.

- **An HTTP 500 on the page does not mean the form is broken.** Observed on `careers.headly.ru`: the
  document arrives with status 500 *and* a fully working React application underneath. Judge the form
  by whether its fields and submit button behave, not by the status line.
- **If it parses the résumé, re-read every field it filled.** Small ATSes lean on a parser harder than
  Ashby does and get more of it wrong — the same upload produced a correct name, email and phone, a job
  title assembled from the CV headline rather than the last employer's actual title, and the literal
  string "Remote" in the Location field. Overwrite, don't rubber-stamp.
- Localised forms ask for fields the English-speaking ATSes never do — patronymic, date of birth,
  marital status, a photograph. Leave the optional ones blank rather than inventing them, and treat a
  required one you cannot answer truthfully as a gate (see SKILL.md → Red flags).

## Postings that limit how often you may apply

Some boards state a rate limit on the application page itself — "candidates may not apply more than 2
times in any 30 day span for any job" is real Ashby copy. This is not decoration: it is the employer
telling you the rule they enforce. Read the banner above the form before filling it, count the
candidate's existing rows for that company in the log, and skip rather than spend the allowance.
Related and worse: the same posting reached through a different channel is still the same posting —
a role applied to through an aggregator turns up again in the next board sweep under the employer's
own URL, and only company+role deduplication catches it.

## Network failures that look like application failures

- **reCAPTCHA never initialises** (`typeof window.grecaptcha === 'undefined'`, zero recaptcha iframes) → the network can't reach `www.google.com` / `www.gstatic.com`. Some boards load it from `www.recaptcha.net` and work fine on the same machine, so the symptom is intermittent across employers. Loading the mirror script yourself is blocked by CSP. Ask the candidate to disable the VPN or DNS filter.
- **Cloudflare challenge returns 400** → same class of problem, different vendor.
- Confirm before blaming the form:
  `curl -s -o /dev/null -w '%{http_code}' --max-time 6 https://www.google.com`
