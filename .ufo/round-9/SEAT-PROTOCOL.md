# Round 9 — seat protocol (L1-issued, binding on all 64 seats)

Repo root for every seat: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Date: 2026-10-18.

## Classes

- **AUDIT** — one seat per corpus/registry/SKILL/PROVINCE surface (20 seats).
- **EVIDENCE** — run real commands, capture complete streams + exits to `.ufo/round-9/gates/<slug>.json` (12 seats).
- **TPS-PROBE** — fixed-shape writing task, self-timed, output to `.ufo/round-9/tps-probes/<slug>.md` (32 seats).

## Hard rules (every seat)

1. Write ONLY inside your declared scope. AUDIT seats may edit exactly their assigned file(s) plus `.ufo/round-9/audit/`; never another seat's file.
2. Existing content is append-only for AUDIT seats: land corrections as appended lines, never delete or modify existing lines. Dated history is retained, not rewritten.
3. No fabrication. Every claim carries a command you actually ran and its observed output. If you cannot run something, say so.
4. If provider/API/rate-limit errors hit you, quote the error verbatim in the telemetry block and complete whatever you still can. A failed task with verbatim errors and honest telemetry is a success as a measurement seat.
5. kama write boundary: never write `~/.config`, `~/.omp`, systemd units, or any sibling repo. Read-only inspection of those is allowed where your scope says so.
6. Do not commit. Do not run `git commit`. The L1 owns the round commit.

## AUDIT protocol

1. `t0=$(date +%s%N)` then audit your file: find every cited path/host surface (absolute paths, `~/...`, `$HOME/...`, `$UFO_SRC/...`, `~/Projects/...`, URLs on loopback ports, commit hashes).
2. Test each path: `test -e` on the expanded path (expand `$UFO_SRC` via `echo "$UFO_SRC"` first; if empty, try `~/Projects/ufo-fsd-alpha` then `~/Projects/origin-work/ufo-fsd-alpha`). Loopback URLs: class as `runtime-surface` (do NOT curl them; endpoint state is the registry's dated sample, not your task). Commit hashes: `git cat-file -e <hash>`.
3. Classify each citation: `active` (in current instructions / current-state prose), `historical` (inside dated examples/lessons/errata), `fossil` (backup files that must never be restored — verify only, never edit), `runtime-surface` (ports/URLs).
4. Write `.ufo/round-9/audit/<slug>.before.json` with schema:
   `{"seat_id","file","state":"before","citations":[{"line":N,"cited":"...","resolves":"yes|no|runtime","class":"active|historical|fossil|runtime-surface","evidence":"<command> => <observed output>"}],"active_unresolved":N}` where `active_unresolved` counts `active` citations whose path does not resolve.
5. For each `active` unresolved citation, append a correction line to your file in exactly this form:
   `*[correction 2026-10-18 (round 9): \`<old pointer>\` does not resolve (<command> => <result>); current anchor: \`<new pointer or "no live successor — report as dead surface">\`]*`
   If no live successor exists, the correction says so — do NOT invent one. If your file has zero active-unresolved citations, append nothing to the corpus file.
6. Re-audit and write `.ufo/round-9/audit/<slug>.after.json` (same schema, `state:"after"`, post-correction classifications). `active_unresolved` should now be 0 or every remaining one named with a reason in its `evidence`.
7. `t1=$(date +%s%N)`.

## EVIDENCE protocol

Run exactly the commands in your scope; capture full stdout, stderr, exit code, and the exact command line into `.ufo/round-9/gates/<slug>.json` as `{"seat_id","slug","commands":[{"cmd","stdout","stderr","exit"}],"notes"}`.

## TPS-PROBE protocol

1. `t0=$(date +%s%N)`.
2. Write a structured explanation of your assigned topic, **300–350 words**, to `.ufo/round-9/tps-probes/<slug>.md` with a `# <topic>` heading. Ground it in the actual repo files — read `SKILL.md` and the cited corpus first; this text is measurement raw data, but it must still be truthful (cite real file paths).
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
