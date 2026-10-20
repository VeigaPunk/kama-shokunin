VERDICT: partial — every named immutable-cell compare individually fails under its targeted mutant (7/7 killed, selftest+e2e), but two fresh comparator-normalization mutants and one exit-mapping mutant pass the delivered selftest byte-identically to pristine and demonstrably misgrade real revision pairs; the bounded named-survivor claim survives, the selftest does not bind these fresh equivalence classes.

# Scope and axes

Seat `KamaR18.AppendCells`, falsify wave, leaf (no subagents). Target `tools/sources-append-only.py` sha256 `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` at clone `/tmp/kama-r18-falsify-AppendCells/clone`, branch `seat/AppendCells` pinned `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (`git rev-parse HEAD` returned exactly this). Axes attacked: (A) per-immutable-cell comparison killability (assigned), (B) comparator value-normalization equivalence classes (found), (C) violation→exit observability channel (adjacent, found). No edits to the clone's working tree at any point — all mutants were sibling copies under `/tmp/kama-r18-falsify-AppendCells/mut/`; `git -C clone status --porcelain` returned empty and the tool hash re-verified after all runs. Installs: none. Ports: none bound by this seat (`ss -ltn` scan shows only unrelated listeners, e.g. omp pid 3092); no teardown needed. Scratch `/tmp/kama-r18-falsify-AppendCells` removed before finish.

# Green pristine baselines (required)

1. `python3 clone/tools/sources-append-only.py --selftest` → exit 0, `42/42 selftest cases passed`, stdout sha256 `e74918130d839a79a0d620dda9bfdac5faaced6762e78fbfe415d270ad729770` — byte-identical to the official `append-only-selftest` record (`runs/commands.json` entry `append-only-selftest`, exit 0; official stdout digest matches).
2. Pristine guard, real transition: `--from cff9e62f05aa7cfb9059444f62eb787100719713 --to 1c325b2e58fcfdc6761f645b44cedfb1d65243e6 --repo <clone> --json` → exit 0, `ok:true`, `violations:[]`, `added:[S042..S055]` (14 rows) — matches the committed expectation that cff9e62→1c325b2 is append-only-clean.
3. Pristine guard, real negative: `--from cff9e62f… --to <T2 with real S001 source-cell rewrite> --repo <tmp repo>` → exit 1, `S001 cell-changed source`, `from: "llama.cpp server README — https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md"` → `to: "https://ATTACKER.example/…"` (receipt `e2e-source-pristine.json`). All seven single-cell T2 variants graded exit 1 under pristine.

# Experiment construction (exact)

- T2 blobs: the committed `cff9e62f…:corpus/SOURCES.md` (55 rows) loaded through the delivered `parse_registry`; for each of the seven immutable cells, exactly that cell of row S001 (and S003 for the case variant) was replaced (S001 `source`→`https://ATTACKER.example/…`, `kind`→`knowledge`, `tier`→`B`, `scope`→`widened scope text`, `anchor`→`§TOTALLY-DIFFERENT @ commit 0000000`, `teaches`→`completely rewritten teaching`, `opened`→`2020-01-01`), the row line rebuilt from parsed values, and `parse_registry` re-run to assert the diff set is exactly the targeted cell (first naive `'|'-split` rebuild corrupted backtick-piped cells — discarded and rebuilt; that intermediate is not evidence). Each blob committed in throwaway repo `/tmp/kama-r18-falsify-AppendCells/revs2` (one commit per cell; R17 fetched in so `git show cff9e62f…:corpus/SOURCES.md` resolves).
- Mutants: text-level single-edit copies of the pristine tool in `mut/`, each `ast.parse`-checked before use.

# A. Assigned attack — mutate each immutable cell compare individually

Two mutant shapes, both at `tools/sources-append-only.py:265` (`for c in immutable_cols if old[c] != new[c]`), the single comparison site (grep count 1).

1. Row-gating shape (`if old["<cell>"] != new["<cell>"]`) — 7 mutants: every one killed by `--selftest` (exit 1) but the failures show *cross-cell* firing (e.g. mut-anchor fails 12 cases, mut-source fires on every changed row); kept only as a demonstration that the shared loop is the sole kill channel.
2. Drop-one-cell shape (`if c != "<cell>" and old[c] != new[c]`) — the literal assignment; results:

| mutant | selftest | FAIL lines (targeted + collateral) | e2e: catches real edit of | e2e: misses (exit 0) |
|---|---|---|---|---|
| mut-source 5260f7b2… | exit 1, 40/42 | `source change`, `only \`source\` changes` | source | kind,tier,scope,anchor,teaches,opened |
| mut-kind | exit 1, 41/42 | `only \`kind\` changes` | kind | other six |
| mut-tier | exit 1, 40/42 | `only \`tier\` changes`, `closing hashes…` | tier | other six |
| mut-scope | exit 1, 40/42 | `only \`scope\` changes`, `edit under a deeper subheading` | scope | other six |
| mut-anchor | exit 1, 40/42 | `anchor change`, `only \`anchor\` changes` | anchor | other six |
| mut-teaches 9367a5aa… | exit 1, 39/42 | `teaches change`, `only \`teaches\` changes`, `edit after a blank line` | teaches | other six |
| mut-opened | exit 1, 40/42 | `only \`opened\` changes`, `edit in a later table segment` | opened | other six |

Full 7×7 e2e matrix on real blobs (`e2e-<cell>-<mutant>.json`): diagonal = `MISSED` (exit 0, `ok:true`), off-diagonal = `caught:<cell>` exit 1 with the correct cell attribution. Example miss receipt `e2e-kind-mut-source.json`: `{"violations":[],"added":[],"ok":true}` for a real `kind` docs→knowledge rewrite. **Every individually-mutated cell compare is killed by the named `only `<cell>`` selftest assertion (plus 0–2 collateral named assertions); no survivor in this family.** Positive allowed-cell control: real S001 `used-by` edit (T2 `057501ec…`, blob `out/t1-usedby.md`) → pristine and all 7 drop-cell mutants plus mut-skip-opened exit 0 `ok:true`; under mut-mutable-teaches/mut-immutable-drop-teaches the same allowed edit exits 2 (self-inconsistent fault, see C).

# B. Fresh survivors — comparator normalization equivalence classes

`diff_registries` compares via `old[c] != new[c]` (`sources-append-only.py:265`); the selftest's oracle `_CELL_EDIT_EXIT` (`:371–374`, written out by design) pins only the *exit outcome* of each single-cell edit, never two byte-distinct values that a normalization would equate.

- `mut-ci.py` sha256 `6783be0652a67e0ba50fb77d439aa8ebe41a7267e9cc6a7902938f98d7d306e4`: `265` → `if old[c].strip().casefold() != new[c].strip().casefold()`. `--selftest` → exit 0, stdout **byte-identical to pristine** (`42/42`, sha `e7491813…`). End-to-end on a real case-only immutable edit — S003 `teaches` `Exact vllm: …` → `exact vllm: …` (T2 `581a3145…`, blob sha `59580bda…`): pristine exit 1 catches `S001… S003:teaches`; **mut-ci exit 0, `{"violations":[],"ok":true}`** (receipt `e2e-t2-ci-s003-mutci.json` sha `211d9573…`). An H1-shaped (case-insensitive) regression inside the append-only comparator would silently accept case rewrites of every immutable cell.
- `mut-normws.py` sha256 `55b5766c6708e232914d54ac32d901a4c9f48b9a255c607697b6ee1d37b33868`: `265` → `if " ".join(old[c].split()) != " ".join(new[c].split())`. `--selftest` → exit 0, byte-identical pristine output. End-to-end on a real internal-whitespace edit — S001 `teaches` `503 loading, 200 loaded` → `503 loading,  200 loaded` (T2 `01a628e1…`, blob sha `c3a4d28a…`): pristine exit 1 with the two-space delta visible in the details; **mut-normws exit 0, `ok:true`** (receipt `e2e-t2-ws-teaches-mutnormws.json` sha `f8bfd010…`).
- Both mutants over the *official* real pair `cff9e62f… → 1c325b2e…`: exit 0, `ok:true`, `added:14` — i.e. on today's data a normalization regression is indistinguishable from the delivered guard.
- Feasibility scan of the committed registry: no committed cell value changes under NFC/NFD and none has edge whitespace (`unicodedata` scan over all 55 rows × 11 cells → empty list), and no two rows share a casefold collision inside one cellname — so today's corpus cannot *yet* distinguish byte-equality from normalized equality either; only a future edited-in byte (case flip, internal whitespace, combining sequence) would diverge, and by then the regressed guard passes it.
- Attempted NFC/NFD real-blob variants were **inconclusive as attacks on this corpus** (the guard parser's cell values happen to be NFC/NFD-stable and no committed anchor string contains a decomposable sequence); not counted as survivors or kills.

Answer to the assigned question — *how does the comparison invariant fail vs actual violation?*: the invariant (immutable cells byte-identical) is enforced pointwise by exact inequality at `:265`, then mapped to exit by `run_check` (`:350`). The selftest observes neither layer directly: its case loop grades `violations` from `diff_registries` itself (`got_exit = 1 if violations else 0`, selftest runner ~`:538`) and pins outcomes only via `_CELL_EDIT_EXIT`. A comparator mutant that coarsens equality (normalization) or remaps the exit channel therefore preserves every fixture outcome: invariant failure (a real violation graded clean) exists off-fixture while the fixture's "actual violation" cases still fire — the delivered bytes do enforce the invariant, but the selftest cannot detect that specific regression class.

# C. Adjacent finding — violation→exit channel unbound

`mut-exit.py`: `:350` `return 1 if violations else 0` → `return 0 if violations else 1`. `--selftest` → exit 0, byte-identical pristine output (run_check is never called by the selftest — all cases invoke `parse_registry`/`diff_registries` directly). End-to-end inversion: real S001 source rewrite → **exit 0** (`e2e-source-mutexit.json` sha `1e342242…`, violations still listed in JSON but the exit contract inverts); real allowed `used-by` edit → **exit 1** (false violation, `e2e-t1usedby-mutexit.json` sha `db203d9e…`). KQ22's gate is exit-code-based ("each exit 0"), so this regression turns the gate both blind (0 on edits) and noisy (1 on allowed edits — loud, so partially self-limiting, but the blindness direction is silent). In `survivors.py` terms this would be recorded `survived` (`selftest_arm`: exit 0 + valid passing selftest = survived), i.e. a fresh wave-2 survivor, correctly reported separately per the round-18 rule.

Structural mutants (positive evidence the floor works): `mut-mutable-teaches` (teaches added to `MUTABLE_CELLS`, `:63`) and `mut-immutable-drop-teaches` (teaches removed from `IMMUTABLE_CELLS`, `:67`) both leave `immutable_cols` inconsistent with the fixture header → exit 2 on every case (all 42 FAIL), and exit 2 on the real allowed edit — fault behavior, not silent narrowing, exactly as the comment at `:59–61` intends. `mut-skip-opened` (floor kept, `:265` → `… and c != "opened"`) is killed by selftest (2 FAILs: `only \`opened\` changes`, `edit in a later table segment`) — the two independent `opened` assertions are both necessary; either alone would also catch this mutant.

# Reproduction of official counter arms (context)

`runs/c2-survivors.json:3079–3180`: AO-opened frozen `survived` ("selftest passes", 14/14) vs current `killed` ("targeted selftest assertion failed: only \`opened\` changes", 15/42); AO-blank frozen `survived` vs current `killed` ("edit after a blank line", 36/42). `before/after` fields match the lesson's claim. Note the AO-opened current kill fires via the *floor* (`compared cells … are not exactly the contract's immutable cells`), not via a value-level comparison — consistent with my structural-mutant observations.

# Findings by severity

1. **HIGH (fresh detector-self hole, bounded-claim-consistent):** the selftest cannot fail on value-normalizing comparator regressions — case-only (`mut-ci`) and internal-whitespace (`mut-normws`) mutants of the single comparison at `sources-append-only.py:265` pass 42/42 byte-identically and demonstrably misgrade real revision pairs (receipts above). Concrete demonstration that "unseen mutant cannot survive" would be false if claimed; the round-18 wording already disclaims it, so this refutes no claim — it is the wave-2 counterexample the lesson promised to keep visible. Minimal repair (if adopted by the C2 owner, not by me): two negative cases asserting a case-only and an internal-whitespace rewrite of an immutable cell each grade exit 1.
2. **MEDIUM:** the exit mapping (`:350`) is unobserved by `--selftest`; an inverted mapping passes 42/42 while the CLI grades the real S041-style negative as 0. Same minimal-repair shape: one selftest case asserting `run_check`'s mapping (e.g. monkeypatch-free direct call on a two-row doc), or route the case loop through `run_check`.
3. **LOW/INFO:** row-gating mutants (`old["<cell>"] != new["<cell>"]` without the `c !=` guard) show the shared compare loop is the sole kill channel and produce noisy cross-cell FAILs; harmless today, but any future refactor that duplicates the comparison loop could pass the selftest while dropping one cell (the drop-cell shape is the one that must keep being mutated).
4. **INFO (verification gap, not a defect):** the only official round-18 command touching this tool is `append-only-selftest` (32 commands in `runs/commands.json`; grep for `sources-append-only` outside advice/frozen → selftest and drafts only). KQ22's consecutive-pair gate runs are a round-end obligation; my e2e receipts (real R17→T2 pairs through the documented `--from/--to/--repo/--json` CLI) are the only executed end-to-end evidence in this wave so far.

# Residual risks and limits

- Mutants were hand-built single edits; a *combined* mutant (normalize + drop exit inversion) would also survive — the two classes compose, no additional experiment needed to infer that.
- `t2-nfd-teaches` and NFC/NFD probes are inconclusive on this corpus (no decomposable committed value found); Unicode-normalization weakness is therefore unproven either way, not cleared.
- The e2e matrix used a synthetic 55-row base (real R17 blob) with one edited cell per T2; consecutive-pair coverage of *added-row-then-edited-inside-range* (KQ22's stated reason for per-pair runs) was not re-derived here beyond the committed `added` semantics.
- All mutant selftest runs are fixture self-consistency only; no official counting command was run against the live lane.

# Hashes and receipts

- Delivered tool: `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d`.
- Mutant sources: mut-source `5260f7b2…`, mut-teaches `9367a5aa…`, mut-ci `6783be06…`, mut-normws `55b5766c…` (full sha256s for the two survivors and two named representatives; all others in `out/` were transient and re-derivable from the snippets below).
- Surviving-mutant selftest stdout == pristine stdout: sha256 `e74918130d839a79a0d620dda9bfdac5faaced6762e78fbfe415d270ad729770` (also the official `append-only-selftest.stdout` digest).
- Attack blobs: `t2-ci-s003.md` `59580bda…`, `t2-ws-teaches.md` `c3a4d28a…`; T2 commits in `revs2`: source `e202a1de…`, kind `22c3e6fa…`, tier `28dca7dc…`, scope `458ca144…`, anchor `1a4bffc4…`, teaches `f23be5be…`, opened `f8091c8c…`, allowed `used-by` `057501ec…`, case edit `581a3145…`, ws edit `01a628e1…`.
- Kill receipts: 49 e2e JSONs + 13 selftest transcripts under `/tmp/kama-r18-falsify-AppendCells/out/` (removed with scratch; per contract the exact experiment source is reproduced below).

# Exact experiment source (verbatim)

```python
# mutants (applied to a copy of the pristine tool; ast.parse-checked)
old = 'for c in immutable_cols\n            if old[c] != new[c]\n        ]'
drop   = 'for c in immutable_cols\n            if c != "%s" and old[c] != new[c]\n        ]' % cell
normws = 'for c in immutable_cols\n            if " ".join(old[c].split()) != " ".join(new[c].split())\n        ]'
ci     = 'for c in immutable_cols\n            if old[c].strip().casefold() != new[c].strip().casefold()\n        ]'
skipop = 'for c in immutable_cols\n            if old[c] != new[c] and c != "opened"\n        ]'
exitmut = ('return 1 if violations else 0', 'return 0 if violations else 1')  # at :350
```

```bash
# per mutant: python3 mut/mut-X.py --selftest            (expect 0 for survivors, 1 for kills)
# per pair:   python3 mut/mut-X.py --from cff9e62f… --to <T2> --repo revs2 --json
# blobs built via the delivered parse_registry so each T2 differs in exactly the targeted parsed cell
```

Installs: none. Ports/listeners owned by this seat: none. Clone byte-identical to pin at finish.
