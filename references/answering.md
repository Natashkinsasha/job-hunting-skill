# Answering forms and writing cover letters

Free text is where an application is won or thrown away. Everything below is drawn from
applications that got written, sent, and in some cases correctly rejected.

## The one rule

**Specific, verifiable, and unflattering where true.** Every application is competing with a
hundred that claim breadth and enthusiasm. A number, a named failure, and a stated limitation
beat three paragraphs of adjectives, because they are the only parts a reader can't get from
anyone else.

Never restate the job description back at them. They wrote it.

## Cover letter structure

Five short blocks. Under 400 words. No "I am writing to express my interest."

1. **Stack match, one sentence.** Name the technologies from their posting that the candidate
   actually uses, in the candidate's words. If the overlap is partial, say which part.
2. **The hardest thing in their posting, answered.** Find the sentence in the posting that most
   applicants can't satisfy — the domain, the scale, the specific failure mode — and answer that
   one. This is the whole letter; the rest is context.
3. **One concrete result with a number.** From real work. "Migrated production to k3s without a
   maintenance window, ~60% lower monthly spend at equal deploy latency." Not "improved
   infrastructure efficiency."
4. **One real limitation or hard-won failure.** This is the credibility purchase. "A ranking signal
   that turned out to have no spatial variance, so sorting by it degenerated into alphabetical
   order." A letter with no failure in it reads like every other letter.
5. **Practical block.** Location, timezone in *their* terms, work-authorisation reality, legal form,
   salary expectation, availability. Plainly, in one paragraph, as facts.

The practical block is not a weakness — it is a filter that saves both sides a call. Write it
even when the form doesn't ask.

Example of the domain paragraph earning its place, for a payments role:

> I have built money-adjacent flows where "the API returned 200" is not the same as "the money
> moved" — idempotency on retries, reconciliation, webhooks from providers that lie, and audit
> trails that still make sense during a dispute months later.

That is one sentence that a person who hasn't done it cannot write.

## Long-form essay questions

Some forms (Linear, Chainstack, VRChat, Canonical) ask three to six real essays. They are worth
the time — few applicants answer them well — but they need structure, not prose:

- **Answer the question that was asked**, in its first sentence. Not a preamble.
- **Architecture questions want the failure mode.** Describe the system, then name what actually
  broke and how you found it. "Stale features silently producing confident-but-wrong offers"
  is the answer; the component diagram is the setup.
- **"How do you use AI?" wants specifics and boundaries.** What you delegate, what you review
  yourself always (anything touching money, auth, migrations, infrastructure), and how output
  is verified mechanically rather than by vibes.
- **Product questions want a real story**, including one where the candidate's own call was wrong.
- **If the candidate doesn't use the product, say so** and analyse what you can from outside.
  Pretending to be a user is the fastest way to be caught.

Draft these in a file under `cover-letters/`, not in the browser. See the Ziina trap below.

## Answering "how many years of X" with no zero option

This is a gate, not a question. If the minimum option overstates the candidate, **stop and ask them**.
Do not round up. Do not pick "1-2 years" for someone who has read the docs.

Where a free-text field exists on the same form, the honest calibrated answer is strong:
"Node.js — Advanced. libuv — no, though I have debugged a wedged event loop down to an O(n²)
polygon simplification. DHT/Kademlia — read, never implemented. C++ — beginner."
Answers like that got applications *through*, because they tell a reviewer exactly what they'd be getting.

## Geography, timezone and work authorisation

The single most common reason a strong application is a waste of everyone's time. Be explicit,
always, even when unprompted.

- **Translate the candidate's timezone into the employer's frame.** "Tbilisi, GMT+4 = CET+2 —
  my day overlaps European hours fully and reaches into Asian ones." Don't make them do arithmetic.
- **State the work-authorisation reality as a fact, not an apology.** "Belarusian citizen based in
  Georgia, with a registered Georgian sole proprietorship, so contracting is straightforward and no
  sponsorship is needed." If they need an EU employment contract, they will filter you out —
  which is the correct outcome and costs zero calls.
- **When a form's options don't describe the candidate's situation**, pick the closest, and say
  in a free-text field on the same form exactly what the real situation is. If there is no free-text
  field, that's a red flag — ask the candidate.
- **A hard geography question with a stated auto-reject** ("are you resident in GMT+3…GMT+0?") is a
  stop, not a puzzle. Answering "yes" on a defensible technicality burns the company permanently.

## Salary

Give a number, in their currency if they state one, with the period spelled out. "USD 100,000 per
year, open to discussion." A blank or a range that starts at zero reads as either evasive or junior.
If the form is a bare number field with no period label, put the annual figure and repeat the period
in the nearest free-text field.

## Application limits are real

Some companies cap how many roles you may apply to (Scribe: 2 per 6 months; many: one repeat per
365 days per role). **Check before spending a slot.** Spray-applying to five roles at one company
is worse than choosing one — it spends every slot and signals nothing.

## When the employer bans AI-written applications

Several do, in the form itself ("obviously AI-generated responses will result in your application
being declined"). **Stop.** Write the candidate a facts sheet — the posting's hard requirements,
the matching pieces of their history, the numbers, the links — and let them write it. Paraphrasing
your way around the rule is the one failure mode that can't be recovered from.

## Two traps that cost real time

- **A "Cover Letter" field that is a file input, not a textarea.** Typing into it opens a file
  dialog per keystroke — 39 dialogs deep, the page is unusable and the tab has to be closed.
  Always check `type` before typing. This is why letters live in files: write once, attach anywhere.
- **Greenhouse required questions are sometimes `<textarea>`, not `<input>`.** A selector like
  `input[id^=question_]` silently misses them, and the form rejects with no visible error.
  Select `input, textarea, select` together, always.

## Logging what you said

Keep every letter as a file, named by company and role. When a recruiter replies three weeks later,
the candidate needs to know what was claimed on their behalf — and the next application to a similar
company starts from the closest existing letter rather than a blank page.
