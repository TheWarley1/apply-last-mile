# 05 Verifying and reporting

A form application either finishes end to end or it stops at a named wall. Both outcomes are useful;
the useless outcome is an optimistic report.

## The only proofs that count

1. **HTTP status from the intake endpoint.** 201 or 200 with a JSON body naming the application. A
   405 or 500 is a failure regardless of what the page looks like.
2. **A confirmation page with a reference number.** "Application received" plus a code you can quote
   later. This is what you report.
3. **A stored copy of a sent email with the attachment**, read back from the service rather than
   trusted from the send call's return value.

Everything else is a claim. A button that is not disabled, a field that holds a value, and a page
that did not show an error are not proofs.

## Instrumenting the submit

Wrap `fetch` before clicking, so the request and its status are captured even if the UI says nothing:

```javascript
window.__calls = [];
const original = window.fetch;
window.fetch = async (...args) => {
  const res = await original(...args);
  window.__calls.push({ url: String(args[0]), status: res.status });
  return res;
};
```

Then click the control, wait, and read `window.__calls` plus the page text. On a successful run you
want one POST whose status is 2xx and a page containing a thank-you string and a reference.

## Failure triage order

1. **Read the server's answer, not the UI's.** The page's error text is a client-side guess.
2. **An empty render is not a dead page.** Confirm server-side before telling the user the role is
   gone. An SPA that did not execute JavaScript looks exactly like a withdrawn posting.
3. **Test the POST.** A 405 means their intake is off; stop retrying.
4. **Check the environment.** A CAPTCHA token that never appears is an IP reputation problem.

## Reporting a batch

- Count **submit-ready** routes, not listings.
- Name the failures in the first report, with the reason, not after the successes. A quiet omission
  reads as completion and the user only finds out when the deadline passes.
- Include the reference number for everything that went through, and the exact remaining human steps
  for everything that did not.
- If an earlier statement turns out wrong, lead with the correction and what it changes.

## Record keeping

One row per application: date, employer, role, location, route, sender or reference, status, and a
notes field carrying the gate that nearly killed it. Two months later the notes field is the only
thing that explains why a batch of twenty produced no replies.
