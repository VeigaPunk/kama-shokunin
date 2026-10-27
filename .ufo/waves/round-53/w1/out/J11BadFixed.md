# J11BadFixed — round 53, C2 ablation control (bad `fixed`, bad `upstream`)

**Verdict: the `fixed` class is calibrated (a replacement that does not resolve is caught: bad=1, undisclosed=1, met=False, exit 1). The `upstream` class is not content-calibrated: it accepts any `raw.githubusercontent.com` URL that answers HTTP 200, so a row citing the b11909 tag/commit — whose `tools/server/server-chat.cpp` is sha256 `5a4acc9b…`, not the `91f48e09…` SKILL.md pins — or the mutable branch `master` leaves the counter at `met=True` (exit 0). A `fixed` row whose replacement resolves but names an unrelated file also passes.**

All measured numbers below come from the **frozen** counter, unmodified:
`sha256(tools/round53-cited-path-check.py) = 1afb8b9d32fd0706d0625a4ea70270890039f93fc32635c28b12fa71b13e3080`.
Fixture work was done only in my own `git clone --shared` at `/fast/scratch/hyaku/kama-r53/J11BadFixed/lane`, branched at the build commit; every commit of mine was made after `git rev-parse --show-toplevel` printed that clone, with `-c user.name=fx -c user.email=fx@invalid`. Nothing in the lane tree, measured/, counters or preregistration was touched.

## 1. Setup and baseline

```
S=/fast/scratch/hyaku/kama-r53/J11BadFixed; export TMPDIR=$S
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane checkout -q -B j11fix c22602bd8d83ab26349d1087e916ca537ee4f9d1
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py \
  --repo $S/lane --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch $S --out $S/c2-baseline.out
```
```
tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1 fleet=d2a6c59aaabcbde2d4a946c31d0276bb2c3d7887
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
exit=0
```
Reproduces the L1's `measured/c2-build.out` counts (`cited=682 unresolved=14 disclosed=14 met=True`) although the fleet tree advanced from `ee9f7341` (L1's run) to `d2a6c59a` (mine); the counts did not move. The fleet rev moved again during the seat (`71256a5d`, then `33540c6e`); no measured line below changed because of it.

## 2. Ablation A — bad `fixed` row (assignment item 1)

Commit `2e0adff2` in my clone (diff in `fixture-commits.txt`): ledger row
`SKILL.md  tests/report-audit/…  fixed  tests/report-audit/` → replacement `tests/report-audit/nope/`, and SKILL.md:895 changed from `` `tests/report-audit/` `` to `` `tests/report-audit/nope/` ``.

```
python3 tools/round53-cited-path-check.py --repo $S/lane --tip 2e0adff2e9e9392997e069fea0493a29cf6c6908 --scratch $S
fixture=1 lane=0 scenarios=8/8 cited=682 unresolved=15 disclosed=14 undisclosed=1 bad=1 stale=0 dropped=0 met=False
detail: undisclosed SKILL.md `tests/report-audit/nope/`: [('tests/report-audit/nope/', 'missing')]
detail: bad ledger line 27 (SKILL.md `tests/report-audit/…` fixed): replacement 'tests/report-audit/nope/' does not resolve at tip
exit=1
```
The class works: the row is `bad` at the resolve check (`tools/round53-cited-path-check.py:248-249`) and the new dangling citation is separately counted `undisclosed`.

## 3. Ablation B — `upstream` row at a wrong ref (assignment item 2)

The suggested ref, the **b11909 tag, does contain `tools/server/server-chat.cpp`** — so the counter does not reject it:

| fixture tip | ledger row evidence | frozen C2 | exit |
|---|---|---|---|
| `2e0adff2` fixed ablation | — | `lane=0 … bad=1 met=False` | 1 |
| `d4d21c5d` | `…/llama.cpp/b0gu5ref/tools/server/server-chat.cpp` (nonexistent ref) | `lane=0 undisclosed=1 bad=1 met=False` | 1 |
| `bf4cca47` | `…/llama.cpp/b11909/tools/server/server-chat.cpp` (tag; 200) | `lane=1 undisclosed=0 bad=0 met=True` | 0 |
| `b5a9cc9d` | `…/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/server-chat.cpp` (b11909's tag commit, full sha, 200) | `lane=1 undisclosed=0 bad=0 met=True` | 0 |
| `ac9d0753` | `…/llama.cpp/master/tools/server/server-chat.cpp` (mutable branch, 200) | `lane=1 undisclosed=0 bad=0 met=True` | 0 |
| `49afa7a0` fixed laundering | `fixed → tools/report-landing-audit.py` (resolves, cited at SKILL.md:895) | `lane=1 undisclosed=0 bad=0 met=True` | 0 |

The 404 case is caught at `tools/round53-cited-path-check.py:307-310`:
```
detail: bad ledger line 26 (SKILL.md `tools/server/server-chat.cpp` upstream): https://raw.githubusercontent.com/ggml-org/llama.cpp/b0gu5ref/tools/server/server-chat.cpp unfetchable: HTTP Error 404: Not Found
exit=1
```

`upstream-ref-probes.txt` (curl + sha256sum, 2026-10-27) shows why 200 is not identity:

| ref for `tools/server/server-chat.cpp` | HTTP | sha256 |
|---|---|---|
| `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (the build's URL) | 200 | `91f48e09…6263e` = SKILL.md:1248 pin |
| `704366d76f8748cf9ad3df62a464bfcc8d1ae6adf` (41 hex, one char too many) | **200** | same bytes — GitHub resolves the prefix, so a mistyped sha does not even 404 |
| `b11909` | 200 | `5a4acc9b…b34c` |
| `caa8191df159f764fb0160e3d2fc6be008948aee` (b11909's commit) | 200 | `5a4acc9b…b34c` |
| `master` | 200 | `5a4acc9b…b34c` |
| `b0gu5ref` | 404 | — |
| fork `ggerganov/llama.cpp/master` | 200 | — |

## 4. Findings

### F1 — `upstream` checks reachability, not the pinned artefact (contract gap, measured)

- Where: `tools/round53-cited-path-check.py:298-311`, docstring `:55` ("the URL answers HTTP 200 when fetched here"). The ref segment is matched by `[\w.-]+` (`:301-302`), so a tag, a branch, a fork or a prefix-resolved mistyped sha all pass, and the body is never hashed.
- Shown by: the `b5a9cc9d` line of §3 — the row cites b11909's commit, whose bytes are `5a4acc9b…`, while the note in the same row and SKILL.md:1248 claim `91f48e09…`; the frozen counter still prints `bad=0 met=True`, exit 0.
- Why it matters for calibration: the lane's own disclosure (`registry/cited-path-corrections.tsv` lines 22-26) rests on "sha256 … equal to SKILL.md's pin". Nothing in C2 re-derives that sentence, so a row can pin content the paper trail contradicts and C2 cannot see it. It also means the ledger's disclosing power decays silently if a cited ref is a branch.
- Proposed fix: `proposed-c2-strengthening.diff` (in this directory) — require a full 40-hex commit in the URL and, where the surface's own line states a 64-hex SHA-256 for that token, compare `sha256(response body)` with it.
- Proposal probe (patched **copy** preserved as `w1/out/J11BadFixed/c2-patched-proposal.py`, `sha256 9b9369c1…`, never the frozen file): build tip `c22602bd` stays `met=True` (`cited=682 unresolved=14 disclosed=14`); `b5a9cc9d` becomes
  `bad ledger line 26 … serves sha256 5a4acc9bceea, not the pinned 91f48e09afc5` → `met=False`; `bf4cca47` and `ac9d0753` become `… URL at a full commit ending in it` → `met=False`; `d4d21c5d` and `2e0adff2` stay failing. 8/8 fixture scenarios still pass in every run.

### F2 — `fixed` does not bind the replacement to what the ellipsis stood for (limit, measured)

- Where: `tools/round53-cited-path-check.py:239-250` — the class asks only that the replacement be cited in the surface and resolve.
- Shown by: `49afa7a0` (row `tests/report-audit/… fixed tools/report-landing-audit.py`, SKILL.md:895 citing it) → `bad=0 met=True`, exit 0, while the sentence at SKILL.md:893-896 then names the auditor file twice instead of the `tests/report-audit/` directory. A `fixed` row can therefore "correct" a citation into a different, unrelated file.
- Proposed fix (same diff): require `ev.startswith(<token up to its ellipsis/brace, truncated to its directory>)`; probe rejects `49afa7a0` with `replacement 'tools/report-landing-audit.py' does not extend 'tests/report-audit/'` and leaves the build tip met.
- This is a limit of a resolution counter, not of its implementation: no in-place semantics check exists. The stem rule is the cheap proxy.

### Not a defect, recorded

- The fixture leg is unchanged by any of the six tips (always `scenarios=8/8`, `fixture=1`), and the lane leg flips only where the ablation says it should.
- Observed lane state at report time (not mine, not modified): `git -C kama-shokunin status --porcelain` shows `M .ufo/waves/round-53/measured/c1-build.out`, `M .ufo/waves/round-53/measured/c2-build.out`, `M SKILL.md` — another seat's in-flight integration.

## 5. Retained evidence, resources, cleanup

- Frozen-counter receipts: `c2-baseline.out`, `c2-bad-fixed.out`, `c2-bad-upstream-404.out`, `c2-upstream-b11909.out`, `c2-upstream-tagcommit.out`, `c2-upstream-master.out`, `c2-fixed-launder.out`.
- Fixture commits and their patches: `fixture-commits.txt` (`2e0adff2`, `d4d21c5d`, `bf4cca47`, `ac9d0753`, `49afa7a0`, `b5a9cc9d`; `252817d2` was a superseded draft and is not cited).
- Proposal: `proposed-c2-strengthening.diff`, probe transcript `proposal-probe.out`, upstream ref table `upstream-ref-probes.txt`.
- No llama-server was started by this seat (C2 only fetches HTTP); no service touched. No tool installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r53/J11BadFixed` removed after copying the receipts above.
