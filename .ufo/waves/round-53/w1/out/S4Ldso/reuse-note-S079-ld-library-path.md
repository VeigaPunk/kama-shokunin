# Reuse note — "LD_LIBRARY_PATH before cache/defaults" is grounded by S079; no new row needed

Seat: S4Ldso (round 53, wave kama-r53-w1). Date: 2026-10-27.
Claim under examination: "LD_LIBRARY_PATH directories are searched before the cache
and defaults, so a file placed in the unpacked tree is loaded by name" — the source
candidate for *why the swapped library runs at all* in the C1 library-swap ablation
(preregistration controls: "a replay that flips one byte in an executable range of an
unpacked library after its member check").

## Verdict

**Reuse. No new SOURCES row is needed.** The grounding row is **S079**
(`corpus/SOURCES.md:91`), whose anchor is the ld.so(8) DESCRIPTION dependency
preamble and search steps 1–5. The claim's loader half is literal numbered-list
content inside that anchor; the tree half is lane own-work plus S079, and must be
cited as such.

## Why S079 grounds it

S079's cells (verbatim from `corpus/SOURCES.md:91`):

- scope: "slash-less shared-object lookup steps, not symlink inspection or a directory scan at every exec"
- anchor: "DESCRIPTION dependency preamble and steps 1–5, especially cache step4; man-pages 6.19; reopened 2026-10-21"
- teaches: "supersedes S067 — slash-less dependencies follow the documented search order; step4 reads ld.so.cache, not a directory walk. The page supplies no symlink-resolution claim."

The "documented search order" that S079's anchor covers is, verbatim on the opened
page (man7.org/linux/man-pages/man8/ld.so.8.html, man-pages 6.19, page dated
2026-08-03; re-opened by this seat 2026-10-27, sha256
d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83 — **byte-identical
to the fetch recorded when S057 was admitted in round 19**, see
`.ufo/waves/round-19/build/advice/DraftS057.md:6`):

> "If a shared object dependency does not contain a slash, then it is searched for in the following order:" (preamble, 19 words)

1. DT_RPATH (only if no DT_RUNPATH)
2. "Using the environment variable LD_LIBRARY_PATH, unless the executable is being run in secure-execution mode (see below), in which case this variable is ignored." (23 words, ≤25)
3. DT_RUNPATH (direct dependencies only)
4. "From the cache file /etc/ld.so.cache, which contains a compiled list of candidate shared objects previously found in the augmented library path." (21 words — already quoted in S079's round-22 Gate row, `corpus/lessons/round-22.md:133`)
5. "In the default path /lib, and then /usr/lib." (8 words)

Step (2) is numbered before steps (4) and (5): "LD_LIBRARY_PATH directories are
searched before the cache and defaults" is a literal reading of the anchored list,
not an extrapolation beyond it. S079's teaches ("slash-less dependencies follow the
documented search order") is exactly this claim. Unlike S067's superseded "directory
search at every exec" wording (which S079 corrected because step 4 is a cache read,
not a directory walk), the precedence claim creates no tension with any other step.

Lane precedent for grounding an ordering claim from this anchored list without a new
row: round-19 seat LdsoSearchOrder settled "(2) LD_LIBRARY_PATH precedes (3)
DT_RUNPATH" the same way — "This settles the claim tagged [INFERENCE] at
.ufo/waves/round-16/build/advice/SentinelLiveSafety.md:41"
(`.ufo/waves/round-19/build/advice/LdsoSearchOrder.md:30`); round-21 recorded all
five steps in `.ufo/waves/round-21/falsify/advice/SrcLdSoNeeded.md:16`.

## What is NOT grounded by any row (cite as own-work)

"…so a file placed in the unpacked tree is loaded by name" is a compound of:

- **S079**: the server's DT_NEEDED entries are slash-less sonames
  (`libllama-server-impl.so`, `libggml.so.0`, …), so they resolve by the step list
  above. Round-16 sentinel verified the binary carries `NEEDED libllama-server-impl.so`
  etc. and `RUNPATH [$ORIGIN]` with no DT_RPATH
  (`.ufo/waves/round-16/build/advice/SentinelInstallChain.md:46-48`).
- **Own-work (lane tool)**: the launcher sets
  `child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)` before exec'ing the
  memfd image (`tools/kama-llamacpp-live.py:2150` at build c22602bd; help text
  `:1563-1565`: "LD_LIBRARY_PATH names --server's directory because $ORIGIN no longer
  does"). With step (2) naming the unpacked tree, the tree's file is the one opened
  for the soname — which is exactly why a post-check byte swap in that tree runs, and
  why C1's `code` leg reads /proc/<pid>/mem instead of trusting the path.
- The causal sentence combining these is lane inference: mark it [INFERENCE] or
  attribute it to the two citations jointly, the same convention round-19 used for
  the settled ordering claim.

## Suggested citation phrasing (for lesson §Errata / SCORECARD §Round 53 or Planned round 54)

> A library swapped inside the unpacked tree still runs because the loader resolves
> the server's slash-less DT_NEEDED sonames by the documented step order (S079):
> LD_LIBRARY_PATH — which the launcher sets to the unpacked tree
> (kama-llamacpp-live.py:2150) — is step (2), before the ld.so.cache step (4) and the
> /lib,/usr/lib defaults step (5). [tree-loading consequence: S079 + own-work]

## Boundary conditions to keep with the sentence

- Step (2) applies "unless the executable is being run in secure-execution mode, in
  which case this variable is ignored" (verbatim in the step). The replay's server is
  an unprivileged child of the replay (no setuid), so the caveat does not bite here;
  a setuid/sudo'd consumer would void it.
- This grounds DT_NEEDED resolution only. The preregistration's other ablation —
  "a replay that loads one library from outside the tree (LD_PRELOAD of a user-owned
  copy)" — is LD_PRELOAD, a different mechanism on the same page; S079 does not
  ground it and this note does not either.
- Why LD_LIBRARY_PATH is needed at all for a memfd-exec'd server ($ORIGIN
  degenerating for a /memfd:… exe) is the launcher's stated reason; the $ORIGIN
  mechanism itself is S057's scope.

## Why not a new row

- The claim's source half is a strict entailment of an existing row's anchor+teaches;
  a new row would restate one clause of a list S079 already anchors.
- `scripts/sources-census.sh:644-645` flags every cross-scope URL repeat as W04; the
  S057/S067/S079 triple already carries these as accepted structural warnings
  (`.ufo/waves/round-19/build/advice/CensusPrefetch.md:41`), and a fourth ld.so(8)
  row adds another without adding scope.
- A same-URL+same-scope non-supersession row would be **E04** (hard error,
  `sources-census.sh:646-648`); only a new scope string would be W04, which is what
  the draft below would have to do.

## Contingency

If the integrator wants a teaches-level row naming LD_LIBRARY_PATH precedence
(e.g. because a frozen counter leg or QUALITY row will cite the sentence by ID), a
contingent S510 draft is provided in `S510-row-draft-contingent.md` in this
directory. Recommended default is still reuse: cite S079 and locate the step-(2)
quote in the lesson Gate, as round 19 did for the (2)-before-(3) ordering.
