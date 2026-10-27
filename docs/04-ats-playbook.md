# 04 ATS playbook

Vendor behaviour, measured against live forms in 2026. **Treat every line as a hypothesis with a
check attached.** These widgets change without notice, and the failure signature is usually
identical across completely different causes, which is why the check matters more than the note.

## The attach check that applies to all of them

```javascript
[...document.querySelectorAll('input[type=file]')]
  .map(e => e.files.length + ':' + (e.files[0] ? e.files[0].name : '-'))
```

Then read the page text for the filename. `files.length === 0` alone is not a failure verdict; see
doc 03.

## Per-vendor

| Vendor | Scripted attach | Filling | Notes |
|---|---|---|---|
| Workable | works | works | Submit control `[data-ui="application-form-submit"]` sits outside the form. Photo and resume inputs are separate; select by `accept` |
| Freshteam | works | works | Widget re-renders and can drop typed values, re-read every field after attaching |
| Google Forms | n/a | works | Often no upload at all. Walk `div[role=listitem]`, click `[role=radio]` by `data-value`, success is the URL changing to `/formResponse` |
| Kora ERP (`<org>.koraerp.com`) | works | works | React SPA, no CAPTCHA, submit is `POST /api/public/recruitment/<org>/jobs/<uuid>/applications` returning 201 plus a reference code |
| Ashby | works via `DOM.setFileInputFiles` | works | Field ids regenerate every render. Read attributes immediately before filling. Custom questions are bare UUIDs, resume input has no name, apply panel is collapsed behind a button |
| Lever | refused | works | Validates server-side: a 20 KB PDF returns "File exceeds the maximum upload size of 100MB" |
| SmartRecruiters | refused | works | Controlled component clears the input itself. Controls live in shadow roots, walk `el.shadowRoot` recursively |
| Aggregator relays | n/a | n/a | `arbeitnow.com/apply`, boards' own `/apply` pages and captcha relays apply through the middleman; the employer's pipeline is untouched |

## Failure signatures and what they actually mean

**"File exceeds the maximum upload size"** on a small file: server-side validation refusing scripted
input. Not a size problem. Re-firing `change` will not clear it.

**"Oops, this page is currently under maintenance"** with HTTP 405 from the applicant endpoint: their
intake is switched off. No retry or CAPTCHA work fixes a 405. Test the POST directly:

```bash
curl -s -o /dev/null -w "%{http_code}\n" -X POST "<applicant-endpoint>"
```

**A submit click that returns the form to its initial state** is a validation failure, not a success.
Confirm with a thank-you string and a changed URL, never with the absence of an error.

**A submit click that fires no network request** means the handler bailed. Watch
`Network.requestWillBeSent` while clicking. `form.checkValidity()` will happily return `true` on a
form that cannot submit.

**A CAPTCHA whose token never appears** (`cf-turnstile-response` stays empty, no challenge iframe,
no widget instantiated) is usually the client environment, not the form. A flagged datacentre IP
gets this from DataDome and Turnstile. Stop diagnosing the form: hand the URL, the field values and
the CV to the user to finish on their own device. Repeated attempts refresh the block.

## Retry budget

One probe per hypothesis. If a scripted attach fails twice on the same input, the answer is a human
handover, not a third technique. The techniques that never work on a controlled component are worth
knowing so you can skip them: a constructed `File` through `DataTransfer`, dispatched
`dragenter`/`dragover`/`drop`, `Input.dispatchDragEvent` with real paths, and a real click with
`Page.setInterceptFileChooserDialog` enabled. All are refused by the framework resetting `files`.

## What to do when the intake is genuinely broken

- Find the employer's published support or contact address, never a `From:` address on their
  automated mail.
- `dig +short MX <domain>` before sending. No MX means the mail bounces silently while looking fine.
- Say plainly that the application did not go through. A verified send to a dead address is not a
  submitted application, and reporting it as one is the failure that loses the opportunity.
