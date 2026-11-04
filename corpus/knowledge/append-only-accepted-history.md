source: S547 — Git gitattributes(5), https://git-scm.com/docs/gitattributes (docs; round-75 reserved source id): `text` attribute, "Set" paragraph — "Line endings are normalized to LF in the index every time the file is checked in". Accessed 2026-11-04 by the retained round-75 source receipt; this entry inspected those bytes, not a fresh fetch.
verified-at: 2026-11-04 — frozen `plans/round-75-claims.md` read in full; `tools/append-only-audit.py` disclosure definitions read; audit JSON measured at `0908bab5cbf0ab6b435144fc525a3e18443dc08f`, exit 1. Retained source: `.ufo/waves/round-75/w1/sources/gitattributes.html`, sha256 ceb3351f931ae86283f51416cf0042fd78265eda59e5af7d09e17581ec0f77f7; access provenance: `.ufo/waves/round-75/measured/before/source-gitattributes.receipt`.
recheck: 180d — re-locate the `text` attribute's "Set" paragraph at the source URL; re-run the audit and accepted-history counter at an explicitly named revision.

# Accepted append-only history is graded history, not restoration

## The audit's three relevant classes

The audit computes deletion events from Git history and the append-only contract.
These three outcomes must not be confused with a register row's mechanical `class`:

- **restored**: the audit's window maximum holds all graded deleted lines again.
  This is historical restoration, not necessarily a claim about their presence at tip;
  `held_at_to` and `regressed` expose that distinction.
- **disclosed**: a non-restored event's missing graded lines are all covered by valid
  disclosure-ledger rows. The disclosure records loss; it is not restoration.
- **undisclosed**: the per-event JSON entries for missing graded lines not covered by
  valid disclosures. This is a list of line hashes, counts and mechanical classes,
  not an alternative spelling of the audit's event status. Event status can remain
  `unrestored` or `partial`; ungraded events and permitted lines are separate.

## The ledger introduction cutoff

`registry/append-only-disclosures.tsv` was introduced at
`b6bed925b032ac2c19b63ef4af358ebdd5922c26` (round 51). The audit permits a ledger
row to disclose only an event whose commit precedes that introduction. A deletion
once the ledger existed must be restored by append, never disclosed through a new
ledger row: otherwise a ledger could bless any later damage.

The measured freeze revision has **53 undisclosed events**, the post-ledger history
identified by frozen C3. The audit summary is `events=223 restored=87 disclosed=5
unrestored=53 ungraded=78 bad_declarations=5`; these outcomes sum to the event total.
The accepted register was absent when this entry's baseline was measured. These are
measurements of that revision, not a claim that the later register already passed.

Reproduce the baseline (audit exit 1 is expected, not a successful acceptance gate):

    python3 tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to 0908bab5cbf0ab6b435144fc525a3e18443dc08f --json

The original measurement omitted `--to`; its JSON `to` was the revision above.

## What the accepted register grades

Frozen C3 specifies `registry/append-only-accepted.tsv` rows with this tab-separated
schema:

    commit  file  line_sha256  count  class  note

Each row is machine-bound to an event the byte-frozen audit computes: `commit` and
`file` identify the event, `line_sha256` and `count` match its `undisclosed` entries,
and `class` matches their mechanical classification. A line key strips one trailing
carriage return before hashing. Mechanical classes are `revert` (subject starts
with `Revert "`), otherwise `in-place-edit` when the hunk adds lines, or `removal`.
The note records the commit subject and a one-line reason, not a substitute hash.
One event can require multiple rows; counting TSV rows does not count events.

The counter is `python3 tools/round75-append-accepted.py --repo <lane>`.
Its frozen rule rejects nonexistent events, restored-event rows, wrong hashes or
counts, and wrong mechanical classes; it also requires bound contract declarations.
This entry describes that contract, not an unobserved execution of the counter.

## Largest accepted-history candidate: the S537 LF re-land

Among the baseline's undisclosed events, the largest deletion event is round 65's
`ea33a78f2b0bcbbebcde60d2851a81c54746baa8`, `corpus/SOURCES.md`: **639 deletions**.
Its subject is `round-65: S537 byte-exact re-land (LF), wave receipts, lesson mistakes 9-10`.
The audit separates **277 permitted** A-row changes from **362 graded undisclosed**
lines, mechanically `in-place-edit`. Thus 639 is not the accepted missing-line count.

Reason: the S537 CRLF-to-LF re-land rewrote the source registry while restoring the
intended LF representation, rather than demonstrating later restoration of each
old graded line. S547's located rule explains the normalization mechanism: "Line
endings are normalized to LF in the index every time the file is checked in".
That Git rule grounds the reason; it does not exempt the event or prove every edit
in the commit harmless. The audit's observed counts remain authoritative.

## What acceptance does not show

The register never lowers the audit's `unrestored` count: the measured **53** remain
historical findings even if every corresponding event is accepted. Acceptance is
not restoration, retroactive disclosure, or permission for future deletion. It
never re-stamps a historical receipt, proves its run occurred, or changes the
byte-frozen audit. Its notes cite historical commit subjects, not invented re-runs.
