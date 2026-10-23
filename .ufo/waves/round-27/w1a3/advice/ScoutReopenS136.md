VERDICT: holds — Independent copies of RFC 8259 §7 contain "Any character may be escaped." once, verbatim, and state the six-character BMP `\u` form; the document is the December 2017 Internet Standard also known as STD 90.

## What was fetched

No packages installed. No llama-server. `count-c1.py` was not run. Scratch: `/fast/scratch/hyaku/kama-r27c/ScoutReopenS136/`. `df -h /fast` before the fetches: 219G free. Every curl was under `ulimit -f 1048576` and `timeout 90` (API calls `timeout 40`). User-Agent `kama-scout/1.0 (RFC re-open)`. All exits 0.

Independent copies named in the seat (not the lane's `.txt`):

```
curl -fsSL --max-time 60 -D datatracker.headers -o rfc8259-datatracker.html \
  https://datatracker.ietf.org/doc/html/rfc8259
# HTTP/2 200, date Fri, 23 Oct 2026 07:07:34 GMT, text/html; charset=utf-8
# sha256 1ce82413387894358cf31069bd696f56413b880826c798952b56f9bdda2db3fb
# 81689 bytes

curl -fsSL --max-time 60 -D rfceditor.headers -o rfc8259-rfceditor.html \
  https://www.rfc-editor.org/rfc/rfc8259.html
# HTTP/2 200, date Fri, 23 Oct 2026 07:07:35 GMT, text/html
# link canonical https://www.rfc-editor.org/info/rfc8259/
# sha256 5302d6ccb6cf221817bdd1f8cd7221661d4519372e0ac0b4cf641e11e8037de7
# 37946 bytes
```

Corroboration of the S136 anchor file (same publisher, not the assigned independent copy):

```
curl -fsSL --max-time 60 -o rfc8259.txt https://www.rfc-editor.org/rfc/rfc8259.txt
# HTTP/2 200, date Fri, 23 Oct 2026 07:08:02 GMT, text/plain;charset=utf-8
# sha256 61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7
# 28360 bytes, 899 newline-terminated lines
```

That sha256 equals the S136 row in `corpus/SOURCES.md` (`61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7`). Line numbers below for the `.txt` count `\n` only. The file also has 16 form feeds (`\f\n` at page breaks); `str.splitlines()` counts those as extra breaks and would mis-number the quote as line 440. Seven form feeds precede the quote.

## §7 quote

The sentence occurs once in each copy. It is verbatim, including the period. RFC sentence spacing puts two spaces after that period; those two spaces are not part of the quoted sentence.

Official `.txt`, section heading and the S136 line range 433–440:

```
424:7.  Strings
433:   Any character may be escaped.  If the character is in the Basic
434:   Multilingual Plane (U+0000 through U+FFFF), then it may be
435:   represented as a six-character sequence: a reverse solidus, followed
436:   by the lowercase letter u, followed by four hexadecimal digits that
437:   encode the character's code point.  The hexadecimal letters A through
438:   F can be uppercase or lowercase.  So, for example, a string
439:   containing only a single reverse solidus character may be represented
440:   as "\u005C".
```

Same words in the independent HTML (tags omitted; HTML line numbers):

- Datatracker HTML: heading `7. Strings` at line 1030 (`id="section-7"`); quote at line 1039; six-character sentence at lines 1041–1042; example `"\u005C"` at line 1046. The apostrophe in "character's" is the entity `&#x27;` (line 1043).
- RFC Editor HTML: heading at line 418 (`id="section-7"`); quote at line 427; six-character sentence at lines 429–430; example at line 434. Apostrophe is a literal `'`.

The token `\uXXXX` does not occur. The six-character form is stated in words: a reverse solidus, the lowercase letter u, and four hexadecimal digits (A–F upper or lower), with example `"\u005C"`.

Scope sitting on the next page of the same section, not inside the quoted sentence: a character outside the Basic Multilingual Plane "is represented as a 12-character sequence, encoding the UTF-16 surrogate pair" (`.txt` lines 455–459; example `"\uD834\uDD1E"`). "Any character may be escaped." is not limited to the BMP. The six-character form is.

## STD 90 / Internet Standard / December 2017

All three are true of the document. They are not all inside the frozen RFC text.

Frozen header, identical in `.txt` lines 8–10 and both HTML renderings (datatracker HTML 621–623, RFC Editor HTML 2–4):

```
Request for Comments: 8259                                    Textuality
Obsoletes: 7159                                            December 2017
Category: Standards Track
```

The `.txt` does not contain `STD 90` or `STD: 90`. Its status boilerplate says "This is an Internet Standards Track document." (`.txt` line 30). "Category: Standards Track" is the header category, not a maturity label of Proposed Standard.

Current index status, fetched the same minute:

- `https://datatracker.ietf.org/doc/rfc8259/` (HTTP/2 200, 07:08:05 GMT, sha256 `9594e926642fb20ccca81a4ad4a7de1eb2541c09b4a5ac763d3cc54a9d38b522`): lines 756–757 `RFC 8259 also known as STD 90`; lines 815–823 `RFC - Internet Standard` and `(December 2017)`. The HTML rendering's chrome says the same (`rfc8259-datatracker.html` lines 150, 196, 202). The RFC Editor HTML rendering does not contain `STD 90` or the exact maturity words `Internet Standard`.
- `https://datatracker.ietf.org/api/v1/doc/document/rfc8259/` (sha256 `80a1cee09de9224a86397e0cea385e92c8b52da9f64b8beed5d1d41ad3256ac5`): `"title": "The JavaScript Object Notation (JSON) Data Interchange Format"`, `"rfc": "8259"`, `"std_level": "/api/v1/name/stdlevelname/std/"`. That name resource (sha256 `431bd9efc1255ae9f36d8d510cc82e4dd6fbc654246f7b6b0c41c17c4776a552`) is `{"name": "Internet Standard", "slug": "std"}`.
- `https://www.rfc-editor.org/info/std90` (followed 301 to `/info/std90/`, sha256 `fce0d1f1ccf65fa83056ef8896d5c253ae3e0687209cc29206c35333fe2fe26d`): title `STD 90 subseries contains 1 RFC`; visible label `STD 90 : The JavaScript Object Notation (JSON) Data Interchange Format` with `title="STD 90 contains RFC 8259"`.
- `https://www.rfc-editor.org/info/rfc8259` (followed 301 to `/info/rfc8259/`, sha256 `6fd09811202d477f54aa65ef3f3e9d4caba2cf6ab4ab8b235b2ca774da419f4c`): `aria-label="RFC 8259 STD 90: The JavaScript Object Notation (JSON) Data Interchange Format"` and a badge whose text is `Internet Standard`.

Datatracker history (`https://datatracker.ietf.org/doc/rfc8259/history/`, sha256 `8604e3718dcce07ebee6e9a39230238a2b89ac81fd51dcaa55254e0f466e9720`), RFC Editor sync rows:

- 2017-12-13 11:17:21 -0800 (history-577026): "changed standardization level to Internet Standard, changed state to RFC, added RFC published event at 2017-12-13, changed IESG state to RFC Published".
- 2017-12-13 13:05:32 -0800 (history-577063): "created alias STD 90".

December 2017 is therefore both the header date and the publication event date, and the STD 90 alias was created the same day. A later row (2023-12-12) only re-imports membership of rfc8259 in std90.

## Lane quote check

`corpus/lessons/round-27.md` §Gate: "Any character may be escaped." — §7 Strings, rfc8259.txt line 433. Holds against this fetch (newline line 433, one occurrence).

`corpus/SOURCES.md` S136 anchor "Section 7 Strings, rfc8259.txt lines 433-440" is exactly the quote through the `"\u005C"` example. The row's raw sha256 matches this fetch. The row's parenthetical "(Dec 2017, Internet Standard STD 90)" matches the index and the 2017-12-13 history, not a string inside `rfc8259.txt`.

## Confidence and gaps

Confidence: high. Quote, six-character form, date, Internet Standard maturity, and STD 90 number were each read from a fetched page this turn.

Not unresolved, but easy to mis-cite: `STD 90` is absent from `rfc8259.txt` and from both assigned HTML renderings of the RFC body. It is on the datatracker document page, the RFC Editor info page, and the STD 90 subseries page.

No remaining unknown that blocks the three confirmations. The promotion-versus-publication question is closed by the 2017-12-13 history row above; this seat did not open the RFC Editor `rfc-index.xml` as a fourth copy.
