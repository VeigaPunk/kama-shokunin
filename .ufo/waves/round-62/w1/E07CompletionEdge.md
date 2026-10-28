# E07CompletionEdge — completion request plane at edge args (round 62, w1)

Seat: leaf executor, axis **operability** (build & verify). Advisory only: no claim verdict,
no commit. Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` at tip
`65d7cad0fce90e34de37527cde22e97b63b118bf` (= `git rev-parse master`).
Frozen instrument: `tools/kama-completion-live.py` sha256
`71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f` (clean in `git status`;
byte-identical to the tip blob the C1 counter extracts).
Fixture digests verified before any run: model `stories260K.gguf`
`270cba1b…bd256d`, server `~/.local/opt/llama-b11755/llama-server` `b6a31a8e…cd804`
(both equal the tool's pins, so every receipt's `model_digest`/`server_digest` are
structurally true).

## What I ran

Edge arguments as assigned: `--temperature 0.5`, `--n-predict 1`, unicode prompt
`Grüße aus Zürich — 日本語 café ① naïve façade ☕🚀`, plus a hold dir with an outside
observer that POSTs its own request the moment `hold.json` appears and then drops
`release`. Three additional runs for contrast/stability (all on unregistered loopback
ports, `TMPDIR` = my scratch, receipts under
`.ufo/waves/round-62/w1/out/E07CompletionEdge/`):

| run | args (delta) | port | verdict | rc | checks | failed | not-evaluated |
|---|---|---|---|---|---|---|---|
| `A-edge-t05-np1` | temp 0.5, n_predict 1, unicode, hold | 33859 | `REQUEST_OK` | 0 | 17 | 0 | `completion_deterministic` |
| `A2-edge-repeat` | same as A (2nd sample) | 37119 | `REQUEST_OK` | 0 | 17 | 0 | `completion_deterministic` |
| `B-base-t00-np1` | temp **0.0**, n_predict 1, unicode, hold | 40239 | `REQUEST_OK` | 0 | 17 | 0 | none |
| `C-edge-nohold` | temp 0.5, n_predict 1, unicode, **no** `--hold-dir` | 36553 | `REQUEST_OK` | 0 | 16 | 0 | `completion_deterministic` (+ `hold_released` **absent**) |

Ports 33859 / 40239 / 36553 / 37119: `grep -c` in `registry/endpoint-consumers.tsv` = 0 each.
Receipts: `out/E07CompletionEdge/{A-edge-t05-np1,A2-edge-repeat,B-base-t00-np1,C-edge-nohold}.json`,
raw driver `out/E07CompletionEdge/drive.py`, llama-server log of run A
`out/E07CompletionEdge/A-edge-server.log`, consolidated `summary.json`, cross-grade
`counter-crossgrade.json`.

## Which checks became not-evaluated, and why

`check()` is called with `None` in exactly one place in the tool
(`tools/kama-completion-live.py:366`; 20 `check(` sites, 17 recorded in a full hold run).
So at temperature 0.5 the **only** degraded check is:

```
completion_deterministic: {"passed": null, "evaluated": false,
                           "reason": "skipped: temperature != 0"}
```

Verdict aggregation behaves monotonically: `evaluated_fail` ignores `None`,
`evaluated_none` only fires when *every* check is unevaluated, so one skip leaves
`verdict = REQUEST_OK`, rc 0 (run A, A2, C). The contrast run B (temperature 0.0) is the
same lifecycle with that check `evaluated: true, passed: true` — 17/17 evaluated. This is
the intended calibration: `--temperature 0.5` skips exactly one check and silently keeps
rc 0; any consumer that counts checks must read `evaluated`, not `passed`.

Run C shows a second, different degradation shape: with no `--hold-dir` the `hold_released`
key is **never created** (key absent, `n_checks = 16`) while the receipt still records
`hold: {"dir": null, "released": false}` and `verdict = REQUEST_OK`. Absent-check and
not-evaluated-check are therefore two distinct states a verifier must distinguish by
"key present?" and `evaluated`.

## Observed request plane at the edge args (run A, as captured)

- `/health` `{"status":"ok"}`; `/v1/models` data[0].id and `/props.model_alias` both
  `kama-completion-probe`.
- `POST /v1/completions` 200, `object=text_completion`, `model=kama-completion-probe`,
  `finish_reason="length"`, `choices[0].text="."`,
  `usage={"completion_tokens":1,"prompt_tokens":57,"total_tokens":58}`,
  `system_fingerprint="b11755-704366d76"` (matches `<build>-<commit>`),
  `timings.predicted_n=1`, `predicted_ms=0.001`.
- Malformed request (prompt removed) → 400 with
  `{"error":{"code":400,"message":"… key 'prompt' not found","type":"invalid_request_error"}}`.
- Unicode prompt is carried through `json.dumps` (ASCII-escaped) and tokenized without
  rejection: **57 prompt tokens** for a 33-character mixed German/CJK/emoji prompt — byte
  fallback on the 260K vocab, i.e. non-ASCII input costs extra tokens but the plane still
  answers 200. Text content is not graded anywhere, correctly.
- Hold window: `hold.released = true` in A, A2, B; my outside observer's own POST during
  the hold returned 200 with `model=kama-completion-probe`, same fingerprint, and
  `cached_tokens=56` (prefix cache already warm from the tool's own request) in A and B.
- Teardown: `sigterm_sent=true`, `returncode=0`, `port_closed=true`, `child_pre_dead=false`,
  `waited_ms` 3–4. After all runs: no listeners on 33859/40239/36553/37119 and no
  `llama-server` child of mine alive (`pgrep -af llama-server` lists only r61 scratch
  processes I did not spawn, untouched).

## Findings for the L1 (findings only — no verdict on C1)

1. **The counter's re-derivation does not read `evaluated`, and it re-derives
   `completion_deterministic` with no temperature gate.** `round62-c1-counter.py:149-152`
   recomputes `completion_envelope and c2.status==200 and ch2.text==ch1.text`; the
   inconsistency filter (`:176-180`) skips any stored `passed is None`. Cross-grading my
   receipts with the counter's own `grade()` (`out/E07CompletionEdge/counter-crossgrade.json`):
   - A / A2 (temp 0.5): stored `passed=null`, recomputed `True`, `inconsistent=[]`,
     `alltrue=True`.
   - C (no hold): stored `hold_released` absent, `required` silently loses the key, so
     `inconsistent=[]`, `alltrue=True`.

   Consequence: the counter would credit a run in which the determinism check was
   explicitly *not evaluated*, and would grade a hold-less receipt as fully true. The
   counter's own `score()` stays honest because `NONCE`/`live` witness come from its own
   `witness_run` (which passes `--hold-dir` and default temperature 0), so this is latent,
   not live — but it is exactly the shape a mutated receipt or a replayed receipt could
   ride. Fixes worth having: re-derive determinism only when the receipt's request records
   `temperature == 0.0` (else expect `None`), treat stored `evaluated=False` as
   not-creditable in `alltrue`, and require `hold_released` in `required` unconditionally.
2. **`--hold-dir` is optional at the tool level.** The frozen predicate requires hold mode,
   but nothing in the tool refuses a receipt without it, and the receipt still says
   `REQUEST_OK`. If the counter is the only holder of that requirement, an operator can
   legitimately get a `REQUEST_OK` request-plane receipt with no outside-observation window.
   Consider making `--hold-dir` required (or emitting `verdict` gated on `hold_released`)
   so the operability receipt cannot claim the lifecycle it did not run.
3. **At `--n-predict 1` the determinism check is weak even when evaluated.** Bodies for the
   two identical requests are never byte-identical (`id`, `timings`, `cached_tokens` all
   differ — see A/B diffs), so the check compares `choices[0].text` only; with one greedy
   token the text collides trivially (`"."` in all four runs, including the sampled
   temperature-0.5 run). The skip at temperature != 0 is therefore load-bearing: without it
   the check would pass for the wrong reason. Nothing to change in the default path
   (temperature 0, n_predict 8), but a receipt at this edge must not be read as evidence
   of sampling determinism.
4. **`timings.predicted_ms = 0.001` with `predicted_n = 1`** at these args; the timings
   check only demands a numeric value and count equality, so it passes. Not a defect at the
   pinned small fixture, but the check cannot detect a degenerate `predicted_ms`
   (e.g. `0.0`); if timing plausibility ever matters, that check needs a floor.
5. Everything else at the edge args behaved: envelope, alias echo, fingerprint shape,
   usage sum, `finish_reason=length`, graded 400 error, listener ownership, clean SIGTERM,
   port closure, hold release, and per-run port freedom. Run A reproduced identically on a
   second sample (A2), so `REQUEST_OK` at these edge args is stable, not a race.

## Bounds / hygiene

- No git/jj mutation anywhere; read-only `git rev-parse`/`status` only. No fleet repo,
  sibling lane, lane index, `shokuknow`, or another seat's files touched.
- Live runs only via `tools/kama-completion-live.py` on unregistered loopback ports; I
  spawned and reaped only my own children. No `SIGKILL` of foreign processes.
- Tool installs/upgrades this seat: **none** (no pacman, no uv/npx installs needed; the
  lane fixtures were already present and digest-matched).
- Scratch `/fast/scratch/hyaku/kama-r62/w/E07CompletionEdge/` removed after copying
  receipts into `out/E07CompletionEdge/`.

## Tally

`A-edge-t05-np1 REQUEST_OK rc=0 17/17 recorded 0 failed not-evaluated=completion_deterministic("skipped: temperature != 0") hold=true outside=200 | A2-edge-repeat REQUEST_OK rc=0 same not-evaluated set | B-base-t00-np1 REQUEST_OK rc=0 17/17 evaluated 0 failed | C-edge-nohold REQUEST_OK rc=0 16 checks completion_deterministic not-evaluated + hold_released absent → 4/4 edge verdicts REQUEST_OK, exactly 1 check not-evaluated at temperature != 0 (3/3 runs), counter-grade cross-check: stored null vs recomputed True, inconsistent=[] alltrue=True (over-credit shape).`
