# S4Ldso — round 53: ld.so(8) source for "the swapped library runs at all"

**Verdict: REUSE — no new SOURCES row needed; the claim is grounded by existing row S079 (corpus/SOURCES.md:91), with the unpacked-tree consequence cited as S079 + lane own-work. Deliverables: reuse note, contingent S510 draft, quote-verification receipt, and the fetched page, in `out/S4Ldso/`.**

## Question

Source candidate for why the swapped library runs at all: does
"LD_LIBRARY_PATH directories are searched before the cache and defaults, so a file
placed in the unpacked tree is loaded by name" need a new row, or does an existing
row (S057/S067/S079) already ground it?

## Decision and basis

**S079 grounds the loader half.** Its anchor ("DESCRIPTION dependency preamble and
steps 1–5", `corpus/SOURCES.md:91`) contains the verbatim step list; step (2)
LD_LIBRARY_PATH is numbered before step (4) `/etc/ld.so.cache` and step (5)
`/lib,/usr/lib`. Its teaches — "slash-less dependencies follow the documented search
order" — is exactly the precedence claim. This is the same grounding pattern round 19
used to settle "(2) precedes (3)" without a new row
(`.ufo/waves/round-19/build/advice/LdsoSearchOrder.md:30`), and round 21 recorded all
five steps at `.ufo/waves/round-21/falsify/advice/SrcLdSoNeeded.md:16`. Unlike S067's
superseded "directory search at every exec" wording (corrected by S079 because step 4
is a cache read), the precedence claim contradicts nothing else on the page.

**The tree half is not page content.** "A file placed in the unpacked tree is loaded
by name" combines S079 (the server's DT_NEEDED names are slash-less sonames; round-16
sentinel verified `NEEDED libllama-server-impl.so`, `RUNPATH [$ORIGIN]`, no DT_RPATH,
`.ufo/waves/round-16/build/advice/SentinelInstallChain.md:46-48`) with lane own-work:
the launcher sets `child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)` at
`tools/kama-llamacpp-live.py:2150` (build c22602bd; help text `:1563-1565`). The
causal sentence is lane inference and should be marked/cited as such.

**Why not a new row:** strict entailment of an existing anchor+teaches; a 4th
ld.so(8) URL repeat adds a W04 (`scripts/sources-census.sh:644-645`) of the accepted
class already carried by S057/S067/S079 (CensusPrefetch.md:41), and a same-scope row
would be a hard E04 (`:646-648`). A contingent S510 draft is provided anyway in
`out/S4Ldso/S510-row-draft-contingent.md` in case a frozen leg needs a teaches-level
ID; recommended default is reuse.

## Evidence (commands, outputs, exits)

1. Lane rows read: `corpus/SOURCES.md:69` (S057), `:79` (S067), `:91` (S079);
   header `:11` confirms the eleven-column contract; max registry id S509
   (`grep -oE '^\| S[0-9]+' … | sort -n | tail -1` → 509).
2. `curl -sSL -o ld.so.8.html https://man7.org/linux/man-pages/man8/ld.so.8.html` →
   exit 0, 41398 bytes, sha256 `d9b7737e…f83` — byte-identical to the fetch recorded
   when S057 was admitted (`.ufo/waves/round-19/build/advice/DraftS057.md:6`), so the
   page S079 anchored is unchanged today. Footer: man-pages 6.19, 2026-08-03.
3. Quote verification over the extracted text (receipt:
   `out/S4Ldso/quote-verification.txt`): preamble 1 occurrence, 19 words; step (2)
   "Using the environment variable LD_LIBRARY_PATH, unless the executable is being
   run in secure-execution mode (see below), in which case this variable is ignored."
   1 occurrence, 23 words (≤25 Gate limit); step (4) 21 words (matches S079's
   round-22 Gate quote, `corpus/lessons/round-22.md:133`); step (5) 8 words.
4. Launcher mechanism: `git -C <clone> show c22602bd:tools/kama-llamacpp-live.py |
   sed -n '2135,2165p'` → `:2150 child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)`
   with the round-52 comment "$ORIGIN cannot find the install tree's libraries any
   more"; help text `:1563-1565`.
5. Live citations of the grounding rows: `corpus/knowledge/llamacpp-loading-lifecycle.md:336`
   ("re-resolves a slash-less DT_NEEDED name … (S067)", line 371 "S067, whose step (4)
   reads the ldconfig cache") and `corpus/lessons/round-22.md:133` (S079 Gate row).
6. Round-53 build asserts the threat without an ld.so citation yet
   (`corpus/lessons/round-53.md:9`: "a library swapped after the member check would
   run unseen"), so the reuse note is prospective phrasing for §Errata/Planned
   (round 54), included in the deliverable.

## Boundary conditions recorded with the sentence

- Step (2) is void in secure-execution mode ("unless the executable is being run in
  secure-execution mode … this variable is ignored", verbatim) — inapplicable to the
  replay's unprivileged child, but it bounds the claim.
- LD_PRELOAD (the preregistration's other C1 ablation) is a different mechanism on the
  same page; neither S079 nor this note grounds it.
- The launcher's stated reason for needing LD_LIBRARY_PATH at all (memfd exe, $ORIGIN
  degeneration) is its own observation; $ORIGIN mechanism itself is S057's scope.

## Deliverables written

- `out/S4Ldso/reuse-note-S079-ld-library-path.md` — the reuse decision, citation
  phrasing, boundary conditions.
- `out/S4Ldso/S510-row-draft-contingent.md` — contingent eleven-column row draft
  (CONTINGENT; delete at integration if reuse stands).
- `out/S4Ldso/quote-verification.txt`, `out/S4Ldso/ld.so.8.html`, `out/S4Ldso/ld.so.8.txt`
  — evidence copies.

No lane files edited; no tools installed; no services started. Scratch
`/fast/scratch/hyaku/kama-r53/S4Ldso` (lane clone + fetch) removed after writing.
