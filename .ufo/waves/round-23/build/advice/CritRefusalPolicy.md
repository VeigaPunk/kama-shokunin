# CritRefusalPolicy — refuse (exit2) vs surrogateescape on invalid UTF-8

Seat: CloseKama22.CritRefusalPolicy (critic). Date: 2026-10-21. Base master=4fe9339f; git 2.56.0; Python 3.14.8 (utf8_mode=0, locale UTF-8).

## Verdict

Neither uniform policy is calibrated. The right policy depends on what role the bytes play:

- **Data the verdict provably ignores** (lane `git log` author/subject, the `ls-tree` name list): evaluate with surrogateescape. Uniform strict refusal there is over-refusal. It masks real verdicts and leaves one repository-local config knob that still flips the outcome.
- **The audited report and authority inputs** (errata, `SOURCES.md`): stay strict, so they refuse with exit2. Uniform surrogateescape is a judge-reject. It turns an error into a traceback verdict, emits JSON that strict parsers reject, and changes frozen draft-path behavior.

Arms tested (scratch clone /tmp/kama-r23/CritRefusalPolicy; copies in /tmp/kama-r23/crp-arms):

- **frozen** = `4fe9339f` blob, sha256 `09ecd63b…`.
- **candidate** = the L1's working-tree diff, sha256 `b6064767…`. It uses strict `decode("utf-8")` on all stdout and maps a decode failure to EvalError (exit2).
- **split** = candidate plus `errors="surrogateescape"` on only the lane `git log` and `ls-tree --name-only` calls, sha256 `f36c289c…`.
- **allsur** = candidate with surrogateescape on every git stdout and on `read_report`, sha256 `4e554f4f…`.

## Evidence: fault grid

Produced by `bash grid.sh` (copy in out/CritRefusalPolicy/grid.sh). Each cell is the exit code; TB = Python traceback; brackets list the defect kinds found.

| case | frozen | candidate | split | allsur |
|---|---|---|---|---|
| ctl | 0 | 0 | 0 | 0 |
| e1 unrelated commit, porcelain `-c i18n.commitEncoding=x-bogus`, subject `caf\xe9` | 1TB | **2** | 0 | 0 |
| ru1 RAW unrelated commit, subject `\xff\xfe` | 1TB | **2** | 0 | 0 |
| ru2 RAW unrelated author `some\xffone` | 1TB | **2** | 0 | 0 |
| rr1 RAW `round-1: caf\xe9` by kama-shokunin, omitted | 1TB | **2** | 1[landed-omitted] | 1[landed-omitted] |
| rr2 same commit, cited | 1TB | **2** | 0 | 0 |
| rk RAW bad byte in a round-1 commit, auditing `--rounds 2` only | 1TB | **2** | 0 | 0 |
| rp / rz2 RAW `\xffround-1:` / overlong `\xc1\xb2ound-1:` prefix, omitted | 1TB | 2 | 0 | 0 |
| z1 valid-UTF-8 zero-width-space `\u200bround-1:` prefix, omitted | 0 | 0 | 0 | 0 |
| q0 fleet has committed `.ufo/reports/round-1/\xff.md`, `--rounds 1-` | 0 | 0 | 0 | 0 |
| q1 = q0 + fleet-local `core.quotePath=false` | 1TB | **2** | 0 | 0 |
| b1 committed report, `\xff` outside Landed | 1TB | 2 | 2 | 0 |
| b2 committed report, `\xff` splitting a fabricated 40-hex in Landed | 1TB | 2 | 2 | 1[landed-unresolved×2] |
| b3/b4 = b2 with valid `é` / ZWSP instead of `\xff` | 1[landed-unresolved×2] | same | same | same |
| d1 draft `--report 1=PATH` with `\xff` | 2 | 2 | 2 | **0** |

The RAW rows use hand-crafted commit objects (`hash-object -t commit --stdin`). Porcelain `git commit` rewrites invalid message and author bytes as Latin-1 to UTF-8; observed: `\xff` was stored as `303 277`. So rows u1, u2, r1, r2, and z2 in the grid output did not exercise raw bytes and are excluded above. e1 shows that raw bytes are still reachable through porcelain alone, via an unconvertible `encoding` header.

## Counterexamples against uniform strict refusal (candidate)

1. **The verdict is fully determined, yet the candidate refuses (calibration axis 7).** `round_commits` uses only `%H`, `%an == "kama-shokunin"`, the digits of `%at`, and the ASCII prefix `^(round-N:|checkpoint\(rN\))`. Invalid bytes cannot satisfy or break any of these. In rr1 the truthful answer is "failed / landed-omitted", but the candidate returns exit2 and hides a real failure. In rk, a bad byte in a round-1 commit makes round 2 unauditable. Lane `master` history is append-only and errata cannot correct exit2, so after one such commit every future default `--rounds 10-` run is exit2 for good. e1 shows such a commit is reachable through porcelain (`git -c i18n.commitEncoding=x-bogus commit`, or that setting in repo config).
2. **Repository-local config still changes the outcome (D4 claim scope, operability axis 8).** Compare q0 and q1: the same committed tree is clean by default but exit2 once the fleet sets `core.quotePath=false`. The candidate's `GIT_ISOLATION` (`--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false`) does not pin `core.quotePath`. The file name can never match the ASCII `round-N/kama.md` pattern, so it is irrelevant to the verdict. This contradicts the updated `git_env` docstring's intent, and the round-23 grid (a)–(e) does not list it.
3. **Refusal is not a security boundary.** rp and rz2 (byte prefixes) are refused, but z1 (valid ZWSP prefix) gives a clean exit0 in every arm, including frozen. b2 is refused, but b3 and b4 (valid `é` or ZWSP inside a fabricated hash) are evaluated by every arm. Strict decoding blocks only the invalid-UTF-8 subset of an evasion class that stays open through valid Unicode. So refusal buys no false-clean protection that justifies its cost.

## Counterexamples against uniform surrogateescape (allsur): judge-reject

1. **An error becomes a verdict.** An errata row whose correction column has `\xff`, committed at `master:registry/report-landing-errata.tsv`, makes allsur exit 1 with a traceback: `UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' ... surrogate`. The cause is that `lookup` calls `stdin.encode()`. The candidate and split arms both return exit2 with `could-not-evaluate: git show master:registry/report-landing-errata.tsv ...`.
2. **The JSON output is invalid for strict consumers.** An errata evidence column with `\xff` yields `"evidence": "ev \udcff"` in `--json`. `jq` at `~/.local/bin/jq` is actually jaq 3.1.1 and fails with `invalid character with index 56575` (rc=5). serde_json 1.0.151 (scratch crate, `cargo run --offline`) fails with `lone leading surrogate in hex escape at line 5 column 25`. Any Rust consumer of `--json` would reject the document.
3. **A frozen behavior changes (controls axis).** d1 goes from frozen exit2 to exit0 because the existing `read_report` strict refusal for drafts is lifted. The "controls unchanged" claim would have to declare this.
4. **Exemption authority would accept undecodable bytes.** `SOURCES.md` URLs exempt hashes, which is the false-clean direction. Frozen code deliberately refuses an undecodable blob at lines 221–224 of the frozen blob (`cannot decode {branch}:{SOURCES}`).

Why the report itself can stay strict without harm: under split, the committed report (b1, b2) and the draft (d1) both give exit2. That keeps the two report paths consistent and preserves the frozen draft semantics. Evaluating the report would be well-defined (b2 vs b3/b4 shows a surrogate is as inert as any non-ASCII character in `FULL`, `ABBREV`, and the headings), but it would be a declared behavior change, not part of this narrow claim.

## Smallest safe correction

Applied in out/CritRefusalPolicy/split-vs-candidate.diff:

- `git(..., errors="strict")` passes `errors` to `proc.stdout.decode("utf-8", errors)`.
- `round_commits`'s `git log` and `parse_rounds`'s `ls-tree --name-only` pass `errors="surrogateescape"`.
- Everything else stays strict.

Surrogates cannot reach output on this path. Subject and author are never emitted, `sha` is `%H`, and EvalError messages use `!r`.

If the L1 prefers to keep uniform strict decoding, the minimum is to add `"-c", "core.quotePath=true"` to `GIT_ISOLATION` (fixes q1). The claim must then declare that invalid bytes in any lane commit reachable from `--branch` refuse every round permanently, including true failures (rr1). That is an honest tradeoff, not a false clean, but it is a weaker calibration than split.

## Ledger and controls checked

- `--selftest`: frozen, candidate, split, and allsur all print `selftest cases=50 failed=0`.
- Real historical ledger: a read-only audit with the default `--rounds 10-` plus errata, lane=/home/vgpnk/Projects/shokunin/kama-shokunin, fleet=/home/vgpnk/Projects/shokunin. Frozen, candidate, and split all exit 0 with rounds 10–22, defects=9, corrected=9, uncorrected=0, errata_rows=9, status=clean. The `--json` outputs are byte-identical (`cmp` frozen==candidate, frozen==split).
- Real-history exposure today is zero. `git log --all --format=%H%x1f%an%x1f%s` gives 0 invalid-UTF-8 and 0 CR lines in the lane (248) and the fleet (1032). All 20 committed `.ufo/reports/round-*/kama.md` files and `master:corpus/SOURCES.md` are valid UTF-8 with no CR. So the policy choice has no historical-ledger cost either way; the difference is entirely prospective.

## Not verified

- No old-git floor and no Python other than 3.14.8.
- No non-UTF-8 caller locale. Note that the candidate's explicit `decode("utf-8")` already removes the frozen dependence on locale.
- I did not attempt invalid bytes in `%H`/`%at` (git-generated; fields are not validated as hex beyond the `%at` digits check).
- Other repo-local knobs besides `core.quotePath` that emit raw path bytes in `ls-tree` output were not enumerated.
- I did not check whether the Rust judge consumes `--json`; serde rejection is demonstrated, but whether it matters for the judge is [INFERENCE].
- The lane working-tree candidate was read at the moment of copy (sha256 `b6064767…`); later L1 edits are not covered.

## Installs

None. jaq 3.1.1 (as `jq`), cargo, and serde_json 1.0.151 from the local cache were already present.

## Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/CritRefusalPolicy.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/CritRefusalPolicy/{split-vs-candidate.diff, allsur-vs-candidate.diff, grid.sh}
- Scratch only: /tmp/kama-r23/CritRefusalPolicy (clone; `tools/report-landing-audit.py` = split arm), /tmp/kama-r23/crp-arms/{frozen,candidate,split,allsur}.py, run.*/, err.*/, hist.*.json, serde/
