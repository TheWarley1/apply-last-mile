---
name: apply-last-mile
description: Use when filling a real job application form end to end. Finds the employer's true apply route, reads eligibility gates before drafting, fills the form without inventing facts, and proves the submission before reporting success.
version: 1.0.0
---

# Apply Last Mile

An agent skill for completing a job application rather than just sourcing one.

Load this when the user says "apply to this", hands over a posting or flyer, or asks why an
application did not go through. The ordering below is the point. Each step exists because doing it
later cost a full rewrite of the work before it.

## Order of operations (do not reorder)

1. **Route.** Find the employer's own intake. The link the user gave may be an aggregator, a
   shortener that expired, or a relay that collects the CV for the aggregator. See
   `docs/01-find-the-real-route.md`.
2. **Gates.** Open the form and enumerate every required field and every sentence of prose that
   restricts who may apply, **before** drafting a letter or filling a field. See
   `docs/02-eligibility-gates.md`. If a required question makes the honest answer a false
   statement, stop and tell the user which question and why.
3. **Draft.** Only now write anything. Short beats long. Name one checkable artifact rather than
   claiming a habit. See `docs/06-cv-and-claims.md`.
4. **Fill.** Mechanically, reading state back after every control. Component libraries lie about
   their own state. See `docs/03-form-mechanics.md` and `docs/04-ats-playbook.md`.
5. **Prove.** Read the endpoint status and the confirmation page. A disabled-looking button, a
   cleared field or a silent click are all failures. See `docs/05-verify-and-report.md`.
6. **Record.** Log date, employer, role, route, reference number, and the reason every other role
   in the batch died. A tracker that only records successes teaches nothing.

## Refusals this skill requires

- **No invented personal facts.** Salary expectation, notice period, start date, street address and
  date of birth are the applicant's to state. Leave them blank and name the blanks, or ask. When the
  user explicitly delegates one, use a defensible range and say the number came from you.
- **No fabricated experience.** In-progress work is marked in progress. A claim a public source can
  disprove is worse than a thin CV.
- **No CAPTCHA solving services.** Clicking the checkbox as a human would is fine. Wiring a paid
  solver to defeat a human-presence check is not, and it is not a negotiating position: hold the
  line once, plainly, then make the handover cheap.
- **No bulk sending.** No recipient scrapers, no blasting a scraped list. Complaint rates and spam
  placement are permanent, and the sending address is the asset that outlives this application.

## Handover rule

When a step genuinely needs a human (image CAPTCHA, a file picker the framework refuses, a recorded
video, a decision the user owns), do everything else first, then hand over **the exact remaining
actions in order** with the field values already typed out. Never hand over a blank form.

## Tools

- `scripts/cdp.py` drives an existing Chrome over the DevTools protocol with no dependencies.
- `scripts/form.py` holds the fill operations and the read-back checks.
- `scripts/render_cv.py` renders an HTML CV to a single page and checks typography.

Reference material lives in `docs/`. Vendor behaviour and its verification commands live in
`docs/04-ats-playbook.md`.
