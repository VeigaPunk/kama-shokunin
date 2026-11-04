# SEN01Bounds — bounds and safety audit, kama round 74 w1

Seat: SEN01Bounds (sentinel, leaf). Scope audited: `tools/round74-*.py` (if present),
`.ufo/waves/round-74/`, `plans/round-74-claims.md`, fixture bytes under
`/fast/scratch/hyaku/kama-r74/`, fleet root, sibling lanes, `/tmp`, pacman lock.

Two passes: pass 1 at seat run time (~2026-11-04 00:47), pass 2 at seat end (~2026-11-04 01:00).
Commands and verbatim outputs are recorded in `pass1-evidence.txt`,
`pass1-scope-evidence.txt`, `pass2-evidence.txt` in the seat scratch dir (copies
alongside this file where noted). A `/tmp` path is never citable evidence; all
evidence below was captured from commands run against the live filesystem.

## 1. Credential / secret sweep

Targets:
- `plans/round-74-claims.md` (frozen plan bytes)
- `.ufo/waves/round-74/` (recursive, all files)
- `/fast/scratch/hyaku/kama-r74/` (recursive, all fixture bytes)
- `tools/round74-*.py` if present (none existed at pass 1; presence checked again at pass 2)

Patterns (10 groups, `grep -rEnI`):
api-key/secret/access-key assignments, `sk-…` OpenAI keys, `gh[pousr]_…` GitHub
tokens, `xox…` Slack tokens, `AKIA…` AWS keys, `Bearer …` tokens,
`connect.sid|sessionid|set-cookie`, `op://…` 1Password refs, PEM private-key
headers, JWT-shaped triples.

Result (both passes): **0 hits across all 10 patterns**.

Keyword note: literal strings `op://`, `cookie`, `session` each appear twice, both
in `.ufo/waves/round-74/w1-spec.json:13` and `w1-dispatch.json:232` — they quote
this seat's own audit contract sentence ("no API keys, tokens, cookies, `op://`
refs, session material"). They are contract prose, not secret material.
No other occurrence anywhere in the round surface.

## 2. Host-write sweep

### Fleet root (`git -C /home/vgpnk/Projects/shokunin status --porcelain`)

Pass 1 and pass 2 output (unchanged between passes):

```
 M .scratch/goal-20261103-hyaku-run15.md
 M .scratch/run15-state.json
?? .scratch/run13-state.json
?? .scratch/run15-kernel.py
?? after
```

Distinguishing orchestrator-owned state: all five paths are under the fleet-root
`.scratch/` operator state dir (plus `after`, 24 bytes, content
`== SCORECARD diff base-`, mtime 2026-11-03 20:05 — pre-wave). No seat-writable
fleet-root tracked file (LOG.md, SCORECARD.md, MANIFEST.json) is modified;
`git diff --name-only` at the fleet root lists only the two `.scratch/` files.
MANIFEST.json mtime 2026-11-04 00:19 (orchestrator write; the seat never touched it).

### /tmp usage over 50 MB

`du -sh /tmp/* | sort -h | tail -10` (pass 1, re-run at pass 2, same result):

```
47M  /tmp/kit-cache-qa-smoke
51M  /tmp/lc-v3final
58M  /tmp/p61-gate-saffron
66M  /tmp/devin-overflows-1000
78M  /tmp/rcbase
90M  /tmp/lh-mine
95M  /tmp/p61-gate-starfall
100M /tmp/p61-gate-bogberry
530M /tmp/lh_sample.jsonl
28G  /tmp/polish61-m47tumble-cache
```

All entries have mtimes of 2026-11-02/03 — pre-existing, none created by this
wave (wave dispatched ~2026-11-04 00:43). `/tmp` files written on 2026-11-04 by
the running waves are all < 1 MB (orchestrator dispatch log `r74-run.out` 39 KB,
selftest temp files 18–46 bytes each, `census-before.txt` 708 B, `alma.log` 1.2 MB).
None exceed the 50 MB HYAKU threshold; none are citable-evidence paths (the
contract's own rule). No kama-r74 seat evidence was observed being written to
/tmp. Cross-lane note: `w5-mado-m52-selftest.*`, `kake-scout-*`, `receipt-exists-selftest-*`
tmp files belong to kake/mado waves, not kama r74.

### Hardcoded /tmp in new committed-intended tools

`grep -rn /tmp` over `.ufo/waves/round-74/controls/*.py`,
`w1-spec.json`, and `plans/round-74-claims.md`: only hit is the contract text
inside `w1-spec.json`'s context string (quoting the HYAKU rule itself). No
committed-intended tool hardcodes `/tmp`. (No `tools/round74-*.py` existed at
either pass; a post-wave re-check is the L1's integration-time duty — command
documented in §6.)

## 3. Fixture-git discipline

Lane repo log authors (pass 1, verbatim):

```
$ git -C kama-shokunin log --format='%an <%ae>' -15
kama-shokunin <kama@shokunin.local>  (x13)
protocol-shokunin <protocol@shokunin.local> (x2)
```

No `fixture` identity (nor `fixture@invalid`) appears in the lane repo's git log
at either pass. Fixture identity appears only inside fixture repos under
`/fast/scratch/hyaku/kama-r74/controls-work/fixtures/*/​.git` (c2_wrapped,
c2_offset, c2_mixed_honest, c2_clean_realizable, c3_edited, c3_clean — all
commits `fixture <fixture@invalid>`, created by the committed
`controls/build-survivors.py`, which the plan freezes). Executor seats rebuilt
fixtures only inside their own scratch subdirs (EX01CanonV2/fixtures verified:
294 files, all under the seat's dir).

`find kama-shokunin -name .git -maxdepth 4` finds only the lane root `.git` —
no fixture repo leaked into the lane repo tree. No stray `.git` dirs anywhere
else under the lane.

## 4. Scope: seat-editable files outside the lane repo

`git -C <sibling> status --porcelain | head -3` for all 21 lane repos at pass 1.
Lanes with changes: kaidoku (untracked tools/round-70/), kasegi (3 untracked
w*.ready.dispatched), kengaku (SKILL.md M, corpus/SOURCES.md M, round-74 dirs —
kengaku's own r74 wave), kumitate (16 changes — its own r74 work), mado, tabi,
tameshi (round-76 dir), tsukuroi (7 changes). All are those lanes' own
orchestrator dispatches; **zero seat-attributable writes outside
`kama-shokunin`** — kama seats can only write kama-shokunin + their scratch dir,
and no path outside those roots was observed being written by this wave.

Within the lane (pass 2, verbatim):

```
 M PROVINCE.md
?? .ufo/waves/round-74/assimilation/
?? .ufo/waves/round-74/measured/pinwatch/
?? .ufo/waves/round-74/w1.ready
?? .ufo/waves/round-74/w1.ready.dispatched
?? .ufo/waves/round-74/w1/SCR01Sources/
?? .ufo/waves/round-74/w1/SEN01Bounds/
?? .ufo/waves/round-74/w1/SCO01Recon/
```

- `PROVINCE.md` working-tree edit: plan-sanctioned C3 token addition
  ("recorded at 868dd701bff531be6a36da742d3418f98818e5eb (round-74 freeze base; …)"
  appended to the Round-73 host-identity block) — exactly the edit the plan's
  C3 section (claims file lines 158–160) prescribes for the round-74 record.
  Diff verified; no other PROVINCE.md bytes changed.
- Frozen tools: `git status --porcelain -- tools/` is **clean at both passes** —
  `round42-selfdesc-reconcile.py`, `round72-*.py`, `round73-*.py`,
  `pre-report-gate.py` all byte-unmodified. Their recent mtimes (1–2 h old)
  predate wave dispatch (00:43) and reflect the L1's pre-freeze commits.
- Freeze integrity re-verified at pass 2: sha256 of `plans/round-74-claims.md`
  and all six `controls/freeze.txt` receipts match the frozen pins (verbatim
  digests in pass-2 evidence).
- `~/.omp/agent/config.yml`: never read, never written (contract route table).
  `~/.local/bin`: no modifications in the last 24 h. Lane `.ufo/state/` and
  `.ufo/watchdog.log`: do not exist (not created).

## 5. Pacman guard

`ls /var/lib/pacman/db.lck` → `No such file or directory` at both passes — no
pacman transaction in progress. This seat installed nothing (pure read-only
audit; only tools used: system python3, grep, git, sha256sum, du — all
pre-installed). No seat needed pacman.

## 6. Findings

**No violations found.** Severity: none. The round-74 surface at both audit
passes is clean on all five assigned checks.

Residual notes (not violations, recorded for the L1):

1. `l1-notes/record-skeleton.md` appeared at pass 2 inside the shared scratch
   root `/fast/scratch/hyaku/kama-r74/l1-notes/` (explicitly L1-owned: "L1
   working notes, not committed"). Seat scratch-dirs are per-seat; the L1's
   notes dir is integrator state, acceptable, disclosed here.
2. Pass-2 secret sweep surfaced two informational matches inside
   `RVW01Plan/base/` — a plain (non-git) read-only copy of a historical lane
   revision kept in the reviewer's own scratch dir:
   - `base/.ufo/waves/round-58/w1-results.json:394` — a round-58 verdict
     sentence ("clean on credentials/op:///private URLs") quoting pattern
     names; not a live `op://` reference.
   - `base/.ufo/waves/round-50/w1/out/X17Cleanup/hygiene.md:303,305` — a
     list of example secret shapes to grep for
     (`` `ghp_…`, `ANTHROPIC_API_KEY=…`, `-----BEGIN RSA PRIVATE KEY-----` ``);
     documentation of patterns, not key material.
   Both verified benign by reading the surrounding lines.
3. At pass 2 exactly one new committed-intended tool had landed:
   `tools/round74-seat-count-check.py` (SCR02Lesson's lesson-mined
   instrument — the plan Frontier step names this exact path for mistake 1).
   Swept with the same patterns: 0 secret hits; `grep /tmp` on it: clean; it
   uses TMPDIR-aware temporaries. The three claim modules
   (`round74-selfdesc-canon.py`, `round74-receipt-claim-binding.py`,
   `round74-province-host-drift.py`) had not yet landed at pass 2 — executors
   were still building in scratch. Post-integration re-sweep command for the
   L1 (same one used here):
   `grep -rEnI -e '<patterns from §1>' tools/round74-*.py .ufo/waves/round-74/w1/`
4. Fleet-root `after` file (untracked, 24 B, 2026-11-03 20:05) predates the
   wave and is orchestrator output; left untouched per host-guard rule.

## Pass log

| Pass | Time (local) | Surface state |
|---|---|---|
| 1 | 2026-11-04 00:46–00:50 | wave dispatched ~00:43; no round74 tools; fixtures pre-built in controls-work; SCR01Sources source capture landed |
| 2 | 2026-11-04 00:52–00:56 | `tools/round74-seat-count-check.py` landed; seat out dirs SCR01Sources/SEN01Bounds/SCO01Recon present; PROVINCE.md plan-sanctioned edit unchanged; freeze digests still match; all sweeps re-run |

Full verbatim command output: `pass1-evidence.txt`,
`pass1-scope-evidence.txt`, `pass2-evidence.txt` (copied into this out dir
from the seat scratch dir before its deletion).
