VERDICT: partial — decoded-string surfaces and credited-row scope match, but Unicode folding and frame normalization do not literally implement the published rule.

# Scope and axis

**Axis: calibration (X1).** Diagnostic dimensions: echo-surface coverage, normalization fidelity, and frame-equivalence fidelity. This is a scoped rule/code finding, **not an X1 verdict or row admission**. C1 is withdrawn and is not scored.

Reviewed `corpus/knowledge/echo-discriminating-counters.md:39-54` against `.ufo/waves/round-27/count-c1.py`, frozen SHA-256 `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765`. Below, **entry** and **counter** mean those two paths. KQ37 repeats the relevant wording at `corpus/QUALITY.md:219`.

# Clause-by-clause comparison

| Entry text | Counter line(s) | Matches yes/no | Gap or qualification |
|---|---|---|---|
| “case-folded” (entry:44) | 343-348 | **No** | `occurs` and `squash` use `lower()`, not Unicode `casefold()`. `invalid-strasse-marker` is not detected in decoded `invalid-straße-marker`, although their casefolded forms agree. |
| “with all whitespace removed” (entry:44-45) | 343-348 | **Yes** | `re.sub(r"\s+", "", text)` removes whitespace from both operands before comparison. Probe included TAB, LF and U+2003. The separate Unicode-folding defect remains. |
| “in the request path” (entry:45) | 365-367, 585-587 | **Yes** | `req["path"]` is always a surface for a valid request; the predicate tests every surface. No URL-decoding requirement appears in this clause. |
| “JSON-decoded key … at any depth” (entry:45-46) | 351-362; registry decode 627; predicate 586 | **Yes** | Parsed dictionaries contribute every key; dictionary values and list elements recurse. Objects inside nested arrays are visited. Arrays have values, not JSON object keys. |
| “JSON-decoded … value … at any depth”: string values (entry:45-46) | 351-362, 368-369 | **Yes** | Strings are appended directly, including strings reached through nested arrays and objects. This is not a raw-byte-only check. |
| Same clause: non-string scalar values | 351-362, 370-371 | **No, as independent leaf surfaces** | Numbers, booleans and null contribute nothing to `json_strings`. Their JSON spellings are nevertheless present in the whole-body serialisations. The scalar-only-array probe detected an integer, scientific-notation number, `true` and `null` there. Thus this is a literal traversal/wording qualification, **not a demonstrated scalar bypass**. The rule does not specify an alternate scalar-to-text conversion; absence of Python `None` spelling is not evidence that JSON `null` escaped. |
| “either serialisation … (ASCII-escaped and UTF-8)” (entry:46-47) | 370-371 | **Yes** | Default `json.dumps(body)` is ASCII-escaped; `ensure_ascii=False` retains Unicode. Both are tested. For top-level `None`, no body is sent by `http` (389), so skipping its serialization is consistent with that request representation. Non-null top-level scalar bodies are rejected at 579-580. |
| “With the signature cut out of the message” (entry:48) | 707-708 | **No under literal deletion** | The code replaces each exact signature occurrence with a NUL placeholder; it does not delete it. Placeholder position affects equality. Two different insertion positions can leave identical deleted text but unequal code frames. See witness below. |
| “remainder (case-folded …)” (entry:49) | 707-708 | **No** | Frame comparison also uses `lower()`. `Straße: <A>` and `STRASSE: <B>` produce equal casefolded remainders but two credited rows in the isolated loop. |
| “remainder (… not blank)” (entry:49) | 707 | **No for whitespace-blank remainders** | `.strip("\0 ")` removes NUL and ASCII space only. A TAB-only or LF-only remainder is treated as nonblank. Two signature-plus-TAB messages trigger `h:same-message-frame`, although their literal remainders contain only whitespace. |
| “equals the remainder of a row already credited” (entry:49-50) | 691-699, 716-722 | **Yes, subject to normalization above** | Rows already carrying rejection reasons are skipped. `seen` receives a row only when it is also added to `counted`. Earlier rejected rows do not reserve a frame. That is the published scope, not a missing comparison. |
| “One message frame earns one row” (entry:50) | 699-722 | **No for the rule's literal normalization; yes for the implemented eligible frame relation** | An ordinary identical positional frame rejects the second row. The Unicode and literal-deletion witnesses produce two rows instead. The nonblank exception is intentional in the text; counting multiple signature-only messages is not by itself a violation of that exception. |

# Counterexamples and measured outputs

The probe reads the frozen bytes, asserts their hash, compiles only the four helper definitions and the original assignment/loop at counter:691-722, and supplies **synthetic component inputs**. It does not import the counter, call `main()`, run static/source eligibility, perform HTTP, or start a server. Its local `counted` list is **not** a full-counter receipt. No full A3 bypass or real-row admission is established.

1. **Unicode echo and frame mismatch.** A decoded request value `invalid-straße-marker` is casefold-equivalent to signature `invalid-strasse-marker`, but `occurs` misses it. Separately, messages `Straße: alpha-marker-123` and `STRASSE: beta-marker-456` both have literal cut-and-casefold remainder `strasse: `, yet the extracted loop credits both synthetic rows. This is a concrete normalization mismatch, independent of the scalar ambiguity.
2. **Deletion versus positional hole.** Messages `pre<alpha-marker-123>lude` and `p<beta-marker-456>relude` both leave `prelude` after deleting their respective signatures. Code frames instead become `pre\0lude` and `p\0relude`, and both rows survive. Angle brackets here only delimit the inserted signature; they are not part of either probe message.
3. **Blank remainder over-rejection.** Messages `alpha-marker-123\t` and `beta-marker-456\t` have whitespace-only remainders. The code credits only A and attaches `h:same-message-frame` to B. This is false saturation relative to the stated nonblank condition, not an echo-admission result.
4. **Negative controls.** Ordinary `fixed: <signature>` messages credit only A. With A already rejected for `a:no-skill-row`, otherwise same-frame B is credited. Nested-array key/value and whitespace-removed request tests detect their signatures. A scalar-only array yields no `json_strings` surfaces but its canonical scalar spellings are all detected through serialization.

## Exact commands and exit codes

From the lane root:

```sh
timeout 10s sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
```

Exit 0; output:

```text
49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/count-c1.py
```

Probe command, executed using `subprocess.run` with captured output and an additional 25-second parent timeout:

```sh
timeout --kill-after=2s 20s bash -c 'ulimit -f 1048576; ulimit -v 262144; ulimit -u 8192; ulimit -t 10; exec /usr/bin/python3 -I -S "$1"' rule-code-probe /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/CriticEntryRuleVsCode/probe.py
```

Exit **0**, stderr empty. It ran twice: the second run strengthened the scalar test from an object to an array containing only non-string scalars, removing any key-name confound. Exact final stdout and command are preserved at `.ufo/waves/round-27/w1a3/out/CriticEntryRuleVsCode/probe.stdout.txt`. Selected final output, verbatim:

```text
nonstring_scalars={"canonical_spellings_detected": {"1.25e+40": true, "123456789012345": true, "null": true, "true": true}, "json_strings": [], "python_None_spelling_detected": false, "serialized": ["[123456789012345, 1.25e+40, true, null]", "[123456789012345, 1.25e+40, true, null]"]}
unicode_frame={"counted": ["A", "B"], "counter_nul_lower_frames": ["stra\u00dfe: \u0000", "strasse: \u0000"], "literal_cut_casefold_remainders": ["strasse: ", "strasse: "], "why": {"A": [], "B": []}}
literal_cut_frame={"counted": ["A", "B"], "counter_nul_lower_frames": ["pre\u0000lude", "p\u0000relude"], "literal_cut_casefold_remainders": ["prelude", "prelude"], "why": {"A": [], "B": []}}
tab_only_remainder={"counted": ["A"], "counter_nul_lower_frames": ["\u0000\t", "\u0000\t"], "literal_cut_casefold_remainders": ["\t", "\t"], "why": {"A": [], "B": ["h:same-message-frame"]}}
already_credited_only={"counted": ["B"], "counter_nul_lower_frames": ["fixed: \u0000", "fixed: \u0000"], "literal_cut_casefold_remainders": ["fixed: ", "fixed: "], "why": {"A": ["a:no-skill-row"], "B": []}}
```

# Impact and smallest safe correction

- **Fixable calibration defects:** lowercasing is not Unicode casefolding; checking only NUL/space is not checking whitespace blankness. The observed directions differ: missed Unicode equivalences can retain two frames, while TAB-only remainders prematurely saturate one.
- **Semantic tradeoff, not an adjudicated defect in server knowledge:** a positional-hole frame preserves insertion location, whereas literal deletion can merge different locations. The probe proves those relations differ. [INFERENCE] The author may have intended the positional relation. The canonical reviewer must resolve that intent against the published contract; this seat does not choose a new frame definition or decide X1.
- **Smallest safe correction at the frozen revision:** qualify the unconditional “implements both” assertion at entry:52-54 with the actual lowercasing/positional-placeholder/ASCII-space behavior. Clarify that scalar JSON spellings are covered by serialized bodies, not by independent scalar traversal. Do not relabel these component results as a full-counter receipt or mutate frozen counter bytes.
- **If a newly identified counter revision is intended to satisfy the unchanged literal rule:** use `casefold()` in the echo normalization and frame normalization; derive the frame with `message.replace(signature, "").casefold()`; test blankness with `frame.strip()` while retaining the unstripped frame for equality. Keep the current credited-only `seen` scope. If retaining a positional placeholder instead, explicitly reconcile that different definition in both the entry and KQ37 rather than silently equating it with deletion.

No lane source, index, runtime configuration, or frozen artifact was changed. Only this report and the two scoped evidence files were written. No tools were installed. Both finite probe processes exited; the probe spawns no children. No server or other long-lived process was started. Full-counter/live behavior and an X1 judgment remain unrun and unverified by this seat.
