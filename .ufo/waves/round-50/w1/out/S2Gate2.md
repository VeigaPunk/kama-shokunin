# S2Gate2 — round-50 Gate decisions (kama, wave 1)

Verdict: **ADMIT** — at the measured build `97c864bead3ee4a2f629574e77263d33834ec98a`, C1 is
`bind=1 teardown=1 newrow=1 bound=3/3 met=True` and C2 is `fixture=1 lane=1 scenarios=12/12
met=True`, both independently reproduced on my own shared clone; the three named rejects
(environ-only, maps-inode-only, pdeathsig-only) and three C2 calibration rejects each resolve
reject-the-shortcut / accept-the-build with a stated flip condition; one minor defect in both
frozen counters (`--out` write) is reported, not patched.

Deliverable: `.ufo/waves/round-50/w1/out/S2Gate2/gate.md` (full claim / evidence / verdict /
flip-condition text for D1–D6, limits, findings).

## Commands, exit codes, outcomes

All runs used `$S=/fast/scratch/hyaku/kama-r50/S2Gate2` (TMPDIR there) and a read-only
`git clone --shared` at `$S/lane` (HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6`). No lane
file, counter, preregistration or control was edited; the lane was not mutated.

| # | command | exit | outcome |
|---|---|---|---|
| 1 | `git show 97c864be:<counter> \| sha256sum` (both counters) | 0 | `ff6ac2ac…` and `925f07a4…`, equal to prereg `counter_sha256` |
| 2 | `round50-replay-bind-audit.py --repo $S/lane --tip 97c864be… --scratch $S --out …/c1-build.out` | 0 | `bind=1 teardown=1 newrow=1 bound=3/3 met=True`; 3/3 binds joined (pids 2795687/2807768/2827712), teardown `3 descendants; after 0.10 s alive [] port refuses ok`, newrow `| S496 |` |
| 3 | `round50-append-audit-v5-check.py --repo $S/lane --tip 97c864be… --scratch $S --out …/c2-build.out` | 0 | `fixture=1 lane=1 scenarios=12/12 met=True`; lane `ungraded_lines 89`; event 0718b6abbda6 `72 <= 72` |
| 4 | same counter `--tip 26ecba64…` | 1 | `fixture=0 lane=1 scenarios=9/12 met=False`; FAILs `order-b`, `fence`, `crlf-launder`; `ungraded_lines 82` — reproduces `controls/base.c2.out` |
| 5 | same counter `--tip 3b79eadd…` (HEAD) | 0 | `fixture=1 lane=1 scenarios=12/12 met=True`; tools unchanged vs build |
| 6 | `python3 $S/exp/exp1.py $S <lane>/tools` | 0 | environ clean while planted `sitecustomize` imported (marker line); `/proc/1/environ` EACCES; `environ_keys(1) -> None` |
| 7 | `python3 $S/exp/exp2.py $S <lane>/tools` | 0 | genuine model: inode+hash pass; host copy: inode-only passes, counter `mapped_model -> None`, live tool records `sha256 afb81fdc… ≠ MODEL_SHA` |
| 8 | `python3 $S/exp/exp3.py` | 0 | `ignore_survives=True`, `fork_grandchild_survives=True`, `default_child_dies=True` |
| 9 | `git -C $S/lane diff --stat 97c864be..HEAD -- tools/ corpus/` | 0 | `corpus/SOURCES.md | 2 +-` only; `tools/` unchanged |
| 10 | `pgrep -af llama-server` / `pgrep -af S2Gate2` after runs | — | nothing referencing my scratch/out; peers' scratch servers visible, untouched |

The C2-at-base run (4) is mine; C1 at the base was not rerun — its preregistered control is
cited, not re-executed (limit below).

## Gate decisions (detail in gate.md)

- **D1 — reject `/proc/<pid>/environ` alone.** Evidence 6 plus the counter's own fail-closed
  path: `tools/round50-replay-bind-audit.py:271-277` (`environ_keys` returns `None` on
  `OSError`), `:353-359` (None graded a problem), `:480-486` (marker check); build side
  `tools/kama-live-replay.py:88,112-115,319` (`-I`, four allowed names + TMPDIR),
  `:314-318,332` (child preexec). Accepted proof: canary absent **and** marker empty.
  Flip: only if environ sampling is shown complete and unforgeable (ablation control "no env
  allow-list" would have to read met with the marker check removed).
- **D2 — reject maps dev+inode without the hash.** Evidence 7 plus
  `round50-replay-bind-audit.py:309-341` (`:333` dev/inode, `:337` `MODEL_SHA`),
  `kama-llamacpp-live.py:678-734,2003` (`O_NOFOLLOW`, fstat dev/inode, hash recorded at
  `child_pid`), `kama-live-replay.py:343-348` (refuses on hash mismatch),
  `round50-replay-bind-audit.py:472-476` (receipt hash/dev/inode == observation).
  Accepted proof: dev+inode+sha256 == frozen model. Flip only under proven byte-immutability of
  a mapped inode with a hash-removed variant still rejecting the host copy.
- **D3 — reject `pdeathsig` alone.** Evidence 8 plus `kama-live-replay.py:100-108,587,312-318,332`,
  `kama-llamacpp-live.py:661-675`, and the observation leg
  `round50-replay-bind-audit.py:497-525` (snapshot `:505`, SIGKILL invoker `:509`, 30 s poll
  `:112,512-514`, `ok` requires empty alive set + refusing port `:515-519`). Accepted proof:
  empirical kill + descendant/port observation (build: 0.10 s). Flip only if tree-wide
  uncatchable delivery is shown and the observation leg can be removed without a survivor.
- **D4–D6 — C2 rejects** (rev-list-order origin, fence-blind sections, byte-exact keys):
  rejected by the *same* counter at the base (`order-b`, `fence`, `crlf-launder` FAIL, evidence 4)
  and accepted at the build (12/12, evidence 3). Flip conditions in gate.md.

## Defect (minor; both frozen counters)

`--out` is opened without creating its parent directory, after the summary is printed. A missing
directory turns a `met=True` run into a traceback and exit 1 — indistinguishable from "not met"
by exit code, with no receipt written. Observed:

```
$ python3 <lane>/tools/round50-append-audit-v5-check.py --repo $S/lane --tip 97c864be… --scratch $S --out <missing-dir>/c2-build.out
tip=97c864bead3ee4a2f629574e77263d33834ec98a
fixture=1 lane=1 scenarios=12/12 met=True
…
Traceback (most recent call last):
  File "<lane>/tools/round50-append-audit-v5-check.py", line 545, in <module>
  File "<lane>/tools/round50-append-audit-v5-check.py", line 537, in main
FileNotFoundError: [Errno 2] No such file or directory: '<missing-dir>/c2-build.out'
C2_EXIT=1
```

- exact lines: `tools/round50-append-audit-v5-check.py:537` and the identical pattern at
  `tools/round50-replay-bind-audit.py:597`.
- proposed fix (not applied): `os.makedirs(os.path.dirname(os.path.abspath(a.out)),
  exist_ok=True)` before the open, or wrap the write and return 2 with
  `could-not-write-receipt: <path>: <err>` so receipt loss is distinguishable from not-met.

My gate reading is unaffected: evidence runs 2–5 used an existing out directory and exited 0/1
as their summaries say.

## Cross-checks (passes)

- Counter sha256 equal to the preregistration (evidence 1); lane measured receipts
  (`.ufo/waves/round-50/measured/c1-build.out`, `c2-build.out`) match my independent runs line
  for line on every summary and lane detail (`ungraded_lines 89`; `0718b6abbda6 72 <= 72`).
- C2 at base reproduces its frozen control (evidence 4 vs `controls/base.c2.out`), including
  `ungraded_lines 82` and the three FAIL scenarios.
- `tools/` unchanged from build to HEAD; both counters still meet at HEAD (evidence 5).

## Out of scope / known integration items (not re-reported)

The two round-50 counters are not yet in SKILL.md's instrument registry; SCORECARD/LOG/lesson/
QUALITY/README round-50 entries are scribe items; S496/S497/S498 `used-by` names
`corpus/lessons/round-50.md`, which lands at integration; the gate registry will report both
counters unregistered. I did not edit any of those. I did not rerun C1 at the base, did not
trace kernel signal delivery, and did not test LD_PRELOAD/modified-PATH injection (prereg limits).

## Environment / tooling

No installs or upgrades; nothing written outside my scratch and the two deliverables. One
`curl` 1 KB range probe to huggingface.co to check connectivity; the counters downloaded
llama.cpp b11909 (~75 MB per replay) and the 1.2 MB model, started three loopback
llama-server processes and tore them down (own teardown: `alive [] port refuses`). No
llama-server I started remains; `pgrep -af` showed only other seats' scratch processes
(untouched).

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/gate.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/c2-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/c2-base.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/c2-head.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/exp1-environ.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/exp2-maps-inode.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/exp3-pdeathsig.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/S2Gate2/exp1.py`, `exp2.py`, `exp3.py` (drivers)
