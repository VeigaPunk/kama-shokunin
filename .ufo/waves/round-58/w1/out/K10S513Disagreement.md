# K10S513Disagreement — S513 source rejection

Axes: operability and calibration; this finding concerns calibration/source selection, not a defect in the round-58 checker.

## Counterexample and verdict

I agree with the round-56 rejection for the *narrow C1 predicate actually described*: detecting the presence of `LD_AUDIT` in the child environment. The strongest local counterexample is that `ld.so(8)` has a dedicated `LD_AUDIT` environment-variable section, yet itself directs readers to `rtld-audit(7)` for details; its useful loader-specific additions (secure-execution behavior, token expansion, namespace behavior) do not establish more than the predicate needs. The overlap is real, but it is not equivalence: rejecting S513 is defensible only while the claim remains name-presence detection, not proof of loader acceptance or successful auditor activation.

## Located evidence (quotes <=25 words)

- Committed snapshot `.ufo/waves/round-56/sources/ld.so.8.html:81-83`: “The programs ld.so and ld-linux.so* find and load the shared objects (shared libraries) needed by a program, prepare the program to run, and then run it.”
- Committed snapshot `.../ld.so.8.html:538` (environment section, as identified in round-56 census evidence) has the `LD_AUDIT` entry; the round-56 filed source verification quotes its exact content at `.ufo/waves/round-56/w1/out/Q02Source513.md:41-46`: “These objects can be used to audit the operation of the dynamic linker.” Its preceding quoted lines define a list of user-specified ELF shared objects loaded before others in a separate linker namespace.
- The same filed verification reports the §LD_AUDIT instruction: “For details, see rtld-audit(7).” (`Q02Source513.md:55`). That is direct evidence for dedicated-source preference, not proof the manuals are wholly interchangeable.
- The live man7 page is https://man7.org/linux/man-pages/man8/ld.so.8.html. Its supplied search result describes `ld.so` as the dynamic linker/loader and says it finds dependencies, maps them, resolves symbols, and transfers control. Round-56's source verification records a live HTTP 200 fetch of 41,398 bytes and byte-identical snapshot SHA-256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83` (`Q02Source513.md:9-21`). I did not independently fetch the page in this seat; that live-fetch statement is attributed to the filed receipt, not my own check.
- Round-56 lesson itself says the quote was 18 words, `.ufo/waves/round-56/corpus/lessons/round-56.md:15` equivalent at `corpus/lessons/round-56.md:15`; Q02Source513 separately measured 16 words, which disagrees with the lesson annotation. This count discrepancy does not affect the rejection rationale.

## QUALITY criterion taught

Source admission must be claim-relative and discriminate *what the evidence proves*: a variable name can be a risk indicator without demonstrating that a selected DSO was accepted or that code ran. Prefer the source that directly specifies the predicate, but retain a rejected source's distinct, potentially relevant scope and an explicit flip criterion. Do not let “overlap” erase non-overlapping semantics, or let a quoted environment-variable description inflate provenance into an activation claim.

## Smallest safe correction

Keep S513 rejected for the frozen name-presence claim; tighten the rationale to say that S512 is sufficient for this predicate and S513 is redundant *for this use*, while preserving the secure-execution/token/namespace flip criterion. If a future claim asserts actual loader behavior or auditor activation, reopen S513 (and test the relevant behavior); do not cite this rejection as evidence against that broader claim. No production edit was made; this report is the seat output only.
