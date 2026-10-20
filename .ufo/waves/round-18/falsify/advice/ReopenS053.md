VERDICT: confirm — the S053 quote is verbatim at `automake-1.19/doc/automake.texi:9776–9777` in the official GNU-signed Automake 1.19 tarball, and the committed registry records S053 as `rejected` with `opened 2026-10-20`, not mined; only low-severity bookkeeping nits below.

# ReopenS053 — Automake 1.19 as a rejected basis

Lane state: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` =
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. `git show HEAD:corpus/lessons/round-18.md | sha256sum` =
`13142d960465790f4955e4e1698ae4a66dccf4a897049ad04bf97faa69e1f253`, equal to the working file, so
the Gate row read below is committed at the claimed revision.

Authoritative locations read:

- `corpus/lessons/round-18.md:35–36` — "Newly written rows S048–S054 are all tier A within their
  narrow scopes (S053 rejected as a basis)."
- `corpus/lessons/round-18.md:49` — Gate row: candidate "Automake defines the lane's exit numbers",
  decision "reject S053 as basis", URL `https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz`
  member `doc/automake.texi`:9776–9777, quote "an exit status of 77 a skipped test, an exit status
  of 99 a hard error", plus "Canonical www.gnu.org page timed out."
- `corpus/SOURCES.md:65` — S053 row: kind `docs`, tier `A`, scope "exit statuses of Automake's
  default test harness without a test protocol", anchor "texi lines 9774-9777", status `rejected`,
  opened `2026-10-20`, recheck `on-release`, used-by `—`.

## Independent opening of the official release

All work was read-only on the lane; the tarball was fetched into `/tmp/kama-r18-falsify-ReopenS053`
and deleted afterward. No lane runtime or gate command was executed.

```
cd /tmp/kama-r18-falsify-ReopenS053
timeout 90 curl -sS -o automake-1.19.tar.xz -w 'http=%{http_code} size=%{size_download} time=%{time_total}\n' \
  https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz
→ http=200 size=1682600 time=1.224521
sha256sum automake-1.19.tar.xz
→ e3e2c2e3abf37898138db5b6c1d1dc35c9160c5978be7947d2c741705251d445
```

That digest equals the pinned bytes at
`.ufo/waves/round-18/sources/raw/ftp.gnu.org/gnu/automake/automake-1.19.tar.xz` (same
`sha256sum`) and `pins.json.sources.automake_release.sha256`; size 1682600 equals
`pins.json.sources.automake_release.bytes`. Release provenance was checked against GNU's own
keyring, not merely the host:

```
timeout 30 curl -sS -o automake-1.19.tar.xz.sig -w 'http=%{http_code} size=%{size_download}\n' \
  https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz.sig
→ http=200 size=228
timeout 90 curl -sS -o gnu-keyring.gpg -w 'http=%{http_code} size=%{size_download}\n' \
  https://ftp.gnu.org/gnu/gnu-keyring.gpg
→ http=200 size=3698125
gpgv --keyring ./gnu-keyring.gpg automake-1.19.tar.xz.sig automake-1.19.tar.xz
→ gpgv: Signature made Thu 10 Sep 2026 02:01:41 AM -03
→ gpgv:                using EDDSA key D5D527E7E338A682CBADB1C1217FCF7314636C07
→ gpgv: Good signature from "Kamila Szewczyk <k@iczelia.net>"
→ gpgv_exit=0
```

The member was extracted from those verified bytes:

```
tar -xJf automake-1.19.tar.xz automake-1.19/doc/automake.texi automake-1.19/doc/version.texi
sha256sum automake-1.19/doc/automake.texi
→ 6d34777affbbadfd7728b41873251768f5808691dac56f704189dec5fe53b6e6  (558617 bytes, 14345 lines)
sha256sum automake-1.19/doc/version.texi
→ ba558fc251f18236f4d5ccaeaa4055e22027438a48e702991fa3258452d263a5  (100 bytes)
cat version.texi
→ @set UPDATED 3 September 2026 / @set UPDATED-MONTH September 2026
→ @set EDITION 1.19 / @set VERSION 1.19
```

Both member hashes equal `pins.json.documents.automake_texi.sha256` /
`documents.automake_version.sha256`, and the on-disk pinned copies
(`.ufo/waves/round-18/sources/raw/ftp.gnu.org/gnu/automake/automake-1.19/doc/{automake,version}.texi`)
hash to the same values. So the pin is reproducible from the live official release, not just a
saved copy.

## Quote verification

`awk 'NR>=9775 && NR<=9777 {printf "%d:%s\n", NR, $0}'` on the freshly extracted member:

```
9775:When no test protocol is in use, an exit status of 0 from a test script will
9776:denote a success, an exit status of 77 a skipped test, an exit status of 99
9777:a hard error, and any other exit status will denote a failure.
```

- The Gate's quoted fragment starts inside line 9776 and ends inside line 9777. `9776–9777` is
  the correct line span; the full sentence starts at 9775.
- Word count of the Gate quote: 16 (`len(q.split())`), within the ≤25-word rule.
- Span hash of lines 9775–9777 (`\n`-joined, UTF-8):
  `e0fbcb97b4b11a8509ddf8a0dd64756890015088fd9c6c80ec681c48d3664122`, identical to
  `pins.json.pins.automake_source_exit_conventions.verbatim_sha256`; that pin's four sub-quotes
  (`exit status of 77 a skipped test`, `exit status of 99 a hard error`, etc.) are all recorded
  `matched: true`, range `[[9775, 9777]]`.
- The `@node Scripts-based Testsuites` is at line 9748 and the statement at 9773–9777, so the
  SOURCES anchor "texi lines 9774-9777" is a superset (two `@cindex` lines included), not a false
  location.

## Rejected-as-basis reason

The reason holds. The source sentence is explicitly governed by "When no test protocol is in use"
(line 9775) and defines the exit status of *Automake's own default test harness/test scripts*:
0 success, 77 skipped, 99 hard error, other failure. It cannot define kama's exit table, so the
Gate candidate "Automake defines the lane's exit numbers" is correctly rejected as a basis.

The lane's not-evaluated number is its own, not Automake's:

- `.ufo/waves/round-18/c1/measure.py:23` — "unverifiable or mismatching frozen bytes exit 2
  before controls run."
- `.ufo/waves/round-18/c1/measure.py:159` — `MeasureFault` docstring: "measure.py could not take
  the measurement (exit 2, never a verdict)."
- `grep -rnE '(^|[^0-9])(77|99)([^0-9]|$)' tools/kama-llamacpp-live.py tests/llamacpp-live/
  tests/probe-verdicts/ .ufo/waves/round-18/c1/ .ufo/waves/round-18/c2/
  .ufo/waves/round-18/dispatch-provenance.py` produced no matches, and
  `grep -rn 'S053' tools/ tests/ .ufo/waves/round-18/c1/ .ufo/waves/round-18/c2/`
  exited 1 (no references). No lane code depends on Automake's 77/99.
- S052 already supplies the empty-observation precedent (pytest exit 5 vs 1) at
  `corpus/SOURCES.md:64`; Automake adds no distinct empty-observation status, so nothing is lost
  by rejecting S053 as a basis. The row's flip condition ("an Automake-based runner needing this
  exact harness contract enters the lane's scope") is coherent with the opened scope.

## Bookkeeping: opened, not unopened, not mined

Committed registry (`corpus/SOURCES.md:65`): `status=rejected`, `opened=2026-10-20`,
`recheck=on-release`, `used-by=—`; the source cell states "(opened as
`automake-1.19/doc/automake.texi` in https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz; the
www.gnu.org page timed out on 2026-10-20)". The search log in the same file says the round "included
6 mined rows S048–S052/S054, excluded 1 as a basis (S053 retained rejected with flip condition)".
The lesson Gate preamble (`round-18.md:32–33`) says "All sources below opened 2026-10-20", and its
S053 row says "reject S053 as basis". No authoritative corpus file records S053 as `mined` or
`unopened`:

```
grep -rn 'S053\|[Aa]utomake' SCORECARD.md corpus/QUALITY.md corpus/knowledge/ README.md tools/ \
  tests/ .ufo/waves/round-18/runs/
→ no matches
```

The pin record is honest about the HTML page not being opened:

```
pins.json.sources.automake_page.status = "unreachable"
pins.json.sources.automake_page.error  = "URLError: <urlopen error timed out>"
pins.json.pins.automake_html_exit_conventions = {"doc":"automake_html","status":"not-evaluated",
                                                 "reason":"source-unavailable"}
pins.json.unevaluated = ["automake_page: URLError: <urlopen error timed out>",
                         "automake_html_exit_conventions: source-unavailable"]
pins.json.failures = []
pins.json.documents = {automake_texi, automake_version}   # no automake_html document
```

Reproduction of the timeout today:

```
timeout 35 curl -sS -o gnu-page.html -w 'http=... size=... time=...' \
  'https://www.gnu.org/software/automake/manual/html_node/Scripts_002dbased-Testsuites.html'
→ curl_exit=124   (no file written)
```

and there is no saved `raw/www.gnu.org/...` page on disk (`test -e` exit 1). This does not prove
permanent unreachability, but it corroborates the recorded reason on the report date.

The official run exercised the pin: `.ufo/waves/round-18/runs/commands.json` records
`source-pins-selftest` as `python3 .ufo/waves/round-18/sources/pin.py --selftest`, `exit=0`,
`expected_exit=0`, `as_expected=true`, at `2026-10-20T22:36:27Z`; `pins.json.pinned_at_utc` is
`2026-10-20T21:29:29+00:00`, consistent with a same-day open.

## Low-severity notes (none change the verdict)

1. The committed build draft `.ufo/waves/round-18/build/drafts/sources-python.md:11` still proposes
   `| mined | 2026-10-20 | on-release | corpus/lessons/round-18.md (L1 to write), C2 test-runner
   exit convention notes |` for S053. The integrated registry row overrides it to `rejected` and
   `used-by —`; the draft header says "Status: draft for L1 integration. Nothing here edits
   corpus/SOURCES.md". This is the only `mined` record found anywhere for S053, and it is a
   superseded build artifact, but a reader of the draft alone could be misled. Worth a one-line
   correction note if the draft is ever cited.
2. Gate location shorthand: the actual tar member is `automake-1.19/doc/automake.texi`
   (`tar -tJf`), while the Gate row writes "member `doc/automake.texi`". The SOURCES row and
   `pins.json.documents` give the exact member path, so the reference resolves, but it is not
   byte-exact.
3. `pins.json.sources.automake_page.saved_as` names
   `raw/www.gnu.org/software/automake/manual/html_node/Scripts_002dbased-Testsuites.html`, a file
   that does not exist. The same record has `status: unreachable`, no `sha256`/`bytes`, no
   `documents` entry, and the derived pin is `not-evaluated`; so this is a naming convention
   (intended path) rather than a claim that the page was saved. A future reader should not treat
   `saved_as` alone as evidence of bytes.
4. The Gate quote is a fragment and omits the governing qualifier "When no test protocol is in
   use" (line 9775). The SOURCES `scope` cell carries that qualifier ("default test harness
   without a test protocol"), and the row is a rejection, so the omission cannot license an
   overclaim; kept visible here because the quote alone is broader than the source sentence's
   condition.

## Limits

- I did not open the www.gnu.org HTML page either; the 35 s fetch timed out. I make no claim about
  that page's bytes or version. The row's basis is the tarball member, which was opened and
  hash/signature-verified; the HTML page is explicitly recorded as not the basis.
- The installed Arch `automake 1.19-1` info copy independently carries the same sentence
  (`/usr/share/info/automake.info-2.gz:1290`; concatenated main-first line 8478, matching the
  seat's draft line claim). This is corroboration only, not part of the registry basis.
- Line numbers 9776–9777 are valid for the pinned 1.19 bytes
  (`sha256 6d34777a…`); they are not stable across Automake versions.

## Installs / footprint

- No installs, no pacman transaction, no systemd/config/service change.
- Tools used read-only: `curl`, `tar`/`xz`, `sha256sum`, `gpgv` with a downloaded GNU keyring,
  `awk`/`sed`/`grep`, `python3` (stdlib only) for JSON/hash inspection.
- No listeners were started; no registered port or loopback service was contacted.
  `ss -ltnp | grep -c kama-r18-falsify-ReopenS053` = 0.
- Scratch `/tmp/kama-r18-falsify-ReopenS053` removed after writing this report; only this report
  remains.
