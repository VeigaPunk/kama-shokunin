# J4OmitLib — round 53, C1 ablation: a library left out of the record

Verdict: the frozen C1 counter catches the omission 3/3 — `code=0 met=False` with `bind=1 sealed=1 teardown=1 newrow=1` — while the unpatched build in the same session reproduces `met=True`; the same omission leaves the build's own artifacts green (`match=True`, `own_code.verified=True`), so the round-53 operability claim rests on the counter's own reading of the process, not on the record's self-report.

## Axes

- operability (judged): does the C1 predicate still hold when one archive library the server executes is left out of the record? Measured: no — it flips to 0 on both record checks, per run, with the reason naming the exact path, dev and inode.
- isolation: every other leg (bind, sealed, teardown, newrow) stays 1 in the ablated run, so the ablation is confined to the code leg.

## 1. Fixture

    S=/fast/scratch/hyaku/kama-r53/J4OmitLib; export TMPDIR=$S
    git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
    git -C "$S/lane" rev-parse --show-toplevel      # /fast/scratch/hyaku/kama-r53/J4OmitLib/lane
    git -C "$S/lane" checkout -q -B ablation c22602bd8d83ab26349d1087e916ca537ee4f9d1
    # edits, then:
    git -C "$S/lane" -c user.name=fx -c user.email=fx@invalid commit -am "round-53 ablation J4OmitLib: ..."

- fixture tip `f2907c789b9a7e837256743e8055980eb9501be0`, parent `c22602bd8d83ab26349d1087e916ca537ee4f9d1`; diff `ablation.patch` (2 files, +7).
- second fixture, record-only, tip `e16c68029003a62412e575e33169dd943dc9d7ff`, parent `c22602bd…` (1 file, +4): the same omission with `verify_code()` untouched (see §4).
- patches, in the fixture tree only (never the lane):
  - `tools/kama-llamacpp-live.py:797-800` — `code_mappings()` skips any path containing `libggml-base`, so no entry for it reaches `code_mappings`.
  - `tools/kama-live-replay.py:322-324` — `verify_code()` skips the same name.
- the lane repo was not touched: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` shows only other seats' work (`M .ufo/waves/round-53/measured/c1-build.out`, `M …/c2-build.out`, `M registry/hexrun-ledger.tsv`, `?? …/hexrun-evidence/`, `?? …/measured/aoa-build.out`), all present before my first command.

## 2. Ablation run (both patches)

    python3 …/kama-shokunin/tools/round53-replay-code-audit.py --repo "$S/lane" \
      --tip f2907c789b9a7e837256743e8055980eb9501be0 --scratch "$S" --out …/c1-omit.out
    # exit=1

    tip=f2907c789b9a7e837256743e8055980eb9501be0
    bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False
    detail: code b1: code: rerun code_mappings has no entry …/work-b1/server/llama-b11909/libggml-base.so.0.27.0 103:05 1694737296 with the archive digest
    detail: code b1: code: replay own_code.members['llama-b11909/libggml-base.so.0.27.0'] None != archive digest
    (b2 and b3 identical in shape; inodes 146805033, 1085615054)
    detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
    detail: newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']

Two independent record checks fire per run — the receipt's `code_mappings` entry and the replay's `own_code.members` entry — and no `code: mapped bytes … differ` line appears: the counter's own `/proc/<pid>/mem` comparison of the same mapped range passed, so the catch is exactly the record omission, not a byte mismatch. `bind 3/3`, `sealed 3/3`, teardown and newrow unchanged.

## 3. Paired control (unpatched build, same session, same host)

    python3 …/round53-replay-code-audit.py --repo "$S/lane" \
      --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch "$S" --out …/c1-build-recheck.out
    # exit=0

    bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
    detail: code b1: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the counter's own archive, 13 root-owned host files; recorded in code_mappings and own_code: ['libggml-base.so.0.27.0', 'libggml-cpu-zen4.so', 'libggml-rpc.so', 'libggml.so.0.27.0', 'libllama-common.so.0.7.0', 'libllama-server-impl.so', 'libllama.so.0.7.0', 'libmtmd.so.0.7.0']

Matches the L1's `.ufo/waves/round-53/measured/c1-build.out` (8 archive libraries, 13 root-owned host files, met=True), so the 1-bit difference between §2 and §3 is the patch alone. Host Yama scope `1` (`/proc/sys/kernel/yama/ptrace_scope` = 1), so the counter reads `/proc/<pid>/mem` as the server's ancestor, as the docstring states.

## 4. What the build's own artifacts say under the same omission

Record-only fixture (`e16c6802`, `verify_code()` untouched — only `code_mappings()` omits the library):

    cd "$S/omit" && python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json \
      --work "$S/ev2/work" --out "$S/ev2/out.json"     # replay-exit=0
    match True mismatches []
    mappings 20 own_code.verified True members 7 host 13
    base_recorded False base_verified False

and the counter on that fixture:

    python3 …/round53-replay-code-audit.py --repo "$S/omit" --tip e16c68029003a62412e575e33169dd943dc9d7ff …
    bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False   # exit=1
    detail: code b1: code: rerun code_mappings has no entry …/llama-b11909/libggml-base.so.0.27.0 103:05 617595508 with the archive digest
    detail: code b1: code: replay own_code.members['llama-b11909/libggml-base.so.0.27.0'] None != archive digest   (b2, b3 same)

So the `verify_code()` skip in §1 is cosmetic for this control: dropping a library from `code_mappings()` alone makes C1 fail, and the replay still reports `verified: True`. The full-patch fixture (`f2907c78`) gives the identical `code=0` result.

## 5. Finding (not a counter defect): `verify_code()` has no required-library set

- File and line: `tools/kama-live-replay.py:305-338` (`verify_code`, at `c22602bd`), specifically the loop at `:320-338` and the terminal `if not members:` at `:336-337`.
- Command that shows it: the §4 replay (`match True`, `own_code.verified True`, `members 7`, `libggml-base` absent) against a record that omits a library the server demonstrably executed (`code_observe` required an entry for it).
- Why: `verify_code()` iterates only the mappings the record carries; `no-archive-library` fires only when the member set is empty, so any non-empty subset verifies. The counter's own `REQUIRED` tuple (`tools/round53-replay-code-audit.py:103`, checked at `:456-458`) is what closes the gap.
- Proposed fix, unapplied, in this seat's out dir: `proposed-fix-verify-code-required.patch` (44 lines, unified diff against `c22602bd`; adds `import fnmatch`, a `CODE_REQUIRED` tuple mirroring the counter's, and a check that every required pattern the archive carries in a recorded member's directory has at least one recorded archive member). It is gated on "pattern present in that archive directory" so the offline selftest archive (no `libggml*` members) is unaffected. Parse-checked only (`ast.parse` ok); **not applied to the lane and not run** — the wave's gate belongs to the parent, and this seat ran no repo test suite.

## 6. Risks

- The control measures the record leg only: the counter's `/proc/<pid>/mem` leg is the counter's own reading and stays green under the ablation by construction. The ablation shows the record leg is load-bearing, not that a swapped library would be caught (`mut*` controls are other seats').
- The ablation was run three times per fixture (3/3 bind replays), so each `code=0` is the same two problems repeated, not three distinct detection shapes.
- `code_mappings()` skipping a path is visible in a diff; a real defect would more likely skip under a name pattern, which this control would also catch (§4), but the control does not test an attacker who patches `code_observe`'s archive-side comparison.
- No tool was installed (pacman is paused host-wide; nothing was needed). Scratch `/fast/scratch/hyaku/kama-r53/J4OmitLib` was removed after the cited files were copied; this seat left no llama-server (`pgrep -af llama-server` shows only peer K2Design's hold under `/fast/scratch/hyaku/kama-r53/K2Design/…`, pids 2826889/2827397, not mine).

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/c1-omit.out` — counter receipt, both-patch fixture (`code=0 met=False`, exit 1)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/c1-omit-only.out` — counter receipt, record-only fixture (`code=0 met=False`, exit 1)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/c1-build-recheck.out` — counter receipt, unpatched build (`met=True`, exit 0)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/ablation.patch` — the fixture commit `f2907c78`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/rerun-receipt-omit.json`, `replay-result-omit.json` — both-patch fixture record: `match True`, `code_mappings` 20 entries, `own_code.members` 7
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/rerun-receipt-omit-only.json`, `replay-result-omit-only.json` — record-only fixture: `match True`, 7 members, no `libggml-base`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J4OmitLib/proposed-fix-verify-code-required.patch` — the §5 proposal (unapplied)
