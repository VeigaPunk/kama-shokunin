VERDICT: partial - origin is the R20 report write (07:12:32 -03:00; first commit fleet 04eb5d2 at 07:13:14); the SCORECARD 891-892 pair is the referent source, but the token is a two-hash splice, not a verbatim copy

# RevengeSpliceOrigin: token 0957ce619789d13d894ef21bc863486bcb35b56c

Scope: lane `kama-shokunin` (master `a29bb84`), fleet `/home/vgpnk/Projects/shokunin`. Read-only on lane, fleet, MANIFEST and config. Installs/updates: none (git, python3 only). Scratch: none under /tmp. Transcript timestamps are UTC `Z`; shown here as -03:00.

## 1. Findings
- **First session-written occurrence:** `KamaR18Recovery.jsonl` L2090 (10:12:32.839Z = 07:12:32 -03:00), a `write` of `/home/vgpnk/Projects/shokunin/.ufo/reports/round-20/kama.md` (11,786 chars). Line 7 carries the token; line 10 carries the correct `0957ce619789d13bb5779606078fa1498114d2c7`.
- **First committed occurrence:** fleet `04eb5d2` "round-20: kama report", 07:13:14, `.ufo/reports/round-20/kama.md:7`. It is still the only fleet `.ufo` file holding the token.
- **Not origins (they quote it):** fleet `221707d` closure note D1 (07:16:43); lane errata row `registry/report-landing-errata.tsv:3` in `00aa148`/`a29bb84` (written 07:24:48, committed 07:24:53); R21 dispatch, spec and advice drafts (07:28 onward).
- **Structure:** token = first 15 hex of `0957ce619789d13bb5779606078fa1498114d2c7` (measured tree) + last 25 hex of `33a6777866d0f63d894ef21bc863486bcb35b56c` (work/frozen population). It is the only two-part splice over all 40-hex objects in both repos. Boundary k=14 or 15 gives the same string because `A[14]=B[14]='3'`; `A[15]='b'`, `B[15]='d'`.
- **Errata prose is off by one:** row 3 says "first 16 hex of 0957ce61 ... last 24 hex of 33a67778". Correct is 15 + 25. Its correction column is right.

## 2. Timeline (local -03:00)
- 04:05:09 lane `33a67778` authored (work/frozen population); 05:23:44 `0957ce61` authored (measured tree, child of 33a67778).
- 05:01:22 and 05:23:46: CloseKama18 bash results print `landed 33a6777866d0f63d894ef21bc863486bcb35b56c` (L702) and `landed 0957ce619789d13bb5779606078fa1498114d2c7` (L763).
- 05:25:52 CloseKama18 `edit` (L791) writes SCORECARD.md: "Work/frozen-population commit `33a6777866d0f63d894ef21bc863486bcb35b56c`; measured tree `0957ce619789d13bb5779606078fa1498114d2c7`." These are exact copies of the `landed` outputs.
- 05:38:15 KamaR18Recovery `read` of SCORECARD.md (L1061): the pair is in its context.
- 06:08:05 lane master-ancestor `92b1462` carries the pair at SCORECARD 891-892, LOG 1204-1206 and lesson 133-134. jj siblings `c823d54`, `bd1886e`, `2109091` carry identical text but are not on master.
- 07:12:32 KamaR18Recovery `write` of the report, token at line 7 (L2090). This is the first token-bearing line in any transcript.
- 07:13:05.636 `edit` at line 67 only (L2096-2098; file mtime 07:13:05.636). Line 7 is untouched; nothing repairs it before commit.
- 07:13:14 commit `04eb5d2` via `fleet-commit.sh --as kama` (L2099).

## 3. Mechanism
- **Verbatim copy: refuted.** The token is in no git object, no committed blob on any ref before 04eb5d2, and no transcript line before 10:12:32Z. The pair's two hashes sit on separate lines and neither line contains the token.
- **Source: confirmed.** Both referents are exact and adjacent in the pair the author read at 05:38. The sentence needed two commits in one hash slot: "Reused the committed R20 implementation/frozen population and original measurement at `<hash>`".
- **Likely mechanism** [INFERENCE]: a generation-time source switch. The emitted 40-hex string copies the measured-tree hash through hex 15, then continues from the work hash, switching at the one character both share (index 14, `3`). Transcript reasoning blocks hold only headings, and no tool call emitted the token before the write.

## 4. Verbatim sources
- lane `SCORECARD.md:891-892` (rev `92b1462`; unchanged at `a29bb84`): "Work/frozen-population commit `33a6777866d0f63d894ef21bc863486bcb35b56c`;" / "measured tree `0957ce619789d13bb5779606078fa1498114d2c7`."
- fleet `04eb5d2` `kama.md:7`: "...original measurement at `0957ce619789d13d894ef21bc863486bcb35b56c`;"
- fleet `04eb5d2` `kama.md:10`: "...at `0957ce619789d13bb5779606078fa1498114d2c7`" (correct).
- errata row 3 (`00aa148`): "splices the first 16 hex of 0957ce61 ... with the last 24 hex of 33a67778".

## 5. Commands and exit codes (executed)
- `git cat-file -t <token>`: lane rc 128, fleet rc 128. `git cat-file -t 0957ce619789d13bb5779606078fa1498114d2c7` (lane): rc 0.
- `git log --all -S<token>`: lane `a29bb84`, `00aa148`; fleet `221707d`, `04eb5d2`. All rc 0.
- `git log --all -S33a6777866d0f63d894ef21bc863486bcb35b56c`: lane first hit `c823d54` (rc 0); fleet none (rc 0).
- `git merge-base --is-ancestor <c> master`: `c823d54` 1, `bd1886e` 1, `2109091` 1, `00aa148` 1, `92b1462` 0, `a29bb84` 0; fleet `04eb5d2` 0.
- `git blame -L 884,896 -- SCORECARD.md` (lane): 891-892 attributed to `92b1462`, rc 0. `git diff --stat c823d54 92b1462 -- SCORECARD.md LOG.md corpus/lessons/round-20.md`: empty, rc 0.
- `python3 splice_check.py`: rc 0 (RESULT PASS). `python3 origin_trace.py`: rc 0. `python3 origin_trace.py --full`: rc 0; 63 session files contain the token; earliest line KamaR18Recovery L2090.
- Fleet `.ufo` grep (tool) for the exact token: only `.ufo/reports/round-20/kama.md:7`.

## 6. Limits
- Fleet working tree outside `.ufo` was not scanned on disk (eval walk timed out at 900 s; tool grep times out at 30 s on the fleet root). Covered instead: all committed content and objects, every omp transcript, and `.ufo` trees.
- The lane object DB grew during the run (3,582 to 4,249 40-hex objects; cause [INFERENCE]: other seats' jj snapshots). The splice result is unchanged. Transcript count rose 61 to 63 between two scans (cause [INFERENCE]: sibling seats still writing transcripts).
- No lane, fleet or errata edits. Suggested fix for the L1 (ledger is append-only): correct row 3's evidence prose to 15 + 25.

Artifacts: `.ufo/waves/round-21/build/out/KamaR21.RevengeSpliceOrigin-6/` (`splice_check.py`, `origin_trace.py`, stdout captures).
