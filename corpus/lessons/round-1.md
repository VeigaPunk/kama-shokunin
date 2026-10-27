# round 1 — lessons and carry-forward rules

Round 1 of kama-shokunin (operability axis). Every rule below is grounded in a command run
on 2026-09-28; the full command ledger is in `corpus/knowledge/listener-census.md` (C1–C19)
and `corpus/knowledge/consumer-registry.md`.

## Carry-forward rules

1. **Identity, not liveness.** `curl -f` / `nc -z` / a TCP accept prove nothing:
   `127.0.0.1:8080` accepts connections and answers `200` on `/metrics`
   (`application/openmetrics-text`, 27461 B) while `GET /v1/models` and
   `POST /v1/chat/completions` return Jetty HTML 404. Only `GET /v1/models` with a
   recognizable model array — plus `Server: llama.cpp` as corroboration — establishes
   identity. Corollary: never gate on a status code.
2. **A request that succeeds is not a model-identity check.** `POST /v1/chat/completions`
   with `{"model":"DEFINITELY-NOT-THE-MODEL"}` returns **200** and the response `model`
   field echoes the loaded model's path; llama.cpp ignores the requested name. Identity must
   come from `/v1/models`, never from a round-trip.
3. **Normalize the id before comparing it.** llama.cpp reports the served id as an absolute
   GGUF path (`/scratch/models/qwen3-coder-30b/….gguf`) while every consumer declares the
   bare id (`Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS`). Compare basename-minus-one-`.gguf`,
   case-sensitive; empty after normalization ⇒ `MODEL_MISMATCH` (`unresolvable-id`), never OK.
   A naive comparison reports a false mismatch on a **healthy** endpoint — it bites the
   correct-pin family (`local-helper.mjs:9`) exactly as hard as the stale one.
4. **A consumer pin can be stale while the config is freshly edited.** `opencode.json` mtime
   is `2026-09-28 16:46`; line 158 still says `http://localhost:8080/v1`. Edit recency is not
   freshness; only re-derivation is.
5. **Read the declared value out of the consumer file, never out of your own registry.**
   The registry row carries a *claim*; the probe re-derives the baseURL from the file
   (`json:` pointer or `grep:`) and reports `file_match=yes|inherited|no`.
6. **Check the whole pin family, not the config tree.** The fourth and fifth stale pins were
   a shell script (`~/.local/bin/the-janitor:19`) and a compiled binary default
   (`~/.local/bin/omp`: `baseUrl = Bun.env.LLAMA_CPP_BASE_URL || "http://127.0.0.1:8080"`).
   A census rooted only at `~/.config/opencode/` finds neither.
7. **Look for the fix before assuming the bug is universal.** The box simultaneously held
   the bug (`8080` family) and its fix (`~/Projects/ufo-fsd-alpha/config/
   the-tick.machine.json:16`, `scripts/local-helper.mjs:8` → `34113`; re-measured
   2026-10-14 after the tree relocated from `origin-work/` — historical path).
   Report the asymmetry; do not silently "fix" the consumer.

## Method traps (each produced a wrong conclusion this round)

| Trap | Symptom | Correct form |
|---|---|---|
| `ss -tnp` without `-l`/`-a` | `grep -c LISTEN` → `0` when 23 exist; a peer concluded "no consumer of 34113" | `ss -ltnp` (or `-tanp`) |
| lowercase `/home/vgpnk/projects` | misses the entire `ufo-fsd-alpha` family; a peer called the pins "unverifiable" | `/home/vgpnk/Projects` — **different directory** (inodes `101125103` vs `27238`, case-sensitive fs) |
| `git remote -v \| head -2` | invents a remote difference between two checkouts | full `git remote -v`; both trees share `origin` = `origin.cursor.com/jo-o-veiga/ufo-fsd-alpha.git`, one adds `github` |
| a transient `ss` snapshot | a peer read 2 ESTAB sockets to 8080 as a standing consumer | re-sample; report transient vs durable explicitly (durable signal here: TIME-WAIT asymmetry, 62/26 vs 12/6) |
| regex redaction by substring | two directions of error: a route containing "token" got redacted, while a real secret keyed elsewhere could slip | classify by the **key name** on the left of `:`, not by a substring anywhere in the line |

## Redaction incident (self-reported)

A whole-file read of `~/.omp/agent/config.yml` surfaced its credential line (`token`,
line 169; 43 chars). **No artifact contains that value** — a key-side scan over every
corpus/report file returned 0 hits. The first L1 redaction pass mis-fired: it matched the
*value* `alibaba-token-plan/...` because the string contains "token", and rewrote four
legitimate model routes across two artifacts; all four were restored and the rule above
recorded. This is the same defect class kagi filed independently in round 10 (a redactor
whose match is too loose in one direction and too strict in the other).

## Peer ledger — contradictions resolved by primary evidence

- "No consumer pins 34113" → **falsified** (ufo-fsd-alpha, two checkouts, `MODEL_OK`).
- "Live ESTAB socket to 8080" → **not reproducible**; transient, superseded by TIME-WAIT
  asymmetry (scout samples) — L1's own two samples read 0, so the asymmetry is intermittent.
- "Zero consumers → the model has no declared consumer" → scoped negative, not box-wide.
- "The two ufo-fsd checkouts share one remote" vs "different remotes" → both partly wrong;
  full `git remote -v` shows a shared `origin.cursor.com` plus a `github` remote on
  `origin-work` only (HEADs `5725fa7d3` / `0522e67a`).
- L1's own F11 (`m_flash` route) → **stale**; live line 24 is
  `m_flash: charm-hyper/deepseek-v4.1-flash:max`. Corrected in
  `corpus/lessons/round-1-citations.md` and never repeated.
- *2026-10-14 errata:* the second checkout (`~/Projects/webzites`) is deleted and
  the surviving tree's remote names changed (`cursor`/`origin` swapped);
  `consumer-registry.md` §Errata carries the current map.

## Round-2 seeds

- Periodic re-verification (the freshness move): a wrapper that runs `check`, stores a dated
  result and flags `MODEL_OK`→anything transitions.
- Attribute the 8080 traffic (TIME-WAIT asymmetry is durable; the source pid is not yet named).
- Measure a non-llama.cpp runtime so rule 6 is measured, not inferred.
- Declared-vs-served *context* drift (`~/.config/the-janitor/opencode.json` declares
  `limit.context: 32768`; the live server runs `--ctx-size 16384`) — a second class in
  province, not yet covered by the registry schema.

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `ea72c3eae4ec` (round-3: re-census — derived --ufo-src, registry cut to live rows, corpus errata):

`````text
   the bug (`8080` family) and its fix (`~/Projects/origin-work/ufo-fsd-alpha/config/
   the-tick.machine.json:16`, `scripts/local-helper.mjs:8` → `34113`), in two checkouts.
`````
