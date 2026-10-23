# RowReview02 — falsify F28-03 (n_indent) / F28-04 (n_keep)

Seat: KamaR28.RowReview02, round 28 wave 2 (FALSIFY), leaf (no subagents).
Scope: rows F28-03 / F28-04 of claim C1. Verdict per row: **holds**. No
statement in either SKILL.md meaning cell was found false, unsupported, or
over-general; both rows are counted in the final receipt and that verdict is
right.

## Port substitution (must-read caveat)

Assigned port **48302** is held by harness infrastructure for the whole run:
`node proxy-tmp.cjs` (pid 3138780, node-MainThread, started 03:40:30Z) keeps an
ESTABLISHED client connection `127.0.0.1:48302 -> 127.0.0.1:3222` (harness
control plane; tx/rx counters show active use). llama-server cannot bind:
`couldn't bind HTTP server socket ... port: 48302`; independent Python bind
tests fail for plain, `SO_REUSEADDR`, and `SO_REUSEPORT` (EADDRINUSE). Not a
lane/seating conflict (no other llama-server uses 48302). Live probes were run
on substitute port **48303** (verified free; outside 47600-47619 and all other
seats' ports). Main (KamaR28) was notified of the blocker and the substitution.
Server: exact pinned argv, `~/.local/opt/llama-b11755/llama-server -m
~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48303`,
under `timeout 900`; process group killed before return and confirmed by
`ss -ltnp` (no 48303 listener remains). No tools installed (nothing to record
under the 2026-10-19 tooling directive).

## Live re-measurement (my own runs, port 48303)

Request shape: counter's exact request `POST /completion` with body
`{"prompt": "Once upon a time", "n_predict": 1}` updated with the row's `set`.

| row | body | status | body sha256 | message |
|---|---|---|---|---|
| base (field-omitted) | `{"prompt": "Once upon a time", "n_predict": 1}` | 200 | `18b7eadd5845fc1fc5f69a165b5f8ad86dd0dee691a6bbcff766c6c111ba9963` | completion generated (generation_settings present) |
| F28-03 | `{..., "n_indent": -1}` | 400 | `23511a19f32b2168042f7fb97ae327256dce4395ca3b417f4edb5d074ca967d3` | `Field 'n_indent': Value must be between 0 <= value <= 2147483647, but got -1` |
| F28-04 | `{..., "n_keep": -2}` | 400 | `748f5fcb3dc688cfb086a826e7228f1d80c27afd70d2b1372be0255ec9231f8d` | `Field 'n_keep': Value must be between -1 <= value <= 2147483647, but got -2` |

Both response sha256s match the registry `live_by_seat.response_sha256` and the
final receipt verbatim. Outcomes confirmed: reject, HTTP 400, exactly the
declared bounds; no clamping, no stored effective value.

## Source verdict (pinned snapshot `llama.cpp-704366d/server-schema.cpp`)

- F28-03: declaring line 50 `add((new field_num("n_indent", params.n_indent))`,
  limits line 51 `->set_hard_limits(0, INT32_MAX)`, desc line 52 (minimum line
  indentation, code-completion tasks). Source fully explains the observed
  reject with bounds [0, INT32_MAX].
- F28-04: declaring line 54 `add((new field_num("n_keep", params.n_keep))`,
  limits line 55 `->set_hard_limits(-1, INT32_MAX)`, desc line 56 ("Use -1 to
  retain all tokens from the prompt"). Source fully explains the observed
  reject with bounds [-1, INT32_MAX].

Local snapshot sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
== raw GitHub fetch at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad == recorded
S### hash. No handler override for either field (plain `field_num` hard-limit
path). Source verdict: **explains the outcome; nothing misleading**.

## Prose verdict (SKILL.md `## Round-28 request-field outcomes` cells)

- F28-03: "A negative n_indent is a hard HTTP 400 rejection rather than a clamp
  to zero, so code-completion clients must send 0 to disable indentation and
  never a negative number." Every clause is true: reject (not clamp) verified
  live; "send 0 to disable indentation" matches desc/default semantics (0 =
  minimum-indentation constraint off) and is not stated as a universal
  requirement beyond this field. **Holds; no corrected text needed.**
- F28-04: "n_keep accepts -1 to retain the whole prompt but rejects anything
  smaller with HTTP 400, so clients must use -1 rather than -2 and cannot rely
  on clamping." Every clause is true: -1 accepted per desc ("retain all tokens
  from the prompt"), -2 rejected live, no clamping observed. **Holds; no
  corrected text needed.**

## SOURCES / Gate verdict

- SOURCES.md S142 (n_indent, line 50) and S143 (n_keep, line 54): URL target
  `.../tools/server/server-schema.cpp#L50` / `#L54` @ 704366d76; fetched raw
  bytes hash `1f9d7b73b436...` (matches row, lesson, preregistration); quote
  verbatim: `add((new field_num("n_indent", params.n_indent)) ->set_hard_limits(0, INT32_MAX)`
  / `add((new field_num("n_keep", params.n_keep)) ->set_hard_limits(-1, INT32_MAX)`
  (lines L/L+1 whitespace-joined, 5 words, matches `corpus/lessons/round-28.md`
  Gate table exactly).
- Gate rows (round-28.md S142/S143): located quotes hold verbatim; per-row
  "fetched sha256" matches my independent fetch; opened-by DataG01 and access
  timestamps are not independently auditable from here but nothing contradicts
  them. SOURCES/Gate verdict: **holds**.

## Counted verdict

Both F28-03 and F28-04 are in `counted_ids` of
`.ufo/waves/round-28/final/c1-e49b4cf7-receipt.json` (counted 26, met true)
with empty `why`. That verdict is **right**: both rows satisfy the predicate
(registry id/field/value/outcome/meaning/source cells verbatim; single-key set;
declaring line cited; live outcome independently confirmed here).

## Findings

None of the two attacked rows is wrong, overstated, or harmful. No actionable
finding remains in scope for F28-03/F28-04. Residual risk: the live probe ran
on 48303 instead of the assigned 48302 (blocked by harness infra); the counter
receipt (run by the L1 from a fresh clone at the tip on its own ports) is
unaffected by this seat's port choice.
