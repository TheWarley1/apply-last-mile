# 01 Finding the real application route

The link you were handed is a claim, not a route. Resolve it before doing anything else.

## A dead shortener is not a dead posting

Measured case: a flyer circulated with a `bit.ly` link. It returned 404 on HEAD, on GET with a
browser user agent, and on the shortener's own expand endpoint. The job was open and taking
applications the whole time.

```bash
curl -sIL "<shortlink>" | grep -iE '^(HTTP|location)'
curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" -o /dev/null \
  -w "%{http_code} -> %{url_effective}\n" "<shortlink>"
```

A 404 from the shortener tells you the shortlink is gone. It tells you nothing about the job.
Search the role title plus the employer, and look for the employer's own domain in the results.

## The aggregator's apply button is usually the aggregator

Boards host their own CV drop. The employer's intake is behind an anchor whose label names the
destination. Read the anchor, not the "Method of Application" prose alone, and prefer the prose as
a hint about where the anchor goes:

```
Interested and qualified? Go to <Employer> on <tenant>.<ats-host> to apply.
```

That sentence is often the only place the real ATS hostname appears, and it survives even when the
aggregator's own panel is a false front.

```bash
curl -sL -A "Mozilla/5.0" "<posting-url>" -o page.html
grep -oE 'https?://[^"'"'"' <>]*(greenhouse|lever|ashby|workday|smartrecruiters|recruitee|personio|workable|teamtailor|breezy|freshteam|koraerp|jobs\.[a-z0-9.-]+)[^"'"'"' <>]*' page.html | sort -u
```

If the fetch is blocked, drive the browser and read the anchors:

```javascript
[...document.querySelectorAll('a')].map(a => a.innerText.trim().slice(0,40) + ' :: ' + a.href)
```

## The org slug names who runs the pipeline

`jobs.ashbyhq.com/<Slug>/...` - if the slug is not the employer's name, an external recruiting firm
owns the hiring, and mail to the employer will not reach a screener. Confirm the owner before
choosing who to write to.

## An SPA renders nothing to curl, and that is not a closed role

Careers sites built on React return a small HTML shell. Server-side checks and browser checks answer
different questions:

```bash
# does the listing exist server side?
curl -sSL -A "Mozilla/5.0" "https://<tenant>/careers" | grep -c "<job-slug>"
```

```javascript
// what does the rendered page actually show?
document.body.innerText
```

An empty render means JavaScript did not run in this session. It does not mean the role was pulled.
Saying a role is closed on the strength of an empty render is a wrong answer that costs the user
their application.

## Choosing the channel

| Route | Finishable without the user | Notes |
|---|---|---|
| Published email address | yes | Verify the domain first, see doc 02 |
| Open ATS form | usually | Behaviour varies by vendor, see doc 04 |
| Google Form | usually | No file upload on many, say so if the CV cannot travel |
| Account-gated portal | no | The application is a profile plus proposal, not a form |
| Aggregator relay (`/apply` on the board) | no | The employer's pipeline is never touched |

Count **submit-ready** routes, not listings. Twelve listings that yield no submittable route is not
a batch of twelve.
