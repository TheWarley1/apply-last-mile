#!/usr/bin/env python3
"""form.py - read and drive an application form over CDP.

The rule this script enforces: every write is followed by a read. A field that holds a value is
not the same as a field the page has accepted.

CLI (all commands act on the tab matched by CDP_TAB_MATCH, or the first real tab):

    python3 form.py survey                 # every field, in document order, with its label
    python3 form.py state                  # current values, aria states, submit button, page errors
    python3 form.py set '<json>'           # {"Label substring": "value", ...} or {"3": "value"}
    python3 form.py tick                   # click every button[role=checkbox]
    python3 form.py attach <file>          # attach to the first file input, then prove it landed
    python3 form.py click '<button text>'  # click a control by its visible text
    python3 form.py watch '<button text>'  # click and report the network calls it fired

Exit status is 1 when the read-back disagrees with the write.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import CDP  # noqa: E402

SURVEY_JS = r"""
(() => {
  const labelFor = (e) => {
    const byRef = e.getAttribute('aria-labelledby');
    if (byRef) {
      const n = document.getElementById(byRef.split(' ')[0]);
      if (n) return n.innerText;
    }
    if (e.id) {
      const forLabel = document.querySelector('label[for="' + CSS.escape(e.id) + '"]');
      if (forLabel) return forLabel.innerText;
    }
    if (e.getAttribute('aria-label')) return e.getAttribute('aria-label');
    const wrap = e.closest('label');
    if (wrap) return wrap.innerText;
    // Greenhouse-style: a label element in the same field container, but only when this element
    // is the only control in it (otherwise the neighbour's label bleeds across)
    let p = e.parentElement;
    for (let i = 0; i < 4 && p; i++, p = p.parentElement) {
      if (p.querySelectorAll('input,textarea,select').length > 1) continue;
      const lab = p.querySelector('label');
      if (lab && lab.innerText.trim()) return lab.innerText;
    }
    return '';
  };
  const fields = [...document.querySelectorAll('input,select,textarea')].filter(e => e.type !== 'hidden');
  return JSON.stringify(fields.map((e, i) => ({
    i: i,
    tag: e.tagName.toLowerCase(),
    type: e.type,
    name: e.name || '',
    accept: e.getAttribute('accept') || '',
    label: (labelFor(e) || '').replace(/\s+/g, ' ').trim().slice(0, 70),
    required: e.required || !!(labelFor(e) || '').includes('*'),
    value: e.value,
    checked: e.type === 'checkbox' ? e.checked : null
  })));
})()
"""

STATE_JS = r"""
(() => {
  const fields = [...document.querySelectorAll('input,select,textarea')].filter(e => e.type !== 'hidden');
  const boxes = [...document.querySelectorAll('button[role=checkbox]')];
  const files = [...document.querySelectorAll('input[type=file]')];
  const buttons = [...document.querySelectorAll('button')]
    .filter(b => (b.innerText || '').trim() && !/^(Choose a file|Select option|Pick a date)/.test(b.innerText.trim()))
    .map(b => ({ text: b.innerText.trim().slice(0, 50), disabled: !!b.disabled }));
  const text = document.body.innerText;
  return JSON.stringify({
    values: fields.map(e => [e.type, e.value, e.type === 'checkbox' ? e.checked : null]),
    role_checkboxes: boxes.map(b => b.getAttribute('aria-checked')),
    file_inputs: files.map(e => e.files.length + ':' + (e.files[0] ? e.files[0].name : '-')),
    filename_on_page: (files[0] && files[0].files[0]) ? text.includes(files[0].files[0].name) : null,
    buttons: buttons,
    url: location.href
  });
})()
"""

SET_JS = r"""
(pairs) => {
  const setValue = (el, v) => {
    const proto = el.tagName === 'SELECT' ? HTMLSelectElement.prototype
                : el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype
                : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, v);
    ['input', 'change', 'blur'].forEach(t => el.dispatchEvent(new Event(t, { bubbles: true })));
  };
  const fields = [...document.querySelectorAll('input,select,textarea')].filter(e => e.type !== 'hidden');
  const results = [];
  for (const [key, value] of pairs) {
    let el = null;
    if (/^\d+$/.test(key)) {
      el = fields[parseInt(key, 10)];
    } else {
      el = fields.find(e => {
        const l = e.closest('label');
        const t = l ? l.innerText : (e.getAttribute('aria-label') || e.name || '');
        return t.toLowerCase().includes(key.toLowerCase());
      });
    }
    if (!el) { results.push([key, 'NOT FOUND']); continue; }
    setValue(el, value);
    results.push([key, el.value === value ? 'ok' : 'MISMATCH: ' + el.value]);
  }
  return JSON.stringify(results);
}
"""

TICK_JS = r"""
(() => {
  const boxes = [...document.querySelectorAll('button[role=checkbox]')];
  boxes.forEach(b => { if (b.getAttribute('aria-checked') !== 'true') b.click(); });
  return JSON.stringify(boxes.map(b => b.getAttribute('aria-checked')));
})()
"""

CLICK_JS = r"""
(needle) => {
  const b = [...document.querySelectorAll('button,a,[role=button]')]
    .find(x => ((x.innerText || '').trim().toLowerCase()).includes(needle.toLowerCase()));
  if (!b) return 'NOT FOUND';
  b.click();
  return 'clicked: ' + (b.innerText || '').trim().slice(0, 40);
}
"""

WATCH_JS = r"""
(needle) => new Promise(resolve => {
  window.__calls = [];
  if (!window.__patched) {
    const original = window.fetch;
    window.fetch = async (...args) => {
      const res = await original(...args);
      window.__calls.push({ url: String(args[0]), status: res.status });
      return res;
    };
    window.__patched = true;
  }
  const b = [...document.querySelectorAll('button,a,[role=button]')]
    .find(x => ((x.innerText || '').trim().toLowerCase()).includes(needle.toLowerCase()));
  if (!b) { resolve('NOT FOUND'); return; }
  b.click();
  setTimeout(() => resolve(JSON.stringify({
    calls: window.__calls,
    url: location.href,
    text: document.body.innerText.slice(0, 600)
  })), 8000);
})
"""


def connect():
    return CDP(match=os.environ.get("CDP_TAB_MATCH"))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 0
    cmd = argv[1]
    cdp = connect()

    if cmd == "survey":
        rows = json.loads(cdp.js(SURVEY_JS))
        for r in rows:
            print("%2d %-8s %-24s %-40s%s" % (
                r["i"], r["type"], repr(r["label"])[:24],
                (r["name"] or (r["accept"] and "accept=" + r["accept"]) or ""),
                "  *required" if r["required"] else ""))
        return 0

    if cmd == "state":
        print(json.dumps(json.loads(cdp.js(STATE_JS)), indent=2))
        return 0

    if cmd == "set":
        pairs = list(json.loads(argv[2]).items())
        results = json.loads(cdp.js("(%s)(%s)" % (SET_JS, json.dumps(pairs))))
        bad = 0
        for key, status in results:
            if status != "ok":
                bad += 1
            print("%-30s %s" % (key, status))
        return 1 if bad else 0

    if cmd == "tick":
        states = json.loads(cdp.js(TICK_JS))
        print("role=checkbox:", states)
        return 0 if all(s == "true" for s in states) else 1

    if cmd == "attach":
        path = argv[2]
        cdp.attach(path)
        time.sleep(1.5)
        files = cdp.js("[...document.querySelectorAll('input[type=file]')]"
                       ".map(e => e.files.length + ':' + (e.files[0] ? e.files[0].name : '-'))")
        name = os.path.basename(path)
        on_page = cdp.js("document.body.innerText.includes(%s)" % json.dumps(name))
        print("input.files:", files)
        print("filename rendered on page:", on_page)
        # either the input holds it, or the app took it into state and reset the input
        held = any(s.split(":")[0] != "0" for s in (files or []))
        ok = held or on_page
        print("attach:", "ok" if ok else "FAILED")
        return 0 if ok else 1

    if cmd == "click":
        print(cdp.js("(%s)(%s)" % (CLICK_JS, json.dumps(argv[2]))))
        return 0

    if cmd == "watch":
        print(cdp.js("(%s)(%s)" % (WATCH_JS, json.dumps(argv[2]))))
        return 0

    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
