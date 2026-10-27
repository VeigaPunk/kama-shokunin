# K2Predicate — round 55 predicate-identity audit (lane kama, wave 1)

Verdict: **PASS with findings** — the frozen C1/C2 predicate sentences in `.ufo/waves/round-55/preregistration.json` are byte-faithful to both counters' docstring PREDICATE paragraphs (modulo docstring hard-wrap and one trailing punctuation mark), the counter bytes hash to the preregistered sha256s, and every printed leg field in the four frozen receipts matches the preregistration targets; but four real sentence↔code drifts exist (two C1, two C2), of which the sharpest is a **C2 `superseded` clause with no code** ("live base citation" is checked only for citation, never for resolution — demonstrated by counterexample below) and a **C1 code-with-no-clause** (named kernel mappings are a fourth admitted executable-mapping kind the frozen sentence does not name).

Seat scope: predicate sentences (plan) vs. docstring PREDICATE paragraphs vs. what the counters print (leg lines) and execute. No counter, control, preregistration or lane file was modified; counters were used read-only (C2 imported once to drive scratch fixtures). Counters and preregistration are FROZEN — every finding below is reported, not fixed in place; proposed wordings are for the next freeze.

## Evidence base

- Preregistration: `.ufo/waves/round-55/preregistration.json` — C1 predicate line 18, C2 predicate line 30, C1 target/kill_rule lines 21–23, C2 target/kill_rule lines 33–35.
- Counters: `tools/round54-replay-code-audit.py` (972 lines, sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` — matches prereg `counter_sha256`), `tools/round54-cited-path-check.py` (862 lines, sha256 `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` — matches). Command: `sha256sum tools/round54-*.py`.
- Receipts: `controls/base.c1.out`, `controls/base.c2.out`, `measured/c1-build.out`, `measured/c2-build.out` (copies in `out/K2Predicate/`).

## 1. Sentence-level diff: preregistration vs. docstring PREDICATE — bound

Character-level diff (`out/K2Predicate/predicate-char-diff.txt`, artifacts `prereg-*.txt` / `docstring-*.txt`):

- C1: identical except (a) 11 positions where the docstring's 80-column wrap replaces a space with `\n`, (b) the docstring ends the sentence with `;` where the preregistration has no trailing punctuation (`...is a registry row` vs `...is a registry row;` — docstring line 81 continues the enumeration `bind=1 …`). No wording drift.
- C2: identical except 8 wrap newlines. No wording drift.

The binding claim "PREDICATE (same sentence in the preregistration)" holds at sentence level for both counters.

## 2. Leg lines vs. docstring Output sections vs. preregistration targets — bound

- C1 docstring Output (`round54-replay-code-audit.py:95`) ≡ code's printed line (`:955–958`) ≡ all four receipts ≡ prereg C1 target. Build receipt: `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True` (exit 0); base control differs exactly at `newrow=0 … met=False` (exit 1). ✔
- C2 docstring Output (`round54-cited-path-check.py:138`) ≡ code (`:846–849`) ≡ receipts ≡ target. Build: `fixture=1 lane=1 scenarios=15/15 … undisclosed=0 bad=0 stale=0 dropped=0 met=True` (exit 0); base: `… dropped=1 met=False` (exit 1). ✔
- Exit codes match the docstrings (0 met / 1 not / 2 could-not-evaluate).
- Docstring `met =` lines (:70 C1, :127 C2) ≡ the code's `met` expressions (:954 C1, :844–845 C2) field-for-field. `anon` and `rehash` are inverted (failure-count) fields while `bound/sealedruns/coderuns/envnames/hostlibs/twopass` are success counts — asymmetric but consistent across docstring, code, target and receipts; not a drift.

## 3. Clause↔code mapping — C1

Every clause of the frozen C1 sentence has code:

| Clause | Code |
|---|---|
| replay of each of the three committed v5 b11909 receipts | `RECEIPTS` :149; per-receipt loop in `main()` :876–972 |
| archive member, two agreeing `/proc/<pid>/mem` passes vs. the counter's own once-read-once-hashed archive | `Archive` :444–465; two `code_observe(collect=True)` passes `:709–714`; snaps compared `:714` |
| server implementation, ggml, ggml-base, a ggml CPU backend among them | `REQUIRED` :151; enforcement `:570–573` |
| root-owned host file whose basename is in the frozen host set | host branch `:543–566`; `HOST_LIBS` :140–143 |
| the sealed memfd image | `sealed_exe` :579–611 (memfd link, nlink 0, seals ⊇ 15, frozen digest); memfd-by-dev/inode check `:518–523` |
| server carries no LD_PRELOAD | `env_leg` :429–440 |
| every observed archive path still hashes to its member after the replay exits | re-stat/re-hash loop `:770–783` |
| rerun receipt records each member mapping with dev, inode, digest; replay names them verified | `:752–766` (`code_mappings` entries `:762–764`, `own_code.verified` + `own_code.members` `:765–766`) |
| every round-52 bind and sealed check still holds | `bind_one` :677–828 (replay exit/match + rerun-receipt cross-checks `:724–748`, post-exit liveness `:783–785`, bind detail `:805–807`); sealed checks in `sealed_exe` :579–611 |
| killing the replay's invoker removes the whole tree within 30 s | `teardown_leg` :831–861, `KILL_WAIT = 30` :153 (process tree + port; "tree" in the round-52 lineage sense — receipt: `teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`) |
| git-environment source row is a registry row | `newrow_leg` :863–873 — see Finding C1-F3 |

## 4. Findings

### C1-F1 (drift, code without clause — material): named kernel mappings are a fourth admitted executable-mapping kind

The frozen sentence (preregistration.json:18, docstring `round54-replay-code-audit.py:72–80`) claims exhaustively: "every one of whose executable mappings is either an archive member … or a root-owned host file … or the sealed memfd image" — **three** alternatives. The code admits a **fourth**: a bracketed kernel mapping whose name is in `KERNEL_MAPS = ("[vdso]", "[vsyscall]", "[vvar]", "[vvar_vclock]", "[vvar_boot", "[uprobes]")` (:144) is silently skipped at `:502–504` ("a named kernel mapping such as [vdso] is the kernel's, not the process's"). Every honest server maps `[vdso]` r-xp — evidence: `grep -n vdso /proc/self/maps` → `230:7f9e92a2c000-7f9e92a2e000 r-xp 00000000 00:00 0  [vdso]` (saved as `out/K2Predicate/vdso-evidence.txt`) — so the frozen three-alternative sentence is literally false on every passing run, and the docstring internally contradicts itself (its own leg text (iv) at :56–63 says "every executable mapping is classified: … or a named kernel mapping ([vdso], [vsyscall])"). The kill rule binds `met=True`, so this does not threaten the round's verdicts; it is a calibration defect in the bound sentence.

Smallest safe correction (next freeze, both files): append a fourth alternative to the sentence, e.g. "… or the sealed memfd image, the named kernel mappings ([vdso], [vsyscall]) excepted".

### C1-F2 (drift, code without clause — minor): `DYLD_INSERT_LIBRARIES`

Frozen sentence: "the server carries no LD_PRELOAD". Code checks `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` (:146) at `:437–439`, and the receipt's own detail line says "none of LD_PRELOAD/DYLD_INSERT_LIBRARIES". The docstring leg (v) (:64–66) names both; only the frozen sentence names one. Practical impact ≈ nil for the counter-launched replay (its env is built from the `PASS_ENV` whitelist in `prepare_env` :615, so `DYLD_INSERT_LIBRARIES` can only appear if the frozen replay tool sets it), but the sentence and code differ.

Smallest safe correction: "carries no LD_PRELOAD (and no DYLD_INSERT_LIBRARIES)".

### C1-F3 (drift, clause weaker than code — moderate): `newrow` checks novelty, the sentence says mere registry membership

Frozen sentence: "the git-environment source row is a registry row". Code (`newrow_leg` :863–873): `new = rows(tip) - rows(BASE)`; `hit = [ln for ln in new if GITDOC_URL in ln]`; `return bool(hit)` — the row must be **new since BASE**, not merely present. Receipt evidence of actual semantics: `detail: newrow: 2 rows new since base; 1 name the git environment doc: ['| S511 |']` (measured/c1-build.out:23). A tree in which the S511 row already existed at BASE would print `newrow=0, met=False` while the frozen clause ("is a registry row") holds — the preregistration's own C1 prose and target encode the stricter "newrow" identity, but the bound sentence does not.

Smallest safe correction: "… and a corpus/SOURCES.md registry row naming the git-environment source row is new since the base".

### C2-F4 (defect, clause with no code — the strongest finding): `superseded`'s "live base citation" is never checked for resolution

Frozen sentence (preregistration.json:30): "`superseded` rows disclosing a **live base citation** re-pointed to a cited, resolving replacement". Docstring class text (`round54-cited-path-check.py:96–104`): "the original token was cited in that surface at --base **and resolved there** (unlike `fixed`, which corrects an UNRESOLVED citation …)". Code (`check_row`, :461–479) checks only that the token was **cited** at base — `base_citelines` is `citation_lines()` (resolution-blind, :289–298) — and never that it **resolved** at base. The sibling `fixed` class does check base resolution (`tok not in base_unres` :429) and the same base line (:430–444); `superseded` has neither.

Counterexample (driver + output: `out/K2Predicate/superseded-counterexample.py` / `.out`; fixtures built in scratch, read-only import of the frozen counter):

- **dead-base**: base cites `` `tools/dead.py` `` (never exists ⇒ unresolved at base); tip re-points to `` `tools/new.py` `` with a superseded row → counter prints `met: True {'bad': 0, 'stale': 0, 'dropped': 0}` — the row is accepted and the drop exempted, contradicting the frozen sentence (the base citation was not live). The honest control (**live-base**) also prints `met: True`, as intended — the instrument cannot tell the two apart.
- **line-bypass**: dead base token + replacement cited at a *different* line + superseded row → `met: True`; a `fixed` row over the same shape fails (`bad: 1` — stem check first). So via `superseded` a correction can dodge the M15 same-line binding that `fixed` enforces.

Why the round's measurements still stand: the lane's real superseded row (`registry/cited-path-corrections.tsv` at 9c60eae: `SCORECARD.md  corpus/lessons/round-52-verifier-spotcheck.md  superseded  corpus/lessons/round-53-verifier-spotcheck.md`) has a genuinely live base token — SCORECARD.md:18 at BASE 0b75a84c cites the round-52 spotcheck, which resolves at that commit — and the fixture's honest superseded scenario uses a resolving base token, so neither verdict is falsified. But the frozen sentence overstates the instrument, the forged half of the fixture scenario (replacement not cited at tip → bad) does not cover the missing check, and the class can be used to slip a dead-base re-point (including one away from the base citation line) past the ledger.

Smallest safe correction: in `check_row`'s `superseded` branch add the mirror of `fixed`'s base check — e.g. reject when `base_unres` is available and the token was unresolved at base (`if tok in base_unres.get(surf, set()): return "superseded token was not a live citation at base"`), and add a fixture scenario pinning the dead-base-forged verdict.

### C2-F5 (observation, minor): the blanket "re-derives from git history" over-generalizes two classes

Frozen sentence: "a correction-ledger row whose class the counter re-derives **from git history**". Of the nine classes, `externalized` re-derives from the tip surface text (:444–460) and `untracked` from the fleet disk (:574 ff.), not from git history. The docstring class list describes each check faithfully; only the frozen sentence's blanket phrase over-claims.

### C2-F6 (observation, minor): `fixed`'s "stem and line" binding has an unstated inheritance exemption

Frozen sentence: "`fixed` rows bound to the original stem and line". Code: rows already present in the BASE ledger (`inherited`, :413) skip both the base-unresolved check and the same-line check (`if not inherited:` :424–443); the exemption exists only in a code comment (:425–427), not in the frozen sentence or the docstring class text. Direction is conservative (less re-checking of append-only-inherited rows), but the sentence and code differ.

## 5. Checked and bound (no drift)

- Preregistration predicate ≡ docstring PREDICATE modulo wrap/punctuation (§1); counter sha256s match preregistration (§Evidence).
- All four receipts' leg lines match the docstring Output sections and the preregistration targets field-for-field (§2).
- C1: required-member set, host-set enforcement, sealed-image dev/inode identity, two-pass agreement, post-exit re-hash, receipt dev/inode/digest + `verified` naming, bind/sealed round-52 lineage, teardown, and the `met` expression all bind (§3). Mechanism-only code beyond the sentence (ROW_CAP 64 MiB :145/:524–531, beyond-member-end :528–531, descendant gate :701–703, sitecustomize canary `:613–628`) is safety framing of the observation, documented in the docstring Legs; noted, not counted as drift.
- C2: three surfaces, frozen fence-aware parser (`citations` :315–340), lane-then-fleet resolution (`resolve` :371–381), all nine classes re-derived (`check_row` :402–583), upstream pins (full 40-hex ref, frozen owner/repo, surface-stated digest with pin fallback :517–566), `fixed` stem+line for new rows (:410–443), bad/stale/dropped legs (`evaluate` :610–638), fifteen fixture scenarios (`SCENARIOS = 15` :168; `fixture()` :673–810 with the case table from :700 and the round-55 superseded honest/forged pair) — all bind.

## Notes

- Tools: no installs or upgrades were needed (nothing installed).
- All fixture git repos were created under `/fast/scratch/hyaku/kama-r55/w1/K2Predicate` with `git init`, identity `fx <fx@invalid>` passed per-command via `-c`-style env, and `rev-parse --show-toplevel` asserted equal to the fixture dir before the first commit; scratch removed on completion. No lane/fleet file was written; counters used read-only.
- Artifacts in `out/K2Predicate/`: the four cited receipts, the extracted predicate sentences, `predicate-char-diff.txt`, `vdso-evidence.txt`, `superseded-counterexample.py`, `superseded-counterexample.out`.
