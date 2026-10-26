# S1Gate — round 49 gate decisions, lane kama

**Verdict: the round-49 gate ACCEPTS both claims at build `74558c71` on the counters' own runs (C1 `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0; C2 `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0), both counters fail at base `438127bc` (exit 1), and the gate REJECTS four substitute witnesses — `/health`+`/props`, cmdline-only, self-consistent `piece` comparison, and lane `exit 0` — each demonstrated with a running stub or a base run.**

Full decision text with claim/evidence/verdict/flip condition: `S1Gate/gate.md` (same directory). Lane was read-only; no lane file, git or jj state was touched; no tool installed.

## Evidence runs (my own `git clone --shared`, receipts in this directory)

| command | exit | receipt |
|---|---|---|
| `round49-replay-witness-audit.py --repo $S/lane --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S/sc1r` | **0** | `S1Gate/c1.tip-74558c71.out` |
| `round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S/sc2r` | **0** | `S1Gate/c2.tip-74558c71.out` |
| `round49-replay-witness-audit.py --repo $S/lane --tip 438127bc01ff3b99f98468549d58046f932490ef --scratch $S/sc1b` | **1** | `S1Gate/c1.base-438127bc.out` |
| `round49-append-audit-v4-check.py --repo $S/lane --tip 438127bc01ff3b99f98468549d58046f932490ef --scratch $S/sc2b` | **1** | `S1Gate/c2.base-438127bc.out` |
| `LANE=$S/lane MODEL=$S/model.gguf SCRATCH=$S OUT=…/S1Gate python3 gate_rejects.py` | **0** | `S1Gate/gate_rejects.out` |
| `binds()` edge probe on the tip tool | 0 | `S1Gate/bind_probe.out` |

`$S=/fast/scratch/hyaku/kama-r49/S1Gate` (removed after copying; all cited output is inside the receipts).

Frozen inputs check: the counter files at `74558c71` hash to the preregistration's `counter_sha256` (`86b4a40d…` C1, `26c465a9…` C2); the build is the single commit on freeze `36d5ed26`; the model downloaded for the probes hashes to `270cba1b…`. My base runs are byte-identical to the frozen controls `.ufo/waves/round-49/controls/base.c1.out` / `base.c2.out` (diff adds only the control builder's `exit=1` trailer).

## Gate decisions

| # | axis | proposal | verdict |
|---|---|---|---|
| D1 | operability | `/health` 200 or `/props` `model_path` as execution witness | **REJECT** |
| D2 | operability | `/proc/<pid>/cmdline` `-m <model>` as model proof | **REJECT** |
| D3 | operability | `piece` comparison self-consistent between `/tokenize` and `/detokenize` | **REJECT** |
| D4 | operability | conjunction `exe ∧ listen-owned ∧ -m-hash ∧ nonce-tokenized-with-counter-decoded-GGUF ∧ gone-after-release` | **ACCEPT** 3/3 |
| D5 | operability | bounded archive-member verification (`cap`) | **ACCEPT** (sparse + size-mismatch legs only) |
| D6 | operability | `/tokenize` source row = registry presence | **ACCEPT as presence** |
| D7 | calibration | lane `tool exit 0` / `bad_declarations 0` as calibration evidence | **REJECT** |
| D8 | calibration | v4 origin rule closes laundering | **ACCEPT** |
| D9 | calibration | whole-word token, 3-word negation window, no wildcard self-declaration | **ACCEPT, with F1 limit** |
| D10 | calibration | `ungraded ≤ natively-exempt` per event | **ACCEPT as a bound** |

### The three required rejects — grounded

D1 (`gate_rejects.out`, probe A; a python `http.server` stub, no llama-server):

```
A: GET /health status=200 body={"status": "ok"}
A: GET /props status=200 model_path=…/model.gguf sha=270cba1b… frozen_model=1
A: exe sha256=375532f8… frozen_server=0 frozen=35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
A: counter observe() nonce='kama witness f12fc0ce9f27e9ca' problems=["exe sha256 375532f8… is not the frozen server"]
```

The stub answers both fields (the `model_path` is a real file with the frozen model digest), owns the listen socket, names `-m <model>` and round-trips the counter's nonce with the model vocabulary; the frozen `observe()` (`tools/round49-replay-witness-audit.py:258`) reports exactly one failure — the exe digest. Corroborated by the frozen control `controls/junk-c1-fake-witness.c1.out` (only exe failures).

D2 (probe B): `argv=["/usr/bin/python3", "-c", "import time; time.sleep(120)", "-m", "…/model.gguf"]`, `-m` hash `270cba1b…` matches, `sockets=0`, `frozen_server=0`. argv is chosen by the process; the counter keeps that leg only as a consistency check beside the exe digest (`:267-274`).

D3 (probe C): invented 3-char vocabulary — `detokenize 'kama witness 84acab0e495322ff' equals_nonce=1`, `pieces disagreeing with the model vocabulary=10/10 (example {"id":0,"piece":"kam"}, vocab[0]='<unk>')`. Only the counter's own GGUF decode (`:275-283`, `gguf_tokens()` `:144`) rejects it.

D7 (base run): `fixture=0 lane=0 scenarios=4/8 met=False` with `launder`, `substring`, `negated`, `wildcard-self` FAIL while the same run reports `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89` and `event 0718b6abbda6 … ungraded 72 > natively exempt 65`. A clean lane coexists with a broken rule; the two legs must be read together.

### Claim verdicts

| claim | tip 74558c71 | base 438127bc |
|---|---|---|
| C1 operability 8→8 | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0 | `witness=0 cap=0 newrow=0 witnessed=0/3 met=False`, exit 1 |
| C2 calibration 7→7 | `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0 | `fixture=0 lane=0 scenarios=4/8 met=False`, exit 1 |

C2 tip: launder graded 25 (ungraded 0, unrestored), native head kept (25 ungraded, exit 0), lane `ungraded_lines 82` (base 89 — 7 lines regraded), event `0718b6abbda6` `ungraded 65 <= natively exempt 65` (base 72 > 65, tight bound).

## Findings

**F1 — the v4 negation window stops at punctuation (limit of D9; frozen, not fixed).** `tools/append-only-audit.py:212-213`:

```
NEG_WINDOW = re.compile(r"(?:\b(?:not|never|no|nor|neither|non|isn't|aren't)\b|\bno longer\b)"
                        r"(?:[\s\-]+[\w'’]+){0,3}?[\s\-]+append[- ]only")
```

Command and output (`S1Gate/bind_probe.out`):

```
$ python3 -c "…import the tip tools/append-only-audit.py…; print(a.binds(text, pat, decl_path))"
binds('SCORE.md', 'NOTES.md'): False  text='SCORE.md is not strictly append-only'
binds('SCORE.md', 'NOTES.md'): False  text='SCORE.md is not under any circumstances append-only'
binds('SCORE.md', 'NOTES.md'): True   text='SCORE.md is not, under any circumstances, append-only'
```

A negation three words before `append-only` binds when commas separate it, because the separator class is `[\s\-]` only. The claim's "a negation within three words before append-only unbinds" is thus narrower than it reads. The same regex is duplicated in the frozen counter (`tools/round49-append-audit-v4-check.py:98`), so its lane leg cannot catch the case either; the lane's own declarations are unaffected (`bad_declarations 0`, all 8 fixtures pass). Proposed fix (file frozen — proposed only, not applied): widen the separator on both sides of the word run, e.g. `[\s\-,;]+` in place of `[\s\-]+`, or normalise `,;` to spaces before matching, in both the tool and the counter.

**F2 — cap evidence is narrower than the tool's bound.** `provenance-archive-not-regular`, `provenance-archive-too-large`, `provenance-archive-too-many-members` exist in `tools/kama-llamacpp-live.py:232,234,253` and its selftest (`:1391-1393`) but the frozen counter's `cap` leg exercises only sparse (`:261`) and size mismatch (`:263`) plus the positive control. D5 is accepted for the exercised legs only; the other three are not counter evidence.

**F3 — `newrow=1` is registry presence, not conformance.** `newrow_leg` (`:394`) matches row presence, the frozen README URL at `caa8191d` and the string `/tokenize` (row S494 at `corpus/SOURCES.md:247`); it does not read the captured README or verify the quoted shape. C1's live nonce is the conformance evidence.

Also observed and recorded as gate limits: C1 witnesses execution of the frozen binary as listener with the frozen model but not the binary's provenance from the downloaded archive at replay time; a host copy of the same binary passes the witness; `/proc` is Linux-only and fails closed. C2 origin is first-appearance, so head-born text later carried in a dated section and deleted from the head again stays ungraded.

## Hygiene

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read-only: only `git clone --shared`, `git show`, `git log`, `git archive` via the counters; no `git add/commit/checkout/stash/reset`, no jj calls, no writes under the lane except this report and `w1/out/S1Gate/`.
- Fixtures: none created outside scratch; the probe stubs ran on ephemeral loopback ports 47097/60809 and were killed, ports checked to refuse (`teardown: A refuses=1 C refuses=1 B alive=0`). The C1 counter's three llama-server runs (pids 1768075/1778812/1792942, ports 44443/35935/42749) were torn down; all six pids verified gone, no `gate_rejects` processes remain, and no llama-server I started is running.
- No tools installed or upgraded (pacman paused; nothing needed).
- Scratch `/fast/scratch/hyaku/kama-r49/S1Gate` removed after copying receipts; all cited outputs live in the paths below. No `/tmp` evidence used.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/gate.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/gate_rejects.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/gate_rejects.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/bind_probe.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/c1.tip-74558c71.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/c2.tip-74558c71.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/c1.base-438127bc.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S1Gate/c2.base-438127bc.out`
