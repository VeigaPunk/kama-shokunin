# ARCHIVAL — ROUND-10 SEAT PROTOCOL IS HISTORICAL, UNDELIVERED AND NONEXECUTED (round-12 notice, 2026-10-20)

**THIS BANNER OVERRIDES THE TITLE BELOW AND EVERY DIRECTIVE IN THE ORIGINAL TEXT.** The phrase `L1-issued, binding on all 64 seats` in the next heading is a dated 2026-10-18 self-description. It binds no seat, agent, round, or host. Nothing below this banner is a current instruction, a current authorization, or a reusable procedure.

**Status.** Historical planning artifact, retained only for provenance. Its own `plan.json` records `"dispatch_utc": null` and loop 1 as blocked-with-data, and `.ufo/round-10/tps-probes/` is empty; the file entered git only in round 11, in `3285cdf7a50481694a36c4425cf32c915ab5e5f0`. The later round-11 verifier defect D5 asked for this in-file label (`corpus/lessons/round-11-verifier-spotcheck.md`). As a live instruction set it is nonexecuted: nothing here is running or pending; dated receipt files that may sit in the same directory are frozen observations, not evidence that this protocol is current.

**Not current authorization.** It grants no permission and imposes no obligation to write, edit, audit, probe, dispatch, capture telemetry, commit, renumber, or "carry verbatim" anything. Only the active round's canonical assignment and lane contract authorize current work; if this text conflicts with them, they win.

**No old routing, host, or environment instruction here is reusable.** In particular:

- *Original L1* — the header `(L1-issued, binding on all 64 seats)` is history; the 64-seat scheme and its classes are not current.
- *Original L13* (hard rule 1) — the AUDIT write grant to an assigned file plus `.ufo/round-10/audit/` is expired; no scope is assigned now.
- *Original L16* (hard rule 4) — "a failed task ... is a success as a measurement seat" is not a success definition today; a blocked or erroring run stays blocked or failed.
- *Original L17* (hard rule 5) — the read-only inspection allowance for `~/.config`, `~/.omp`, systemd units, or any sibling repo is not a live allowance; those surfaces remain host/config-owned and out of this lane's scope, and its short "never write" list is not a complete boundary — the active lane contract alone defines the boundary.
- *Original L22–L23* (AUDIT steps 1–2) — expanding `$UFO_SRC` and falling back to `~/Projects/ufo-fsd-alpha` or `~/Projects/origin-work/ufo-fsd-alpha` authorizes no environment read and no path probe; no fallback root is endorsed.
- *Original L23* — loopback-URL `runtime-surface` classification authorizes no endpoint call, curl, probe, or config-body read.
- *Original L23* — `git cat-file -e <hash>` bookkeeping is historical; round-10 hashes carry no current action.
- *Original L27–L29* (AUDIT step 5) — the correction template is never to be re-issued: it hard-codes `2026-10-18 (round 10)` and would back-date a new claim.
- *Original L35* (EVIDENCE) — "run exactly the commands in your scope" defines no command set today, and full stdout/stderr capture into committed JSON could persist credential-adjacent output; no such execution or capture is authorized.
- *Original L35, L39–L41* (EVIDENCE and TPS-PROBE) — capture targets under `.ufo/round-10/gates/`, `.ufo/round-10/audit/` and `.ufo/round-10/tps-probes/` are not live; the round-10 tree already holds 14 tracked paths, so replay would write into retained history.
- *Original L43–L54* — the `SEAT-TELEMETRY` block is an expired reporting format, not a current requirement or acceptance format.
- *`plan.json:7,11`* — the pinned route/model `opencode-go/deepseek-v4.1-flash-free` and `carried verbatim modulo round number` authorize no routing reuse, copy-forward, renumbering, or re-dating of this protocol into any later round.

**Scope of this notice.** It covers this file only. The same template is tracked at `.ufo/round-6/SEAT-PROTOCOL.md` through `.ufo/round-9/SEAT-PROTOCOL.md`, each opening with the same binding header; each needs its own archival label before any reuse.

**Original bytes preserved.** Everything from the `---` rule below is the unaltered round-10 file: 56 lines, 4413 bytes, SHA-256 `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a` (the tracked blob `69659feb5f77a80a7c6020fbe95ba75c3d38ff72` at `3285cdf`). Verify with `tail -c 4413 .ufo/round-10/SEAT-PROTOCOL.md | sha256sum`; append only, never rewrite those bytes.

**No claim.** This banner asserts no host, service, endpoint, capability, score, or freshness state. It is a scope label required by D5, not evidence about any surface the original text cites.

---

# Round 10 — seat protocol (L1-issued, binding on all 64 seats)

Repo root for every seat: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Date: 2026-10-18.

## Classes

- **AUDIT** — one seat per corpus/registry/SKILL/PROVINCE surface (20 seats).
- **EVIDENCE** — run real commands, capture complete streams + exits to `.ufo/round-10/gates/<slug>.json` (12 seats).
- **TPS-PROBE** — fixed-shape writing task, self-timed, output to `.ufo/round-10/tps-probes/<slug>.md` (32 seats).

## Hard rules (every seat)

1. Write ONLY inside your declared scope. AUDIT seats may edit exactly their assigned file(s) plus `.ufo/round-10/audit/`; never another seat's file.
2. Existing content is append-only for AUDIT seats: land corrections as appended lines, never delete or modify existing lines. Dated history is retained, not rewritten.
3. No fabrication. Every claim carries a command you actually ran and its observed output. If you cannot run something, say so.
4. If provider/API/rate-limit errors hit you, quote the error verbatim in the telemetry block and complete whatever you still can. A failed task with verbatim errors and honest telemetry is a success as a measurement seat.
5. kama write boundary: never write `~/.config`, `~/.omp`, systemd units, or any sibling repo. Read-only inspection of those is allowed where your scope says so.
6. Do not commit. Do not run `git commit`. The L1 owns the round commit.

## AUDIT protocol

1. `t0=$(date +%s%N)` then audit your file: find every cited path/host surface (absolute paths, `~/...`, `$HOME/...`, `$UFO_SRC/...`, `~/Projects/...`, URLs on loopback ports, commit hashes).
2. Test each path: `test -e` on the expanded path (expand `$UFO_SRC` via `echo "$UFO_SRC"` first; if empty, try `~/Projects/ufo-fsd-alpha` then `~/Projects/origin-work/ufo-fsd-alpha`). Loopback URLs: class as `runtime-surface` (do NOT curl them; endpoint state is the registry's dated sample, not your task). Commit hashes: `git cat-file -e <hash>`.
3. Classify each citation: `active` (in current instructions / current-state prose), `historical` (inside dated examples/lessons/errata), `fossil` (backup files that must never be restored — verify only, never edit), `runtime-surface` (ports/URLs).
4. Write `.ufo/round-10/audit/<slug>.before.json` with schema:
   `{"seat_id","file","state":"before","citations":[{"line":N,"cited":"...","resolves":"yes|no|runtime","class":"active|historical|fossil|runtime-surface","evidence":"<command> => <observed output>"}],"active_unresolved":N}` where `active_unresolved` counts `active` citations whose path does not resolve.
5. For each `active` unresolved citation, append a correction line to your file in exactly this form:
   `*[correction 2026-10-18 (round 10): \`<old pointer>\` does not resolve (<command> => <result>); current anchor: \`<new pointer or "no live successor — report as dead surface">\`]*`
   If no live successor exists, the correction says so — do NOT invent one. If your file has zero active-unresolved citations, append nothing to the corpus file.
6. Re-audit and write `.ufo/round-10/audit/<slug>.after.json` (same schema, `state:"after"`, post-correction classifications). `active_unresolved` should now be 0 or every remaining one named with a reason in its `evidence`.
7. `t1=$(date +%s%N)`.

## EVIDENCE protocol

Run exactly the commands in your scope; capture full stdout, stderr, exit code, and the exact command line into `.ufo/round-10/gates/<slug>.json` as `{"seat_id","slug","commands":[{"cmd","stdout","stderr","exit"}],"notes"}`.

## TPS-PROBE protocol

1. `t0=$(date +%s%N)`.
2. Write a structured explanation of your assigned topic, **300–350 words**, to `.ufo/round-10/tps-probes/<slug>.md` with a `# <topic>` heading. Ground it in the actual repo files — read `SKILL.md` and the cited corpus first; this text is measurement raw data, but it must still be truthful (cite real file paths).
3. `t1=$(date +%s%N)`; `wc -c` your file.

## Telemetry block — end of EVERY seat result, exact format

```
===SEAT-TELEMETRY===
seat_id: <slug>
t_start_ns: <t0>
t_end_ns: <t1>
deliverable: <path(s) you wrote, comma-separated>
deliverable_bytes: <sum of wc -c over deliverable paths, 0 if none>
errors_verbatim: <verbatim provider/rate-limit/transport errors, or "none">
===END-SEAT-TELEMETRY===
```

After the block, one line: `RESULT: <one sentence — what was done or what blocked you>`.
