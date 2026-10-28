# X04Regress3 - C2 sensitivity: planted regressions for pin-watch, digest-ledger, hexrun-census

Seat: round 64 wave b, advisory leaf. No lane file edited. Everything ran in my scratch clone
(`/fast/scratch/hyaku/kama-r64/b/X04Regress3/clone`, base f6a4ea9a; one wip commit
a0efebaf = f6a4ea9a + one hexrun-ledger row, see Finding 1). No tool installed.

## Deliverable
`.ufo/waves/round-64/b/out/X04Regress3/capability-regress-r64.part3.tsv` (TAB: cap, tool_path, find, replace; no header; no tabs in cells):

| cap | tool_path | find (exactly once in file) | replace |
|---|---|---|---|
| pin-watch | tools/pin-watch.py | `newer = sum(1 for k in tags.values() if k > key)` | `... if k >= key)` |
| digest-ledger | tools/digest-ledger.py | `h = hashlib.sha256() if typ == "blob" else None` | `... if typ == "tree" else None` |
| hexrun-census | tools/hexrun-census.py | `if len(token) == 40 and token in self.lane_oids:` | `if len(token) == 41 and ...` |

Why each is not a pattern deletion:
- pin-watch: the "newer" count now includes the pin itself, so every `current` pin reads `behind` and every `newer=N` is off by one; selftest cases fail, summary becomes `pass=6 fail=3`, exit 1.
- digest-ledger: the blob set is built from tree-object digests instead of blob digests; no cited digest matches a blob, so they fall to external/unknown (`blob=0 ... unknown=129`), exit 1.
- hexrun-census: git object ids are no longer recognised as lane oids (`lane_oid=0`, `unknown=278`), exit 1.

## Evidence (driver `out/X04Regress3/drive.py`, full transcript `drive.out`, raw outputs `<cap>.{U,M}.out`)
Method: `git archive a0efebaf tools registry` -> tree U; copy -> tree M with the single replacement applied; `py_compile` and `importlib` exec of the mutated file both succeed (importable); template run verbatim from registry/capability-claims-r63.tsv with %T = tree, %S = fresh scratch, %R = clone, TIPREV = a0efebaf, env allowlist PATH/HOME/LANG/LC_ALL/TMPDIR, cwd = tree. Verdict = pattern in stdout and exit 0 (round-63 `verdict_fn`).

| cap | pattern | unmutated (exit, pattern, last line) | mutated (exit, pattern, last line) | verdict U -> M |
|---|---|---|---|---|
| pin-watch | `selftest pass=9 fail=0` | 0, present, `selftest pass=9 fail=0` | 1, absent, `selftest pass=6 fail=3` | true -> false |
| digest-ledger | `unknown=0` | 0, present, `tokens=149 blob=130 external_ok=10 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` | 1, absent, `tokens=149 blob=0 external_ok=11 external_absent=1 unverifiable=7 wrong_flagged=0 ledger_bad=1 wrong_unflagged=0 unknown=129` | true -> false |
| hexrun-census | `unknown=0` | 0, present, `tokens=2092 distinct=404 lane_oid=281 md5_blob=1 upstream_ok=109 unverifiable=10 wrong_flagged=3 ledger_bad=0 unknown=0` | 1, absent, `tokens=2092 distinct=404 lane_oid=0 md5_blob=1 upstream_ok=112 unverifiable=10 wrong_flagged=2 ledger_bad=1 unknown=278` | true -> false |

Each mutant flips on both legs independently (pattern absent AND exit != 0), so it survives neither a pattern-only nor an exit-only verdict. `find_count=1` for all three (str.count on the whole file).

## Findings for the L1
1. **hexrun-census row is already false at the freeze tip f6a4ea9a and at the base 0c1eff3c.** Unmutated run at f6a4ea9a (real lane repo and clone alike): `tokens=2092 distinct=404 ... unknown=1`, exit 1 (`out/X04Regress3/hexrun-freeze-tip-baseline.txt`). Cause: `72c7713ef48cd5d5d02964ece2975602e3402a08` (fleet-repo commit of the round-63 kama report) is cited twice in corpus/lessons/round-63-verifier-spotcheck.md (lines 5 and 17) and is not in the lane object store (`git cat-file -t` fails). Round 63's r63 row was true before that lessons file existed. The r64 counter's "bound run is a declared outcome" check, and the baseline-met precondition for crediting regressions, will fail unless a ledger row lands. I added this row in my clone (diff in `hexrun-ledger-row.diff`) and then the unmutated run is `unknown=0`, exit 0:
   `72c7713ef48cd5d5d02964ece2975602e3402a08<TAB>unverifiable<TAB><TAB><TAB><TAB>2026-10-28<TAB>fleet-repo commit of the round-63 kama report cited in round-63 verifier spot-check; fleet objects are not in the lane object store, git cat-file -t fails here`
   (The two precedent rows 124/125 use class `upstream` with a committed fleet-commit-evidence.json; `unverifiable` needs only a note >= 10 chars.) Any new 40/32-hex run cited in later round-64 documents (lessons, SCORECARD) has the same exposure: re-run the scan at the final tip.
2. Unmutated digest-ledger at the same tip is green (`unknown=0`, exit 0). pin-watch selftest is green (9/0).
3. Scale note: `git archive` + copy of the full tip tree is 35,697 files / 456 MB; copying it (shutil.copytree/rmtree) blew a 300 s cap on a busy host. The three tools read only `%T/tools/<tool>.py` and the repo at TIPREV, so a counter that copies only `tools/` (plus the one mutated file) per regression is enough and ~100x cheaper; my proof used `tools registry` only.
4. Substring caveat, no action needed: pattern `unknown=0` is matched as a substring; it cannot be spoofed by `unknown=0N` (counts have no leading zeros), but a printer that emits the literal `unknown=0` is exactly the control the printer-rejection family covers.

## Not-possible rows
None: all three rows admit a one-line live regression.

## Cleanup
Scratch `/fast/scratch/hyaku/kama-r64/b/X04Regress3` removed at yield; receipts copied to out dir.
