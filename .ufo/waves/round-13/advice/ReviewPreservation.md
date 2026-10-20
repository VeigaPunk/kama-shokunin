# Round 13 — ReviewPreservation (KQ16 design vs immutable KQ15)

Seat: KamaR13.ReviewPreservation (reviewer, leaf, static). Scope: append-only KQ16
design and the immutable KQ15 criterion. Read-only apart this report.
Tools installed or updated: **none**.

## Limits of this review

- Static reads and read-only git plumbing only. **No** `fidelity.py`, `reproduce.py`,
  `--selftest`, `measure.py`, build, lint, or test was run. Receipt values below are
  recorded observations in `acceptance.json`, not new executions.
- KQ16 has landed at `corpus/QUALITY.md:61` (see Final static disposition below). The findings
  below are the pre-landing design findings; disposition is recorded per finding.
- `.ufo/waves/round-13/measure.py` does not exist yet (mid-flight).
- Advisor files are author-side; they are not independent closure.
- The false comment at `fidelity.py:55-56` is marked in the lesson; the code is not
  rewritten by this round.

## Preservation status (observed now)

| Check | Command (read-only) | Observed |
|---|---|---|
| Worktree QUALITY.md equals start blob | `git cat-file blob 941bb32:corpus/QUALITY.md \| cmp - corpus/QUALITY.md` | exit 0; both 8619 bytes, 49 lines |
| KQ15 row bytes | `git cat-file blob 941bb32:corpus/QUALITY.md \| sed -n 49p \| sha256sum` | `b559befa6bf3bbdabd00482d6a6630bbfbefdf8d4371f74d998f6e1f9c07618c` |
| Start commit lacks the two assertions | read `QUALITY.md:49` at 941bb32 | neither `source_mismatch=1` nor the capture/comparison literal present (before state) |
| Verifier lesson unchanged | `sha256sum` vs blob at 941bb32 | `ca3a91f8…03ff` both |
| `round-12.md` unchanged | `git status --short` | not modified |
| `LOG.md` append-only | `git diff --numstat 941bb32 -- LOG.md` | `28 0` (insertions only) |
| Lane status | `git status --short` | `M LOG.md`, `?? .ufo/waves/round-13/`, `?? corpus/lessons/round-13.md` |

No KQ15 byte has changed. The mistake is still visible in the file.

## Exit-map facts (static code; receipt observations)

- `fidelity.py:64-72` `PRIORITY` (highest first): snapshot_unavailable, manifest_invalid,
  snapshot_tampered, source_unavailable, **source_mismatch**, **unpinned**, clean.
- `fidelity.py:317-319`: `finding = next(fid for fid in PRIORITY if present)`;
  `exit = 0 if clean else (1 if finding == 'source_mismatch' else 2)`.
- Therefore the **primary finding** decides the exit. Exit-2 findings
  snapshot_unavailable, manifest_invalid, snapshot_tampered and source_unavailable
  outrank source_mismatch. `unpinned` (exit 2 when alone) ranks **below**
  source_mismatch, so `unpinned` + `source_mismatch` exits 1.
- The comment at `fidelity.py:55-56` ("Every exit-2 finding outranks source_mismatch")
  is false for `unpinned`. It is a historical comment; the lesson marks it.
- `fidelity.py:229-236`: a pin mismatch adds `snapshot_tampered`. `fidelity.py:295-296`
  runs the source comparison whenever snapshot bytes exist, so a tampered snapshot that
  also differs from source carries **both** findings. Primary = snapshot_tampered, exit 2.
  This is the higher-ranked tamper case: source_mismatch is still listed in `findings`,
  but the exit is 2. The selftest expectation is `fidelity.py:501-505`.
- Receipt `acceptance.json` (observations): source_mismatch exit 1 (`:148-156`,
  `:281-289`, `:461-462`); snapshot_tampered exit 2 (`:330-338`); manifest_invalid exit 2
  (`:379-387`); source_unavailable exit 2 (`:421-429`); clean exit 0 (`:196-204`,
  `:468-469`). The unpinned + mismatch case is receipt-recorded as exit 1 at `:461-462`.
- Source retrieval: `fidelity.py:272-273`, `:443-444` and `reproduce.py:80` use
  `git cat-file blob`. No code calls `git show`.

## Findings

### 1. (High) Exit map needs primary-finding precedence, not a bare literal

`source_mismatch=1; snapshot_tampered=2; source_unavailable=2` is correct only for a
single finding. The exit is decided by the highest-ranked finding present, per the
`PRIORITY` order above. Two concrete cases:

- snapshot_tampered + source_mismatch (tampered snapshot that also differs from source):
  primary snapshot_tampered, **exit 2**. The source_mismatch finding is still reported.
- unpinned + source_mismatch: primary source_mismatch, **exit 1**.

**Repair:** keep the exact literal and add a sentence along the lines of: "The exit is
that of the highest-ranked present finding in the order snapshot_unavailable,
manifest_invalid, snapshot_tampered, source_unavailable, source_mismatch, unpinned,
clean; source_mismatch exits 1 only when it is that primary finding." Do not cite the
false comment at `fidelity.py:55-56`. KQ16 stays inside proposition 1 (exit/finding
distinction), so the denominator stays two.

### 2. (High) `git show` capture is an authored-provenance boundary, not gate-checked

- SKILL.md:396 states that the default snapshot was "captured byte-exactly via
  `git show`". That is registry prose.
- No code calls `git show`. `frozen/README.md` does not exist. `frozen/expected.json`
  has no capture-command field. `Fidelity.md:37-40` records the capture as
  "generated from `git show` raw stdout", observed during generation.
- Per the accepted boundary, the capture method is authored provenance. The gate verifies
  only the `git cat-file blob` comparison. KQ16 must not make `git show` an admission
  requirement, and must not claim `git show` is byte-preserving. Byte equality is shown
  by the comparison that passed.
- The textconv/filter question for `git show` is an [INFERENCE] limit. The advisor quote
  at `AttackSourceCuration.md:27` was not reopened here. Current
  `git check-attr -a -- corpus/SOURCES.md` returns no attributes (current state only).

### 3. (Medium) Probe immutability check is not specified

`measure.py` is specified to read the start blob and final QUALITY and count literal
presence. The spec does **not** state a byte-prefix check that the start blob is a prefix
of the final file. Without it, a KQ15 edit that also adds the two literals passes.
**Repair:** assert `final.startswith(start)` (bytes), and assert the KQ15 line-49 SHA
`b559befa…7618c` is unchanged. Scope the "mistaken wording absent" check to the single
line beginning `| KQ16 |`. Either avoid repeating "distinct nonzero exits" even in
negation, or define negation as allowed.

### 4. (Medium) Supersession wording must name the error, not soften it

`QUALITY.md:3-5` says supersession names the old criterion and does not erase it. The
KQ14 precedent is `KQ14 (supersedes KQ7's sufficiency, preserves its append-only rule)`.
Words like "clarifies" would hide that KQ15 was inaccurate. **Repair:** the KQ16 heading
should say it supersedes KQ15's exit-class and capture/comparison formulations as
inaccurate, with the KQ15 row retained byte-identical. Keep the round-12 heading
"no outside review yet" unchanged; it is historical.

### 5. (Low) Stale sentences must not be copied into KQ16

- `round-12-verifier-spotcheck.md:147` says KQ15 should distinguish capture "as the lesson
  and registry already do." The registry (SKILL.md:396) does state capture by `git show`
  as prose, while the comparison is `git cat-file blob`. The verifier's attribution is
  consistent with that, so it can be cited as the registry's prose, not as gate-checked.
- `AttackSourceCuration.md:60` quotes `round-12.md:12-13` as "compares both against
  `git show`". The committed `round-12.md` (blob 941bb32, lines 14–15) reads "Capture uses
  `git show` (S032); … comparison with `git cat-file blob`". The advisor quote is not in
  the file. Rely on the committed text.

## Verdict on the design

**Approve the append-only approach, conditional on Findings 1–4.** KQ15 is preserved
byte-for-byte; KQ16 names the mistake and supersedes only the two formulations. KQ14's
semantic-human boundary and the manifest/source separation remain in force. Re-review
after KQ16 lands and `measure.py` exists.

## Residual risk / verification gaps

- KQ16 row and `measure.py` absent at review time; findings are not yet tested against
  actual text.
- Literal presence is documentation conformance, not semantic proof (as round-13.md states).
- The textconv behaviour of `git show` on blobs is an [INFERENCE] limit; the design does
  not rely on it.
- No independent non-author review of KQ16 exists. This seat is an author-side advisor.

## Final static disposition (KQ16 landed; no execution)

Read-only observations (commands: `git cat-file blob 941bb32:corpus/QUALITY.md`, `cmp`,
`sha256sum`, python byte checks on the file, `git status --short`,
`git diff --numstat 941bb32 -- corpus/QUALITY.md`, `git diff --quiet 941bb32 -- .ufo/waves/round-12`):

- Prefix: final 12382 bytes starts with the 8619-byte start blob: **True**. Append-only holds.
- KQ15 row (line 49) sha256 `b559befa…7618c`: **unchanged**. Final line 49 is byte-identical.
- KQ16: exactly one row, line 61 of 61. It contains `source_mismatch=1; snapshot_tampered=2; source_unavailable=2`: **True**; `capture: git show; comparison: git cat-file blob`: **True**; the bare phrase `distinct nonzero` is absent from the KQ16 row.
- Start blob contains neither literal (before state); the diff is 12 insertions, 0 deletions.
- Historical code and receipts: `.ufo/waves/round-12` unchanged vs 941bb32 (`git diff --quiet` exit 0). `fidelity.py` and `reproduce.py` are not modified.
- Label edit: the row reads "a textual gate does not establish semantic admission" and "the quoted audit phrases are documentation anchors, not semantic proof". Present.
- S033 row exists at `corpus/SOURCES.md:45`. Its scope and quote are owned by ReviewRegistry; not re-reviewed here.

Per-finding disposition:

1. Exit precedence: **resolved.** The KQ16 row states primary-finding selection under the `PRIORITY` order, matching `fidelity.py:64-72,317-319`. It says `source_mismatch` exits 1 only when it is primary. It states that a co-occurring byte mismatch with a higher-precedence finding exits 2 with the correspondence count still recording it. It states that a lower-precedence listed ID does not imply its exit. It does not cite the false comment at `fidelity.py:55-56`.
2. Capture provenance: **resolved.** `git show` is labelled author-recorded provenance (S032). Comparison is by `git cat-file blob`. The row forbids presenting the capture as command-verified, reproducible from code, or independent. The textconv behaviour of `git show` remains an [INFERENCE] limit.
3. Immutability / probe: **file-level resolved; probe-level open.** The prefix and KQ15 hash hold in the file. The probe-level check (prefix assertion and `| KQ16 |`-scoped wording check in `measure.py`) is not verifiable until `measure.py` exists. Re-check when it lands.
4. Supersession naming: **resolved.** The heading and the row name KQ15's two inaccurate formulations and preserve every other KQ15 clause.

Static disposition: **approved** for the criterion text. The criterion is textual conformance only and does not admit serving, runtime or semantic claims. Open item: the measure prefix check, pending `measure.py`.

Report: .ufo/waves/round-13/advice/ReviewPreservation.md
