# S9Skill — round-47 instrument-registry rows (C1 append-only v2, C2 live replay)

**Verdict: rows drafted and gate-proven.** On a scratch clone at `3a09a1d93dcc16799cf6c4b48786e6440af134c4` with the proposed section appended to `SKILL.md`, `python3 tools/gate-registry-check.py` prints `registered 40 unregistered 0 defective 0` and exits 0; the same commit without the section prints `registered 38 unregistered 2 defective 0`, exit 1, the two unregistered paths being exactly the round-47 counters. No lane file was modified; no counter was rerun to decorate the report.

## Behavior delivered

Proposed `SKILL.md` text (append after the `## Round-46 instrument registry` table, i.e. after line 1442 of the lane's SKILL.md; in the demo clone it lands at `SKILL.md:1444`):
`## Round-47 instrument registry (append-only v2 calibration, live receipt replay)` — intro sentence, the four-requirement table header the gate accepts (`| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`), and five rows:

| Row | Instrument | What the row pins |
|---|---|---|
| Round-47 C1 append-only v2 calibration audit | `tools/round47-append-audit-v2-check.py` | flags `--repo --tip --base --scratch --out`; output line `selftest= contract= lane= fixture= stable= files= lane_events= lane_mismatch= fixture_mismatch= met=` plus `tip= base=` and `detail:` lines; exit 0/1/2; the five legs and the frozen 20-line threshold; measured `files=85 lane_events=5 met=True`; the graded tool's source at the tip must not contain `round47`; read-only on `--repo` |
| Round-47 C2 live-replay operability audit | `tools/round47-live-replay-audit.py` | flags `--repo --tip --scratch --out`; `receipts= replay= tamper= newrow= rerun_checks=` + `tip= started=`; exit 0/1/2; the v4 receipt requirements, the fresh-home replay and its self-check, the two tamper copies, the b11909 SOURCES row; network size and the 20-minute per-replay timeout; L1 pre-wave dry run `newrow=0 met=False` labelled as such |
| Round-47 live receipt replay | `tools/kama-live-replay.py` | `--receipt --work --out [--live] [--timeout]`, `--selftest [--scratch]`; `kama-live-replay/v1` JSON keys; exit 0 match / 1 differs / 2 refused, with all ten refusal reason strings; `KLR_SELFTEST pass=10 fail=0`; writes only `--work` and the `--out` JSON |
| Round-47 append-only audit v2 | `tools/append-only-audit.py` | `--repo --to --contract/--files --threshold --json`, `--selftest`; `event … deleted= restored_max= status= restored_best= restored_by=` and `summary commits= files= events= restored= partial= unrestored=`; `append-only-audit/v2` JSON keys; exit 0/1/2 with the `could-not-evaluate: <reason>` stderr path; `AOA_SELFTEST pass=15 fail=0`; the v2 semantics (byte-exact `--` lines, numstat equality, window maximised restoration) |
| Round-47 live lifecycle receipt v4 | `tools/kama-llamacpp-live.py` | full flag set including the four provenance flags; exit 0 pass / 1 fail / 2 not-evaluated or setup error; the `kama-llamacpp-live/v4` receipt skeleton with `provenance` and `teardown.log_path: null`; `selftest: ok; closed tcp6 listeners …`; receipt-1 pins (`11` checks all evaluated and passed, `build_info` `b11909-caa8191df`, member `llama-b11909/llama-server`); port-refusal set and child-env allowlist |

Plus the requested how-to, `### Re-running live evidence` (6 bullet lines): receipt-only provenance input, the concrete replay command, the 0/1/2 meaning, the network/offline-selftest note, the counter form, and why a null `teardown.log_path` still replays.

Two drafting corrections made against the docstrings while writing (both now in the text): `kama-live-replay.py`'s digest refusal is `digest-mismatch:<file>:want=<hex>:got=<hex>` (tools/kama-live-replay.py:94), and `append-only-audit.py`'s exit 2 writes `could-not-evaluate: <reason>` to stderr and also covers `--threshold < 1`, an unreadable `--contract` and a hunk-count/numstat disagreement (tools/append-only-audit.py:203, :484-495).

## Gates

Reproduction (scratch only; clone removed at the end):

```
S=/fast/scratch/hyaku/kama-r47/S9Skill; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel   # /fast/scratch/hyaku/kama-r47/S9Skill/lane
git -C "$S/lane" checkout -q --detach 3a09a1d93dcc16799cf6c4b48786e6440af134c4
cd "$S/lane" && printf '\n' >> SKILL.md && cat <skill.md> >> SKILL.md
python3 tools/gate-registry-check.py
```

Before (registry at the frozen commit, `--rev` mode; SKILL.md at 3a09a1d9):

```
$ python3 tools/gate-registry-check.py --repo "$S/lane" --rev 3a09a1d93dcc16799cf6c4b48786e6440af134c4
unregistered tools/round47-append-audit-v2-check.py
unregistered tools/round47-live-replay-audit.py
registered 38 unregistered 2 defective 0
exit=1
```

After (worktree mode on the clone detached at the same commit, proposed section appended):

```
$ git -C /fast/scratch/hyaku/kama-r47/S9Skill/lane rev-parse HEAD
3a09a1d93dcc16799cf6c4b48786e6440af134c4
$ grep -n "^## Round-47" SKILL.md
1444:## Round-47 instrument registry (append-only v2 calibration, live receipt replay)
$ python3 tools/gate-registry-check.py
registered 40 unregistered 0 defective 0
exit=0
```

`git diff --stat` in the clone: `SKILL.md | 21 +++++++++++++++++++++`, 1 file changed, 21 insertions — the change is a pure append, no existing line touched. `defective 0` is the gate's meaning check too: every repo-relative path token in the entry/self-test/write-scope cells exists at the evaluated revision, and no row is thin or has an empty entry/exit-map cell.

Selftests measured at the same commit (values quoted in the rows):

```
$ python3 tools/append-only-audit.py --selftest --scratch <existing dir>
AOA_SELFTEST pass=15 fail=0            exit=0
$ python3 tools/kama-live-replay.py --selftest --scratch <existing dir>
KLR_SELFTEST pass=10 fail=0            exit=0
$ python3 tools/kama-llamacpp-live.py --selftest
selftest: ok; closed tcp6 listeners ::1:42295, ::ffff:127.0.0.1:40633   exit=0
$ python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip 3a09a1d9…
selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True
tip=3a09a1d93dcc16799cf6c4b48786e6440af134c4 base=172b8ad040d51ce8c011238c1408d4e0b6aa9595
exit=0
```

Not run by this seat: the C2 counter's network legs (three ~24 MB replays, ~73 MB total). Its row carries the L1 pre-wave dry-run line `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False` and says in the cell that these are the L1's values, so the row cannot be read as this seat's measurement. Also not run: `gate-registry-check.py --selftest` — its arm 6 evaluates the lane's `master` tip (46a924e0), whose `SKILL.md` is byte-identical to 3a09a1d9's (`git diff --stat 3a09a1d9 46a924e0 -- SKILL.md` empty), so that arm stays red until the L1 integrates this section.

## Touched surfaces

- `.ufo/waves/round-47/w1/out/S9Skill/` (all deliverables, listed at the end).
- `/fast/scratch/hyaku/kama-r47/S9Skill/` — one `--shared` clone, detached at 3a09a1d9, plus selftest fixture dirs; deleted before exit.
- Nothing else. The lane repo was read only (`git -C … show`, `cat-file`, `ls-tree`, file reads); no jj or git mutation there, no fleet-root write, no service started, no package or tool installed, no subagent spawned, no `agent://all` message.

## Findings

1. **Both new tools crash (exit 1, traceback) instead of refusing (exit 2) when `--scratch` does not exist.** `tools/append-only-audit.py:477` (`root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())`) and `tools/kama-live-replay.py:178` (`d = tempfile.mkdtemp(prefix="klr-st-", dir=root)`) call `mkdtemp` on a caller-supplied directory without creating it. Reproduction at 3a09a1d9:
   ```
   $ python3 tools/append-only-audit.py --selftest --scratch /nonexistent/x
   FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/x/aoa-77177vit'   exit=1
   $ python3 tools/kama-live-replay.py --selftest --scratch /nonexistent/x
   FileNotFoundError: [Errno 2] No such file or directory: '/nonexistent/x/klr-st-mf_evsvn'   exit=1
   ```
   Neither docstring states that `--scratch` must pre-exist, and exit 1 is the documented "ran and differs" / "at least one event partial" code, so a caller reading the exit code alone misdiagnoses a setup error as a substantive failure. Proposed fix (not applied: lane is read-only for this seat):
   ```diff
   --- a/tools/append-only-audit.py
   +++ b/tools/append-only-audit.py
   @@ -474,7 +474,8 @@ def main(argv=None):
        a = ap.parse_args(argv)
        if a.selftest:
   -        root = tempfile.mkdtemp(prefix="aoa-", dir=a.scratch or tempfile.gettempdir())
   +        base = a.scratch or tempfile.gettempdir()
   +        os.makedirs(base, exist_ok=True)
   +        root = tempfile.mkdtemp(prefix="aoa-", dir=base)
   ```
   and the same two-line shape at `tools/kama-live-replay.py:176-178`; alternatively catch `OSError` around `mkdtemp` and return 2. The two round-47 counters do not share the defect — they call `os.makedirs(root, exist_ok=True)` first (`tools/round47-append-audit-v2-check.py:597`, `tools/round47-live-replay-audit.py:216`), which is why the counter path is safe and this only bites a human re-running the tools by hand. Both rows in the proposal state the current behaviour and the required workaround, so the registry does not advertise a flag contract the tool does not honour.
2. **The C2 row must stay visibly non-green until integration.** At 3a09a1d9 the counter is `met=False` purely on `newrow` (no `b11909` row in `corpus/SOURCES.md` yet). The row quotes the L1 dry run verbatim and attributes it, so a reader cannot mistake a pre-wave red for a pass; when the row is integrated the L1 should replace that cell's pre-wave line with its integration receipt.
3. **The gate resolves paths in three of the five cells only.** `defective 0` covers the entry-command, self-test and write-scope cells; running the gate's own `registry_rows`/`RE_PATH` over the proposal lists exactly `tools/round47-append-audit-v2-check.py`, `tools/round47-live-replay-audit.py`, `tools/kama-live-replay.py`, `tools/append-only-audit.py`, `tools/kama-llamacpp-live.py` and `registry/endpoint-consumers.tsv`, all committed at 3a09a1d9 (each counter's own path is exempt). The C2 row's `.ufo/waves/round-47/c2/live/receipt-1.json` sits in an exit-map cell, which the gate never resolves, so moving or deleting that evidence would not turn the gate red — prose drift stays a review duty.

## Out of scope / not done

- The proposed text is not applied to the lane's `SKILL.md` (read-only for this seat; the L1 integrates). The patch is in the out dir.
- No C2 network replay, no counter reruns beyond the one local C1 run whose output is quoted.
- No fix applied to the `--scratch` defect; proposed diff only.

## Artifact paths (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill.md` — this report
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/skill.md` — proposed SKILL.md section (registry table + `### Re-running live evidence`), ready to append
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/proposed-skill.patch` — the same section as `git diff` against the clone's SKILL.md (sha256 `6048e60c17c4d5718b123d759d636c038b7adf96d3643750de1f8d658321e472`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/gate-before.txt` — gate at 3a09a1d9 without the section (exit 1)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/gate-after.txt` — gate in the clone at 3a09a1d9 with the section (exit 0)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/selftests.txt` — measured selftest and counter transcripts
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/finding-scratch.txt` — the missing-`--scratch` transcript
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Skill/receipt-1.json` — byte copy of `.ufo/waves/round-47/c2/live/receipt-1.json` (sha256 `a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d`, equal to the lane file)
