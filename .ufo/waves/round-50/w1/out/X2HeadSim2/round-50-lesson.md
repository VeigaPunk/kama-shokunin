# kama round 50 lesson

author: the integration rehearsal of seat `X2HeadSim2` on a scratch clone; the lane L1's integration replaces the body. The file is landed here so the three rows whose `used-by` names it (`S496`, `S497`, `S498`) stop tripping `E11` in `scripts/sources-census.sh validate`
date: 2026-10-27
base: `26ecba64ad6fb571d09074b07202d1618a46ecd1` (round-49 closure; round-50 start census `.ufo/waves/round-50/census/start.out`)
freeze: `.ufo/waves/round-50/preregistration.json` (`frozen_at_utc` 2026-10-27T00:20:47Z)
build: `97c864bead3ee4a2f629574e77263d33834ec98a`
measured: SCORECARD §Round-50 measured results

## Claims

- **C1 operability 8→8 — the replay bound to its own process tree and to the model bytes the server mapped, sourced on S496 and S497.** `tools/kama-live-replay.py` starts the live tool isolated (`python -I`) with an allow-listed environment (PATH, HOME, LANG, LC_ALL, TMPDIR) and a parent-death SIGTERM through `preexec_fn`, and sets its own parent-death signal, so killing whatever started a replay takes replay, live tool and server down (round-49 closure R2). `tools/kama-llamacpp-live.py` records `model_mapping` in the receipt (dev, inode and pathname of the file the server maps, re-opened `O_NOFOLLOW`, `fstat`-checked and hashed), and the replay refuses a rerun whose mapped model does not hash to the receipt's model (closure R1). Frozen counter `tools/round50-replay-bind-audit.py`: each of the three committed v5 b11909 receipts replayed from a `python3 -I -c` invoker with planted canaries, then judged on the exe digest, listener ownership, a fresh nonce against the counter's own vocabulary, the replayed tree, canary absence, the mapped model joined through the rerun `child_pid`, and a SIGKILL of the invoker. Build time `bind=1 teardown=1 newrow=1 bound=3/3 met=True`; base `bind=0 teardown=0 newrow=0 bound=0/3 met=False`.
- **C2 calibration 7→7 — append-only-audit v5, sourced on S498.** `key(l)` drops one trailing carriage return; sections ignore `## ` lines inside CommonMark fenced blocks; `origin(l)` is the union, over every birth of `key(l)` among the commits reachable from the tip, of the section titles holding it there, so the verdict no longer depends on rev-list order; `graded + ungraded == deleted` and the deletion count equals `git diff --numstat`. Frozen counter `tools/round50-append-audit-v5-check.py`: twelve constructed fixtures (the round-49 eight plus order-a, order-b, fence, crlf-launder) and the lane leg. Build time `fixture=1 lane=1 scenarios=12/12 met=True`; base `fixture=0 lane=1 scenarios=9/12 met=False`.

Measured values: SCORECARD §Round-50 measured results.

## Gate

| Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why |
|---|---|---|---|---|---|
| S496 | admit (tier A, mined) | https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html | 2026-10-27 (man-pages 6.19, page dated 2026-02-08; text copy `.ufo/waves/round-50/c1/proc_pid_maps.5.txt`) | "The pathname field will usually be the file that is backing the mapping." (§DESCRIPTION) | grounds reading which file a running server maps, then hashing that same file through its pathname |
| S497 | admit (tier A, mined) | https://man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html | 2026-10-27 (man-pages 6.19, page dated 2026-02-08; text copy `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt`) | "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process" (§DESCRIPTION) | grounds the replay's and the live tool's parent-death signal, which takes replay, live tool and server down when the process that started them dies |
| S498 | admit (tier A, mined) | https://spec.commonmark.org/0.31.2/#fenced-code-blocks | 2026-10-27 (text copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`) | "A code fence is a sequence of at least three consecutive backtick characters or tildes." (§4.5) | grounds a section scanner that must not treat a `## ` line inside a fence as a heading |

## Rehearsal scope

This body is a rehearsal stub: it carries the claims and the three source gate rows so the registry's `used-by` resolves on disk. `corpus/lessons/*.md` is graded (`A-corr`, every line): the L1's integration appends the measured lesson rather than rewriting these lines.
