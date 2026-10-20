# SafetyArchive — round 12, D5 replay-safety review (sentinel, author advisor)

Scope: `.ufo/round-10/SEAT-PROTOCOL.md` and routed defect D5
(`corpus/lessons/round-11-verifier-spotcheck.md:226-230`) only. I classified the old
directives. I did not follow or execute any of them. No edits outside this file, no host
inspection, no endpoint calls, no installs. This is an author advisor's review, not
independent closure.

## Observed state (read-only commands run 2026-10-20)

- `sha256sum .ufo/round-10/SEAT-PROTOCOL.md` gives
  `e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a`. This matches the
  round-11 record (`.ufo/waves/round-11/advice/AttackAdmission.md:75`). **No D5 disclaimer
  has landed yet:** the file is still 56 lines and opens with
  `binding on all 64 seats`.
- `git log -- .ufo/round-10/SEAT-PROTOCOL.md` shows `3285cdf round-11: …`. The file is now
  tracked, and `git status` is clean for `.ufo/round-10`. Because it is committed, it can be
  found and reused by any future reader.
- Companion `plan.json`: sha256 `3fa5df3c…809197c` (unchanged). It has `dispatch_utc: null`,
  model `opencode-go/deepseek-v4.1-flash-free`, and at line 11
  `"seat_protocol": ".ufo/round-10/SEAT-PROTOCOL.md (carried verbatim modulo round number)"`.
- 14 tracked files exist under `.ufo/round-10` (audit 2, gates 7, fragments 3, plus the
  pair). Round-6 through round-9 copies of the same template exist (`.ufo/round-{6..9}/SEAT-PROTOCOL.md`).
  The plans for rounds 7 to 9 each say `carried verbatim`.
- In my shell, `echo "$UFO_SRC"` printed an empty value. That is exactly the condition that
  sends line 23 to its home-directory fallbacks.

## Classification of stale directives

| Sev | Line | Directive | Class | Replay exploit path / impact |
|---|---|---|---|---|
| HIGH | 1 | `L1-issued, binding on all 64 seats` | false live authority | A reader who sees only the header (a `head` read, a truncated read, or a grep hit) treats a never-dispatched plan as the current contract. This is a fabricated-readiness/provenance defect. |
| HIGH | plan.json:11 (+r7–r9 plans) | `carried verbatim modulo round number` | template-replay mechanism | The documented lineage is copy-forward with the round number renumbered. Renumbering `round-10` to `round-13` makes every grant below live again under a new date. |
| HIGH | 17 | `Read-only inspection of [~/.config, ~/.omp, systemd units, sibling repo] is allowed where your scope says so` | host-inspection grant | The round-12 contract forbids this, and D5 says no host-inspection instruction is authorized. The corpus it audits cites `~/.omp/agent/config.yml` (auth-broker) and systemd units (`frozen/before/corpus/knowledge/consumer-registry.md:102-103`), so a replayed audit would read credential-adjacent config. |
| HIGH | 17 | `never write ~/.config, ~/.omp, systemd units, sibling repo` | incomplete deny-list (negative permission) | Anything not listed can be read as permitted: verifier files, MANIFEST, fleet repo, `tools/`, `registry/`, env, services, `sudo`. The current contract forbids all of these. |
| HIGH | 25, 30, 35, 40 | fixed output paths `.ufo/round-10/{audit,gates,tps-probes}/<slug>…` | evidence clobber | A replay overwrites the 14 tracked round-10 evidence files. That destroys immutable prior-round evidence without any append. |
| MED | 22–23 | enumerate `~/...`, `$HOME/...`, `$UFO_SRC/...`; expand `$UFO_SRC`, else fall back to `~/Projects/ufo-fsd-alpha`, then `~/Projects/origin-work/ufo-fsd-alpha` | env-dependent path resolution, out-of-lane host probing | Results depend on ambient env and sibling-repo presence. An attacker or a stale `UFO_SRC` controls which tree counts as "resolves". Step 5 then writes those results into the corpus. |
| MED | 13, 27–29 | AUDIT seats edit assigned corpus files; append `*[correction 2026-10-18 (round 10): …]*` | durable corpus write plus back-dated provenance | A replay appends corrections stamped with the wrong round and date to append-only corpus files. That is fabricated provenance, and append-only rules mean it cannot be removed. |
| MED | 35, 8 | `Run exactly the commands in your scope`; capture full stdout/stderr | unscoped execution, secret capture | The commands are not in the file, so any replaying planner supplies them. Full-stream capture into committed JSON can persist env or credential output. |
| LOW | 16 | failed task with errors `is a success as a measurement seat` | success redefinition | Out of context, this lets a blocked run read as success. That is a readiness-inflation risk. |
| LOW | plan.json:7 | model `opencode-go/deepseek-v4.1-flash-free` | stale routing | The route was blocked in rounds 6–9 (plan.json:12). Reusing it is routing outside the current dispatch. |
| SAFE | 14, 15, 18, 23 (`do NOT curl`) | append-only, no fabrication, no commit, no loopback curl | protective | Still consistent with current rules. These are not a source of permission. |

## Required explicit wording (owner: `KamaR12.ArchiveDisclaimer`; peer already messaged)

The contract allows appending only. Adding a prefix would change the immutable original
prefix, so the disclaimer has to work on its own when appended. It should quote line 1 and
void it by line number. Suggested block:

```
---
## ROUND-12 ARCHIVAL DISCLAIMER (appended 2026-10-20; D5, corpus/lessons/round-11-verifier-spotcheck.md:226-230)

HISTORICAL, NEVER EXECUTED. This file is a round-10 pre-dispatch plan authored 2026-10-18 and
never dispatched (plan.json `dispatch_utc: null`). The actual round 10 ran a different
12-seat campaign. Line 1's "L1-issued, binding on all 64 seats" is VOID. This file binds no
seat, in any round.

It grants nothing. Its preservation authorizes none of: line 13 corpus edit grants; line 17
read-only inspection of ~/.config, ~/.omp, systemd units or sibling repos; line 17's write
list as a complete boundary; line 23 `$UFO_SRC` expansion or the ~/Projects/ufo-fsd-alpha /
~/Projects/origin-work/ufo-fsd-alpha fallbacks; line 27-29 dated correction lines; line 35
command execution or stream capture; writes to any .ufo/round-10/ path; plan.json model or
routing (`opencode-go/deepseek-v4.1-flash-free`).

DO NOT COPY FORWARD. plan.json:11 "carried verbatim modulo round number" does not apply:
renumbering, re-dating or re-issuing this text does not revive it. Current authority is only
the current round's canonical assignment and lane contract. If this file conflicts with
them, they win.

Bytes above this block are preserved unchanged: original sha256
e9fbaa02b4329ec415ac73eb0a6a5eaf4c91ae17f2889cc96232fb51f5d49c0a.
```

Residual risk: a disclaimer appended at line 57+ is invisible to a reader who reads only the
top of the file. Smallest mitigations within current write bounds:

1. Make the disclaimer heading greppable (`ARCHIVAL DISCLAIMER`, `NEVER EXECUTED`).
2. Have the round-12 report and LOG cite `SEAT-PROTOCOL.md` only together with "historical,
   never executed, void".
3. `plan.json` cannot take a comment without breaking its JSON and immutability. Name it in
   the disclaimer by path and model, as above, rather than editing it.
4. Rounds 6–9 copies carry the same grants. They are outside D5. Route them to L1 as an
   optional follow-up rather than editing them silently.

## Checks for L1 (not run here)

- `sha256sum` over the `.ufo/round-10/SEAT-PROTOCOL.md` prefix: `head -n 56 … | sha256sum`
  must equal `e9fbaa02…5d49c0a` (prefix unchanged, append-only).
- `git diff -- .ufo/round-10/SEAT-PROTOCOL.md` shows additions only. `plan.json` sha
  `3fa5df3c…809197c` is unchanged.
- `grep -n 'ARCHIVAL DISCLAIMER\|NEVER EXECUTED\|DO NOT COPY FORWARD' .ufo/round-10/SEAT-PROTOCOL.md`
  hits once each. The block names lines 1, 13, 17, 23, 27–29 and 35, plus plan.json:7 and plan.json:11.
- `git status --short .ufo/round-10` shows only the one modified file. No audit/gates files changed.

Tools installed or updated: none.
