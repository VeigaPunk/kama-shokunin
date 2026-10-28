# SC03ProcEnvCmd — re-open S531, S532 (round 64, wave b, axis: operability)

Seat: source re-verification only. No code run against any counter; no live server started; no lane file
touched except this report and the receipts below.

## Method

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` HEAD = `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a`
  (the freeze commit); `git status --porcelain -- corpus/SOURCES.md` empty. The rows verified are the
  frozen rows.
- Re-opened both pages on 2026-10-28 and fetched raw bytes with curl.
- Byte equality: live fetch today is sha256-identical to the retained copies the rows cite.
  - `proc_pid_environ.html`: `93394d9edb801ad44e342e8e8ab057bea619d995803221edaf008226b2062c46` (live = retained = row claim)
  - `proc_pid_cmdline.html`: `1fc6816805fa28c1fe015700e7c40efc21d9bbc032e02c35a447004075a91f15` (live = retained = row claim)
- Version: both footlines read `Linux man-pages 6.19  2026-02-08` — matches the rows' anchor
  "Linux man-pages 6.19 (2026-02-08)". Colophon: tarball fetched 2026-09-09, HTML rendered 2026-09-09.
- Access dates: rows `opened` = 2026-10-28; this re-open = 2026-10-28. All quoted sentences were
  confirmed verbatim in the fetched HTML (line refs cited).
- No tool installed or upgraded (curl already present); pacman untouched.

## S531 — Linux proc_pid_environ(5) — VERIFIED, scope clause incomplete

Row scope (verbatim): "what `/proc/<pid>/environ` holds: the initial environment at execve, not later
modification; Linux only". Anchor: §DESCRIPTION. Kind docs, tier A, opened 2026-10-28, recheck 180d.

Quotes (both in §DESCRIPTION of the page; ≤25 words each):

1. > This file contains the initial environment that was set when the currently executing program was
   > started via execve(2).

   18 words. Location: §DESCRIPTION, first paragraph (`/proc/pid/environ` block), HTML lines 73-75.

2. > Permission to access this file is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check;
   > see ptrace(2).

   17 words. Location: §DESCRIPTION, final sentence, HTML lines 90-91.

Every limit the page states (§DESCRIPTION only; page has no other normative text):

| # | Limit (page wording, condensed) | In scope clause? |
|---|---|---|
| 1 | Contents = the initial environment set at execve(2) startup | YES ("the initial environment at execve") |
| 2 | Entries NUL-separated, possibly a trailing NUL | no |
| 3 | Post-execve environment changes (putenv(3), environ(7)) are NOT reflected: "will not reflect those changes" (HTML line 84) | YES ("not later modification") |
| 4 | Process may relocate the referenced memory via prctl(2) PR_SET_MM_ENV_START (line 88) | no |
| 5 | Access governed by ptrace access mode PTRACE_MODE_READ_FSCREDS (lines 90-91) | no |

Verdict: the scope clause is accurate in what it states and states limits 1 and 3; it omits the
permission mode (5), the NUL layout (2), and prctl relocation (4). The row's `teaches` column ("with the
stated limit that only the initial environment is visible") is true as written, but that limit is the
same one the scope already carries; it does not backfill 2/4/5. The intended use — a counter splitting
environ on NUL to detect an injected `LD_*` variable — leans on limit 2 (the format fact), which the
scope clause does not state.

## S532 — Linux proc_pid_cmdline(5) — VERIFIED, scope clause incomplete

Row scope (verbatim): "the layout of `/proc/<pid>/cmdline` as null-separated argument strings; Linux
only; a process may rewrite its own argv". Anchor: §DESCRIPTION. Kind docs, tier A, opened 2026-10-28,
recheck 180d.

Quotes (all in §DESCRIPTION; ≤25 words each):

1. > For processes which are still running, the command-line arguments appear in this file in the same
   > layout as they do in process memory

   23 words. Location: §DESCRIPTION, second paragraph, HTML lines 79-80.

2. > This read-only file holds the complete command line for the process, unless the process is a zombie.

   17 words. Location: §DESCRIPTION, first sentence, HTML lines 73-74.

3. > Think of this file as the command line that the process wants you to see.

   15 words. Location: §DESCRIPTION, final sentence, HTML lines 96-97.

Every limit/behaviour the page states (§DESCRIPTION only):

| # | Limit (page wording, condensed) | In scope clause? |
|---|---|---|
| 1 | File is read-only | no |
| 2 | For a zombie there is nothing in the file: a read returns 0 characters (lines 74-76) | no |
| 3 | Layout as in process memory; "If the process is well-behaved", NUL-separated strings with a further NUL after the last (lines 80-82) | YES ("null-separated argument strings") — but the page states this only as the well-behaved/common case |
| 4 | Processes "have the freedom to override the memory region and break assumptions about the contents or format" (lines 84-86) | no |
| 5 | Post-execve modification of the argv *strings* shows up here; "This is not the same thing as modifying the argv array" (lines 88-90) | YES ("a process may rewrite its own argv") |
| 6 | Process may relocate the referenced memory via prctl(2) PR_SET_MM_ARG_START (lines 93-94) | no |
| 7 | "the command line that the process wants you to see" — displayed argv is self-reported (lines 96-97) | no (the `teaches` column does state the consequence: "argv alone is spoofable") |

Verdict: the scope clause is accurate in what it states and states limits 3 and 5; it omits read-only
(1), zombie-empty (2), the well-behaved qualifier and format-breakage freedom (3's caveat, 4), prctl
relocation (6), and the wants-you-to-see self-reportedness (7, present only in `teaches`). No
permission mode is stated anywhere on this page — unlike the environ page there is no ptrace
access-mode sentence — so the scope clause stating none is faithful, not an omission.

## Cross-row findings

- Both anchors ("§DESCRIPTION") are correct: every fact cited above sits in DESCRIPTION; neither page
  has other normative sections.
- Both sha256 pins and the 6.19 (2026-02-08) version pin reproduce exactly against a fresh 2026-10-28
  fetch; the retained copies are current, not stale.
- Operability notes for counter designers (advisory, from the pages' stated limits, not a verdict):
  - PTRACE_MODE_READ_FSCREDS (S531 limit 5) governs environ reads; a same-uid child is normally
    readable, but a server that drops privileges or turns undumpable would blank this source
    [INFERENCE from ptrace(2) semantics, not stated on this page].
  - Zombie-empty (S532 limit 2) means a cmdline read of an unreaped dead child yields 0 bytes — an
    argv check must distinguish "empty because zombie" from "empty because spoofed".
- Suggested (not applied — leaves are edit-banned): either extend the two scope clauses with limits 5
  (S531) and 2/4/7 (S532), or note in the rows that the fuller limit list lives in this report's
  receipts. Left to the L1.

## Receipts

- Fresh fetch copies (byte-identical to retained, hashed above):
  `.ufo/waves/round-64/b/out/SC03ProcEnvCmd/proc_pid_environ.html`
  `.ufo/waves/round-64/b/out/SC03ProcEnvCmd/proc_pid_cmdline.html`
- Scratch root `/fast/scratch/hyaku/kama-r64/b/SC03ProcEnvCmd` removed after copying receipts.

## Remaining unknowns

- None for the assigned question. Both rows verify against today's live pages; the only defect class is
  scope-clause incompleteness (S531: permission mode + NUL format + prctl; S532: zombie-empty,
  read-only, format-breakage freedom, prctl, self-reportedness), enumerated above.
