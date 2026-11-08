# DRAFT — corpus/knowledge/router-props-autoload.md (seat SB01Entry, round 99, lane kama)

Status: DRAFT for the committer (KamaR99). Not applied to any tracked lane file by this seat.
Every number below was re-derived by this seat on 2026-11-08; the commands are in
`../receipts/` next to this file.

Proposed file body (replaces/extends `corpus/knowledge/router-props-autoload.md` committed at
the round-99 freeze commit `f6e7ccc2`):

---

source: S624 (llama.cpp `tools/server/server-models.cpp` @ tag b12177, line 2030 — the router's bare `GET /props` body is built from `params.models_autoload`), S625 (llama.cpp `common/common.h` @ same tag, line 705 — `bool models_autoload = true;`), S626 (rejected lead: the server README option table names the launch flag, not the props JSON field); own work `tools/kama-probe.sh` `router_autoload()`/`router_refine()` at the round-99 candidate and `tools/round99-autoload-states.py` cells. Prior art held before round 99: S581/`router-mode-readiness.md` (the bare `/props` reports `role: router` and `models_autoload`; autoload is the default and `--no-models-autoload` disables it), SKILL.md decision row `router-unloaded` (which lumped every unconfirmed-autoload answer into the autoload-off reason).
verified-at: 2026-11-08 — the three b12177 files fetched raw by this seat (HTTP 200; 111 675 B / 58 830 B / 136 429 B; digests `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108`, `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073`, `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137`; receipt `../receipts/s624-s626-reopen.txt`), the five live cells run against a loopback stub by `tools/round99-autoload-states.py` (`cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True`, probe_sha256 `829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21`, base_sha256 `40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e`; receipt `../receipts/c3-candidate-rerun.out`), and the frozen round-98 19-cell budget counter re-run on the candidate probe (`ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1`, exit 0; receipt `../receipts/c3-regression-r98.out`).
recheck: on-release — re-open `tools/server/server-models.cpp` at the then-pinned tag and confirm `get_router_props` still emits `models_autoload`; re-run `python3 tools/round99-autoload-states.py --repo . --rev master --work <scratch>` and require `mismatches=0`; if the field is renamed or the props body changes shape, the three-state rule is void.

# llama.cpp router: an unread `/props` autoload flag is not an "off" answer

## What the sources state (S624, S625)

- The router's bare `GET /props` builds its body from the running configuration: `{"models_autoload",      params.models_autoload},` (`server-models.cpp:2030`, inside `get_router_props` at 2021-2046), alongside `role` and `max_instances`.
- The field defaults to `true`: `bool models_autoload = true;` with the comment "automatically load models when requested via the router server" (`common/common.h:705`). The per-request `?autoload=true|false` parameter changes a request's behaviour (`is_autoload`, `server-models.cpp:1968-1973`), not the reported default.
- Therefore an "autoload off" router is an **explicit** configuration (`--no-models-autoload`), and an answer that could not be read is not evidence of it. Treating the two as the same reason misdirects the operator: one case is a configuration state, the other is a measurement failure that a re-probe can clear.

## The lane's three-state rule (round 99)

`router_autoload()` returns one of three states for a router whose matching entry is `unloaded` and not failed:

| State | Answer read | Probe reason |
|---|---|---|
| on | valid router document, `models_autoload: true` | `MODEL_OK` / `router-unloaded-autoload` |
| off | valid router document, `models_autoload: false` | `MODEL_UNLOADED` / `router-unloaded` |
| unread | fetch failed/timed out, body over the 4 MiB cap, not JSON, not a router document, or the field absent/not boolean | `MODEL_UNLOADED` / `router-autoload-unread` |

The verdict stays `MODEL_UNLOADED` (drift) for both off and unread: the change is the reason vocabulary, not the
verdict. An unread answer keeps the fail-closed reading; it no longer asserts an autoload-off state the probe did
not observe.

## Live cells (round 99, loopback stub, one unloaded entry with an existing `status.args[0]`)

| Cell | `/props` answer | base reason | tip reason |
|---|---|---|---|
| U1-slow-props | valid autoload-true body after 6.5 s (probe `--timeout 5`) | `router-unloaded` | `router-autoload-unread` |
| U2-oversize-props | 4.5 MiB body (over the 4 MiB cap) | `router-unloaded` | `router-autoload-unread` |
| U3-nonjson-props | HTML body | `router-unloaded` | `router-autoload-unread` |
| U4-nonrouter-props | `{"status":"ok"}` (no router role, no field) | `router-unloaded` | `router-autoload-unread` |
| P1-autoload-off | `{"role":"router","models_autoload":false}` | `router-unloaded` | `router-unloaded` |

U1–U4 flip; P1 is the positive control that kills a blanket rename of every non-on answer.

## Limits

- The cells are stub-fed HTTP answers, not a live llama.cpp router; the field's existence and default are source-grounded (S624/S625) but the runtime's current answer was not re-observed.
- Without `python3` the probe cannot parse the props body; the round-99 candidate reports `unread` in that branch, while the pre-round-99 probe reported off.
- `/props?model=<id>` routes to an instance and is not read; a per-request `?autoload=false` consumer is not modelled.
- A valid router document whose field is absent, or whose value is not a boolean, is graded `unread`. "Off" requires an explicit `false`.
- The verdict/exit code is unchanged; an undecided→loadable rule change is a different claim, not this one.

---

## SB01Entry notes for the committer (not part of the file body)

0. **What this draft changes against the committed file** (`corpus/knowledge/router-props-autoload.md`
   at `f6e7ccc2`) — exactly three lines, everything else byte-identical
   (`receipts/knowledge-draft-diff.out`):
   - `verified-at:` — the committed line cites `.ufo/waves/round-99/controls/c3-regression.out`
     (absent) and quotes `ROUTER_BUDGET99 cells=19` for the round-98 counter (which prints
     `ROUTER_BUDGET98`); the draft names the receipts this seat produced and adds `met=True` and both
     probe digests.
   - the S624 quote — the committed body collapses the source's inter-column spacing to one space;
     the draft keeps the source bytes (`{"models_autoload",      params.models_autoload},`,
     `server-models.cpp:2030`), so the "located quote" and the file agree.
   - the notes below (not part of the body).

1. The `verified-at` line in the freeze-commit copy of this file cites
   `.ufo/waves/round-99/controls/c3-regression.out` and quotes `ROUTER_BUDGET99 cells=19 mismatches=0`.
   Two problems, both checked by this seat:
   - that receipt path does not exist in the lane (the file is a measurement-time control the plan says is
     committed with M1/M2/M3; `ls .ufo/waves/round-99/controls/` shows no `c3-regression.out`);
   - the round-98 counter prints the prefix `ROUTER_BUDGET98`, not `ROUTER_BUDGET99`
     (`tools/round98-router-budget.py:7,716`). `ROUTER_BUDGET99` is the round-99 counter's prefix
     (`tools/round99-router-budget.py:21,711`). The plan's own C3 regression wording says
     `ROUTER_BUDGET98 cells=19 …` (`plans/round-99-claims.md`, C3 "Regression control"). The draft above
     uses `ROUTER_BUDGET98` and names the receipt that this seat produced.
2. The freeze-commit copy's `verified-at` also says "the round-98 19-cell budget counter re-run on the
   candidate probe"; the receipt that proves it is a measurement-time artifact. Either commit it with
   M3 or drop the sentence — the draft above keeps it and names the receipt path.
3. This seat's own re-run of that regression is complete:
   `ROUTER_BUDGET98 cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1`, exit 0,
   probe_sha256 `829fbde5…`, `slow_files=72`, `w03_seconds=644.8`, both passes
   (`receipts/c3-regression-r98.out`; a first attempt was SIGTERM'd by a 3000 s wall clock inside
   the load pass and is recorded there too). The counter's `base_sha256` in that run
   (`27065a5c…`) is the **round-98 counter's own BASE constant**, not the `439fdb3d` probe
   (`40ab387e…`) the round-99 instruments use; quoting the line without that distinction mixes two
   bases.
4. **The landed `controls/c3-regression.out` does not carry the line the landed `verified-at`
   quotes.** At `00394f3b` the file exists (untracked) with three lines — a `# command:` line
   (`--rev 00394f3b --burners 0`) and a two-line note that `burners 0` makes the second pass a plain
   re-pass — and **no** `ROUTER_BUDGET98 cells=…` summary line
   (`receipts/landed-state-vs-drafts.out` section D). The knowledge entry's `verified-at` cites it
   for `ROUTER_BUDGET98 cells=19 mismatches=0`. Either land this seat's receipt (which does carry the
   line, at default `--burners 64`, i.e. with a genuine load pass) under that path, or run the
   `--burners 0` command to completion and append its output — as landed, the citation has no bytes
   behind it.
