source: S498 — CommonMark 0.31.2 specification, §4.5 Fenced code blocks, https://spec.commonmark.org/0.31.2/#fenced-code-blocks; the row was opened in round 50 and the page was re-fetched live in round 76 (2026-11-04, sha256 `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`, bytes `.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html`).
verified-at: 2026-11-04 — page re-fetched and the quote re-located in the retained bytes; frozen plans/round-76-claims.md read in full. This entry records source semantics and the frozen C1 policy, not an execution of its counter.
recheck: on-release — re-open the versioned specification when the scanner's declared CommonMark version changes.

# Fenced quotation is history, not a live receipt citation

## Decided fence semantics

CommonMark §4.5 makes fenced content literal text rather than parsed inlines.
For the lane's frozen C1 citation population, a receipt-looking path inside a
fenced code block is quoted history, not a live citation. CommonMark supplies
the syntax; the citation classification is the lane's declared policy, not a
claim that CommonMark defines evidence admission.

An opening fence uses at least three consecutive backticks or tildes, with up
to three leading spaces; the characters cannot be mixed. An optional info string
on a backtick opener must not contain a backtick. A closing fence uses the same
character, at least the opener's length, up to three leading spaces, and only
spaces or tabs afterward. A shorter fence or one with trailing non-whitespace
is content, not a closing delimiter. See retained HTML lines 2729–2750.

CommonMark allows an unclosed fence to consume the remaining lines through the
end of its containing block or document (lines 2750–2757). C1 deliberately adds
a stricter evidence-scanner rule: an unclosed fence is could-not-evaluate,
exit 2, not success with the rest of the citation population hidden. This is a
lane refusal policy, not a CommonMark syntax error. Likewise an empty live
population is could-not-evaluate, never evidence of complete classification.

## Why quoted bytes stay

The round-76 frozen C1 motivation identifies the round-75 lesson's superseded
and restored paragraphs as append-only history. Removing their obsolete path
strings to make the counter succeed would destroy the history the record must
retain. Preserve those bytes and classify their fenced context instead of
rewriting the record or treating a historical script mention as a present
receipt claim. The authoritative lane decision is the frozen plan's C1 scope
ruling; the external specification does not grant append-only exceptions.

## Boundary: no evidence laundering

Exclusion from the live citation population is not exclusion from checking or
disclosure. A quoted non-receipt must be counted in `fenced_quoted` and shown,
never silently dropped. A live non-receipt remains a finding, exit 1. Moving a
path into quotation does not authenticate it, bind its revision, or prove its
command ran. A record containing only fenced receipt-looking paths must refuse
with exit 2 rather than report an empty successful population.

These are falsifiable frozen obligations: `fence-unclosed` and `fence-none-live`
refuse with exit 2; `fence-live-nonreceipt` finds with exit 1. Their expected
outcomes come from the plan; this seat did not run those arms. Record-path
revision binding is a separate C1 rule and is not justified by CommonMark.

## Gate

URL: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
Access date: 2026-11-04. Section: **4.5 Fenced code blocks**.
Located quote, retained HTML lines 2760–2761:
“The content of a code fence is treated as literal text, not parsed as inlines.”

Retained exact response bytes:
`.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html`
SHA256: `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`.
The closing-fence rule is at lines 2741–2750; the unclosed-fence rule is at
lines 2750–2757. The source opening receipt and identifier census are retained
beside the page; the round lesson's Gate must carry this same URL, date, and
located quote under its owner's authorship.
