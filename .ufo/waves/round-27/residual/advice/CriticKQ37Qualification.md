VERDICT: partial — the body-form qualification holds, but boundary ownership remains ambiguous and permits same-template inflation, while ASCII signatures do not make lower() Unicode-safe.

## Scope and axes

Advisory critic evidence about `corpus/QUALITY.md:221-242`, not a judgment of X1, lane admission, or C1. C1 was withdrawn before data and is not scored here (`.ufo/waves/round-27/a3/plan.json:6-18`). No canonical judging runtime was invoked.

**Primary axis: calibration** — the criterion's stated guarantees and its description of frozen-counter conformance. **Impacted dimensions: operability** (a reproducible ownership/frame definition) and **depth/coverage** (false multiplicity or unnecessary exclusion of genuine signatures). No measured axis delta or actual deployed loss is asserted. Axis definitions/no-trade rule: `/home/vgpnk/Projects/shokunin/AXES.md:11-16,34-51`.

Paths below are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`. `P` denotes `.ufo/waves/round-27/residual/out/CriticKQ37Qualification/probe.json`; its adjacent `probe.py` is the reproducer. Inputs, including the reviewed QUALITY bytes, are SHA-256 recorded at `P:5-29`. The frozen counter and S137 source hashes were asserted before evaluating their selected functions. Nothing from the prohibited dead-seat directories was read.

## 1. Boundary shift — partial

### The exact original and frame-tail attacks are stopped

A conforming decoded-request test cannot accept the **unchanged** round-26 shortcut signatures: each signature equals its decoded `response_format.type`. This replay finds **12/12 decoded echo hits**, versus **0/12 raw hits** (`P:32-38,79-151`).

The **unchanged** twelve frame-tail variants also fail the qualification: each overlaps the source-derived appended-value interval, and none is contained in S137's fixed literal (`P:153-237`; original variants: `.ufo/waves/round-27/w1a3/out/CriticKQ37Wording/frame_boundary_probe.json:14-67,322-347`). Thus these exact rows are not a bypass of the strengthened row-level rule.

### “A decoded request string occupies” is not an ownership definition

Let `F` be the genuine 70-character S137 literal:

```text
response_format type must be one of "text" or "json_object", but got: 
```

Pinned `.ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp:1363-1375` reads `response_type` and throws `F + response_type`. The first retained round-26 response is exactly that message (`.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json:24-31`). Its request contains keys `response_format` and `type` (`shortcut.registry.json:15-19`).

For the **full fixed prefix as signature**, the probe finds:

| Interpretation of request-string spans | Intervals in the decoded message | Overlaps signature `[0,70)`? |
|---|---|---|
| Every textual occurrence of every decoded key/value | `response_format` at `[0,15)`; `type` at `[16,20)` | **Yes: rejects the genuine fixed prefix** |
| Source-derived contribution from the appended `response_type` expression | `[70,117)` | **No** |

Evidence: `P:48-77`. The full prefix is in the source literal and is **not** an echo hit under KQ37's existing whole-signature comparison. Therefore matching all occurrences of short/common request strings adds an exclusion that the original echo rule did not require. These two ordinary key names suffice; an adversarial one-character value is unnecessary.

This is a **specification ambiguity and a concrete false-positive consequence of a plausible implementation**, not an observed A3 boundary-check rejection: QUALITY itself says no lane counter implements that overlap check (`QUALITY.md:234-235`). Byte equality does not establish provenance. Conversely, merely selecting one convenient equal occurrence is not proof of server ownership.

The entry already discloses conservative rejection when an **entire signature** occurs incidentally in a request (`corpus/knowledge/echo-discriminating-counters.md:89-92`). That existing policy does not resolve whether every occurrence of a much shorter key taints an otherwise fixed literal.

### A same-template variant still passes the literal comparisons

Keep all twelve captured round-26 requests and messages unchanged, but choose each signature entirely **inside** `F`:

```text
S_i = F[21+i : 41+i], i = 0..11
```

For example, X26-01 uses `must be one of "text` at `[21,41)`; X26-12 uses ` of "text" or "json_` at `[32,52)`.

All twelve signatures:

- are distinct 20-character ASCII substrings of the **one actual emitting literal** at S137;
- are absent from the decoded request surfaces and both serialisations;
- overlap neither the actual appended-value span **nor any equal request key/value occurrence**;
- leave distinct nonblank case-folded messages after signature deletion, because the caller-supplied tails remain.

Observed result: **12/12 component passes; 12 distinct deleted frames; one actual fixed prefix** (`P:32-46,239-539`; first/last rows at `P:240-263,515-538`). This attack survives either interpretation of the ambiguous overlap rule. It exposes echoed residue **outside** the chosen, genuinely server-owned signature.

[INFERENCE] A counter implementing KQ37's parenthetical deletion-based frame identity, plus all three qualification points, could have bona fide non-author pre-data receipts for its named classes and still credit these rows. The comparisons do not force signature-independent template identity. That is an incompatibility between the literal algorithm and the intended “one message frame” meaning, not a fabricated claim that the missing administrative receipts exist. No such receipt or full-counter admission is produced here.

**Not an A3 bypass:** A3 separately rejects same-source-line/shared-message rows (`count-c1.py:701-706`). These component results do not establish source novelty, other A3 guards, a target count, or a live rerun. KQ37 is described as necessary, not sufficient (`knowledge/echo-discriminating-counters.md:123-133`); nevertheless, qualification 1 has not made its own frame comparison identify the emitting template.

**Smallest safe correction:** define request-derived spans by the pinned **executed emitting expression/template**, not arbitrary substring equality, using half-open offsets in the decoded message before normalization. For S137, explicitly identify `F` as server-owned and only the appended value as request-derived. Define frame identity independently of the submitted signature: mask **all** request-derived spans of the pinned emitting template. Here every row then has frame `F + <request-value>`, including a row whose signature is the genuine prefix. Retain the original decoded whole-signature echo test and pre-data receipt obligation. Include both boundary-spanning signatures and fixed-owned signatures with echoed residue in future controls; do not change the frozen counter.

## 2. Body form — holds for the named evidence

`QUALITY.md:236-239` accurately distinguishes rejecting stored raw JSON strings from decoding them before comparison. The frozen A3 shape guard permits only `None`, dict or list bodies (`count-c1.py:576-581`); its sender serialises accepted bodies itself (`:388-390`). Its helper does not parse an already-serialised string (`:351-372`). The qualification explicitly acknowledges this rather than attributing refusal to a decode that never ran.

Concrete example: the first round-26 body contains `"type":"\\u005fNSGetExecutablePath failed after buffer resize"` as stored JSON text. After one document decode, the value is `_NSGetExecutablePath failed after buffer resize`, exactly the signature. The offline replay sees 12/12 such decoded echoes (`P:32-35,79-151`). A raw-string-only test cannot satisfy point 2 by claiming it compared JSON-decoded values; refusing those bodies, as A3 does, is an allowed alternative.

No body-form bypass was found in these named fixtures. This does not establish a universal parsing theorem or full A3 conformance. No correction is required for this point; retain the distinction between actual wire-document decoding and serialising a string as a JSON scalar.

## 3. Case folding — partial; the ASCII-signature sufficiency statement breaks

The definition “Unicode case folding” is appropriate. The statement at `QUALITY.md:241-242` that lowercasing “meets KQ37 for ASCII signatures only” is not a sufficient safe-domain qualification: **both compared operands matter**.

Concrete frozen-helper result:

```text
signature:             invalid-strasse-marker       (entirely ASCII)
decoded request value: invalid-straße-marker
A3 occurs()/lower():   false
Unicode casefold():    true
```

The probe also uses the **actual entirely ASCII S137 fixed prefix** as signature and places that prefix in a decoded user-content field with ASCII `s` replaced by U+017F LONG S. LONG S is unchanged by `lower()` but folds to `s`. A3's real extracted `request_surfaces` + `occurs` functions miss it; Unicode folding detects it (`P:541-550`). This is a comparison counterexample, not an observed server response or a full A3-eligible registry row.

Frames have the same problem with ASCII signatures: removing ASCII `alpha-marker-123` / `beta-marker-456` from messages with `Straße: ` / `STRASSE: ` leaves unequal lowercase remainders but equal Unicode-folded remainders (`P:551-563`). Restricting signature characters cannot restrict the remainder's alphabet.

**Smallest safe correction:** say “`lower()` agrees with Unicode case folding when **all compared text**, not merely signatures, is ASCII; this alone does not establish full KQ37 conformance.” Preserve the separately documented positional-placeholder/blankness shortfalls (`knowledge/echo-discriminating-counters.md:116-121`). A future counter intended to implement the Unicode rule must fold both operands and frame text; this review does not edit frozen bytes.

## Defect versus tradeoff

The missing provenance/frame definition and the overbroad ASCII conformance sentence are fixable calibration defects. The existing whole-signature incidental-overlap exclusion is a disclosed conservative policy, not proof of causal echo. A new implementation that rejects S137's fixed prefix solely because its request contains `type` would create an additional unnecessary exclusion; disclosure alone would not establish no harm. Any actual trade or exploratory-claim judgment belongs to the canonical reviewer, not this seat.

## Exact commands, outputs and exits

Line-oriented inspections above used the read/grep tools. The following bounded offline probe was run once, from the lane directory:

```sh
timeout --kill-after=2s 25s /bin/bash -c 'ulimit -f 1048576; ulimit -v 262144; ulimit -t 15; ulimit -u 8192; exec /usr/bin/python3 -I -S "$1"' critic-kq37 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/residual/out/CriticKQ37Qualification/probe.py
```

Exit **0**. Trimmed stdout, verbatim:

```text
{"actual_fixed_prefixes": 1, "ascii_prefix_casefold_echo_hit": true, "ascii_prefix_lower_echo_hit": false, "fixed_owned_component_passes": 12, "fixed_owned_distinct_deleted_frames": 12, "fixed_owned_distinct_signatures": 12, "original_decoded_echo_hits": 12, "original_raw_echo_hits": 0, "original_rows": 12, "prefix_false_overlap_by_text_matching": true, "prefix_provenance_overlap": false, "tail_provenance_overlap_failures": 12, "tail_rows": 12, "tail_source_literal_failures_at_s137": 12}
```

The remaining stdout prints the full prefix-boundary example, first/last fixed-owned variants, Unicode examples and the absolute JSON output path; these data are retained in `P`. The script compiles only six helper definitions and the literal-regex assignment from the hash-checked counter, never imports the counter or calls `main()` (`probe.py:24-40`). No model, server, network, nested agent, or other judging runtime was used.

```sh
timeout 10s /usr/bin/pgrep -af '[l]lama-server'
```

Exit **1**, no output: no matching server process remained at this observation. This seat started none. The finite probe spawned no children and completed; no process tree was left running.

Only this report and the adjacent scoped `probe.py` / `probe.json` were written. Fixture output ran inside the stated timeout, process/memory/CPU bounds and 1 GiB per-file cap; no output exceeded 100 MB. No source, index, Git/JJ state, config, frozen counter or sibling-owned file was changed. **Tool installs/updates: none.** Full live-counter behavior and canonical X1 judgment remain unrun/unverified by this seat.
