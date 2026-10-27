# Apply Last Mile

Agent skills and scripts for the part of a job application nobody automates well: **the form itself**.

Most "AI job agent" repos stop at the shortlist. They scan boards, filter roles and draft a letter,
then hand you a link. The hard part starts there. The link is often dead. The aggregator that
listed the role is not the employer's intake. The real form asks questions that decide the
outcome before a human ever reads your CV.

This repo is a distilled playbook plus working, dependency-light scripts for that last mile:

- find the employer's real application route when the link you were given is dead
- read the form's gates **before** writing a word
- fill forms programmatically, including the component-library traps that silently do nothing
- prove the submission actually happened, using the server's answer rather than the button
- know which forms to refuse to fill

## The doctrine in six lines

1. **The listing is not the application.** An aggregator's apply button is often the aggregator.
2. **Read every required field first.** A gate discovered after drafting wastes the draft; one
   discovered after filling wastes the fill.
3. **Never invent a personal fact.** A guessed salary, address or date of birth inside a form that
   carries a truthfulness declaration is a self-inflicted rejection.
4. **A click is not a submission.** Verify against the endpoint's status and the confirmation page,
   not against the absence of an error.
5. **Refuse forms a human must own.** CAPTCHA image challenges, recorded video intros, portfolio
   uploads that do not exist. Say so at the top, not after twenty filled fields.
6. **Volume is not the scarce resource.** A tailored five beats a scraped five hundred, because
   complaints and spam placement are permanent and the address you apply from is the one you need
   later.

## Contents

```
SKILL.md                     agent-facing skill file (Hermes / Claude-style SKILL.md)
docs/
  01-find-the-real-route.md  dead links, aggregator relays, ATS host discovery
  02-eligibility-gates.md    hard filters, silent ATS screens, when email beats the form
  03-form-mechanics.md       filling React forms over CDP: setters, checkboxes, file inputs
  04-ats-playbook.md         per-vendor behaviour, measured, with the failure signature
  05-verify-and-report.md    proving a submission, and reporting what failed
  06-cv-and-claims.md        one-page CV rendering and claims that survive checking
scripts/
  cdp.py                     zero-dependency Chrome DevTools client (WebSocket + HTTP)
  form.py                    form helpers: enumerate, set, tick, attach, snapshot
  render_cv.py               HTML to one-page PDF, with page count and typography checks
examples/
  worked-run.md              a full worked run, including the two traps that cost the most time
```

## Quickstart

Requires Python 3.10+ and a Chrome instance started with a debugging port.

```bash
# 1. start Chrome with CDP enabled
google-chrome --remote-debugging-port=9333 --user-data-dir=/tmp/agent-profile &

# 2. open a page
python3 scripts/cdp.py nav "https://example.com/careers" 5

# 3. read the rendered page (SPAs render nothing to curl)
python3 scripts/cdp.py text 3000

# 4. enumerate the application form before touching it
python3 scripts/form.py survey
```

`scripts/form.py --help` lists the operations. Everything is plain Python standard library plus
the Chrome you already have.

## What this is not

- Not a mass mailer. There is no recipient scraper here and no bulk sender.
- Not a CAPTCHA solver, by design.
- Not a source of anyone's personal data. The examples are redacted.
- Not a substitute for reading the posting. Half of these gates are only visible in prose.

## Status

The vendor notes were measured against live forms in 2026. ATS vendors change their widgets
without notice, so every claim in `docs/04-ats-playbook.md` carries the check that proves or
disproves it on the day you run it. Trust the check, not the note.

## License

MIT.
