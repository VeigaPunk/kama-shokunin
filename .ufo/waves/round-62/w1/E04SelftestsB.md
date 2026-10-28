# E04SelftestsB — heavier bound selftests (round 62, w1)

Seat: leaf executor. Item: run the two heavier bound selftests and report their pass
lines and exit codes. This is a measured instrument check, not a verdict on C1/C2.

## Environment / pinning

| fact | value |
|---|---|
| lane tip (`git rev-parse master`) | `65d7cad0fce90e34de37527cde22e97b63b118bf` |
| tools/append-only-audit.py @ tip | clean (`git status --porcelain` empty), sha256 `343e8c18cab102fceb0c8735b60916015f2bfc6dbe4423e45471c7558c97d459`, last commit `c5ec93d5` |
| tools/kama-live-replay.py @ tip | clean, sha256 `29b473989fbbe01dd72cbb075d8096fde3b8d45c0c1395566de16d4c14fd605c`, last commit `c5ec93d5` |
| python3 | 3.14.8 (GCC 16.2.1) |
| git | 2.56.0 |
| scratch | `/fast/scratch/hyaku/kama-r62/w/E04SelftestsB/{aoa,klr,tmp-aoa,tmp-klr}` (explicit `--scratch`, explicit `TMPDIR`) |

Both selftests were read before running: `append-only-audit.py --selftest` builds its own
throwaway fixtures via `git init`/`git commit` under `--scratch` (toplevel asserted inside
the fixture, `Fixture.__init__`) and removes them; `kama-live-replay.py --selftest` is fully
offline (`file://` accepted only under `allow_file`), fabricates a fake archive/model/live
tool under `--scratch` and never touches the lane checkout. Neither runs git writes against
the lane, so no sandbox clone was required. Lane touched read-only.

## Result

| selftest | pass line | exit |
|---|---|---|
| `python3 tools/append-only-audit.py --selftest --scratch $S/aoa` | `AOA_SELFTEST pass=51 fail=0` | **0** |
| `python3 tools/kama-live-replay.py --selftest --scratch $S/klr` | `KLR_SELFTEST pass=48 fail=0` | **0** |

Wall time: 1.94 s (aoa); klr completed in the same batch window. No `fail`, no case
`exception`, no stderr lines in either capture.

### append-only-audit.py — 51 named cases, all `pass`
`no-deletion, below-threshold, exact-threshold-unrestored, restored-later, partial,
undeclared-file, declared-file-removed, merge-first-parent, dashdash-lines, crlf-and-eof,
multiset, window-max, relocation, contract, threshold-flag, crlf-restore-exact,
dup-kept-not-restored, final-segment, vanished-and-paths, exempt-rewritten, exempt-gutted,
exempt-gutted-then-regrown, dated-rewritten, only-errata, clamp, bad-declarations, clean,
preamble-graded, launder-through-head, binding-v4, wildcard-token-bound,
origin-preamble-moved-under-head, negation-window-three-vs-four, negation-curly-apostrophe,
origin-multi-title, negation-typographic-isnt, v6-default-threshold, v6-arow-mutable,
v6-arow-immutable, v6-arow-code-span-pipe, v6-arow-row-dropped, v6-disclosed,
v6-bad-disclosures, v6-in-place-edit-class, v6-partial-disclosure,
v6-restored-not-disclosable, v6-two-files-one-commit, v6-ledger-cutoff, v6-revert-class,
v6-crlf-key-and-ledger-cr, v6-short-id-not-a-row`

### kama-live-replay.py — 48 named cases, all `pass`
`match, check-differs, model-digest-wrong, asset-digest-wrong,
model-digest-differs-from-receipt, v3-receipt, missing-url, unsafe-member, absent-member,
member-digest-differs, http-refused, no-evaluated-check, live-exit-nonzero, v5-match,
v5-bad-commit, v5-url-not-at-commit, v5-not-verified, v5-rerun-schema-differs,
v5-rerun-unverified, projection-differs, server-exe-absent, server-exe-not-own-memfd,
server-exe-digest-differs, server-exe-unsealed, server-exe-seals-partial,
server-exe-other-inode, server-exe-linked, server-exe-path, code-absent,
code-digest-differs, code-foreign, code-not-a-member, code-unopened,
code-no-archive-library, code-path-missing, code-required-absent, code-foreign-memfd,
code-own-members, code-hostonly-no-library, code-non-regular-member,
sealed-member-refuses-writes, sealed-member-cloexec, sealed-member-digest-mismatch,
sealed-member-closes-on-refusal, sealed-member-short-writes, witness-passthrough,
compare-instance-only, compare-stable-differs`

## Findings for the axes

- **Operability (C1):** the replay instrument C1's request-plane receipt chain leans on
  (`kama-live-replay.py`) self-tests its round-52/53 memfd + code-mapping binding and its
  round-49 witness passthrough offline against a fake live tool; all 48 cases rejected/accepted
  as designed, so the replay side is not the weak link when a v5 receipt is re-driven. The
  append-only grader that the lane's declared append-only surface depends on also self-tests
  51/51, including the v6 threshold/declaration/disclosure cases.
- **Calibration (C2):** both instruments are `fail=0` at the frozen tip, i.e. a bound run that
  uses them is not being graded by a tool with a known-broken case. Nothing here re-executes
  the 12 capability rows; this item is instrument health only.
- **Scope honesty:** these selftests do not exercise `tools/round62-c1-counter.py` or
  `tools/round62-c2-counter.py` predicates, nor the live request plane; they cover only the
  two heavy instruments named in the assignment.

## Tool installs

None. No pacman transaction was attempted (host-wide pause), no uv/npx/binary install was
needed; stock `python3 3.14.8` and `git 2.56.0` ran both selftests.

## Receipts (durable)

- `.ufo/waves/round-62/w1/out/E04SelftestsB/aoa-selftest.txt` (52 lines, verbatim stdout)
- `.ufo/waves/round-62/w1/out/E04SelftestsB/klr-selftest.txt` (49 lines, verbatim stdout)

Scratch `/fast/scratch/hyaku/kama-r62/w/E04SelftestsB/` was `rm -rf`'d after copying; both
fixture roots were already empty (each selftest removes its own `aoa-*`/`klr-st-*` tree).
Lane checkout was read-only; no file under the lane was modified by this seat except this
report and the receipts above.

## Tally

```
AOA_SELFTEST pass=51 fail=0 exit=0
KLR_SELFTEST pass=48 fail=0 exit=0
```
