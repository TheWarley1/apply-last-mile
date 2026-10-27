# 02 Eligibility gates

Most rejections are not judgements of ability. They are filters applied before a human reads
anything, and nearly all of them are visible in the posting or on the form if you look before you
spend the effort.

## Hard exclusions: drop, do not rank

| Signal | Why it is fatal |
|---|---|
| "No sponsorship", "US/UK/CA/EU work authorisation required" | No route exists, stated directly |
| "Local candidates only", "must reside in <place>" | Geography the applicant cannot meet |
| "Nigeria excluded", restricted remote with an unrelated salary band | Not a remote role, a regional one |
| Student-enrolment gated internship | Not enrolled |
| Degree class above the applicant's, at an employer that filters automatically | A silent ATS cut |

Dropping these is not pessimism. A shortlist that includes them makes the user read five dead
opportunities to find one live one.

## The gate is often a required field, invisible in the listing

Measured: a listing labelled "remote worldwide" carried a required form question reading
*"Considering this is a remote role, from which country will you be working? Mandatory: America."*
The only two postings were Bogota and El Salvador. The label described where the company was; the
textarea described who may apply.

So the sequence is: open the form, enumerate required questions **with their exact wording**, then
decide whether the role is applyable, and only then write. A gate found after drafting wastes the
letter; after filling, it wastes the fill.

## When the gate is time, not place

Graduation windows ("obtained within the two years preceding application"), age ceilings and NYSC
status are common on graduate programmes and are applied by the ATS silently. Read the exact
sentence and check it against the candidate's real dates. If it does not fit, say so in one line and
let the user decide. Do not quietly apply, and do not quietly drop it.

## Truthfulness declarations change what "required" means

A form carrying *"any false or misleading information may lead to your application being rejected"*
makes a guessed field a self-inflicted rejection. Required means the **field** must be filled by
someone; it does not mean the agent may invent the answer.

- Leave it blank and name it in the handover.
- If the user delegates the decision, give a defensible range and say where the number came from.
- Never invent a date of birth, a street address, a salary history or a degree classification.

## Email beats the form when the gate is policy

The form rejects mechanically; a human can weigh what the form cannot. When the only blocker is
location, payroll entity or authorisation, a short email to a real recipient is the higher-value
move.

Shape that works, under 300 words:

- lead with the blocker, first sentence, no preamble
- ask the question that is answerable in one line ("is this a payroll constraint or a policy one?")
- offer the arrangement that removes the entity problem (contract, invoice)
- end with one clickable artifact, not a paragraph of claims
- give them the easy out: "if it is a hard requirement I would rather know"

Before sending, prove the address can receive mail. An MX record validates the domain, not the
mailbox, and a `From:` address on automated mail is usually send-only.

```bash
dig +short MX <domain>
```

Never invent `careers@`. If it is not published on a current page, it does not exist.

## Reading a rejection

Almost all replies land on eligibility rather than capability, and the wording shows which:

- "It is a local opportunity, onsite in <country>" is a geography gate.
- "It is not a judgement of your skills or your work" is what a company writes when the
  disqualifier was location or entity, not ability.
- A fast personal reply, by name, means the application was read and cleared the screening step.

Report the distinction, because the failure mode is the user concluding their CV is bad from silence
that has not had time to become an answer.
