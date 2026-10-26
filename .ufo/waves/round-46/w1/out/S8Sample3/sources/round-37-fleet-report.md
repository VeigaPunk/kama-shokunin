# kama round 37 report

author: kama L1, round 37
date: 2026-10-25
base: 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea
lane tip (landed): `e97ce4964b177a5f0473642032a239319cafc593`
claim measurement commit (landed): `e97ce4964b177a5f0473642032a239319cafc593` (C1 and C2 both measured at this tip; after-receipts landed at `8a2d08e618ee3a45a89281142bff8f61ebbffe6c` and fixes at `de16b62d26c1e13d29ed8a018c212ecc9c6fd497`/`e97ce496…`, all ancestors of the cited tip)
Stale-lane: the lane's working copy is still parked on the five foreign-identity commits (r36 L0 open); this round's commits were made through `jj-lane.sh` in a scratch clone of the lane remote (`/tmp/kama36-clone`), and the lane's branch was advanced by the helper's push.

## Work performed

Claims this round (both hold their numeric axis reading; the measured deltas are the falsifiable evidence):

- **C1 (calibration 7 → 7, delta 0)** — the four r36-spotcheck routed statements are corrected by append in `corpus/lessons/round-37.md`: R36-D1 (census receipt committed), R36-D2A (S371 native_api miswritten), R36-D2B (http_server.py S364/S365/S377/S396), R36-D3 (ScribeLog/RevQ206 429). Counter: `tools/round37-statement-audit.py`; control `c1-noop.out`; receipt `c1/after.out`.
- **C2 (coverage 9 → 9, delta 0)** — the round-37 coverage block names the three admitted entries; all three exist; each cites an S-id present at the tip and absent at base. Entries: `knowledge/kv-cache-reclamation-models.md`, `knowledge/prefix-cache-reuse-models.md`, `knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`. Counter: `tools/round37-coverage-audit.py`; control `c2-base.out`; receipt `c2/after.out`.

## Landed changes

| Change | LOG section | Commit |
|---|---|---|
| r36 corrections (census receipt + four lesson rows), three knowledge entries, seven registry rows (S330/S333/S334/S335/S346/S347/S363), README coverage block, KQ46, SCORECARD/LOG round sections | round 37 | `09b4d36e805763f911ddf8e032b9e288f38ff5b9` |
| c1/c2 after receipts at the measured tip | round 37 | `8a2d08e618ee3a45a89281142bff8f61ebbffe6c` |
| S334 quote attribution fix (kv entry), amendment conclusion narrow (prefix amendment) | round 37 | `de16b62d26c1e13d29ed8a018c212ecc9c6fd497` |
| KQ46 hardened wording per ReviewQuality | round 37 | `e97ce4964b177a5f0473642032a239319cafc593` |

`PROVINCE.md` and `SKILL.md` unchanged at the lane root (`git diff` empty versus base). `SCORECARD.md` is a pure addition (`git diff --numstat <base> <tip>` → `N 0`).

## Before → after measurements

- C1: base `uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False` (exit 1, `controls/c1-noop.out`) → tip `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True` (exit 0). Command: `python3 tools/round37-statement-audit.py --repo <fresh clone> --tip e97ce4964b177a5f0473642032a239319cafc593`.
- C2: base `named 0 files_exist 0 cited_new 0 met False` (exit 1, `controls/c2-base.out`) → tip `named 3 files_exist 3 cited_new 3 met True` (exit 0). Command: `python3 tools/round37-coverage-audit.py --repo <fresh clone> --tip e97ce4964b177a5f0473642032a239319cafc593`.

## Sources & frontier

**Assimilation: three entries, seven rows, one theme.** The read-only shokuknow `corpus-expansion-1` package was read, never written. Theme: engine internals that shape what a served endpoint answers — KV-cache reclamation and prefix-cache reuse models in vLLM and SGLang.

- Admits (all opened by this lane 2026-10-25 and re-opened by wave-1 seats; URL + access date + ≤25-word located quote in the lesson Gate): S330 (vLLM V1 guide — unified token budget, chunked prefill default, `--scheduling-policy`), S333 (SGLang radix eviction policy — evictable leaves, lowest score first), S334 (SGLang session-aware radix cache — soft protection, not memory pins), S335 (SGLang paper — reference-counter-zero evictability, LRU leaves), S346 (community source map — tier B, never A), S347 (vLLM v0.9.0 prefix-cache design — hash-based blocks, full blocks only, SHA256 advice), S363 (vLLM v0.32.0 line — sha256 default as of v0.11, `--prefix-caching-hash-algo`).
- Rejects (with flip conditions in the lesson Gate): `hosted-health-route-configuration-amendment-2026-10-23-r4.md` (remote-platform deployment field; kake's province), `openai-compat-host-vendor-contracts.md` (remote cloud-hosted vendor contracts), `cross-literate-endpoint-venues.md` (Eastern-literature spine on hosted venues; S346 carved out and admitted).
- Id collision: registry 203, staged 142 (S325–S458), collisions **0** (`comm -12` empty). Guard proven able to fail on the indented-row fixture (`  | S330 |` → collision caught). Renumber map: none required — each adopted id follows its document, never arithmetic.
- Quarantine hand-check (register not edited): seven kama rows (S200/S202/S206/S210/S211/S224/S230), verdicts agree 7/7 with round 36 (S202/S206/S230 present; S200/S210/S211 absent; S224 quote-not-located); no register row appended.
- Validate-before-append: mirror `validate --file` exit 0 with 93 pre-existing W04 warnings and no E finding; rows parsed as 11 cells (NF=13), no literal/escaped pipes, enums valid, community never tier A. Receipt: `.ufo/waves/round-37/w1/out/ExecValidate.md`.

## Trend verdicts

- **expansion — improved.** Three knowledge entries on ground the base map did not hold (README base lacks radix/prefix-cache/reclamation/eviction rows; nearest is llama.cpp `context-capacity.md`), seven registry rows, one coverage-map pointer, one new criterion KQ46. Bounded: documentation-and-source reading of two engines, not a live sample (each entry's "Does not establish" section discloses this).
- **quality — improved.** The four r36 routed statements now carry append-only corrections that the C1 counter re-derived from committed bytes; both pinned r36 blobs unchanged; the append passed the scratch census gate before landing; KQ46 lands as the criterion for the id-drift class. Counter-evidence noted in the wave: C1's D2A has no forbidden-id list and D2B's `rc=1` count is substring-based (CriticC1Sound, MutD2, MutD3), and C2's `cited_ids` is a bare regex (ReviewQuality) — the rounds are held on the frozen predicates as declared (ReviewC1Predicate/ReviewC2Predicate verified byte-identical freeze), and the over-credit probes were reported, not fixed, because the predicates are frozen. KQ46 is the follow-up instrument.
- **discernment — improved.** All seven sources were opened by both the L1 and at least one seat with byte counts and sha256 sums; per-claim claim-vs-source checks ran (ReviewS330Claims, ReviewSGLangClaims, ReviewPrefixClaims); the sibling-overlap scan (ConnSibling) confirmed kama holds the answer-shaping slice and the integrator owns the rest. Four staged rejects stand with reasons and flips. Withheld: C1's row-shape legs are weaker than their wording (documented in wave reports).

## Wave evidence

Wave 1 (37 seats, v1, policy band 32–64): reviewer 10, scout 10, critic 5, scribe 4, mutation-tester 3, executor 3, connector 1, revenger 1. Spec/run/out under `.ufo/waves/round-37/w1/` (all committed). Seat accounts: 37/37 returned reports. Dead seats: none — the two rc=1 seats of the r36 wave-3 (`ScribeLog`, `RevQ206`, `provider.rate_limit: 429`) are the D3 correction named in the lesson and here; the r36 report's wave table accounted for 30 of 32, these two are the missing pair (their exact last error text: `error: failed to run prompt: provider.rate_limit: 429 Rate limit reached for requests` + `See log: /home/vgpnk/.kimi-code/logs/kimi-code.log`). Residual: no wave 2; wave 1 covered the round's 1–3 claims.

## SHONEN

- [~] SKILL.md decision tables, error patterns, checklists, cited sources — Author assertion; no named non-author verifier this round (unchanged).
- [~] At least one end-to-end domain task executed and logged — round-16/17 live receipts stand; this round is documentation-and-source; no non-author mark.
- [~] Instructions executable by an agent without oral context — independent execution review remains open.
- [~] No cross-domain bleed (PROVINCE.md still accurate) — unchanged; the sibling-overlap scan ratified the boundary; service repair, routing and credentials remain operator/sibling-owned.

## Tools

No tool was installed or upgraded this round; the pacman guard (all pacman transactions paused host-wide) was carried in every wave context and no seat ran pacman. No `[x]` SHONEN line is written; promotion stays operator-owned.
