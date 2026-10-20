VERDICT: confirm — C1/C2 instruments are lane-local; only the wave-provenance record and the verdict vocabulary cross into kumitate, and kama touches both read-only.

# Axes

operability + calibration (calibration 7, the lowest). Everything below targets calibration; nothing below requires a runtime change, a port, or an edit to a frozen file, so operability is untouched by construction.

# Contested scope (three seams, each already half-crossed)

**S1 — the wave dispatch record.** kama's round-17 wave was produced by kumitate's script, not by lane code: `kama-shokunin/.ufo/waves/round-17/build/validation.json:2-8` records argv `node .../ufo-swarm-wave.mjs run --spec ...`, and the payload is schema-tagged `"schema": "ufo-swarm-wave-dispatch-v1"` (`build/dispatch.json:2`). The format authority is kumitate's (`kumitate-shokunin/SKILL.md:37-45`: the producer "persists, in ONE critical section, the pair `swarm-registry.json` + `swarm-dispatch.json`"). kama's *wrapper* records next to it carry no schema at all: `build/validation.json:19-23` starts at `"canonicalization"` / `"counts"` with no `"schema"` key. That is a read-side observation artifact, and it must stay named as one.

**S2 — four distinct "verdict" vocabularies now coexist.** (a) seat advice first line, which this very wave mints: `add("VerdictCounter", ...)` (`kama-shokunin/.ufo/waves/round-17/build/make_spec.py:114`) classifying `VERDICT: confirm|partial|refute|n/a`; (b) kumitate's hermetic-suite line `VERDICT: PASS` (`kumitate-shokunin/SKILL.md:619-630`); (c) the fleet closure record `"verdict": "admitted"|...` plus `"verdicts": {"<axis>": "<verdict>"}` (`shokunin/scripts/hyaku/closure-prompt.md:63-66`); (d) kama's probe verdicts `MODEL_OK`/`MODEL_MISMATCH` as graded at `kama-shokunin/tests/probe-verdicts/check.py:341`. Only (c) is a judged fleet verdict; kumitate states the rule that separates them: "Need a verdict? Only the native judged round produces one. Swarm output and" (`SKILL.md:25`), and "Swarm lanes NEVER enter a `NativeRoundHandoff`" (`SKILL.md:18`). A lane counter may count (a); it must not emit anything a consumer could read as (c), and it must shard (a) from (b) by name.

**S3 — counting convention is borrowed, instrumentation is not.** kama's own province line already draws the boundary: "**Refuses:** … dispatch/route mechanism (kumitate)" (`kama-shokunin/PROVINCE.md:40-41`), and "Out of province → report, never absorb" (`:51`), while the adjacent list names this lane the serving owner in the other direction — "Local model serving and endpoints → kama" (`kumitate-shokunin/PROVINCE.md:27`). So the round's counting scripts may *read* kumitate artifacts and must not become dispatch code. C1's `mutants.py`, C2's `controls.py`, `count-verdicts.py` and `dispatch-provenance.py` are all "counting commands" under kumitate's admission rule: "every count carries its counting command and a dated re-run" (`QUALITY.md:23`) and per-identity, not aggregate: "reads MATCH on the strict/row check, not just the aggregate" (`QUALITY.md:36-37`). The rule is importable; no kumitate instrument is.

# What kama must hand off rather than absorb

1. **Any verb/schema change to `ufo-swarm-wave.mjs` / `ufo-swarm-collect.mjs`.** Those sit in kumitate's gated origin layer (`kumitate-shokunin/PROVINCE.md:12`). Two gaps are kama's to *report*, not fix:
   - `taskCall_sha256` + its canonicalization are lane-invented (`kama-shokunin/.ufo/waves/round-17/build/validation.json:19`). Read-only check today: `grep -n "taskCall_sha256\|canonicalJson" /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs` → no match, so the digest is not part of the produced dispatch schema. Keep it `kama-*`-prefixed and supplementary; if it proves worth having, file it upstream.
   - The first round-17 attempt was refused by the host, not the lane: `build/attempts.json:5-8` — `"result": "refused"`, `"refused": 82`, `"error": "Background job limit reached (100)"`. Fleet tooling already documents this class: "a `task` call is refused while >= cap jobs run" (`shokunin/scripts/hyaku/await-capacity.sh:2-4`). kama's configured band is 64–100 (`build/validation.json:42-45`), inside kumitate's 16–100 spawn band (`SKILL.md:18`), but the host cap is shared with co-running fleets; kama must not encode a lane-level retry policy, and kumitate should name the interaction (its table has no row for it). [INFERENCE: whether this belongs in the dispatch-shape table or in `hyaku` docs.]
2. **Mutation-battery naming.** The fleet already has one: "`gates` (ParetoGate mutation battery)" (`SKILL.md:306`). kama's `mutants.py` must be presented as a lane-local detector score, never as that battery (tameshi owns methodology; this is the naming collision only).
3. **Counter vocabulary.** spawn/resume/attempt naming is fixed fleet-wide: "Four counters never to conflate: `attempts` … `resumeAttempts` … `launchMisses`" (`SKILL.md:139-149`). kama's ledger may add `spawned`/`refused` but must not let `spawned` absorb resumes, and should not mint a sixth name for the same idea.
4. **`.ufo/state/` and `registry/history/.lock` ignore hygiene** (frontier item, jj audit). The lane may add its own `.gitignore` lines; the fleet-wide answer to "which `.ufo/` paths are ignored" is not kama's to set. [INFERENCE: split between kumitate and mado; the mado connector owns the jj wording.]

# Reusable conventions (import as rules, not as code)

- **R1 — exit map.** `0` clean, `1` failed, `2` fail-closed, `64` usage; "`2` (fail-closed) and `64` (usage) → could-not-evaluate" (`SKILL.md:593-594`). kama's `check.py` already uses 0/1/2 (`tests/probe-verdicts/check.py:26-27`) and lacks 64; C2's planned "internal fault, exit 2" lands exactly on the fail-closed arm.
- **R2 — fault vs finding.** "Exit 2, or no verdict line at all, is a tool/environment fault: fix the tool, not the claim" (`SKILL.md:632-633`). This resolves C1's malformed-output question cleanly and *keeps* the split `check.py` already makes: unparseable *probe* output is a subject failure recorded per row (`check.py:332-336`), while a stub bind/exec failure is `HarnessError` (`check.py:479-480`). Do not convert either into the other.
- **R3 — no fabricated zeros.** "`opaque`/`unavailable`/`null` mean \"evidence absent\" — never fabricated zeros" (`SKILL.md:99-100`). Live counter-example in this lane: the round-16 ledger stores `"parseable": true` with `"spawned": 0` (`kama-shokunin/.ufo/waves/round-16/falsify/provenance-ledger.json:51-56`) because the extractor recognized no member rows. That is a recognition failure presented as a measurement. Fix shape: non-empty unrecognized result → `null` plus a typed reason.
- **R4 — bidirectional bijection.** "every dispatch member needs exactly one result row (`unmapped_member`), every result row needs a member" (`SKILL.md:60-61`). `count-verdicts.py`'s `--expect-names` only reports *missing* names per its spec (`make_spec.py:114`); without *extra* names the 36/41/2-vs-36/43/0 defect recurs one level up.
- **R5 — revision beside the count.** "no verdict line names the revision it measured — cite the commit beside the verdict instead" (`SKILL.md:607-609`). Every JSON count in this round should carry the lane tip (`git -C kama-shokunin rev-parse master`) that it measured.
- **R6 — pin in validators, single-source vocabularies.** These two rules look opposed and are not: "Vocabularies are single-sourced; … never restate a second copy" (`SKILL.md:423-424`) vs the checker that pins its expectations internally — "frozen member set + family counts inside the script" (`SKILL.md:604`). Applied to C2: the v2 check-id set belongs pinned in `tests/llamacpp-live/check-receipt.py` (the existing `REQUIRED_CHECKS` pattern at `:53`), *not* imported from `tools/kama-llamacpp-live.py`, or a tool edit silently redefines the gate. The values a check compares (e.g. the ready body literal) should still come from one place.
- **R7 — schema-tagged, refuse-to-clobber artifacts.** kumitate's producer publishes a tagged pair (`SKILL.md:41-45`); kama's own ledger already refuses an unknown schema (`kama-shokunin/.ufo/waves/round-16/dispatch-provenance.py:114-116`, ledger tag at `provenance-ledger.json:59`). Round-17's `build/attempts.json:1` is a bare array — a regression against the convention the lane itself used last round.
- **R8 — exported, not absorbed: the "two evidences" pair.** kumitate names as an own gap: "no gate yet ships the §Gate standard \"two evidences\" frozen-snapshot run with a digest-pinned expected-verdict file" (`SKILL.md:607-608`). C1's frozen-vs-current pair is precisely that pattern. kama should export the shape in its report; kumitate owns any adoption.
- **R9 — a validator refusal is fixed, never bypassed.** The fleet closure helper states it outright: "A refusal from the helper is fixed, not bypassed" (`shokunin/scripts/hyaku/closure-prompt.md:72`), and it validates enums at write time (`append-closure.py:21` `TREND_VERDICTS`). Applies to C2's `controls.py` and C1's `mutants.py`: a mutant that will not apply, or a control whose fake server will not bind, is a runner fault to fix (exit 2), never a silent skip that shrinks the denominator.

# Proposed move (one, bounded)

**Give all four counting surfaces of this round one envelope and one rule for when a number may be printed.**

Envelope keys, identical across `c1/mutants.py`, `tests/llamacpp-live/controls.py`, `build/count-verdicts.py`, `build/dispatch-provenance.py`:
`{"schema":"kama-<name>/v1","command":[…],"revision":"<lane tip before/after>","subject":{"path","sha256"},"members":{"expected":n,"observed":n,"missing":[…],"extra":[…]}, "counts":{…},"nulls":[{field,reason}],"exit":n}`.

The rule that carries the calibration gain: **a count is printed only if `members.expected` is known and `expected == observed + missing`; otherwise the count is `null` with a typed reason.** So C1's "survived" is a fraction of a *named* mutant set, C2's `accepted_bad` is a fraction of K1–K7, `count-verdicts.py` totals are a fraction of `spec.json` items plus extras, and the provenance ledger's `spawned` is a fraction of the registry's members — never a bare numerator.

Why this is the non-obvious move: the four items were specified with four unrelated JSON shapes, and the failure each can still commit is the same one round 16 committed (55/17 vs 72/0 — a denominator that moved while the numerator was quoted). The cheapest fix is not a new gate or a shared library; it is one shape plus one honesty rule about when a count exists. It improves calibration directly, and it cannot harm operability: no runtime path, no port, no frozen file, no kumitate file is touched.

# Risks

1. **Envelope misread as a gate.** Keep counts at exit 0; only C2's control suite exits 1 on `accepted_bad > 0`, and 2 means could-not-evaluate (R1). Otherwise the counter becomes another gate that can overclaim.
2. **Revision captured too late.** Read the lane tip before and after the run; unequal → `revision: null`, not the later value. [INFERENCE: mid-run commits are unlikely in this lane but cheap to detect.]
3. **Additive-only.** `round-16/measure.py` consumes `check.py`'s `parsed` document (`measure.py:15`); new keys are safe, renamed keys are not. Same for v1 receipts: `check-receipt.py:53` must keep the v1 tuple intact.
4. **Self-fulfilling expectations.** The mutant list and K1–K7 list must predate the run; the frozen copies (`round-17/frozen/manifest.json`) give C1 that property, C2's controls do not yet have it.
5. **Quoting risk for L1.** `--expect-names` must be non-optional whenever `spec.json` is in scope, or the count is still unauditable by omission.

# Verification (advice; L1 runs the official numbers)

- `python3 .ufo/waves/round-17/c1/mutants.py --json` → `members.expected` equals the mutant set size; `counts.survived` for frozen-vs-frozen detector is unchanged; `revision` present.
- `python3 tests/llamacpp-live/controls.py --json` → `members.expected == 7` (K1–K7), `accepted_bad == 0`, `good_ok true`.
- `python3 .ufo/waves/round-17/build/count-verdicts.py .ufo/waves/round-16/falsify/advice --expect-names <names.json> --json` → observed 79, 5 nonconformant, 0 extra (scratch check I ran: 79 `.md`, 5 first lines not starting `VERDICT:` — *advice only, not the official count*).
- `python3 .ufo/waves/round-17/build/dispatch-provenance.py` ledger → the refusal attempt is a row (`refused 82`, `spawned null`, reason) and is not folded into the successful `spawned 82`.
- No-harm: `python3 .ufo/waves/round-16/measure.py` still verifies the frozen manifest and matrix set digest; both round-16 v1 receipts still validate.

# Limitations, installs, disclosure

- Read-only seat: I ran no lane gate, no official measurement, no mutant/control run; the only numbers above are scratch `ls`/`grep`/JSON parses labelled as such.
- [INFERENCE] on the kumitate/mado split for `.ufo/state/` hygiene, and on whether kumitate wants `taskCall_sha256` upstream; both are framed as reports, not patches.
- Privacy disclosure: one recursive grep in the kama root omitted `--exclude-dir=interactive-sessions` and its output included three lines from `.ufo/interactive-sessions/…jsonl` (echoes of origin script text). I did not use them, opened no session file, and did not repeat the pattern. L1 should treat that as a bound violation by this seat, not by the lane.
- Installs: none. No pacman/uv/npx channel was used.
