# Q03SourceS513Reopen — S513 live recheck

Axes: operability (whether the source supports the existing LD_AUDIT name check); calibration (whether S513's registered rejection/flip remains appropriately scoped).

## Live evidence

Fetched `https://man7.org/linux/man-pages/man8/ld.so.8.html` live on 2026-10-27. Under ENVIRONMENT → Secure-execution mode, it lists LD_AUDIT among environment variables whose effects are voided/modified and which are stripped. Under ENVIRONMENT → `LD_AUDIT`, it states:

> “In the usual case, the audit list is initialized before the preinit array is executed”

(14 words; more directly relevant wording in same section: “The names of the audit libraries are specified in a colon-separated list”; 11 words.) The section says names are loaded as audit shared objects; it also documents secure-execution behavior and dynamic string-token expansion for LD_AUDIT.

## Registry comparison and recommendation

Observed `corpus/SOURCES.md` S513: rejected because broad `ld.so(8)` overlaps dedicated `rtld-audit(7)` S512 for the sole claim need (LD_AUDIT loads auditor objects); flip condition is a future claim about secure-execution, dynamic string tokens, or loader namespace semantics.

Recommendation: **keep rejected for the current LD_AUDIT variable-name detection claim.** The live manual does confirm that LD_AUDIT names auditor libraries and provides additional relevant detail, but it does not defeat the redundancy rationale: the narrower S512 is purpose-fit for that single need. **Reopen/flip S513 only if the claim expands** to secure-execution stripping/alteration, LD_AUDIT token expansion, or loader namespace/initialization semantics; the live text directly covers the former two. The current registry flip condition appropriately names these distinct scopes. I did not find a basis to flip for the current claim.

## Checks

- Command: `read https://man7.org/linux/man-pages/man8/ld.so.8.html` — output included ENVIRONMENT → Secure-execution mode and `LD_AUDIT` sections — exit code: not exposed by reader.
- Command: `read /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:266:raw` — S513 row confirms registered reason, flip condition, status `rejected` — exit code: not exposed by reader.

Attacks: source row S513 and its scope/rejection; no claim/counter/variant was run. Confidence: high on the documented live text and registry comparison. Unknown: whether a future lane claim actually expands into the registered additional semantics; not this seat's evidence.