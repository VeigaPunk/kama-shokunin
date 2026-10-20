VERDICT: partial — the counter is built, self-tested, and reproduces the falsify defect's shape (5 nonconformant of 79, exit 0), but under the specified first-non-empty-line rule the committed falsify count is 34/40/0, not the routed defect's 36/43/0, and all 81 build-advice files are nonconformant (different format).

Seat: KamaR17.VerdictCounter-2. Lane: kama-shokunin. Axes: operability + calibration.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/count-verdicts.py` — sha256 `1ffa75604728f9d6993fdb7f7173ba8915de7f0ff1d8f8d75487641773fa905a`, 10916 bytes, mode 0755, stdlib-only.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/VerdictCounter.md` — this report.

No other lane file touched. No installs (tooling directive: nothing needed beyond stdlib `python3`).

## Measured counts (runs explicitly permitted by the item)

`python3 count-verdicts.py .ufo/waves/round-16/falsify/advice --expect-names .ufo/waves/round-16/falsify/spec.json` → exit 0:

- `files=79` (the `swarm-registry.json` in the directory is not `.md`, and `swarm-registry*` is excluded regardless).
- `confirm=34 partial=40 refute=0 n/a=0 nonconformant=5`.
- Nonconformant five: `ConnectSiblingCollision.md`, `ExecNoPythonFallback.md`, `ReviewLesson.md`, `ScribeNumbersLedger.md`, `ScribeReportWaves.md` — each opens with `# <Name> — …` and carries its `VERDICT:` on line 3.
- `missing`: none; `unexpected`: none — all 79 `items[].name` in falsify `spec.json` map 1:1 onto the file stems.

`python3 count-verdicts.py .ufo/waves/round-16/build/advice --expect-names .ufo/waves/round-16/build/spec.json --json` → exit 0:

- `files=81`; `confirm=0 partial=0 refute=0 n/a=0 nonconformant=81`; `missing`/`unexpected` none.
- Every build-wave report opens with `# <Name> — …`; their `VERDICT` grep hits are `C_VERDICT` code references inside `tools/kama-probe.sh` quotes, not verdict lines (verified `grep -n VERDICT` on all 12 hit files: e.g. `ScoutRouterMode.md:66` is `C_VERDICT=MODEL_OK`).

## Reconciliation with routed defect 2

The routed defect states "committed reports count 36/43/0, 5/79 not opening with VERDICT". Under this tool (spec'd rule: first non-empty line must start `VERDICT:` + lowercase token) the reproducible committed count is **34/40/0, 5/79 nonconformant**. If the five misplaced-but-present `VERDICT:` lines (line 3 of each nonconformant file: confirm×2, partial×3) are folded in as the outside check apparently did, the totals are 36/43/0 — matching the defect's second number. Both numbers cited in the defect thus exist under different first-line rules; the item's specified rule yields 34/40/0. The falsify summary's own "36/41/2" matches neither rule — the defect stands as a real counting inconsistency, and the counter now makes the convention explicit and reproducible. [INFERENCE] The "outside check" counted verdicts wherever the `VERDICT:` line appeared rather than requiring it first.

## Design choices

- Regex `^VERDICT:[ \t]+(confirm|partial|refute|n/a)(?:[ \t]*[—\-:].*)?$` on the first non-empty raw line: `VERDICT:` anchored at column 0 and case-sensitive; token lowercase and unglued; optional whitespace then one of `—`/`-`/`:` separators then free text, or end-of-line.
- Nonconformant includes empty/whitespace-only files; the nonconformant list records the first line (truncated to 80 chars) so the misplaced-VERDICT case is diagnosable, not just counted.
- `--expect-names` accepts `{"items":[{"name":...}]}` or a bare list of strings/objects; reports `missing` (expected, absent) and `unexpected` (present, unlisted); duplicate expected names surface under `duplicate_expected_names`.
- Exit codes: 0 when counting ran (any verdict mix, including all-nonconformant); 2 for unreadable advice dir, unusable `--expect-names` file, or any unreadable `.md` file (unreadable files are listed and counting still completes).
- `--selftest` runs 16 classifier cases plus a temp-directory scan covering blank-leading-lines, heading-first, empty file, swarm-registry exclusion, and missing/unexpected-name detection; exits 1 on failure. Verified: `SELFTEST PASS: 16 classifier cases + directory scan`; `python3 -m py_compile` clean; `EXIT=2` confirmed for missing dir and missing expect-names file.

## Limitations

- First non-empty line only, by spec. Reports like round-16 build advice (verdict absent or deeper) are nonconformant, not scanned further — intentional, since the tool exists to catch format drift.
- Only `—`, `-`, `:` accepted as post-token separators; en dash `–`, `(` and friends are nonconformant. BOM is not stripped, so a BOM-prefixed file is nonconformant.
- `swarm-registry*` exclusion is by basename prefix, applied before the `.md` filter (a `swarm-registry.md` would also be excluded).
- Unreadable `.md` files are listed under `unreadable` and exit 2 rather than classified nonconformant — a permission fault is distinguished from a format fault.

## Blockers

None. No ports bound, no services started, no lane gate run, scratch confined to tempfile dirs auto-removed by `TemporaryDirectory`.
