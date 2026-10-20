# TemporalRisk — round-11 verification: nine legacy provenance supplements (C1, calibration)

Seat: `KamaR11.TemporalRisk` (critic, leaf). Advisory only, NOT an outside non-author review.
Review time: `date -u` → `2026-10-20T03:44:19Z` (round label stays the steered 2026-10-19).
Axis authority: `../shokunin.conf:52` → `kama|kama-shokunin|operability + calibration`.
Write set: this file only. No implementation, corpus or fleet file was edited.
Installs/updates: **none**. I read `~/.omp/agent/RULES.md`; no tool was needed.

What I ran (read-only evidence, not acceptance checks):
- `git diff`, `stat`, `date -u`, `ls`.
- A stdlib Python sha256 prefix comparison against `legacy-baseline.json`.
- Telemetry key reads.
- A one-line `sed` syntax demonstration on empty input.
- A fetch of one public document (the pinned S001 README).

I did not run `measure.py`, `kama-probe.sh`, `test-snapshot.sh`, builds, lint or formatters. No endpoint, listener, host config or service was contacted.

## Axes
1. **Calibration**: dates, confidence and authority are honest. No metadata review reads as revalidation or authorization.
2. **Operability**: the recheck paths can run and do not damage their own evidence.
3. **Integrity**: original byte prefixes are preserved.

## Verdict

No supplement claims live revalidation. All nine separate the original observation dates from the 2026-10-20 metadata review, and all nine state that no endpoint was contacted. **The 27 → 0 metadata count is honest as calibration and is not a freshness refresh.**

Two kinds of residual overclaim remain:
- **Present-tense state wording.** Three spots imply a current host or endpoint state that round 11 never observed (T1, T2, T3).
- **Authorization or tool wording.** One spot calls a recheck "authorized" when its admissibility is contested (T4). One recheck mutates the tracked evidence it cites (T5).

There are also two broken or false pointers in recheck/source fields (T6, T7). Every item has a small wording fix. None needs a score change or a re-derivation.

## Integrity evidence (observed)
- All 9 files keep their original prefix. `sha256(data[:bytes]) == baseline.sha256` is **True** for all nine.
- In every file, the supplement starts with `\n## ` right after the original extent.
- `listener-census.md` starts its supplement with `\n\n##`. This handles the missing-final-newline trap (AttackFreshness F5).
- Write times (mtime): 2026-10-20T02:15:59Z–02:24:07Z UTC. Each seat's `date -u` reading was 02:14:19–02:14:56Z (advice files). So `02:14Z` is when each review **started**, not when the supplement was written. This is not an overclaim at date precision (see L1).

## Findings (overclaims and defects)

### T1 — `served-model-identity.md:41`: "retired since" asserts current state on the wrong evidence (MEDIUM, calibration / false provenance)
**Quote:** "against the then-live 127.0.0.1:34113 llama.cpp server, retired since the 2026-10-14T12:42:32Z snapshot (`registry/history/DELTA.md` systemd-qwen-coder row-absent)".

1. **"Retired since" claims continuity up to now.** Round 11 did not observe 34113, so that continuity is unsupported.
2. **The cited row does not show a retired server.** `DELTA.md:20` `systemd-qwen-coder row-absent` records a *registry row deletion*. `LOG.md:228-230` explains the cut: "Registry cut 11 → 3 rows: the eight consumer files no longer exist … deletion recorded as 16 transitions". The evidence that the server was down is elsewhere:
   - `DELTA.md:9-14` (`ufo-fsd-thetick` / `ufo-fsd-local-helper` on 34113: `MODEL_OK -> DEAD`, `connection-refused`);
   - `LOG.md:245-246` ("`qwen-coder.service` is inactive and its unit deleted; ports 34113 and 8080 both refuse connections").

**Smallest repair:** "…observed connection-refused at the 2026-10-14T12:42:32Z snapshot (`registry/history/DELTA.md:9-14`; unit deleted per `LOG.md:245-246`); current state not re-observed in round 11."

### T2 — `drift-timeline.md:34`: the recheck presumes the answer (LOW-MEDIUM, calibration)
**Quote:** "`DEAD`/`connection-refused` is the expected reading while nothing listens, per `registry/history/latest.tsv:2-4`".

`latest.tsv` is the 2026-10-14 snapshot (`#@snapshot_id 20261014T124232Z`). "While nothing listens" states as current fact something nobody has observed since then. That primes a future checker to read a DEAD result as confirmation rather than as new evidence.

**Smallest repair:** "the last tracked reading (2026-10-14, `latest.tsv:2-4`) was `DEAD`/`connection-refused`; any new reading is new evidence, not a confirmation."

### T3 — `consumer-registry.md:393`: "not live files" (LOW, calibration)
**Quote:** "Host-side row targets (#1–#16, #35; relocated/deleted trees) are historical record only, not live files."

The deletions were recorded 2026-10-14 (`LOG.md:245-255`), and round 11 did not re-check them. The sentence can be read as a present-tense statement about the filesystem.

**Smallest repair:** "…recorded deleted/relocated as of 2026-10-14 (`LOG.md:245-255`); not re-checked in round 11."

### T4 — `drift-timeline.md:34`: "current authorized revalidation is the lane's own read-only probe" (MEDIUM, authorization overclaim)
1. **"Authorized" is unsupported.** The supplement says the probe is currently authorized, but the lane's own records leave that open:
   - `corpus/SOURCES.md` S030: an L1 `kama-probe.sh check` run is **rejected** because its "admissibility under the kaika documentation-only rule is contested … flip: L0 rules lane-own registered-endpoint gate runs admissible".
   - `corpus/QUALITY.md:32` KQ10: probe commands must be inside the task's declared scope.

   No standing authorization exists. The other eight supplements correctly say "next authorized …" or "on authorization".
2. **"Read-only" is false for `snapshot`.** The same sentence pairs the probe with `kama-probe.sh snapshot`, which writes (T5).

**Smallest repair:** "revalidation, when an operator/L0-authorized probe scope exists (S030 contested; KQ10), is `bash tools/kama-probe.sh check --json` …". Drop "read-only" next to `snapshot`, or add `--history "$(mktemp -d)"`.

### T5 — `consumer-registry.md:395` and `drift-timeline.md:34`: the `snapshot` recheck overwrites the evidence the supplements cite (MEDIUM, operability / temporal integrity)
1. **`snapshot` writes to tracked files by default.** `tools/kama-probe.sh:10-22,40-45`: snapshot "additionally writes", `latest.tsv` is rewritten as the new baseline, and `DELTA.md` gets appended transitions. The default history directory is `registry/history` (`:102`).
2. **Two rechecks run it with the default.**
   - `consumer-registry.md:395` says "`bash tools/kama-probe.sh snapshot` (dated state + DELTA.md under registry/history/)".
   - `drift-timeline.md:34` says "with `bash tools/kama-probe.sh snapshot` for invocation-to-invocation drift".
3. **That run destroys cited anchors.** One run replaces the `#@snapshot_id 20261014T124232Z` header and rows that these supplements cite:
   - `drift-timeline.md:34` → `latest.tsv:2-4`;
   - `snapshot-history.md:102` → "`#@snapshot_id 20261014T124232Z`, 3 rows";
   - `consumer-registry.md:393` → `registry/history/latest.tsv`.
4. **Only one file avoids this.** `snapshot-history.md:104` offers `--history DIR`.

**Smallest repair:** In both rechecks, use `snapshot --history "$(mktemp -d)"`. Alternatively, cite the pinned copies (`git show 2f7303c:registry/history/latest.tsv`) so the anchors survive a tracked re-sample.

### T6 — `cross-lane-scope.md:85`: the "retained-metadata check" cannot run (MEDIUM, operability)
**Quote:** "re-open the drift evidence with `sed -n '23-27p' …/round-3/kagi.md` and `sed -n '18-25p' …/round-4/kengaku.md`".

`sed` addresses use a comma (`23,27p`), not a hyphen. On this host, `echo | sed -n '23-27p'` gives `sed: <script argument 1>:1:3: error: invalid command code '-'`, exit 1. GNU sed rejects it the same way.

The target ranges themselves are correct. With commas they show the drift evidence:
- `kagi.md:23-27`: "8080 is a **Jitsi videobridge** … llama-server serves the pinned Qwen3-Coder-30B model on **34113**";
- `kengaku.md:18-25`.

**Smallest repair:** `sed -n '23,27p'` and `sed -n '18,25p'`.

**Secondary (LOW):** `cross-lane-scope.md:84` records "`corpus/knowledge/consumer-registry.md` 390" as a pointer bound. After this wave that file has **395** lines, so a later `wc -l` recheck reports a mismatch. Label it "pre-round-11 count".

**Secondary (LOW):** `:85` says "a mismatch fails freshness review". The axis is calibration, and a prefix-hash match is integrity, not freshness. Say "fails prefix-integrity review".

### T7 — `snapshot-history.md:103`: wrong anchor for the baseline (LOW-MEDIUM, false provenance)
**Quote:** "baseline timestamp and 11-row count corroborated by `registry/history/DELTA.md:1`".

`DELTA.md:1` is the file header ("# kama snapshot DELTA.md — endpoint-verdict transition ledger"). The baseline line is at `DELTA.md:6` ("- 2026-09-29T04:30:44Z baseline recorded (11 rows)"). `consumer-registry.md:393` cites `DELTA.md:6-22` correctly.

**Smallest repair:** `DELTA.md:1` → `DELTA.md:6`.

### T8 — `endpoint-identity.md:155-164`: a semantic correction outside the provenance trio (LOW-MEDIUM, calibration)
1. **The content is sound.** I opened the pinned S001 README on 2026-10-20 at 03:45Z: https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md line 1256. Located quote: "The `meta` field can be `null` (for example, while the model is still loading)." The line-89 overstatement is real (`endpoint-identity.md:89`: "Gate traffic on a matching expected ID").
2. **The provenance does not cover it.** The `### Readiness terminology correction` block sits inside the provenance-supplement region, but the trio never mentions it:
   - `source:` (`:151`) lists only F1–F12 and local artifacts, not S001/S011/S012.
   - `verified-at:` (`:152`) says the review was "metadata only … re-opened read-only".

   So a claim drawn from external documentation carries a "metadata only" date and no source pin.
3. **The S011 citation is superseded.** It cites S011. S031 (`SOURCES.md`, added 2026-10-20) "supersedes S011" for the locality implication. The block's wording ("available inventory") does not claim local residency, so this is only a citation-freshness gap.

**Smallest repair:** Add one line under the `###` heading: "Source: S001 @c0fd7862 README:1256 (opened 2026-10-20 UTC); S011/S031, S012 per `corpus/SOURCES.md`; documentation only, no runtime contacted."

### T9 — `listener-census.md:387`: census scope is treated as privilege authorization (LOW, authorization)
**Quote:** "revalidation requires a future L1-declared census scope; then re-derive with … and, for the 5 ownerless §0 rows, the privileged §7 one-liner `sudo -n ss -ltnp …`".

The one-liner already exists in the original §7 (`:321`), so nothing new is invented. The risk is the wording: a declared *census* scope is presented as enough to run a *privileged* command. Passwordless sudo exists on this host (`listener-census.md:4`), so `-n` will not stop it.

**Smallest repair:** "…the privileged §7 one-liner only under explicit privilege authorization (else record `UNDECIDABLE` per KQ8)."

## Limits of this review and the gate (not defects in the supplements)
- **L1 — Shared `02:14Z` stamp.** Every `verified-at` says 02:14Z, which is each seat's `date -u` at the start of its review. The files were written 02:16–02:24Z. Date precision is correct. Minute precision overstates "actual review" slightly.
  - Optional repair: "review started 2026-10-20T02:14Z".
- **L2 — Heading dates.** Every heading reads "round 11 (2026-10-19)", the steered label, which is also the round-10 correction date. A heading-only index cannot tell round-10 corrections from round-11 supplements. Each field discloses this, so it is a tradeoff the parent accepted, not a defect.
- **L3 — `measure.py` cannot catch T1–T9.** Its `verified-at-live-claim` guard (`measure.py:126-142`) matches only literal `live revalidat(ed|ion)` followed by `today` or the run date, and only in `verified-at:`. In practice:
  - "retired since", "while nothing listens" and "current authorized" all pass;
  - `source:`, `recheck:` and `###` sub-blocks are not scanned;
  - a run on any later date misses a claim dated 2026-10-20.

  Its docstring admits this (`:50-58`). A clean `measure.py` exit therefore says nothing about T1–T9. The non-author review has to read the values.

## Already correct (keep)
- **Integrity:** all 9 prefixes are byte-preserved, with column-zero headings after the original extent. `listener-census` gets the `\n\n` guard.
- **No revalidation claimed:** every `verified-at` names its original observation dates and denies live revalidation.
  - `endpoint-identity.md:152`: "provenance-of-record only, not endpoint health".
  - `cross-lane-scope.md:84`: "presence/dates/pointer-bounds only".
- **No retired command revived as current:**
  - `drift-timeline.md:34` declares the historical rows "never replayed".
  - `served-model-identity.md:42` says "do not replay the 34113 samples above as current".
  - `alias-endpoint-normalization.md:70` refuses credential-bearing config-body reads.
- **`free-tier-provider-limits.md:73-75`** is clean:
  - the telemetry keys in its recheck all exist;
  - `recorded_utc` 18:35:08Z/18:38:06Z/18:40:17Z/18:42:06Z match;
  - 18:32Z is grounded in round-6 `wave_start_utc` `2026-10-18T18:32:33Z`;
  - the wire ids `opencode-go/deepseek-v4.1-flash-free` and `opencode-go/glm-5.3-flash-free` match `model_dispatched`;
  - the fleet reports for rounds 6–9 are present.
- **`consumer-registry.md:393`** labels `.ufo/round-10/gates/check.json` "contested admissibility, not admitted authority", which agrees with S030.
- **`snapshot-history.md:102-103`** is honest about missing evidence. Round-2 dated JSONs are not retained (only `20261014T124232Z.json` and `20261014T124525Z.json` exist). `.ufo/round-2` is absent (both confirmed with `ls`). `pass=24` is dated round-2 and is not presented as a round-11 run.
- **Cited anchors I re-opened that hold:** `LOG.md:72`, `:159-163`, `:203-255`, `:245-255`; `consumer-registry.md:100` (epoch 1788033391 row); `latest.tsv:2-4` (3 DEAD rows); `listener-census.md:321` (§7 one-liner).

## Impacted axes summary
| ID | Severity | Axis | File:line | Fix size |
|---|---|---|---|---|
| T1 | medium | calibration / provenance | served-model-identity.md:41 | 1 clause |
| T2 | low-med | calibration | drift-timeline.md:34 | 1 clause |
| T3 | low | calibration | consumer-registry.md:393 | 1 clause |
| T4 | medium | calibration (authorization) | drift-timeline.md:34 | 1 clause |
| T5 | medium | operability / integrity | consumer-registry.md:395; drift-timeline.md:34 | add `--history "$(mktemp -d)"` |
| T6 | medium | operability | cross-lane-scope.md:85 (+:84) | `-` → `,` |
| T7 | low-med | provenance | snapshot-history.md:103 | `:1` → `:6` |
| T8 | low-med | calibration | endpoint-identity.md:155-164 | 1 source line |
| T9 | low | calibration (authorization) | listener-census.md:387 | 1 clause |

**Score implications:**
- C1 provenance-field count: none. All 27 fields are present, and none of T1–T9 removes one.
- If T1/T4 are left unfixed, two values present unobserved current state or authorization as fact. KQ11 rejects that: "Field presence … alone is offered as refreshed runtime evidence."
- The repairs are append-region-only edits, so no original prefix moves. The parent owns them.
