VERDICT: confirm — both predicates were born in `b8e485c` as literal transcriptions of the L1 spec, no later commit ever touched them, and every pre-falsify warning stopped short of the exact failure mode (one seat actively certified `returncode is not None` as "a real proof").

# Reconstruction — why `teardown_exited` is `returncode is not None` and `health_ready` is status-only

Scope: `tools/kama-llamacpp-live.py` only, reconstructed from committed bytes (`git log -p`/`git show`/`git blame`/`git log -S`), the round-16 wave specs, advice files and the round-16 lesson. No harness, gate, probe or llama-server was run.

## 1. Timeline with hashes

| When (local, 2026-10-20) | Object | Fact |
|---|---|---|
| 10:24:39 | build wave dispatched | `build/spawn-result.json` `"at": "2026-10-20T13:24:39.838098+00:00"` |
| before 10:50:42 | `build/make_spec.py:69` | The LiveHarness prompt fixes both semantics (quoted in §2) |
| 10:50:42 | **b8e485c** | Creates the file: 989 lines, blob `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea`; `health_ready` at `:872-873`, `teardown_exited` at `:955-958`, DOC at `:107-109` |
| 10:53:14 | falsify wave dispatched | `falsify/spawn-result.json` `"at": "2026-10-20T13:53:14.911901+00:00"` |
| 10:5x–11:10 | working tree | L1 applies falsify-wave repairs while the wave runs; reviewers observe the file change under them |
| 11:10:32 | **726f737** | Repair commit; file +187/−98 → 1078 lines, blob `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` (**= current bytes**) |
| 11:11:54 | `falsify/advice/ReviewLiveHarnessCode.md` written | Reviews exactly blob `b8c5e8d4…`; finds H1/H2/M1 (§4) |
| 11:15:00 | **ccc4bb3** | Records dispositions; lesson keeps the weak checks as debt, not defect |
| 11:16:57 | **cff9e62** (tip) | Round-16 verifier spot-check repeats the debt line |

`git log --all -S"returncode'] is not None" -- tools/kama-llamacpp-live.py` returns exactly one commit, `b8e485c`: the predicate was introduced once and never rewritten. `git blame` confirms both predicate lines still carry `b8e485c`; `git diff b8e485c 726f737 -- tools/kama-llamacpp-live.py | grep -c "health_ready\|teardown_exited"` = **0**.

## 2. Which commit and what intent

**Single origin: `b8e485c`** (author and committer `kama-shokunin <kama@shokunin.local>`, 10:50:42). The later commit `726f737` changed `teardown()`'s `sigterm_sent` guard (F5) but neither check.

`teardown_exited` — the predicate is a **literal transcription of the L1-written spec**, not an implementer's shortcut:

- `.ufo/waves/round-16/build/make_spec.py:69` — "Teardown: SIGTERM process group, wait 10s, SIGKILL fallback; **prove process exited (returncode)** and port refuses connections". The same sentence is in the dispatched artifact, `.ufo/waves/round-16/build/spec.json:59` (both files first committed in `b8e485c`, so this is the build-wave text).
- `tools/kama-llamacpp-live.py:1026` — `receipt['teardown']['returncode'] is not None,` — exactly that clause, nothing more.
- The same file's own provenance string, `tools/kama-llamacpp-live.py:107-109`: "lane ownership: the spawned process group must terminate on SIGTERM/SIGKILL (**returncode observed**)". The doc says *process group*; the code observes one child's exit code. The conflation is present from birth. [INFERENCE] The intended meaning was "the child was reaped (not a zombie, not a hang)", i.e. a harness-completion sentinel — consistent with `teardown()` returning `returncode=None` only when `wait()` times out twice.
- The implementer's own report records the same intent verbatim (`build/advice/LiveHarness.md:17`): "SIGTERM process group → 10 s → SIGKILL; **proves returncode + port refusal**". No caveat about abnormal exits appears there; its "Known limitations" lists only the bind race and the `/proc`-only ownership proof.
- The capability statement that this check underwrites is `build/make_spec.py:15`: "captures the documented lifecycle surfaces, runs kama-probe against it, **tears it down and proves teardown**".

`health_ready` — the predicate implements the spec's readiness exit condition, while its `documented_by` cites a body that is never graded:

- Spec readiness loop: "tight loop alternating GET /health … **until /health is 200** or timeout" (`make_spec.py:69`), and the checks list names `health_ready` with no body clause.
- `tools/kama-llamacpp-live.py:938-939` — `checks.append(_check('health_ready', health_status == 200, {'status': health_status}))`.
- The same file's provenance string, `:79-80`: "GET /health returns 200 **{"status":"ok"}** once the model is loaded". The doc asserts the body; the predicate discards it. That divergence was created in `b8e485c`, not introduced later.

[INFERENCE] Both predicates were authored as *conformance reproductions of spec claims* ("did the run reach the documented ready state; was the child reaped"), not as *falsification hypotheses about the subject*. That is why neither has a negation: the spec never stated one, and no seat was tasked with writing one during build.

## 3. What the predicates actually establish

- `teardown_exited` passes whenever `wait()` returned anything: normal SIGTERM rc 0/−15, self-exit rc 0 with no signal sent, and SIGKILL rc −9. It fails only if the process survives SIGKILL for 5 s (D-state) — i.e. it grades the **harness's** ability to reap, never the **server's** shutdown behaviour. The `sigkill_sent` field is recorded in `observed` from `b8e485c` onward but never read by the predicate (`:1025-1028`).
- `health_ready` re-fetches `/health` after readiness (`ready_captures`, `:566-570`), so it *can* flip if the server degrades in that sub-millisecond window, but it accepts any body under status 200. A `{"status":"degraded"}` 200 passes.
- Round-16's real receipt cannot distinguish strong from weak predicates: it records the cooperative case — `health_ready.observed {"status": 200}` with `captures.health.body {"status":"ok"}`, `teardown_exited.observed {"returncode": 0, "sigkill_sent": false}`, `teardown.sigterm_sent true, term_wait_ms 3` (`.ufo/waves/round-16/live/receipt.json`). The "10/10, gate VALID" evidence is therefore compatible with both a fail-capable and a vacuous check.

## 4. Did any seat warn before round-16 falsify? Yes — four, none exactly

| Seat (pre-falsify, committed in `b8e485c`) | Warning | Strength |
|---|---|---|
| `build/advice/ReviewHarnessDesignRisk.md:227-228` | "`teardown_exited`'s `returncode is not None` is a real proof." | **False reassurance** — the design review certified the exact predicate that later proved vacuous; told under "Checked and adequate" |
| `build/advice/SimplifierHarness.md:204` | "`health_ready` is the readiness loop's exit condition, so it cannot fail independently; keep" | Names non-falsifiability, then recommends **keep** |
| `build/advice/ConnectMori.md:45-46` | "Neither proves the **process group** is gone." | Correct scope critique of the *spec*; proposes a `pgid_absent` fold at `:92`, never implemented |
| `build/advice/SentinelLiveSafety.md:70` | "`teardown_exited` (child returncode) does not prove that MCP/tools subprocesses … are gone." | Same group-scope point; recommends a new `teardown_group_empty` check, not adopted |

Nothing in the build wave warned that the **health body** was ungraded. The build wave (81 seats) contained no seat scoped to "can this check fail?" — that question first appears as the falsify seat `ReviewLiveHarnessCode` ("correctness of each of the 10 checks … any check that cannot fail?").

## 5. The falsify wave found it — 82 s after the repair commit, and it was filed as debt

- `falsify/advice/ReviewLiveHarnessCode.md:1` — "two cannot fail for any userspace process behavior … no check at all grades the loading envelope the harness now captures". Its reviewed sha256 is `b8c5e8d4…`, i.e. **the bytes committed as `726f737`**.
- H2 `:82-93` — "`teardown_exited` proves reaping, not teardown"; the `se` control: self-exit rc 0, "`teardown_exited` **passed**, `returncode 0`, `sigterm_sent false`".
- M1 `:95-102` — "`health_ready` ignores its documented body"; `hb`: 200 + `{"status":"degraded"}` → "10/10, exit 0, gate VALID".
- Its mtime is 11:11:54, the repair commit is 11:10:32: the findings post-date the commit and could not have been incorporated without a further change, and none was made. [INFERENCE] the reviewer was also watching the file mutate mid-review ("The harness changed twice under me during this review"), so the fix owner was coding against earlier findings while this review was still in flight.
- The round then **recorded** the defect instead of repairing it: `corpus/lessons/round-16.md:160-162` — "live checks `health_ready` (status only), `teardown_exited` and `teardown_port_closed` are weak and `loading_envelope_exact` is not graded (`ReviewLiveHarnessCode.md`)". The same debt is repeated in `corpus/lessons/round-16-verifier-spotcheck.md:187`.

## 6. Two structural reasons the defect survived the repair

1. **The repair added the missing evidence and left it unused.** `726f737` added the F5 guard `if proc.returncode is None:  # F5: killpg only while child is alive` before setting `sigterm_sent` (diff hunk at `teardown()`), which is exactly what makes the self-exit case *observable* as `sigterm_sent: false`. The check that should consume it was not touched (§1: 0 diff lines). The fix made the receipt truthful and the verdict still blind.
2. **The gate mirrors the producer instead of re-deriving a stronger claim.** `tests/llamacpp-live/check-receipt.py:745-756` re-derives `teardown_exited` only from `teardown.returncode is not None` (plus an `observed`-equals check); `:628-636` re-derives `health_ready` only from `captures.health.status == 200`. The falsify gate review names this: `falsify/advice/ReviewReceiptGateCode.md:177` — "`teardown_exited` is vacuous, identical to the producer". So the v1 gate can never catch either defect, which is why C2 must state that `check-receipt.py` "re-derives every v2 check" rather than "still validates v1 unchanged" alone.

## 7. Consequence for the C2 repair (advice only)

- The v2 predicates are not "tighten a comparison"; they must encode a **negation that the subject can exhibit**: `teardown_exited` should require harness-initiated termination (`sigterm_sent or sigkill_sent`) plus the documented graceful status family, and must distinguish self-exit from SIGKILL; `health_ready` should parse the body and require `status == "ok"`. `sigterm_sent` and the captured body are already in the receipt, so no schema widening is needed to make them fail-capable.
- Because the receipt is producer-written, any v2 check must be re-derived by `check-receipt.py` from raw fields (not from `passed`), or a forged receipt re-opens the same hole; the existing gate's conditional `observed` cross-checks (`ReviewReceiptGateCode.md` F9) are the pattern to avoid copying.
- The integrity lesson is upstream of the code: the spec sentence "prove process exited (returncode)" is what both the producer and the gate implemented. A v2 spec should state the falsifier, not the observation.

## Limitations

- Read-only reconstruction; nothing was executed (no harness, gate, probe, llama-server, or `ss`). No scratch runs were needed.
- "Intent" is inferred from the committed spec text, the file's own `documented_by` strings, and the implementer's report. Private reasoning is not in the repo; all attributions of motive are [INFERENCE].
- The 11:11:54 timestamp is filesystem mtime, not committed metadata; git only proves the review was committed at `ccc4bb3` (11:15:00). The post-commit ordering rests on the mtime plus the fact that no later commit changes the predicates.
- Whether H2/M1 were also raised mid-wave over IRC is not recorded in the repository; the mtime only bounds the written report.
- Line numbers cited for `b8e485c` are that blob's own numbering (`:872`, `:955-958`, `:107-109`); current numbering is `:938`, `:1025-1028`, `:107-109`.

## Tools installed or updated

None. No pacman, `uv`, npm or binary installs; no network access.
