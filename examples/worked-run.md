# Worked run: a dead shortlink, a real portal, and two traps

A redacted, end to end account of one application. Times are what they were. Identification details
are removed.

## Situation

A flyer circulated on social media advertised a 12-month paid graduate programme at a consultancy.
It carried a shortened link and a list of requirements, including a degree class floor, a graduation
window and an NYSC status clause. The candidate was outside the graduation window and applying from
a different city than the role's location, and asked to apply anyway.

## Step 1: the link was dead, the job was live

```
curl -sIL "https://bit.ly/XXXXXXX" | grep -iE '^(HTTP|location)'
HTTP/2 404
```

A 404 from the shortener. Searching the role title plus the employer found five aggregator copies of
the same posting, all recent. So the shortlink had expired, not the vacancy.

## Step 2: the aggregator named the real host

The board's own page carried a CV drop that belonged to the board. The line below it read:

```
Interested and qualified? Go to <Employer> on <tenant>.koraerp.com to apply
```

That hostname existed nowhere else in the search results. Resolved, it was a React careers SPA: a
listing page and a per-job page carrying the JD plus the form. `curl` returned a 749-byte shell,
which is the SPA signature, so the browser was the only way to see the form.

## Step 3: the gates, read before anything was written

The form's required fields, enumerated with labels:

```
0 text     Full name *
1 email    Email address *
2 tel      Phone number *
3 file     Resume / CV *            accepts .pdf,.doc,.docx
4 select   Years of relevant experience *     0-2 / 3-5 / 6-10 / 10+
5 text     Current location *
6 text     Earliest availability *
7 popover  Date of Birth *          Radix calendar
8 select   What is your NYSC status? *
9 checkbox Applicant declaration *
10 checkbox Privacy consent
```

No cover letter field, no CAPTCHA, no account. Two of these are silent gates (graduation window,
location), and one is a truthfulness declaration that forbids guessing the rest.

The date of birth was not in any stored profile. It was requested from the candidate rather than
inferred from a birth year, because the declaration below the fields says false information may lead
to rejection.

## Step 4: filling, and the first trap

Everything filled mechanically except the checkboxes, which reported `input.checked === true` while
the form refused to submit:

```
Accept the declaration before submitting.
Confirm that the hiring team may process your application.
```

The real controls were `button[role=checkbox]` elements with `aria-checked="false"`. The hidden
inputs were decoration. Clicking the buttons and re-reading `aria-checked` cleared both errors.

## Step 5: the second trap, and the reason it matters

`DOM.setFileInputFiles` reported success. `files.length` read `0`. On a vendor known to refuse
scripted attaches that is a flat failure, and the natural next move is a human handover.

Reading the page instead:

```
Resume / CV *
  CV-FILE.pdf
  PDF, DOC or DOCX, up to 10 MB.
  Change   Remove
```

The app had copied the file into React state and cleared the raw input. The attach had worked. This
is the single most expensive misread in the whole run: the read-back check has a false negative, and
the page text is the check that settles it.

## Step 6: submission and proof

With `fetch` instrumented before the click:

```
POST /api/public/recruitment/<org>/jobs/<uuid>/applications   -> 201
```

The page then rendered "Application received", a reference code, and the address that would be
written to. Reference in hand, the application was recorded with its two known disqualifiers.

## What this run demonstrates

- The provided link was worthless; the employer's host was one line of prose away.
- The form's gates were legible before a single word was drafted.
- Both submission-blocking bugs were state-visibility bugs, not network bugs.
- The one fact the agent could not supply was asked for, not invented.
- The result was a status code and a reference, not a screenshot of a filled form.
