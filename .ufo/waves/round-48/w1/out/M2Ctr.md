# M2Ctr — round-48 C2 counter mutation test

Verdict: **27 mutants of the frozen C2 counter (`tools/round48-live-replay-v5-audit.py`, sha256 `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09`) each run against lane tip `380bcdff9c8af06997c482f6eb03db926a794a2b` and against the rebuilt r47-relabel control: 18 killed (15 tip-side, 3 control-side), 3 exercised at detail level, 6 survived — every survivor is a suite-coverage gap, none is a counter defect; exit-level discrimination (tip exit 0 / control exit 1) held under every mutant, and the lane file was never modified (sha256 identical before and after).**

## Setup

- Scratch `S=/fast/scratch/hyaku/kama-r48/M2Ctr` (removed at the end; nothing cited lives only in /tmp).
- One live clone: the frozen builder `build_controls.py` (copied to scratch unmodified, sha256 `c892d0c9dd0e897711b9a5a9f69c480b9c7d151acabfd53340a78b420a309d8a`) created `git clone --shared --no-checkout` of the lane at `$S/ctl-r47-relabel`, checked out the round-47 closure `33e005827742b29772b153cda036ec9f27f653be`, relabeled the three round-47 b11909 receipts to v5 with the pinned model URL/commit and a `provenance.verified` block filled from their own digests, installed the receipt-copying cheat replay stub, and committed `a907a87fb7b6182f931f733c85e5ea6efb7c5126`. That single clone served as `--repo` for **both** targets (it contains all lane objects via alternates; the counter is read-only on `--repo`).
- Pristine baselines (both reproduced the recorded controls exactly):
  - tip, my run: `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0 (13.3 s) — matches the L1 dry-run line byte for byte. Evidence: `evidence/pristine-tip.out`.
  - control, the builder's own score run with the lane counter: `receipts=1 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False`, exit 1 — matches the recorded `controls/junk-c2-r47-relabel.c2.out` flag line exactly (commit hash differs from the recorded `8dd7f751…` only because rebuild timestamps differ; tree content is identical by construction). Evidence: `evidence/pristine-ctl-builder-score.out`.
- Mutants: `gen_mutants.py` applied single-site substring edits to a scratch copy per mutant, asserted each anchor matches exactly once, `py_compile`-checked every mutant (no syntax-error false kills), and recorded before/after sha256 plus preregistered predictions in `mutants.json`. The 27 mutant scripts are in `mutants/`; raw per-run output (55 JSONL records: stdout, stderr tail, exit, duration) in `ledger.jsonl`; verdicts in `verdicts.json`.

## Run budget

56 counter runs total = 1 (builder's pristine control score) + 1 (pristine tip) + 27 mutants × 2 targets = **56 < 60**. Tip-side runs download ~75 MB each (~2.1 GB total); control runs are offline (the cheat replay stub does no network). No retries were needed; no run timed out. Tooling installed: **none** (python3 + git only; no pacman touched).

## Results

Flags abbreviated `rec/rc/rp/cmp/tam/url/row`, then `replayed`, exit. Pristine: tip `1/1/1/1/1/1/1 3/3 exit0`, ctl `1/0/0/0/0/0/0 0/3 exit1`.

| mutant | site (pristine file:line) | edit | tip | ctl | verdict |
|---|---|---|---|---|---|
| M01-schema-v4 | :146 | `SCHEMA` v5→v4 | `0/1/0/1/1/1/1 0/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M02-asset-sha | :135 | frozen asset digest 1st hex char | `0/1/0/1/1/1/1 0/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M03-model-commit | :136 | frozen model commit 1st hex char | `0/1/0/1/1/1/0 0/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M04-model-url-path | :138 | `tinyllamas`→`tinyllama` in MODEL_URL | `0/1/1/1/1/1/0 3/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M05-model-sha | :139 | frozen model digest 1st hex char | `0/1/0/1/1/1/1 0/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M06-eval-threshold-3 | :234 | `len(ev) < 10`→`< 3` | pristine | pristine | SURVIVED |
| M07-all-passed-false | :234 | `all(v is True)`→`all(v is False)` | `0/1/1/1/1/1/1 3/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M08-verified-at-rerun | :246 | `verified.at "record"`→`"rerun"` | `0/1/1/1/1/1/1 3/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M09-member-binding-asset | :248 | `member_sha256 == server.sha256`→`== ASSET_SHA` | `0/1/1/1/1/1/1 3/3 exit1` | `0/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M10-marker-always | :333 | `executed = os.path.exists(marker)`→`True` | `1/0/1/1/1/1/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M11-rc-ignore-executed | :337 | drop `not executed` from negative-case predicate | pristine | pristine flags, detail loses `partial-flags` line | EXERCISED |
| M12-rc-want-3 | :314 | unpinned-URL want 2→3 | `1/0/1/1/1/1/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M13-inside-true | :182 | `inside()`→`return True` | pristine | pristine flags, `not under scratch`→`does not hash` | EXERCISED |
| M14-replay-no-hash | :422 | `elif sha_file(fpath) != want:`→`elif False:` | pristine | pristine | SURVIVED |
| M15-started-utc-drop | :412 | `st < t0` term dropped | pristine | pristine flags, 3 `precedes counter start` lines gone | EXERCISED |
| M16-compound-mno | :182+:422+:412 | M13+M14+M15 together | pristine | `1/0/1/0/0/0/0 3/3 exit1` | KILLED-CTL |
| M17-projection-metrics | :223 | projection `metrics` key→`None` | pristine | pristine | SURVIVED |
| M18-cmp-instance-want1 | :478 | instance-only want 0→1 | `1/1/1/0/1/1/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M19-cmp-props-want0 | :480 | props-n_ctx want 1→0 | `1/1/1/0/1/1/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M20-tamper-noop | :509 | digest flip→`pass` | `1/1/1/1/0/1/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M21-tamper-accept-all | :517 | refusal assertion→`if False:` | pristine | `1/0/0/0/1/0/0 exit1` | KILLED-CTL |
| M22-urlswap-prefix-loose | :541 | `"digest-mismatch"`→`"digest"` | pristine | pristine | SURVIVED |
| M23-urlswap-rerun-ok | :541 | drop `or rr is not None` | pristine | pristine | SURVIVED |
| M24-urlswap-code0 | :541 | `code != 2`→`!= 0` | `1/1/1/1/1/0/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |
| M25-newrow-noshape | :546 | drop `\| S` row-shape term | pristine | pristine | SURVIVED |
| M26-newrow-src-only | :546 | `bool(src) and any(`→`bool(src) or any(` | pristine | `1/0/0/0/0/0/1 exit1` | KILLED-CTL |
| M27-replayed-2 | :435 | `rep = replayed == 3`→`== 2` | `1/1/0/1/1/1/1 3/3 exit1` | `1/0/0/0/0/0/0 exit1` | KILLED-TIP |

Verdict rule: KILLED-TIP = tip exit/leg flags deviate from pristine tip; KILLED-CTL = control exit/leg flags deviate from pristine control; EXERCISED = flags and exit identical on both targets but a detail line attributable to the mutated site changes; SURVIVED = output indistinguishable from pristine on both targets. Detail comparison normalized timestamps and truncated the volatile 200-char subprocess-tail window (its slice offset varies with scratch path length — an artifact of my per-run roots, not of any mutant; the raw stdout in `ledger.jsonl` is untruncated).

## Findings

- **F1 (M16, KILLED-CTL) — the replay leg's anti-copy cheat is exactly three guards, and they are jointly necessary.** With `inside()` disabled, the counter's own cross-hash disabled and the `started_utc ≥ counter start` check disabled, the control's receipt-copying replay stub passes the replay leg completely (`replay=1 replayed=3/3`). Each guard alone is only detail-level (M13, M15) or unreachable (M14, because `inside()` gates the hash branch). The control still exits 1 only because recordcheck/compare/tamper/urlswap/newrow fail independently — defense-in-depth at `met` level holds. No fix proposed: keep all three guards; the finding is that none of them is redundant *in combination*, so any future simplification of the replay leg must not remove one on the strength of a single-guard test.
- **F2 (M13, EXERCISED) — scratch containment, not digest equality, is what binds re-acquisition.** With `inside()` returning True, the control's host paths `/home/vgpnk/.local/opt/llama-b11909/llama-server` and `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` hash *correctly* (this host holds byte-identical copies), so digest checks alone would accept the round-47 D1 host-cache cheat; only `inside(--scratch)` rejects those paths. The round-48 counter's `inside()` is load-bearing precisely where digests are blind.
- **F3 (M17, SURVIVED) — the counter's own stable projection is self-consistent by construction and therefore unverifiable by this suite.** `projection()` is applied to both sides of the receipt-vs-rerun comparison (`p0 = projection(rec)` vs `p1 = projection(rr)`), so deleting the `metrics` key (or any key) changes nothing on either target. The compare leg validates the *replay tool's* `--compare`, not the counter's projection. Coverage gap: no target feeds the counter a rerun whose stable surface differs from the receipt's outside the replay tool's own match.
- **F4 (M22+M23, SURVIVED) — the urlswap leg's refusal assertions are only exit-code-load-bearing on these targets.** Loosening the required refusal prefix from `digest-mismatch` to `digest`, and dropping the no-rerun-receipt term, both leave both targets unchanged; only `code != 2` (M24, killed) does work here. A future replay tool that refused with an arbitrary `digest…` message, or that wrote a rerun receipt alongside the refusal, would pass this leg on both targets.
- **F5 (M25, SURVIVED) — the newrow row-shape guard is not discriminated.** Dropping the `| S` prefix term leaves both targets unchanged: URL-in-a-registry-row reduces to URL-anywhere-in-SOURCES.md on this suite.
- **F6 (M06, SURVIVED) — the ≥10 evaluated-checks floor is not discriminated.** No target ships a receipt with 3–9 evaluated checks, so `len(ev) < 10`→`< 3` is invisible.
- **F7 (M11, EXERCISED) — recordcheck's `not executed` term matters only at detail level here.** Dropping it hides the `partial-flags` failure detail on the control (the v4 live tool refuses with exit 2 and `outcome=setup-error`, which already fail the case); no target ships a live tool that both refuses and executes the stub, so the marker guard is not exit-level-load-bearing on this suite.
- **F8 (observations, no defect).** (a) M04@tip shows the replay leg never compares the rerun's model *URL* to the frozen `MODEL_URL` — only `provenance.model.commit` and the model digest — so a rerun naming a different URL with the pinned commit and pinned bytes passes the replay leg; the receipts leg pins the URL, so `met`-level discrimination holds (M04 killed via `receipts=0`). (b) M03@tip shows `newrow` tracks the `MODEL_URL` constant, so a frozen-commit mutation also flips `newrow=0` — the leg is intentionally coupled to the frozen names. (c) M15's detail diff confirms the copied-receipt rerun is flagged first by `started_utc` freshness, second by scratch containment.

**No defect in the frozen counter:** every mutant that weakened a check was still caught at exit level by another leg, and every mutant that strengthened or broke a check was caught by the tip run. The six survivors (F3–F6) are coverage findings against the two-target suite, not permission to change the contract.

## Restoration evidence

- Lane counter file `tools/round48-live-replay-v5-audit.py` sha256 `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09` before the sweep and `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09` after — identical; the lane was never written (all runs read-only against the scratch clone; mutants lived only in scratch).
- Pristine copy `M00-pristine.py` verified equal to the lane file by sha256 before its run.
- Scratch `$S` removed after evidence copy-out; no evidence lives only in /tmp.

## Artifacts

- Report: `.ufo/waves/round-48/w1/out/M2Ctr.md` (this file)
- `out/M2Ctr/mutants.json` — 27 mutants: region, exact edit, pristine line numbers, before/after sha256, preregistered predictions
- `out/M2Ctr/mutants/M01…M27*.py` — the mutant scripts (py_compile-clean)
- `out/M2Ctr/ledger.jsonl` — 55 raw run records (tag, exit, duration, full stdout, stderr tail)
- `out/M2Ctr/verdicts.json` — per-mutant verdicts with normalized tip/ctl outputs and diffs vs predictions
- `out/M2Ctr/evidence/pristine-tip.out`, `out/M2Ctr/evidence/pristine-ctl-builder-score.out` — pristine baselines
- `out/M2Ctr/evidence/receipt-1.at-tip.json` — receipt-1 as committed at the tip (cited for the frozen provenance values)
- `out/M2Ctr/gen_mutants.py`, `out/M2Ctr/runner.py`, `out/M2Ctr/summarize.py` — the three scripts, rerunnable
