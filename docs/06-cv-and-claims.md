# 06 CVs and claims

The CV is often the only artifact that travels with an application, since many forms have no cover
letter field. That raises the cost of every line on it.

## Fit it to one page, and prove it

```bash
python3 scripts/render_cv.py cv.html out.pdf
```

The script renders with WeasyPrint and fails loudly unless the result is exactly one page, contains
no em dashes, and carries a reachable contact line. Rendering is step one of any sending task: the
PDF is derived output, and its absence fails later steps for reasons that look unrelated.

## Order experience newest first

Ordering by relevance instead of chronology makes the timeline jump backwards and reads as a
formatting error to a screener. Put the role-specific emphasis in the summary and the skills
section, not in the ordering.

## A checkable claim beats a strong-sounding one

A claim that describes a *pattern* ("regularly", "extensively", "across many teams") invites the
reader to test it against whatever public trace exists, and a stale blog disproves it in seconds. A
claim that names *one artifact with a URL* invites them to look at the artifact, where the work is
real.

```
weak, falsifiable   "I publish technical writing regularly."
strong, checkable   "My walkthrough on setting up a multisig wallet is published on Hashnode."
```

## Never let in-progress work drift into the past tense

A course, a paper, a prototype still being built is marked as such on the CV and stays marked in
every letter and form answer. The risk is highest at exactly the employers whose product is
verifying claims.

## Quantify, or say plainly that you cannot

The common weakness on graduate CVs is not thin experience, it is experience described without any
number: no volume, no named clients, no scale. Fix it with real figures from the applicant, never
with invented ones. If the applicant does not have the figures, the honest CV keeps the prose and
the weakness is stated in the report rather than papered over.

## Tailoring variants drift apart

Corrections applied to one CV variant do not propagate. Before attaching any variant, diff it
against the most recently corrected one: same roles, same titles, same dates, same ordering. A
correction that exists in one file and not the one you are sending has never happened.

## Personal data is not part of the repo

If you publish tooling built around a real job search, the playbook travels and the personal
material does not: no names, no contact details, no CV, no employer lists, no reference codes, no
tracker identifiers, no machine paths.
