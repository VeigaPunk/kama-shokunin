# Q02Source513 — S513 live-fetch verification (ld.so(8))

Seat item: Live-fetch `https://man7.org/linux/man-pages/man8/ld.so.8.html`; verify the S513 quote and the stated rejection rationale.
Axis judged: calibration. Scope: S513 row in `corpus/SOURCES.md` line 266 and the S513 Gate entry in `corpus/lessons/round-56.md` line 15.

## Fetch receipt (run)

```
$ curl -sL --max-time 60 -o <scratch>/ld.so.8.html -w '%{http_code} %{url_effective} %{size_download}\n' \
    https://man7.org/linux/man-pages/man8/ld.so.8.html
200 https://man7.org/linux/man-pages/man8/ld.so.8.html 41398
```

Fetched 2026-10-27. Live bytes are **byte-identical** to the committed snapshot:

```
d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83  .ufo/waves/round-56/sources/ld.so.8.html
d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83  <scratch>/ld.so.8.html   (live)
```

So the committed snapshot faithfully represents what man7.org serves today.

## Claim under test (SOURCES.md S513, verbatim fields)

- Source: `ld.so(8) — https://man7.org/linux/man-pages/man8/ld.so.8.html`, type docs, tier A.
- Use field: "broad dynamic-linker environment and token handling; candidate source for the round-56 LD_AUDIT name check".
- Anchor/revision: "§LD_AUDIT, Linux man-pages 6.19 (2025-05-17), HTML snapshot `.ufo/waves/round-56/sources/ld.so.8.html`".
- Disposition: "REJECTED: this broad loader manual overlaps the dedicated rtld-audit(7) source S512 for the claim's only need (the LD_AUDIT variable loads auditor objects); flip: a future claim about secure-execution, dynamic string tokens, or loader namespace semantics". Status `rejected`, opened 2026-10-27.

## Verification results

### 1. Quote — VERIFIED (16 words)

The lesson/row's located quote at `§LD_AUDIT`:

> "A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace"

appears verbatim (whitespace-only differences from HTML wrapping) in the live page under the `LD_AUDIT (since glibc 2.4)` heading inside `Environment variables`:

```
LD_AUDIT (since glibc 2.4)
       A list of user-specified, ELF shared objects to be loaded
       before all others in a separate linker namespace (i.e., one
       that does not intrude upon the normal symbol bindings that
       would occur in the process) These objects can be used to
       audit the operation of the dynamic linker. ...
```

Word count of the quoted span: 16 — matches the "(16 words)" annotation.

### 2. Rejection rationale — VERIFIED as sound

The stated reason is overlap with S512 for C1's only need ("the LD_AUDIT variable loads auditor objects"). Confirmed:

- The §LD_AUDIT section itself defers to rtld-audit(7): *"For details, see rtld-audit(7)."* — the page openly cedes the audit-interface contract to the dedicated manual.
- Every fact C1's predicate needs — LD_AUDIT names shared objects loaded into the process environment before others — is stated in S512's §DESCRIPTION quote ("the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries, each of which can implement (parts of) the auditing API"), which I confirmed verbatim in the committed rtld-audit.7.html snapshot.
- The extra content ld.so(8) adds (secure-execution voiding incl. "LD_AUDIT is ignored in secure-execution mode", glibc 2.13 slash filtering, $ORIGIN/$LIB/$PLATFORM token expansion) is not needed by the C1 predicate, which is a *name-detection* check on the child environment, not a claim that an audit DSO successfully injects. The preregistration `limits` field confirms: "it does not claim a foreign audit DSO successfully injects code on this glibc."
- C1's counter header (`tools/round56-replay-code-audit.py` lines 4–6) cites only S512. No consumer of S513 exists.

The flip criterion is also coherent: ld.so(8) is the natural source if a later claim touches secure-execution env stripping, dynamic string tokens, or linker namespaces — all real sections of this page.

### 3. Revision field — DEFECT (minor, one field wrong)

The row and lesson claim "Linux man-pages 6.19 (2025-05-17)". The fetched page footer (and the committed snapshot, byte-identical) reads:

```
Linux man-pages 6.19            2026-08-03
```

Page version 6.19 is correct; **the date is wrong** — 2025-05-17 is the footer of `rtld-audit.7.html` (S512's snapshot: `Linux man-pages 6.19            2025-05-17`). The date appears copied across from S512 rather than read from the ld.so(8) snapshot. Both files' mtimes (13:00 vs 13:02) show they were fetched in the same sitting, consistent with a copy-paste slip.

**Defect (advisory, non-falsifying):** S513 revision date `2025-05-17` should be `2026-08-03` in `corpus/SOURCES.md` line 266 and `corpus/lessons/round-56.md` line 15. Proposed fix: correct the two date strings in-place on a future append/annotate pass per lane rules (do not rewrite the frozen lesson if the gate freezes lesson text — record the correction per the round-56 stale-premise precedent instead). It does not falsify C1/C2: no claim predicate, counter, or kill rule consumes the revision date; the snapshot hash match means the located quote was genuinely verified against served bytes.

### 4. Other row fields — VERIFIED

- Page identity: title `ld.so(8) — Linux manual page`; URL matches; §LD_AUDIT anchor exists.
- "opened 2026-10-27" consistent with snapshot mtime 13:02 Oct 27 and today's date.
- Status `rejected` and tier `A` consistent between SOURCES.md and the lesson Gate entry; wording identical in substance.

## Verdict

- S513 quote: **accurate** (verbatim, correct section, 16 words).
- Rejection rationale: **accurate and appropriately scoped** — S513 genuinely duplicates S512 for C1's single need, and the page itself delegates audit-interface detail to rtld-audit(7). Rejecting it keeps the source registry minimal without weakening C1's grounding.
- One calibration nit: the recorded man-pages date `2025-05-17` is wrong for this page; correct value `2026-08-03`. Field-level defect, not a falsifier.

## Tools installed

None. curl + python3 stdlib only; no pacman invoked (transactions paused host-wide).

## Cleanup

Scratch `/fast/scratch/hyaku/kama-r56/Q02Source513/` removed after verification (fetched bytes were identical to the committed snapshot, which is the durable receipt).
