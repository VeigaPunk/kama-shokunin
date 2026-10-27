# K0Harm2 — round-50 no-harm attack (operability, freshness, depth, coverage, calibration, adjacency)

VERDICT: One real defect at the measured build (corpus/SOURCES.md:251 — the S498 row breaks `sources-append-only.py`, exit 2; already fixed at real tip 3d42897b); one latent coverage weakening introduced by v5's origin-union definition (a key ever born under an exempt title keeps an exempt origin forever: ungraded 82→89); one env-allowlist portability tradeoff for non-RPATH llama-server installs; all other probed harms either pre-exist at base 26ecba64 or are the known integration items.

Measured commit: `97c864bead3ee4a2f629574e77263d33834ec98a` on a `--shared` clone at `/fast/scratch/hyaku/kama-r50/K0Harm2/lane` (rev-parse asserted). Base: `26ecba64ad6fb571d09074b07202d1618a46ecd1`. Note: the real lane tip has already moved three commits past the measured build (6f3bd322 wave spec, 3d42897b S498 build-fix, 3b79eadd regression-battery receipts).

## Battery results at 97c864be

| Command | Exit | Result |
|---|---|---|
| `python3 tools/gate-registry-check.py` | 1 | `registered 44 unregistered 2 defective 0` — the two round-50 counters (known integration item; base reads `registered 44 unregistered 0 defective 0` exit 0) |
| `python3 tools/capability-repertoire-audit.py` | 0 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` |
| `python3 tools/round41-scorecard-reconcile.py` | 1 | `run_bad=1 mismatches=1` — calibration row states 35 `*verifier-spotcheck.md`, tree holds 36. PRE-EXISTING: identical at base (36 blobs there too; SCORECARD.md:18 states 35 at both revs). Not a round-50 harm. |
| `python3 tools/round42-selfdesc-reconcile.py` | 1 | same single mismatch (spotcheck count), pre-existing at base |
| `python3 tools/round43-registry-audit.py` | 1 | `unreg=2 … selftest=1 spot=1 mismatches=4` — unreg are the known item; `GATE_SELFTEST pass=5 fail=1` vs documented `pass=6 fail=0` because the selftest's "lane-tip" arm measures the live registry (fails on the unregistered counters); spot is the pre-existing 35-vs-36 |
| `python3 tools/planned-pointer-check.py SCORECARD.md` | 0 | `met=True` (planned round-50 section found at end) |
| `python3 tools/digest-ledger.py scan --repo . --rev 97c864be…` | 0 | `tokens=130 blob=114 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 unknown=0` (identical counts at base) |
| `python3 tools/hexrun-census.py scan --repo . --rev 97c864be…` | 1 | `unknown=1` (`f8cdb853aaff29393faeb0b6d4c2a2296778b698`, len 40, in `corpus/lessons/round-49-verifier-spotcheck.md`). PRE-EXISTING: identical totals at base (tokens=1858 distinct=305 unknown=1). Not a round-50 harm. |
| `python3 tools/sources-append-only.py --from 26ecba64… --to 97c864be…` | 2 | `error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)` — DEFECT, see D1 |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | `16 VALID and 1 NOT-EVALUATED accepted; 107 mutations + unreadable rejected` |
| `python3 tools/gguf-identity.py --selftest` | 0 | `30 cases passed` (`gguf-identity-selftest/v2`) |
| `python3 tools/kama-live-replay.py --selftest` | 0 | `KLR_SELFTEST pass=23 fail=0` |
| `python3 tools/append-only-audit.py --repo . --to 97c864be… --json` | 0 | `append-only-audit/v3 definition v5, events 5, ungraded 89, bad_decl 0, regressed 0` (matches claim) |
| `python3 tools/round49-append-audit-v4-check.py --repo . --tip 97c864be…` | 0 (not met) | `fixture=1 lane=0 scenarios=8/8 met=False` — expected by construction: v4's own origin counts the seven `## Capabilities` rows of 0718b6abbda6 as natively exempt (65) while v5 gives them a head birth (72 ungraded). Same shape as the round-48 v3 counter at the v4 build (`tool=82 counter=89`). The registered round-49 C2 row now reads met=False until integration retires/re-pins it — report below under coverage. |
| `python3 tools/round49-replay-witness-audit.py --repo . --tip 97c864be…` | 0 | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` — the old counter still passes at the build (see §W) |

## D1 — DEFECT: S498 row breaks the sources-append-only row parser at 97c864be (fixed at real tip)

- File/line: `corpus/SOURCES.md:251` (S498 row) at `97c864bead3ee4a2f629574e77263d33834ec98a`.
- Cause: `tools/sources-append-only.py` (cell-splitting note at lines 51-55) treats `|` inside a backtick code span as literal, not a delimiter. The S498 evidence quote held an unbalanced backtick — `characters (`) or tildes` plus the inline code `` `## ` `` plus the `` `c85f56cc…` `` sha parenthetical leaves an odd tick count, so a code span stays open across the remaining cells and the row's trailing pipes parse as literal text: the row never "closes". Every consumer using that parser (the append-only ledger check that must certify S496/S497/S498 `added (allowed)`) refuses the whole registry table — at the measured commit the three new rows were unverifiable by the lane's own freshness tool.
- Resolution already landed: `git show 3d42897b` removes the inner backticks and the sha256 parenthetical; `sources-append-only.py --from 26ecba64… --to 3b79eaddf382…` exits 0 with `added S496 (allowed) / added S497 (allowed) / added S498 (allowed)`.
- Proposed prevention (not a patch to a frozen file — a process note): the S-row author should run `tools/sources-append-only.py --from <prev> --to HEAD` before the build commit; the parser's tick-handling is documented nowhere and every future row that quotes spec text containing backticks is at risk. A defensive fix to `tools/sources-append-only.py` (treat `|` inside an even number of backticks as literal) can be proposed to L1.

## Per-axis findings

### Operability
- D1 above (build-time failure of a lane freshness tool) — fixed downstream of the measured commit.
- Risk tradeoff, not a defect: `tools/kama-live-replay.py:88` `LIVE_ENV_KEYS = ("PATH","HOME","LANG","LC_ALL")` and `tools/kama-llamacpp-live.py:125` `CHILD_ENV_KEYS` (same + TMPDIR) drop `LD_LIBRARY_PATH`, `LD_PRELOAD`, GPU vars (`CUDA_VISIBLE_DEVICES`, `ROCR_VISIBLE_DEVICES`) and `HF_*`. On this host the pinned binary `/home/vgpnk/.local/opt/llama-b11909/llama-server` carries `RUNPATH $ORIGIN` (verified `readelf -d`), so it resolves its libs without env. A llama-server that needs `LD_LIBRARY_PATH` (CUDA builds, some distro packages) now fails under replay (`launch-failed`/exit-2 refusal) where the pre-round-50 inherited environment worked — the replay hardening narrows the set of servable installs to RPATH/system-linked ones. Smallest safe correction if this matters: `live_env()` passes `LD_LIBRARY_PATH` only when the receipt's `server` object records the same value (record `env_notes` at capture), keeping hijackability bounded to the recorded run. Report; the strip itself is the claim's intent.
- Non-harms checked: `python -I` is safe (the live tool imports stdlib only, imports list verified lines 68–86); the pdeathsig race (parent dead before prctl) is handled both sides — `set_own_pdeathsig` re-reads `getppid()` after the prctl (`tools/kama-live-replay.py:108-110`) and the live child's `_preexec_pdeathsig` exits if `getppid() != _FORKED_PPID[0]` (`tools/kama-llamacpp-live.py:669`); `prctl` availability is checked (`_prctl()` returns None when the platform lacks it, lines ~93-97) and the receipt records `pdeathsig` honestly; `model_mapping` opens the model `O_NOFOLLOW|O_NONBLOCK` and fstat-compares dev+inode (`tools/kama-llamacpp-live.py:702-718`) so a swapped path cannot pass silently — it fails honestly `mapped-file-is-not-the-model-path`.

### Freshness
- hexrun `unknown=1` and `wrong_flagged=2`, digest-ledger `external_absent=1 unverifiable=5 wrong_flagged=1`: identical at base — no round-50 regression.
- S496/S497/S498 rows carry `2026-10-27` verified-at while the commit is dated 2026-10-26 (-0300 = 2026-10-27 UTC): defensible, noted only.
- `python -I`+env strip means the replay's fetch path (in the replay process, which runs under the counter's env, not stripped) still honors proxy vars; the live child does no downloads — no freshness harm.

### Depth
- `model_mapping` records only file-backed mappings: llama-server launched `--no-mmap`, or a model split across shards mapped under several pathnames (`model-path-not-in-maps`, `model-path-maps-several-files`, `tools/kama-llamacpp-live.py:701`), yields `mapped:False`, and a replay of that receipt now exits 1 (`model-mapping:<reason>` mismatch, `tools/kama-live-replay.py:343-348`). Pre-round-50 the same replay passed. The b11909 default path mmaps and the three frozen receipts replay fine, so this is a representable-state shrink at the margin: legal server configurations whose receipts v4 could now record cannot produce a *matching* replay. Report as residual depth gap (a fix would record all mapped model files or a `bind_mode` instead of refusing).
- Replay still accepts v4 and v5 receipts (`LIVE_SCHEMAS`, line 80-81); `projection()` (lines ~205-240) does not include `model_mapping`, so old receipts without the key still replay and match — the new check only fails when the *rerun* lacks/mismaps the model. No replayability regression for recorded evidence.

### Coverage
- v5's origin(l) is the union of section titles at EVERY birth of key(l) (`tools/append-only-audit.py` docstring and `origins()`): once a key is ever born inside an exempt (`## `) title — including on a side branch merged later — it carries that exempt title in origin forever, so any later deletion is ungraded even if the line lived under a graded heading when deleted. Net effect on this lane: `ungraded_lines 89` vs v4's 82 (the seven `## Capabilities` mirror rows of 0718b6abbda6 now have an exempt birth, F6 resolved as designed). Coverage of deletions is strictly weaker than a latest-birth rule; it is the frozen C2 definition so this is a spec-level tradeoff, not an implementation defect — reported because the axis question is harm: ~7 previously-graded lines' worth of enforcement is gone.
- `sections()` still only titles `## ` lines at column 0 (`elif b.startswith(b"## ")`): CommonMark also accepts up to 3 leading spaces and `##` inside indented code; a `   ## ` heading is not a title under v5 (same as v4 — residual, unchanged).
- The superseded v4 counter now fails on the lane leg (see battery): expected obsolescence, but any consumer still running the registered round-49 C2 row reads `met=False` until integration retires it — flagged so L1's registry edit re-pins the row rather than leaving a permanently-failing registered counter (round-48 left the v3 row in the same state; precedent).

### Calibration
- The only SCORECARD counter drift (spotcheck 35 vs 36) pre-exists at base; the round-50 build did not touch SCORECARD/calibration rows.
- v5 accounting adds `graded + ungraded == deleted` checked against `git diff --numstat` — a calibration *strengthening*: unaccountable deleted lines can no longer hide in either bucket.
- `GATE_SELFTEST pass=5 fail=1` vs documented `pass=6 fail=0` is entirely explained by the two unregistered round-50 counters (the failing arm is "lane-tip … registered 44 unregistered 2"); it heals when the registry rows land. Known item.

### Adjacency
- S496/S497/S498 `used-by` names `corpus/lessons/round-50.md` (absent until integration) — known item; the SOURCES row parser break (D1) was the only adjacency harm beyond the listed items and is already fixed at the real tip.
- `kama-live-replay/v1` and `append-only-audit/v3` schema strings are unchanged while semantics changed (new replay check; `definition: v5`). Consumers keyed on `schema` alone cannot tell a round-50 replay verdict from a round-49 one — same precedent as `definition: v4`; the `definition` key disambiguates, so borderline.

## §W — round-49 C1 (witness) counter at the build

`python3 tools/round49-replay-witness-audit.py --repo <clone> --tip 97c864be… --scratch $S/r49c1` → **exit 0, `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`** (12 s). All three witness replays bound correctly under the new isolated replay (`exe+listen+model ok`, nonce round-trips recorded), the capability legs still refuse the sparse/member controls, and `newrow` found S494. The old counter still reads met=True at the build — its surface (exe digest, listener ownership, nonce, teardown of the one replay it holds) is unharmed by the new isolation, pdeathsig and model_mapping checks; but it met=True while missing exactly the binding the round-50 counter grades (env hygiene, observed-pid↔child_pid join, mapped model bytes, whole-tree teardown) — the expected counter-supersession, not a harm. Receipt: `round49-witness-counter-at-build.out` in this directory.

## Commands log (selected)

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane; git checkout -q 97c864be…
python3 tools/gate-registry-check.py                       # exit 1: registered 44 unregistered 2 defective 0
python3 tools/gate-registry-check.py --rev 26ecba64…       # exit 0: registered 44 unregistered 0 defective 0
python3 tools/capability-repertoire-audit.py               # exit 0: met True
python3 tools/round41-scorecard-reconcile.py               # exit 1: run_bad=1 (spotcheck 35-vs-36, pre-existing)
python3 tools/round42-selfdesc-reconcile.py                # exit 1: same mismatch
python3 tools/round43-registry-audit.py                    # exit 1: mismatches=4 (unreg 2 known, selftest arm, pre-existing spot)
python3 tools/planned-pointer-check.py SCORECARD.md        # exit 0: met=True
python3 tools/digest-ledger.py scan --repo . --rev 97c…    # exit 0
python3 tools/hexrun-census.py scan --repo . --rev 97c…    # exit 1 unknown=1 (identical at base — pre-existing)
python3 tools/sources-append-only.py --from 26ec… --to 97c…# exit 2  <-- D1
python3 tools/sources-append-only.py --from 26ec… --to 3b7…# exit 0  (fixed at real tip)
python3 tests/llamacpp-live/check-receipt.py --selftest    # exit 0
python3 tools/gguf-identity.py --selftest                  # exit 0
python3 tools/kama-live-replay.py --selftest               # exit 0 pass=23
python3 tools/append-only-audit.py --repo . --to 97c… --json  # exit 0 v5, ungraded 89
python3 tools/round49-append-audit-v4-check.py --repo . --tip 97c…  # met=False lane leg (expected)
python3 tools/round49-replay-witness-audit.py --repo . --tip 97c…   # see §W
python3 tests/llamacpp-live/check-receipt.py <v5-receipt + model_mapping>  # exit 0 VALID (validator tolerates the new key)
```

Tool installs: none (all checks ran on host python3; pacman untouched).

Evidence receipts copied to `.ufo/waves/round-50/w1/out/K0Harm2/`: `round49-v4-counter-at-build.out`, `aoa-v5-at-build.json`, `round49-witness-counter-at-build.out`.
