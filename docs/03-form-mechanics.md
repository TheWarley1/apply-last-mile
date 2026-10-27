# 03 Form mechanics

Everything here is about component libraries that do not behave like the HTML they look like. Each
section ends with the check that proves the write landed.

## Read the structure before filling anything

```javascript
// every field, in document order, with its label
[...document.querySelectorAll('input,select,textarea')]
  .filter(e => e.type !== 'hidden')
  .map((e, i) => {
    const l = e.closest('label');
    const label = l ? l.innerText.replace(/\s+/g, ' ').slice(0, 60) : '';
    return `${i} ${e.type} ${JSON.stringify(label)} name=${e.name || ''}`;
  })
```

Three traps this catches:

- **A repeated field name.** Page builders reuse `name="phone"` for the applicant and for every
  referee. Setting all matches writes your number into the referees' boxes and every field still
  looks filled.
- **Every field reporting missing.** That is an unopened form, not a broken selector. Reload or
  click the collapsed apply control, then re-enumerate.
- **Zero file inputs.** Some employer forms carry no upload at all. Say so in the handover rather
  than hunting for a hidden input.

## Setting values the framework will notice

React, Vue and Svelte all track state separately from the DOM value. Assigning `el.value` updates the
DOM and leaves the framework's state at the old value, so the form submits empty while looking
correct. Call the native setter, then dispatch the events:

```javascript
function setValue(el, v) {
  const proto = el.tagName === 'SELECT' ? HTMLSelectElement.prototype
              : el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype
              : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, v);
  ['input', 'change', 'blur'].forEach(t => el.dispatchEvent(new Event(t, { bubbles: true })));
}
```

Check: read the value back, and then read the rendered page. A value visible in the UI is real;
a value only present in `el.value` may be your own reflection.

## Checkboxes in component libraries lie

Measured, Radix/shadcn: `input[type=checkbox].checked` returned `true` for both boxes while the form
refused to submit with "Accept the declaration before submitting". The visible control was a
`button[role=checkbox]` carrying the real state in `aria-checked`, and the hidden input was
decoration.

```javascript
// the state the framework reads
[...document.querySelectorAll('button[role=checkbox]')].map(b => b.getAttribute('aria-checked'))

// the action
document.querySelectorAll('button[role=checkbox]')[0].click()
```

Check: both controls must read `aria-checked="true"` before submit. Generalise the rule: on any
component library, read state from the role element (`aria-checked`, `aria-selected`,
`aria-expanded`), never from the underlying input.

## Dropdowns

Native `<select>` takes the setter plus `change`. Custom comboboxes need a click to open, then a
click on the option by its text, and the option usually lives in a portal appended to `body`, not
inside the field's parent.

Check: the trigger's own label text changed, not just the hidden input's value.

## Date pickers

A Radix popover calendar frequently carries native `<select>` elements for month and year
(`.rdp-months_dropdown`, `.rdp-years_dropdown`) that accept the setter, and the day is a button
whose `aria-label` reads the full date (`Monday, July 1st, 2002`). Set month, set year, wait for the
grid to re-render, click the day.

Check: the trigger button's text now shows the date.

## File uploads

Attach through CDP by walking the DOM with piercing, because `document.querySelector` will not reach
inputs inside shadow roots:

```python
doc = cdp("DOM.getDocument", {"depth": -1, "pierce": True})
```

Take `backendNodeId` from that walk and call `DOM.setFileInputFiles`. With two file inputs, choose by
the `accept` attribute: the one containing `.pdf` is the resume, the one containing `image` is the
photo.

**The read-back check has a false negative.** After a successful attach, a React uploader may copy
the file into state and clear the raw input, so `files.length` reads 0 while the page shows the
filename with a Remove button. Read both:

```javascript
[...document.querySelectorAll('input[type=file]')].map(e => e.files.length)
document.body.innerText            // does the filename appear in the dropzone?
```

A cleared input with a rendered filename means the file is attached and the app just reset the
field. A cleared input with nothing on the page means the attach failed.

## Judging completion

```javascript
[...document.querySelectorAll('input,textarea,select')].filter(e => e.type !== 'hidden')
  .map(e => [e.name || e.id, e.type, e.value])
[...document.querySelectorAll('button')].map(b => [b.innerText, b.disabled])
```

`button.disabled` answers "can this be submitted". The DOM values answer "is it filled". A screenshot
answers neither: a form can be 3,800px tall and one viewport proves nothing about the rest of it.

## Submitting

Some buttons sit outside the `<form>` element, so `form.submit()` and `requestSubmit()` do nothing.
Click the control element itself. Then confirm the submission, which is the subject of doc 05.
