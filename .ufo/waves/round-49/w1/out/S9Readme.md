# S9Readme — round 49 (kama): `## Frontier` disposition draft for `corpus/README.md`

**Verdict:** drafted the round-49 `## Frontier disposition — round 49` section (11.6 KB,
build-time figures, ready to append at the end of `corpus/README.md`); independently
re-ran the frozen C2 counter at the build commit (`fixture=1 lane=1 scenarios=8/8
met=True`, exit 0, 3.9 s); did **not** re-run C1 (its measured receipt and two peer
re-runs already carry it) — so C1's figures are cited, not observed by me; identified the
seven lines v4 newly grades. No lane file was edited, no counter/preregistration/control
was touched. Two findings go to integration: the round-48 v3 counter now exits 1 at this
build by construction (supersession, not regression), and the C1 witness still does not
join the observed pid to the rerun receipt, which is the load-bearing limit the draft
states.

## 1. Deliverable

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Readme/frontier.md`
  — one section, heading `## Frontier disposition — round 49`, in the round-48 voice.
  It states: the build/base/frozen-counter commits; what the witness proves (frozen
  binary executing as the listener of the announced port, frozen model at `-m`, a fresh
  counter nonce through `/tokenize`+`/detokenize` decoded against the counter's own GGUF
  vocabulary, then gone); what the bounded archive verification refuses; v4's origin and
  binding with the lane effect (ungraded 72 → 65, 89 → 82, event stays restored) and the
  identity of the seven newly graded lines; and what stays frontier (pid/capture join,
  archive origin at witness time, loaded-model binding, signed/provenance evidence,
  content-aware eligibility, binding's lexical edges, sub-20 threshold, prerelease cliff,
  b11906 population at b11909+, K05, registered consumers).
- No edit to `corpus/README.md`: the section is a draft for integration (append-only, so
  it is appended, never inserted).

## 2. Contract read before drafting

- `.ufo/waves/round-49/preregistration.json`: C1 operability 8→8, C2 calibration 7→7,
  predicates, `limits[0..3]`, counter digests `86b4a40d…f0d6c1` (C1) and `26c465a9…066945`
  (C2). Both counters at `74558c71` hash to those values
  (`git show 74558c71:tools/round49-*.py | sha256sum`), so the frozen bytes were the ones
  measured.
- Counter docstrings are the contract: `tools/round49-replay-witness-audit.py:1-88`,
  `tools/round49-append-audit-v4-check.py:1-88` (read at the build tree).
- Controls, all `met=False` (read, not run): `.ufo/waves/round-49/controls/base.c1.out`
  (`witness=0 cap=0 newrow=0 … met=False`, exit 1), `base.c2.out` (`fixture=0 lane=0
  scenarios=4/8`, exit 1, `unclassified 72 > 65` at the base),
  `junk-c1-fake-witness.c1.out` (exe digest `375532f8…` not the frozen server),
  `junk-c2-no-exempt.c2.out` (`regressed=1`, exit 1), `junk-c2-word-token.c2.out`
  (`launder` fails, exit 1).

## 3. What I ran (observed), and what I did not

### 3.1 Frozen C2 counter at the build — my run

```
S=/fast/scratch/hyaku/kama-r49/S9Readme
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane checkout 74558c71c38ceaeace15fd4cf8aa9d84977584b1
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-append-audit-v4-check.py \
  --repo $S/lane --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S/c2 --out $S/c2.out
```

Output (13 lines, exit 0, 3.9 s): `fixture=1 lane=1 scenarios=8/8 met=True`; all eight
scenarios `ok`; `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines
82`; `0718b6abdda6 SCORECARD.md ungraded 65 <= natively exempt 65`. Receipt copied to
`…/out/S9Readme/c2-S9Readme.out`; it equals `.ufo/waves/round-49/measured/c2-build.out`
line for line.

### 3.2 The seven lines v4 newly grades — my scratch analysis

A read-only script imported the build's `tools/append-only-audit.py` from my clone and
re-ran the `0718b6ab` event's deleted lines through the build's own `origins()`/grading
loop (no lane file touched). Result (`…/out/S9Readme/seven-v4-only-lines.txt`): exactly 7
lines, parent `21945c61` `SCORECARD.md` lines 121–127 — the six round-34 capability rows
(`sources-registry`, `ollama-offline-evidence-replay`, `live-llamacpp-lifecycle`,
`gguf-declared-identity-replay`, `context-capacity-receipt`, `instrument-agreement`, each
originating under `## Round 34 …`) and the round-41 `pin-watch` row (originating under
`## Round 41 …`), all deleted from the head `## Capabilities` table. That is the concrete
instance behind the draft's sentence.

### 3.3 C1 not re-run by me

I did not execute the C1 counter. Its evidence is the committed measured receipt
`.ufo/waves/round-49/measured/c1-build.out` (`witness=1 cap=1 newrow=1 witnessed=3/3
met=True`, exit 0; pids/ports and nonces per witness) plus independent peer re-runs
(`.ufo/waves/round-49/w1/out/R1Rerun/c1-build.out`, `…/c1-build.run2.out`). I verified the
build-tree code paths the receipt's legs rest on (`kama-llamacpp-live.py:280-296`,
`:212-272`; `kama-live-replay.py:275-281`; counter `:258-339`, `:343-390`, `:394+`) and
that `child_pid` appears nowhere in the counter. The draft attributes the C1 figures to
the measured receipt, never to a run of mine.

## 4. Gates

| Gate | Result | Evidence |
|---|---|---|
| C1 `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` | met, exit 0 | measured receipt; peer re-runs; not run by me |
| C2 `fixture=1 lane=1 scenarios=8/8 met=True` | met, exit 0 | my run, `c2-S9Readme.out` |
| Controls all `met=False` | met | five control outputs read |
| Counter digests = preregistration | met | `sha256sum` of build blobs |
| Sources append-only over base→build | `added S494 (allowed)`, `added S495 (allowed)`, no violations | `.ufo/waves/round-49/w1/out/X0Census/sources-append-only-438127bc-to-74558c71.out` (peer receipt) |

## 5. Findings for integration (no in-place fix attempted; counters/prereg frozen)

**F1 — the round-48 v3 counter now exits 1 at the v4 build, by construction.**
`tools/round48-append-audit-v3-check.py` compares the tool's output to its own v3
recompute; at `74558c71` it reads `lane: 0718b6abbda6 SCORECARD.md graded tool=2356
counter=2349`, `ungraded tool=65 counter=72`, `ungraded_lines tool=82 counter=89`,
`met=False`, exit 1 (`.ufo/waves/round-49/measured/r48c1-build.out`). That is the seven
lines v4 grades — intended supersession, not a lane regression. Proposed handling: record
it as superseded in the round-49 measured results (do not count it green, do not edit the
frozen counter); the draft already says so in one sentence so the README does not mislead.

**F2 — the witness does not join the observed server to the replay or to the captures.**
`ready.json`'s pid is observed, then only `witness.released` is checked
(`tools/round49-replay-witness-audit.py:306-329`; `grep -c child_pid` = 0), and
`--compare` treats `child_pid`/`port` as instance facts (`tools/kama-live-replay.py:198`,
`:291`). Round-49 seats K1Design (F1) and K1Cheat demonstrated a decoy replay and an
env-injection variant reaching `met=True` at this build; the counter builds the child env
from `os.environ` (`:431-434`). The draft states this limit verbatim rather than calling
the class "closed". Proposed next counter: accept `ready.json` only when the pid descends
from the replay process and `/proc/<pid>/exe` resolves under the replay's work dir, require
`rr["child_pid"] == ready["pid"]`, and allowlist the child env.

**F3 — v4's negation window remains a lexical tripwire.** At the build
(`tools/append-only-audit.py:212-213`, `:216-233`) the window misses `cannot`, `can't`,
curly apostrophes, em dashes, comma-separated and trailing negations, and unbinds
`no edits append-only`; the whole-word class excludes only `[a-z0-9_]`
(.ufo/waves/round-49/w1/out/K2Negation.md F1–F3). The draft keeps only the gaps that
survive the integration edit it observed (see F4) and says the lane's 384 flagged lines
are all judged correctly today.

**F4 — the lane working tree is a live integration surface.** At drafting time:
`M SKILL.md`, `M corpus/QUALITY.md`, `M corpus/knowledge/llamacpp-loading-lifecycle.md`,
`M tools/append-only-audit.py` (NEG_WINDOW broadened per K2Negation F1),
`M tools/kama-llamacpp-live.py` (archive check now single-descriptor / `O_NONBLOCK` /
`fstat`, per V1Live F1), `?? corpus/lessons/round-49.md`, `?? .ufo/waves/round-49/measured/`,
`?? .ufo/waves/round-49/w1/out/`. All figures in the draft are from committed trees at
`74558c71`; the draft is the build-time disposition and needs L1's integration addendum
for anything the uncommitted edits close. (The SKILL registry rows the assignment lists as
outstanding are among these uncommitted edits.)

**F5 — minor.** `corpus/SOURCES.md:247-248` `used-by` names
`corpus/lessons/round-49.md`; that file exists only untracked now, so the row's pointer
lands when the lesson is committed.

## 6. Out of scope / untouched

Capability rows, the SCORECARD round-49 section, LOG/QUALITY/README/lesson edits,
PROVINCE, the instrument registry, and promotion are other seats'/L1's. I wrote only my
report and `…/out/S9Readme/`. No `git add/commit/checkout/stash/reset` in the lane (the
clone checkout was in my scratch clone); no counter, preregistration or control edited; no
llama-server started by me (`pgrep -f llama-server` checked before finishing — nothing of
mine).

## 7. Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Readme.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Readme/frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Readme/c2-S9Readme.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Readme/seven-v4-only-lines.txt`
