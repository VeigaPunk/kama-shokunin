# EX01OriginFixtures — round 86 w2 — C3 freshness refusal arms (falsification)

Revision measured: `67eddac89f44e768b670301ea0feff06e766f32d` (clone HEAD, verified `rev-parse HEAD`).
Tool under test: `tools/round86-pin-origin.py`, sha256 `6c90e3885e6e67f005a85f955ab353e2c25ed56a9801ad560f331552dbb96b4a`
(identical to `git show 67eddac:tools/round86-pin-origin.py`; the source worktree copy is unmodified).
Fixture: scratch clone `git clone --no-hardlinks` of the fleet repo (toplevel asserted before every commit), `--repo` = that clone, row file committed per case and passed as `--rev <commit>`. Upstream: in-process `ThreadingHTTPServer` on `127.0.0.1` (ephemeral port), one upstream file per case. No external network.
Driver: `out/EX01OriginFixtures/drive.py`; log `out/EX01OriginFixtures/run.log`; per-case `*.out`/`*.err`; committed row and anchor bytes in `out/EX01OriginFixtures/rows/`.
Tooling: no installs. Python 3.14.8 (host). Scratch removed after receipts were copied.

Command shape per case (exact):
`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-pin-origin.py --repo /fast/scratch/hyaku/kama-r86/EX01OriginFixtures/fixture --rev <commit>`
(default `--rows registry/pin-recheck-rows.tsv`; exit read from the subprocess return code).

## Required cases (a)–(e)

| case | rev (fixture commit) | tool stdout (line 1 / row line) | exit | verdict vs. expectation |
|---|---|---|---|---|
| (a) byte-identical | b1e6da4a | `PIN_ORIGIN rows=1 verified=1 mismatch=0 unreachable=0 bad=0`; row `verdict=verified anchors=2/2` | 0 | correct |
| (b) hash-consistent, bytes differ from upstream | 0856bb8a | `rows=1 verified=0 mismatch=1`; row `verdict=mismatch anchors=1/2` ("stored body differs from upstream 2-4") | 1 | correct (`mismatch`, not `verified`) |
| (c) digest lie (header sha = 0×64) | fa116ce3 | `rows=1 verified=0 mismatch=0 bad=1`; row `verdict=bad` ("declared digest does not match") | 1 | correct |
| (d) range outside upstream (5-99 of 6 lines) | 188f2261 | `rows=1 mismatch=1`; row `verdict=mismatch` ("declared range 5-99 outside upstream (6 lines)") | 1 | correct |
| (e) malformed header (`sha256=abc`) | 9bd61c0d | `rows=1 bad=1`; row `verdict=bad` ("malformed anchor header") | 1 | correct |

Selftest (`--selftest`, pristine tool at 67eddac): `PIN_ORIGIN_SELFTEST pass=7 fail=0`, exit 0.

So the five named refusal arms behave as the predicate requires on this host, measured at 67eddac.

## Extra falsification probes (my own, same instrument, same harness)

The predicate says: exit 0 only when every row's anchor extracts "match the live upstream bytes at their declared ranges". The probes below test that clause beyond the five named cases.

| case | rev | tool result | exit | assessment |
|---|---|---|---|---|
| X1 CRLF upstream (`L1\r\nL2 crlf\r\nL3 crlf\r\nL4\r\n`), committed body LF `L2 crlf\nL3 crlf\n`, lines 2-3 | f77e51bb | `rows=1 verified=1`; both anchors `upstream 2-3 byte-identical` | 0 | **FALSE VERIFIED.** Upstream bytes at 2-3 contain `\r\n`; stored body does not. `str.splitlines()` strips `\r`, so the window compares equal. Violates "byte for byte". |
| X2 upstream last line has no final newline (`...L3 nonl` EOF), body `L2 nonl\nL3 nonl\n`, lines 2-3 | 4682cc53 | `rows=1 verified=1` | 0 | **FALSE VERIFIED** (bytes at 2-3 end without `\n`; the window adds one unconditionally). |
| X3 form feed inside upstream line 2 (`L2 before\x0cFF-AFTER`), body `FF-AFTER\n`, lines 2-2 | eb50dd02 | `rows=1 mismatch=1` | 1 | Correct for this body (`splitlines` sees line 2 as `L2 before`); but shows line numbers used by the tool differ from `\n` line numbering. |
| X3b form feed fabricated body: upstream `L1\nAAA\x0cBBB\nL3\n`; both anchors declare lines 3-3 with body `BBB\n` (the `splitlines` fragment of line 2, not the LF line 3 `L3`) | bb2973f5 | `rows=1 verified=1`; both `upstream 3-3 byte-identical` | 0 | **FALSE VERIFIED — fabricated extract graded verified.** Under the declared LF line 3 (`L3`) the body is not upstream bytes. This hits the C3 kill rule ("a fabricated hash-consistent extract that grades verified"). |
| X4 inverted range `lines=4-2`, body `\n` (blank line), upstream 6 lines | e1133be7 | `rows=1 verified=1`; `upstream 4-2 byte-identical` | 0 | **FALSE VERIFIED.** `start > end` is not refused. `text_lines[3:2]` is empty, and `"" + "\n" == "\n"`, so an empty window matches a blank stored body. No upstream bytes exist at 4-2. |
| X5 register with only the header line (all rows removed) | abfb596b | `PIN_ORIGIN rows=0 verified=0 mismatch=0 unreachable=0 bad=0`, no row lines | 0 | **Vacuous green.** Exit is 0 because `verified == rows == 0`. The predicate's `rows=5 verified=5` is not enforced; a truncated register is green. Also `parse_rows` only refuses a file with no non-comment lines at all, not a header-only file. |

Informational (not a falsification): X3 shows the tool counts lines with `str.splitlines()` (form feed, `\r`, U+2028 etc. are line breaks), while `git`-committed anchors and their digests use `\n`. This produces both the X1/X3b false verifies and false mismatches in other shapes.

## Code basis (read at 67eddac, lines as in the file)

- `check_anchor` window: `text_lines = upstream.decode(...).splitlines()`; `window = "\n".join(text_lines[start-1:end]) + "\n"` — explains X1, X2, X3b (`splitlines`, unconditional trailing `\n`).
- Range check: `if info["end"] > len(text_lines) or info["start"] < 1` — no `start <= end` check; explains X4.
- `grade`/`main`: exit `0 if result["verified"] == result["rows"] and ...`; zero rows passes — explains X5.
- Anchor is read via `git show <rev>:<rel>` (text mode); the stored digest is over the same text. Not a falsification in this round.

## Verdict on C3 (freshness)

- Named refusal arms (a)–(e): **hold** at 67eddac on this host (verdict tokens and exit codes above).
- Predicate clause "a hash-consistent extract whose bytes differ from upstream is `mismatch`, never `verified`": **falsified** by X3b (fabricated `BBB\n` graded `verified`), and by X1 / X2 / X4 (bytes differ or range is not upstream bytes, graded `verified`). The C3 kill rule ("a fabricated hash-consistent extract that grades `verified`") fires on X3b.
- Predicate clause "exits 0 only when ... `PIN_ORIGIN rows=5 verified=5`": **not enforced** — X5 exits 0 with `rows=0`.

Suggested minimal fixes for the author/L1 to weigh (advice only; no production edits made): compare against the upstream lines split on `\n` (not `splitlines`) and compare the raw bytes including `\r` and a final newline; refuse `start > end`; require `rows >= 1` (or `rows == 5`) for exit 0.

## Scope / honesty notes

- Fixture leg only, as assigned; no live fetch of the real anchor URLs was made.
- The row file was the only variable: `--repo` pointed to the scratch clone and each case used a separately committed `registry/pin-recheck-rows.tsv`; the tool file is the unmodified 67eddac copy (sha above).
- Revision-measured `67eddac89f44e768b670301ea0feff06e766f32d`; the fixture commits are scratch commits with their own hashes (listed in `rows/commits.txt`), not product commits.
- No production file, no fleet-repo mutation, no mutating git in the fleet repo, no config/credential reads.
- Receipts: `.ufo/waves/round-86/w2/out/EX01OriginFixtures/` (`*.out`, `*.err`, `run.log`, `summary.json`, `selftest.out`, `tool.sha256`, `rows/`, `drive.py`).
