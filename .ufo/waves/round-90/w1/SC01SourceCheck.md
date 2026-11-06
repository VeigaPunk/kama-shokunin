# SC01SourceCheck — round 90 wave 1 (kama)

## Scope

Re-open round 90's two frozen sources independently and look for one more.

- (1) S587 — curl `--max-filesize` doc at tag `curl-8_23_0`: sha256 + located quote.
- (2) S588 — RFC 8259 §7: sha256 + located quote.
- (3) curl's own code for the abort at tag `curl-8_23_0`: file:line and a ≤25-word quote.
- (4) one candidate a careful curator should REJECT, with the reason.

Also checked: the lane's own use of these two sources (probe comments, `corpus/knowledge/probe-answer-bounds.md`),
and one falsification test of the C1 claim against a real listener answer.

Host: curl 8.23.0 (`curl --version`), python 3.14.8, Linux. Lane read-only; scratch under
`/fast/scratch/hyaku/kama-r90/SC01SourceCheck/` (removed before yield). No lane file edited; `corpus/SOURCES.md` untouched.

## Commands and outputs

```
$ curl -fsSL -o max-filesize.md https://raw.githubusercontent.com/curl/curl/curl-8_23_0/docs/cmdline-opts/max-filesize.md
$ sha256sum max-filesize.md
4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f  max-filesize.md      # == frozen S587 digest
$ grep -n "aborts the transfer if it reaches the" max-filesize.md
34:Starting with curl 8.4.0, this option aborts the transfer if it reaches the
35:threshold during transfer.
$ grep -n "exit code 63" max-filesize.md   -> 22 ;  "before curl 8.4.0" -> 30-32
$ curl -fsSL -o rfc8259.txt https://www.rfc-editor.org/rfc/rfc8259.txt ; sha256sum rfc8259.txt
61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7  rfc8259.txt         # == frozen S588 digest
$ grep -n "the control characters (U+0000" rfc8259.txt
430:   quotation mark, reverse solidus, and the control characters (U+0000   (431: through U+001F).)
```
Both digests re-fetched a second time, byte-identical. Every quote I cite was checked byte-exact against the
fetched bytes (whitespace-collapse comparison, plus line numbers); one multi-line C quote needed the collapsed
form, all others matched on the first try.

```
# curl's own code for the abort at tag curl-8_23_0
$ curl -fsSL .../curl-8_23_0/lib/sendf.c   -> sha256 deb44efc2947f106138d42946330144e2b6d51f07d7dc57c0cd5d640ca8bfb51
   (git blob d6ff92500fb62a43c66550dda6286069449c2a3b; commit 3163ec065643ba20709f190111f42c3e1fe95273)
$ grep -n "CURLE_FILESIZE_EXCEEDED" curl_lib_sendf.c
291:    return CURLE_FILESIZE_EXCEEDED;              # preceded by the message at line 288
   lib/sendf.c:288  "Exceeded the maximum allowed file size (%" FMT_OFF_T ") with %" FMT_OFF_T " bytes",
   lib/sendf.c:291  return CURLE_FILESIZE_EXCEEDED;
$ curl -fsSL .../curl-8_23_0/lib/http.c   -> sha256 40d0c67f9c8ba34431e19a3722f6af96a1d0f53c6debbea77bcbae7a44909ba1
$ grep -n "CURLE_FILESIZE_EXCEEDED" curl_lib_http.c
3306:  (Content-Length overflow)   3871:  return CURLE_FILESIZE_EXCEEDED;   # "Maximum file size exceeded" at 3870
$ curl -fsSL .../curl-8_23_0/include/curl/curl.h -> sha256 ad8989a81e79b407355e14d673410d51420bfec48287f4b890d0b211d9235ec3
$ grep -n "CURLE_FILESIZE_EXCEEDED" curlver.h2
594:  CURLE_FILESIZE_EXCEEDED,       /* 63 - Maximum file size exceeded */
$ curl -fsSL .../curl-8_3_0/lib/sendf.c | grep -c max_filesize   -> 0     # pre-8.4.0 has no such check
$ curl -fsSL .../curl-8_4_0/RELEASE-NOTES ; grep -n "max filesize option stop too big"
94: o lib: let the max filesize option stop too big transfers too [44]
   (commit 914e49b9b737, 2023-09-23: "Previously it would only stop them from getting started if the size is known to be too big then.")
$ curl -fsSL https://www.rfc-editor.org/errata/rfc8259 | sha256sum   # 5819db2e0233addf17ed540db88cf92cbefda5a60c38877e0d4cbf6b876b7cf4 (x3, stable)
   errata 7673 Status: Rejected (Zachary Collier, 2023-10-11; rejected by Andy Newton 2026-05-28)
$ curl -fsSL https://curl.se/docs/manpage.html | sha256sum              # 3d01dafc630b08f29d6a6871120308558a7c6c2359dc13289289b1cd5fe27199
   line 572: "This man page describes curl 8.23.1."   # no curl-8_23_1 tag; latest release curl-8_23_0; master = 8.23.1-DEV
$ curl -fsSL .../curl/master/docs/cmdline-opts/max-filesize.md | sha256sum
4bbc00ec37d8cab75479a7803a80552019e0bca6d83f68ecddf9feb893ea038f   # master == curl-8_23_0 text
```

Falsification test (lane-owned stub on a free loopback port, killed after):

```
# stub answers /v1/models with header "Server: llama\x9bpp" (a C1 byte)
$ bash probeM.sh listeners --port <free> --expect '*' --registry <lane>/registry/endpoint-consumers.tsv --json
PROBE(M) EXIT=1
stderr: UnicodeDecodeError: 'utf-8' codec can't decode byte 0x9b in position 718: invalid start byte
        kama-probe: internal error: generated JSON failed to parse (this is a probe bug)
```
`probeM.sh` = `tools/kama-probe.sh` at the C1 measured commit `f968fb19bb2a0c2afe271bfe606f11b52d10823f`
(`strip_ctl` at that commit: `LC_ALL=C tr -d '\000-\037\177'` — bytes ≥ 0x80 survive). The same stub against
the current lane tip (`1f8eed67`, `strip_ctl` = `tr -d '\000-\037\177-\377'`) exits 0 and emits valid JSON.

## Findings

**NOTE — both frozen sources are confirmed, digests and quotes exact.**
S587: sha256 `4bbc00ec…` and the sentence "Starting with curl 8.4.0, this option aborts the transfer if it reaches
the threshold during transfer." sit byte-exact at `max-filesize.md:34-35`; the exit-63 sentence is at line 22 and
the pre-8.4.0 caveat at lines 30-32, so the lane's `probe-answer-bounds.md` line anchors (S587 lines 20-22, 30-32,
34-35) are correct. S588: sha256 `61a5378f…`, quote byte-exact at `rfc8259.txt:429-431`; RFC status still
INTERNET STANDARD. No correction needed to either row.

**NOTE — the "one more" source: curl's own code, which pins the claim to bytes, not prose.**
`lib/sendf.c:288-291` at `curl-8_23_0` is where the cap aborts mid-transfer (`"Exceeded the maximum allowed file
size (%" FMT_OFF_T ") with %" FMT_OFF_T " bytes",` → `return CURLE_FILESIZE_EXCEEDED;`); `lib/http.c:3867-3871`
is where a declared-oversize body is refused before any byte is read (`"Maximum file size exceeded"` →
`CURLE_FILESIZE_EXCEEDED`); `include/curl/curl.h:594` binds that constant to exit code 63, the code the probe's
`case 63)` branch keys on. `curl-8_3_0/lib/sendf.c` contains no `max_filesize` check at all and curl 8.4.0's
RELEASE-NOTES line 94 names the change — so S587's version boundary is visible in curl's code, not only in its
docs. Candidate rows S591-S594 are in the out dir.

**NOTE — the reject candidate: the floating curl.se manpage.** `https://curl.se/docs/manpage.html` carries the same
abort sentence, but its bytes change with every release (no digest pins it), and it self-declares "This man page
describes curl 8.23.1." while no `curl-8_23_1` tag or release exists upstream — the newest release is
`curl-8_23_0` and master is `8.23.1-DEV`. It therefore cannot describe the host's 8.23.0 build. Runner-up reject:
the pre-8.4.0 doc at `curl-8_3_0` (`docs/cmdline-opts/max-filesize.d:21-23`), which says the option "has no effect"
on an unknown-length body — the opposite of the frozen rule for the host's curl.

**DEFECT — the lane over-claims what RFC 8259 §7 requires.** RFC 8259 §7's MUST-escape set is exactly
U+0000-U+001F (lines 429-431); U+007F and U+0080-U+009F are *not* in it. The ABNF's `unescaped` production
(line 479, `%x20-21 / %x23-5B / %x5D-10FFFF`) permits those code points literally, and the erratum that would have
added them (7673) was **Rejected** by the IESG on 2026-05-28. Yet `tools/kama-probe.sh:211` (at M, M2 and tip)
cites "S588 RFC 8259 section 7" as the reason "every other control character U+0001-U=001F **and DEL** is escaped",
and `corpus/knowledge/probe-answer-bounds.md:30-34` presents DEL/C1 escaping as RFC-driven. The escaping itself is
correct and harmless (RFC 8259 §7 line 433 permits escaping any character); the *citation* is over-broad. No
predicate changes; this is a provenance/attribution defect the L1 should fix by narrowing the S588 citation to
U+0000-U=001F and citing §8.1 (UTF-8, lines 485-486) for the byte-validity rule. Candidate rows S589, S590, S595.

**DEFECT — measured at M and M2, the probe's `--json` output breaks on a C1 byte in a header.** A listener answering
`Server: llama\x9bpp` makes the probe at `f968fb19` (the C1 measured commit) die with
`UnicodeDecodeError: 'utf-8' codec can't decode byte 0x9b` → `kama-probe: internal error: generated JSON failed to
parse (this is a probe bug)`, exit 1, empty stdout. Root cause is the source-level one S588/S589 point at: §8.1
requires JSON text to be UTF-8, and a raw 0x80-0xFF byte is not valid UTF-8; at M `strip_ctl` deletes only
`\000-\037\177`, so the byte reaches the JSON. The frozen C1 counter's 13 cells do not cover it (H7 uses ESC, a C0
byte), which is why the predicate stayed green. The lane tip `1f8eed67` already repairs it
(`strip_ctl` = `tr -d '\000-\037\177-\377'`) — my run against the tip exits 0 with valid JSON — so this is a
**harm/attribution gap at the measured commits M and M2**, not a live defect at tip. It is reported because the
frozen C1 receipts were taken at M, where the probe can abort on a hostile answer.

**NOTE — freshness.** The pinned `curl-8_23_0` doc is byte-identical to upstream master's copy (same sha256), and
`curl-8_23_0` is the newest upstream release (published 2026-10-14); master is `8.23.1-DEV`. The host's curl is
8.23.0. RFC 8259 remains the current Internet Standard and its only reported erratum (9095) touches §11, not §7.
Both frozen sources are fresh as of 2026-11-06; no recheck urgency.

**NOTE — no tooling installed.** Nothing was missing for this seat, so no package was installed; no update-safety
gate was needed.

## Deliverables

- `.ufo/waves/round-90/w1/out/SC01SourceCheck/SOURCES-candidates.md` — 11 candidate SOURCES rows in the lane's
  11-column format: S587/S588 re-verifications (admit, unchanged), new S589-S595 (admit), S596/S597 (reject,
  with reasons). Every row carries URL, access date 2026-11-06, sha256, the located quote with its line, and an
  explicit admit/reject + reason.
- `.ufo/waves/round-90/w1/SC01SourceCheck.md` — this report.

`corpus/SOURCES.md` was not edited. Scratch `/fast/scratch/hyaku/kama-r90/SC01SourceCheck/` removed.

VERDICT: holds — S587 and S588 re-verify byte-exact with unchanged digests and correct line anchors; curl's own
code (sendf.c:288-291, http.c:3867-3871, curl.h:594) corroborates the abort and exit code 63 at the pinned tag, one
reject candidate is identified (the floating curl.se manpage), and one over-broad RFC 8259 §7 citation plus one
hostile-C1-byte abort present at the measured commits M/M2 are reported for the L1.
