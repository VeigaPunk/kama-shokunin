source: S624 (llama.cpp `tools/server/server-models.cpp` @ tag b12177, line 2030 — the router's bare `GET /props` body is built from `params.models_autoload`), S625 (llama.cpp `common/common.h` @ same tag, line 705 — `bool models_autoload = true;`), S627 (llama.cpp `common/arg.cpp` @ same tag, line 3682 — the option callback is the only writer of `params.models_autoload`), S626 (rejected lead: the server README option table names the launch flag, not the props JSON field), S628 (rejected: the seat-reported `tests/unit/test_router.py` path is HTTP 404 at the pinned tag); own work `tools/kama-probe.sh` `router_autoload()`/`router_refine()` at the round-99 candidate and `tools/round99-autoload-states.py` cells. Prior art held before round 99: S581/`router-mode-readiness.md` (the bare `/props` reports `role: router` and `models_autoload`; autoload is the default and `--no-models-autoload` disables it), SKILL.md decision row `router-unloaded` (which lumped every unconfirmed-autoload answer into the autoload-off reason).
verified-at: 2026-11-08 — the b12177 files fetched raw (HTTP 200; digests in `.ufo/waves/round-99/sources/`; S628 is a 404 rejection), the eight live cells run against a loopback stub by `tools/round99-autoload-states.py` (`cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1`, `.ufo/waves/round-99/measured/c3.out`), the plain-call regression control (`listeners` on/off/non-router, `.ufo/waves/round-99/controls/c3-plaincall.out`), and the round-98 19-cell budget counter re-run on the candidate probe (`ROUTER_BUDGET98 cells=19 mismatches=0`, `.ufo/waves/round-99/controls/c3-regression.out`).
recheck: on-release — re-open `tools/server/server-models.cpp` at the then-pinned tag and confirm `get_router_props` still emits `models_autoload`; re-run `python3 tools/round99-autoload-states.py --repo . --rev master --work <scratch>` and require `mismatches=0`; if the field is renamed or the props body changes shape, the three-state rule is void.

# llama.cpp router: an unread `/props` autoload flag is not an "off" answer

## What the sources state (S624, S625)

- The router's bare `GET /props` builds its body from the running configuration: `{"models_autoload", params.models_autoload},` (`server-models.cpp:2030`, inside `get_router_props` at 2021-2046), alongside `role` and `max_instances`.
- The field defaults to `true`: `bool models_autoload = true;` with the comment "automatically load models when requested via the router server" (`common/common.h:705`). The per-request `?autoload=true|false` parameter changes a request's behaviour (`is_autoload`, `server-models.cpp:1968-1973`), not the reported default.
- The only writer of `params.models_autoload` is the option callback (`common/arg.cpp:3682`, S627): the bare props body reports exactly the launch/environment value, so an "off" answer is a configured state and there is no other assignment that could produce one.
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

## Live cells (round 99 amendment 1; loopback stub, one unloaded entry with an existing `status.args[0]`)

| Cell | `/props` answer | base reason | tip reason |
|---|---|---|---|
| U1-slow-props | valid autoload-true body after 6.5 s (probe `--timeout 5`) | `router-unloaded` | `router-autoload-unread` |
| U2-oversize-props | 4.5 MiB body (over the 4 MiB cap) | `router-unloaded` | `router-autoload-unread` |
| U3-nonjson-props | HTML body | `router-unloaded` | `router-autoload-unread` |
| U4-nonrouter-props | `{"status":"ok"}` (no router role, no field) | `router-unloaded` | `router-autoload-unread` |
| U5-field-absent | `{"role":"router"}` (router document, no field) | `router-unloaded` | `router-autoload-unread` |
| U6-field-nonboolean | `{"role":"router","models_autoload":"false"}` (string) | `router-unloaded` | `router-autoload-unread` |
| U7-wrong-role | `{"role":"worker","models_autoload":false}` (non-router doc) | `router-unloaded` | `router-autoload-unread` |
| P1-autoload-off | `{"role":"router","models_autoload":false}` | `router-unloaded` | `router-unloaded` |

U1–U7 flip and grade the exit code (`MODEL_UNLOADED`/exit 2); P1 is the positive control that kills a blanket rename of every non-on answer.

## Limits

- The cells are stub-fed HTTP answers, not a live llama.cpp router; the field's existence and default are source-grounded (S624/S625) but the runtime's current answer was not re-observed.
- Without `python3` the probe cannot parse the props body; the round-99 candidate reports `unread` in that branch, while the pre-round-99 probe reported off.
- `/props?model=<id>` routes to an instance and is not read; a per-request `?autoload=false` consumer is not modelled.
- A valid router document whose field is absent, or whose value is not a boolean, is graded `unread`. "Off" requires an explicit `false`.
- The verdict/exit code is unchanged; an undecided→loadable rule change is a different claim, not this one.
