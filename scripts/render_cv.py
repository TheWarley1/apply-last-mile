#!/usr/bin/env python3
"""render_cv.py - render a one-page CV from HTML and prove the result.

Why a script: the PDF is derived output. It goes missing, gets stale after an HTML edit, or grows a
second page when a bullet is added, and all three fail later steps for reasons that look unrelated.

    python3 render_cv.py cv.html out.pdf
    python3 render_cv.py cv.html out.pdf --expect-phone +234... --expect-text "Project Name"

Checks, all of them failing loudly:
  * exactly one page
  * no em dashes anywhere in the extracted text
  * every --expect-text string present
  * every --expect-phone digit sequence present (compared without spaces or plus signs)

Requires WeasyPrint for rendering and pypdf for the checks:

    pip install weasyprint pypdf
"""

import argparse
import os
import re
import subprocess
import sys


def render(html_path, pdf_path):
    try:
        import weasyprint  # noqa: F401
        from weasyprint import HTML
    except ImportError:
        raise SystemExit("WeasyPrint is not installed: pip install weasyprint")
    HTML(filename=html_path).write_pdf(pdf_path)


def extract(pdf_path):
    try:
        import pypdf
    except ImportError:
        raise SystemExit("pypdf is not installed: pip install pypdf")
    reader = pypdf.PdfReader(pdf_path)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return len(reader.pages), text


def digits(value):
    return re.sub(r"[^0-9]", "", value)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("pdf")
    ap.add_argument("--expect-text", action="append", default=[],
                    help="string that must appear in the extracted text (repeatable)")
    ap.add_argument("--expect-phone", default=None,
                    help="phone number that must appear, compared on digits only")
    ap.add_argument("--allow-em-dash", action="store_true",
                    help="skip the em dash check (outward-facing documents should not skip it)")
    args = ap.parse_args()

    if not os.path.exists(args.html):
        raise SystemExit("no such file: %s" % args.html)

    render(args.html, args.pdf)
    pages, text = extract(args.pdf)

    problems = []
    if pages != 1:
        problems.append("page count is %d, expected 1 (tighten spacing, font size or margins)" % pages)
    if not args.allow_em_dash:
        count = text.count("\u2014")
        if count:
            problems.append("%d em dashes in the text" % count)
    for needle in args.expect_text:
        # case-insensitive: headings are usually uppercased by CSS, and the extracted text
        # carries that transform rather than the source casing
        if needle.lower() not in text.lower():
            problems.append("missing expected text: %r" % needle)
    if args.expect_phone:
        if digits(args.expect_phone) not in digits(text):
            problems.append("phone %s not found in the PDF text" % args.expect_phone)

    size = os.path.getsize(args.pdf)
    print("%s -> %s  pages=%d bytes=%d chars=%d" % (args.html, args.pdf, pages, size, len(text)))
    if problems:
        for p in problems:
            print("FAIL: " + p)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
