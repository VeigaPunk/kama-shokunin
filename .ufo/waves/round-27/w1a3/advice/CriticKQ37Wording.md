VERDICT: partial — KQ37 rejects the round-26 escaped-JSON shortcut, but its signature-dependent frame definition accepts a concrete boundary-shift variant of the same captured error.

# Scope and axes

This is an attack on KQ37 wording, not a judgment of X1, a measured C1 result, or lane admission. **Calibration** is the affected axis: the criterion must distinguish the mechanism it checks from a claim that a counter discriminates all shortcuts. **Depth** is not scored: C1 was withdrawn before data (`.ufo/waves/round-27/a3/plan.json:6-18`; `corpus/lessons/round-27.md:13-30`). Possible exclusions of genuine fault rows concern depth/coverage only conditionally; no axis delta is established here. Canonical axis definitions are `/home/vgpnk/Projects/shokunin/AXES.md:11-16,34-51`.

Only assigned/committed evidence was read. No prohibited dead-seat scratch, server, counter `main()`, judging runtime, nested agent, or tool installation was used. Counter sources and the criterion were not edited.

# Applying KQ37 to both counters

The criterion is `corpus/QUALITY.md:215-219`, especially the full admit/reject row at line 219.

| Counter | Outcome on the criterion's targeted mechanism | Full evidence/admission status |
|---|---|---|
| Round 26, `eb09e742:.ufo/waves/round-26/count-c1.py` | **FAIL.** Lines 369-374 construct a raw-string request surface; line 384 tests only `sig not in req_bytes`. Lines 392-395 compare signature overlap and complete channel text, not signature-removed message frames. | Algorithmic failure is sufficient; no receipt discussion can turn it into a KQ37 pass. This is a retrospective application of the new criterion, not a claim that KQ37 existed in round 26. |
| Round 27 A3, `.ufo/waves/round-27/count-c1.py` | **Passes the specific ASCII decoded-value/shared-frame repair, not a demonstrated general discrimination result.** Lines 351-372 walk nested decoded keys/strings and both body serialisations; lines 585-587 reject any matching surface. For the original shortcut, the signature is exactly the decoded `response_format.type` value, so this condition rejects it. Lines 707-709 additionally reject equal nonblank signature-masked residuals among already eligible/credited rows. | **LIMITED / full KQ37 admission not established.** The frozen attempt plan records no committed A3 non-author shortcut-control receipt and no data seat (`a3/plan.json:6-18`); the lesson records withdrawal (`lessons/round-27.md:13-21`). No-data is not a retrospective ordering violation, but also is not an observed receipt-backed discrimination result. Literal “case-folded” conformance is a further qualification: A3 actually uses `lower()` (`count-c1.py:343-348,707-708`); this report does not establish Unicode-wide conformance. |

The historical failure is concrete, not just a possible mutation. `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json:15-20` supplies a raw JSON string whose first payload character is escaped. Its receipt reports `e_not_echoed: true`, status 400, the echoed payload, and `counted: true` at `shortcut.receipt.json:18-31`; totals are registered 12, counted 12, met true at lines 321-323. The independent spot-check describes all 12 as one generic frame at `corpus/lessons/round-26-verifier-spotcheck.md:98-116`. I did not rerun the historical live count.

The A3 assessment is about the semantically same decoded requests, not a trivial replay of obsolete registry syntax: A3 rejects raw string bodies as bad requests at lines 576-581. A full counter run was neither needed nor performed.

# Concrete wording loophole: move the signature boundary

Let `F` be the constant prefix emitted by S137:

```text
response_format type must be one of "text" or "json_object", but got: 
```

Pinned source `.ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp:1363-1375` reads the decoded request value and throws `F + response_type` at line 1375. The committed shortcut receipt already contains 12 such messages, `F + L_i`.

Keep each captured request and message unchanged, but submit the signature

```text
S_i = last k_i characters of F + L_i, with distinct k_i = 2..13.
```

Examples from the retained probe:

- First signature: `: _NSGetExecutablePath failed after buffer resize`.
- Second signature: `t: GetModuleFileNameW failed or path too long`.

Neither full signature occurs in its request path, any decoded key/value, or either decoded-body serialisation: the caller supplies `L_i`, not the added fixed-frame suffix. Yet the observed error contains `S_i`. Cutting `S_i` from the message leaves `F` with a different suffix removed for every row. Thus all residuals are nonblank and different **by KQ37's own parenthetical definition**, despite a single emitting template/raising statement. NUL-marker replacement has the same boundary problem.

An offline probe used only the frozen counter's AST-extracted `squash`, `occurs`, `json_strings`, and `request_surfaces` functions; it separately computed literal-cut/casefold frames and A3-style NUL/lower frames. Result:

```text
captured_messages_reused: 12
 different_actual_fixed_prefixes: 1
 decoded_echo_hits_a3: 0
 decoded_echo_hits_casefold: 0
 different_literal_cut_frames: 12
 different_a3_nul_frames: 12
 kq37_mechanical_accepts: 12
```

Evidence: `.ufo/waves/round-27/w1a3/out/CriticKQ37Wording/frame_boundary_probe.json:2-11`; complete first/second rows at lines 14-67; last variant at lines 322-347. Reproducer: the adjacent `frame_boundary_probe.py`.

**Boundary of this finding:** this demonstrates a KQ37-computational-conjunct loophole, **not** that these rows satisfy the full A3 predicate or meet its target 15. A3 independently requires a signature in a pinned source-line literal, unique literal provenance, and a distinct source line (`count-c1.py:565-571,701-702`); the boundary-spanning signatures have not been shown to satisfy those guards. No source, novelty, table, positive-control, or main-program admission result is claimed for the variants.

[INFERENCE] A counter implementing the literal KQ37 substring/residual rules could have successful non-author pre-data receipts for the named direct-echo classes and still accept these later boundary-shifted rows: the criterion does not explicitly require this variant as a control, and different selected-signature residuals satisfy its frame definition. Receipt existence cannot repair a missing comparison. This is why the result attacks the wording rather than asserting an A3 bypass. The entry itself correctly says the rule is necessary, not sufficient (`corpus/knowledge/echo-discriminating-counters.md:56-66`).

# Can a shortcut-refusing counter fail for another reason?

**Yes; two distinct cases must not be conflated.**

1. **Evidence chronology, not algorithmic discrimination.** A counter can reject the complete round-26 shortcut and still have only an author-generated receipt, an uncommitted receipt, or its first non-author receipt after data. KQ37's final admit conjunct then fails. That is an intentional calibration/provenance requirement, not evidence that its echo algorithm failed. A3's withdrawn/no-data situation must be described separately rather than called either a measured pass or a missed target.
2. **Conservative input overlap, not necessarily causal echo.** The same pinned source throws the constant `Cannot use both json_schema and grammar` when the parsed schema is non-null and grammar is nonempty (`server-common.cpp:1357-1360`). [INFERENCE] A request that triggers those conditions and also includes that exact sentence in an otherwise irrelevant user-message content field has an independently fixed-source error, but KQ37 must reject the signature because it occurs in a decoded value. A causal/source-aware counter could reject the round-26 injection and retain that genuine row, yet fail KQ37's stronger substring policy. This is a source-derived example, not an observed live response. Removing the incidental content can retain the same fault; no actual loss of fault coverage has been measured here.

The second case is an explicitly conservative exclusion if the rule is advertised only as a necessary admission condition. It becomes overreach if advertised as proof of causal echo or complete genuine-fault discrimination. Neither case authorizes waiving the receipt gate or claiming a no-harm trade; the canonical reviewer must keep mechanism, evidence eligibility, and any demonstrated loss separate.

# Smallest safe correction

Append a qualification to KQ37 rather than rewriting its historical row:

> A message-frame identity is derived from the pinned emitting template/raising site with request-derived variable segments masked independently of the submitted signature; moving the signature's boundaries cannot create a new frame. Pre-data controls include a signature spanning fixed text plus an echoed value, and echoed residue outside the selected signature.

Keep the non-author, committed-before-data obligation. Say explicitly that incidental request overlap is a conservative exclusion, not proof that the server derived the error from that field. Do not mutate the frozen A3 counter or revive withdrawn C1 to present this exploratory finding as a counted result.

# Commands, outputs, exits

All commands below completed successfully (command/pipeline exit 0; individual pipeline-stage exit statuses were not separately captured). Reads of line-numbered artifacts above were through the read tool. No full counter or live-server command ran.

```sh
timeout 30s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show eb09e742:.ufo/waves/round-26/count-c1.py | timeout 30s nl -ba
```

Trimmed output: lines 369-374 raw request construction; `384 c["e_not_echoed"] = sig not in req_bytes`; lines 392-395 overlap/trigger checks without frame comparison.

```sh
timeout 30s git -C /home/vgpnk/Projects/shokunin/kama-shokunin show eb09e742:.ufo/waves/round-26/count-c1.py | timeout 30s sha256sum
```

```text
6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588  -
```

```sh
timeout 30s sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
```

```text
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
```

```sh
timeout 30s /bin/bash -c 'ulimit -f 1048576; ulimit -v 262144; ulimit -t 15; ulimit -u 64; exec /usr/bin/python3 -I -S /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/CriticKQ37Wording/frame_boundary_probe.py'
```

Output: the seven probe quantities pasted above, frozen SHA-256, first/last signatures and residuals, and the scoped JSON output path. Exit 0. This bounded offline command wrote only its adjacent JSON evidence file; its input Python source and imported files were never output/marker paths. No process tree remains from the finite commands. No scratch directory or installation was needed.
