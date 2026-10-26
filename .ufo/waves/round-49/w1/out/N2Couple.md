# N2Couple — round 49: C1/C2 separability

Verdict: **C1 and C2 each meet alone.** C1's counter met=True on a clone at
36d5ed2681111b68c180f8ab1646d8dc9beaedee + only the C1 build; C2's counter
met=True on a clone at 36d5ed… + only `tools/append-only-audit.py` from
74558c71c38ceaeace15fd4cf8aa9d84977584b1. Their read sets are disjoint; no
cross-build dependency observed.

## Evidence

Fixture vehicles: single scratch clone `git clone --shared` of the lane
(`/fast/scratch/hyaku/kama-r49/N2Couple/lane`), rebuilt between runs; each
fixture commit created after `git rev-parse --show-toplevel` == clone root.

### C1 on F1 (36d5ed + only the C1 build)

F1 head `c29df542287d8c1eefed1217ac3bdec460606935`; `git diff 36d5ed26 HEAD`
= exactly the three C1 build files:
`corpus/SOURCES.md` (+2 rows S494/S495), `tools/kama-live-replay.py`,
`tools/kama-llamacpp-live.py`. `tools/append-only-audit.py` deliberately left
at its 36d5ed (v3) state.

Command (exit 0):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py \
  --repo /fast/scratch/hyaku/kama-r49/N2Couple/lane \
  --tip c29df542287d8c1eefed1217ac3bdec460606935 \
  --scratch /fast/scratch/hyaku/kama-r49/N2Couple/pad1 --out .../c1-fixture.out
```

Output (`c1-fixture.out`):

```
tip=c29df542287d8c1eefed1217ac3bdec460606935
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: pid 322402 port 36043 exe+listen+model ok, nonce 'kama witness a2811c1727703662' round-tripped
detail: witness w2: pid 324471 port 34057 exe+listen+model ok, nonce 'kama witness df244606b3dc493a' round-tripped
detail: witness w3: pid 327780 port 37073 exe+listen+model ok, nonce 'kama witness 13783d0b319b9c70' round-tripped
detail: cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok
detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok
detail: newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']
```

C1 meets alone. It never invoked `tools/append-only-audit.py` (v3 present at
36d5ed, untouched in F1) and never read any C2-only path.

### C2 on F2 (36d5ed + only `tools/append-only-audit.py` from 74558c)

F2 head `5d167d039d9a117b7a6d4165f2b805a575692968`; `git diff 36d5ed26 HEAD`
= exactly `tools/append-only-audit.py` (v4, +94/−7). The C1 tools were left at
their 36d5ed versions.

Command (exit 0):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-append-audit-v4-check.py \
  --repo /fast/scratch/hyaku/kama-r49/N2Couple/lane \
  --tip 5d167d039d9a117b7a6d4165f2b805a575692968 \
  --scratch /fast/scratch/hyaku/kama-r49/N2Couple/pad2 --out .../c2-fixture.out
```

Output (`c2-fixture.out`):

```
tip=5d167d039d9a117b7a6d4165f2b805a575692968
fixture=1 lane=1 scenarios=8/8 met=True
detail: scenario launder: ok exit 1 (want 1) event {... 'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'} ...
detail: scenario native-head: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} ...
detail: scenario dated-loss: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'status': 'unrestored'} ...
detail: scenario substring: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario word-token: ok exit 0 (want 0) bad_declarations 0 want 0
detail: scenario negated: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-self: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-named: ok exit 0 (want 0) bad_declarations 0 want 0
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
```

C2 meets alone. The lane leg reproduces the dry-run result (0718b6ab event:
ungraded 72 → 65, held, still restored). No C1 tool or C1-only path was used.

## Paths each counter reads

C1, `tools/round49-replay-witness-audit.py`:
- `--repo` git ops: `rev-parse --verify <tip>^{commit}`, `archive --format=tar <tip>`.
- Tip tree (from archive): `.ufo/waves/round-48/c2/live/receipt-1.json`, `-2.json`, `-3.json` (`RECEIPTS`, lines 106–108, 450–455); `tools/kama-live-replay.py` (`REPLAY`), `tools/kama-llamacpp-live.py` (`LIVE`).
- `git show <rev>:corpus/SOURCES.md` for `<rev>` = tip and `BASE=438127bc…` (newrow leg, lines 394–405).
- Transitive (via the two tools it runs): `registry/endpoint-consumers.tsv` and `tools/kama-probe.sh` (kama-llamacpp-live.py lines 88–90); network downloads (server archive from receipts' provenance `asset_url`, model from receipts' provenance `model.url`).
- Outside the repo: model download from `MODEL_URL` (huggingface.co, lines 99–101) + sha256 + GGUF `tokenizer.ggml.tokens` parse; `/proc/<pid>/{exe,cmdline,cwd,fd/*,stat}`; `/proc/net/tcp`, `/proc/net/tcp6`; loopback socket to 127.0.0.1:<port>; env `HOME`/`XDG_CACHE_HOME`/`TMPDIR` redirected into scratch.

C2, `tools/round49-append-audit-v4-check.py`:
- `--repo` git ops: `rev-parse --verify <tip>^{commit}`, `archive --format=tar <tip>`, `rev-list --topo-order --reverse --parents <tip>`, `cat-file --batch-check=%(objectname) %(objecttype)` + `cat-file blob`, `show <parent>:<file>`, `diff -U0 <parent> <commit> -- <path>` (lines 260–280, 312–335), `show <tip>:registry/append-only-contract.tsv` (line 296), `show <tip>:<declaring file>` (line 300).
- Tip tree (from archive): `tools/append-only-audit.py` (`TOOL`, line 87) — run as subprocess.
- Transitive (via the tool): `registry/append-only-contract.tsv` and the audited files' git history/blobs (LOG.md, SCORECARD.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md, corpus/lessons/*.md, corpus/knowledge/consumer-registry.md, corpus/knowledge/error-is-not-a-verdict.md, registry/history/DELTA.md, registry/report-landing-errata.tsv — per contract rows).
- Fixtures: fresh git repos created under `--scratch`; contract TSVs written under `--scratch`.

Disjointness: C1's repo paths are `{.../receipt-{1,2,3}.json, tools/kama-live-replay.py, tools/kama-llamacpp-live.py, corpus/SOURCES.md, registry/endpoint-consumers.tsv, tools/kama-probe.sh}`; C2's are `{tools/append-only-audit.py, registry/append-only-contract.tsv, declaring files, audited event files}`. Empty intersection. The only shared object is the repo being measured itself.

## Findings

No defect. Both counters pass in isolation on their minimal fixture clones
(C1 exit 0, C2 exit 0), confirming the preregistration's `separability` block:
C1 touches no C2 path and C2 no C1 path. No leftover `llama-server` processes
(`pgrep -f llama-server` empty after the runs).

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/N2Couple.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/N2Couple/c1-fixture.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/N2Couple/c2-fixture.out`
