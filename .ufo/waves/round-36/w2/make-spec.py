#!/usr/bin/env python3
"""Write the round-36 v1 falsify wave (w2) spec. Does not dispatch.

Wave 1 (32 seats) is inherited from the attempt-1 L1 and settled; 18 of its
seats died on a provider 403. Wave 2 is the falsify half of the default
two-v1-wave shape: every item attacks something wave 1 prepared or a
committed byte the round's frozen claims rest on.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w2/spec.json")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
KNOW = "/home/vgpnk/Projects/shokuknow"
BASE = "e5a8ececf3d60fd53b36bb74299693a29e8f74b6"

CONTEXT = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Goal
kama lane, round 36, attempt 2, wave 2 of a two-v1-wave round: the falsify wave. The L1 (Kimi fresh L1) holds the canonical planner seat. A planner role is never a swarm role. Wave 1 already ran and settled; every wave-2 item attacks something wave 1 prepared or a committed byte the frozen claims rest on.

# Lane and bounds
Lane repo: /home/vgpnk/Projects/shokunin/kama-shokunin. Your one allowed report write is the absolute path named by your Report trailer: /home/vgpnk/Projects/shokunin/kama-shokunin/<that relative path>. Scratch files go only in your seat directory /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w2/out/<YourSeatName>/. Never mutate the fleet repo /home/vgpnk/Projects/shokunin, any sibling lane, the lane jj state, or the lane Git index. Never run git add/commit/stash/checkout/switch/reset/pull/push and never run a mutating jj command. Read-only git is permitted. Never write into /home/vgpnk/Projects/shokuknow. Never edit MISSION.md, corpus/SOURCES.md, corpus/README.md, corpus/QUALITY.md, SCORECARD.md, LOG.md, or considerthese/. Never read secrets or credentials. No endpoint-admin actions and no service restoration. A git-writing gate must run on a sandbox clone in your seat directory, never in the lane.
Every Report: trailer path is relative to /home/vgpnk/Projects/shokunin/kama-shokunin — write it at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path>. Never message agent://all. You are a leaf. Do not spawn subagents.

# Frozen claims (do not retarget)
C1 calibration 7 -> 7. Predicate: A frozen r35 routed statement is corrected iff corpus/lessons/round-36.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the correction row does not contain the token 429, and the r35 lesson blob and the r35 fleet report blob are unchanged.
Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>
C2 coverage 9 -> 9. Predicate: The round-36 coverage block names knowledge/sglang-native-route-deprecation.md, that file exists, and it cites an S-id present in corpus/SOURCES.md at the tip and absent at base e5a8ececf3d60fd53b36bb74299693a29e8f74b6; none of those three hold at that base.
Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>
Do-nothing controls already printed met False. Do not change either predicate.

# What wave 1 produced (your attack surface)
Drafts to attack, all read-only:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/correction-lines.md  (the four R35-* correction rows)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/append-block.md  (the two drafted SOURCES rows, ids S328 and S329)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/sglang-native-route-deprecation.md  (the drafted knowledge entry)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/validate/corpus/SOURCES.md  (the census mirror: lane registry + the two drafted rows)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/guard/  (the indent-collision guard proof)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/assimilation/quarantine-slice  (the 7 kama rows of the campaign absent-defect register)

Two facts the L1 re-derived this round with curl, for you to check independently:
- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx returns HTTP 200; the string get_model_info occurs 2 times and the string /model_info occurs 0 times; line 9 is the route-list entry.
- https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py returns HTTP 200; lines 790-791 carry the deprecation warning for /get_model_info.

# Frontier
Theme: a published native route name is not the engine's current route. One theme, one admitted entry. The staged package under /home/vgpnk/Projects/shokuknow is READ-ONLY: never write, commit, fetch or push there, and never run renumber-staged.py, merge-plan.py, quote-lint.py or absent-defect-register.py (they write into the campaign tree). Quarantine rows are not appendable until they are hand-checked; every slice row carries an S-id. considerthese is operator-authored: mine, never edit.

# Tooling
You may install or upgrade tools that help the task — read /home/vgpnk/.omp/agent/RULES.md first. Install via uv tool, npx, or an official binary in ~/.local/bin. Pacman guard: ALL pacman transactions are PAUSED host-wide. Never run pacman.
"""

ITEMS = [
    # --- attack seats (19 of 32: reviewer, critic, mutation-tester, labrat) ---
    ("RevC1S211", "reviewer", "calibration", f"""# Target
The R35-S211 arm of holds() in {LANE}/tools/round36-statement-audit.py, and the committed bytes it reads.
# Task
Re-derive each sub-condition of the R35-S211 arm by hand from committed bytes: does the committed .ufo/waves/round-35/w1/out/ScoutQuarantineS211.md contain "fetched successfully", "still-live" and "absent"? Does the committed corpus/lessons/round-35-verifier-spotcheck.md contain "HTTP 200" and "still-live"? Does the drafted row in {LANE}/.ufo/waves/round-36/assimilation/correction-lines.md contain "ScoutQuarantineS211.md", "still-live" and "200"? Does it contain the token 429? State each answer with the file and line you read. Do not edit any file.
Report: .ufo/waves/round-36/w2/out/RevC1S211.md"""),
    ("RevC1Words", "reviewer", "calibration", f"""# Target
The S327 quote in the committed {LANE}/corpus/lessons/round-35.md.
# Task
Read the committed blob with git -C {LANE} show e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/lessons/round-35.md. Extract the sentence between 'Quote: "' and its closing quote. Count whitespace-delimited words. State the count and the recorded count in the same paragraph. Does the drafted R35-WORDS row in {LANE}/.ufo/waves/round-36/assimilation/correction-lines.md contain "20 words"? Do not edit the lesson.
Report: .ufo/waves/round-36/w2/out/RevC1Words.md"""),
    ("RevC1Mirror", "reviewer", "calibration", f"""# Target
The R35-MIRROR arm of holds() in {LANE}/tools/round36-statement-audit.py.
# Task
Check that the committed {LANE}/corpus/lessons/round-35-verifier-spotcheck.md contains "11 symlinks" and "84 regular files". Check that the fleet's committed round-35 report at {FLEET} (.ufo/reports/round-35/kama.md, read with git -C {FLEET} show HEAD:.ufo/reports/round-35/kama.md) contains "symlink tree". Check that the drafted R35-MIRROR row contains "mixed", "11" and "84". State each answer with file and line. Do not edit either file.
Report: .ufo/waves/round-36/w2/out/RevC1Mirror.md"""),
    ("RevC1KeepPaths", "reviewer", "calibration", f"""# Target
The R35-KEEP arm of holds() in {LANE}/tools/round36-statement-audit.py.
# Task
Run git -C {LANE} ls-tree -r --name-only e5a8ececf3d60fd53b36bb74299693a29e8f74b6 and say whether either ScribeGate HTML path or .ufo/waves/round-35/assimilation/validate/ appears. Run git -C {LANE} status --porcelain and list the seven paths that are the r35 leftovers. Say whether each of the seven is named in the drafted R35-KEEP row, and whether the row contains the classes seat-log-flush, overwrite-not-committed, mixed-mirror-not-committed, helper-skipped and the size 1066624. Do not add, commit or delete anything.
Report: .ufo/waves/round-36/w2/out/RevC1KeepPaths.md"""),
    ("RevC1Selftest", "reviewer", "calibration", f"""# Target
{LANE}/tools/round36-statement-audit.py --selftest
# Task
Run python3 {LANE}/tools/round36-statement-audit.py --repo {LANE} --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 --selftest. Paste the output lines and the exit code. Say what the selftest proves and what it does not. Do not edit the counter.
Report: .ufo/waves/round-36/w2/out/RevC1Selftest.md"""),
    ("CritC1Forbidden", "critic", "calibration", f"""# Target
The FORBIDDEN token check in {LANE}/tools/round36-statement-audit.py.
# Task
In your seat directory only, construct a candidate correction row for R35-S211 that contains the token the counter forbids, run the counter's own score() logic on it, and show the false_corrections count it produces. Show the constant's value and where it is compared. State whether a correction row that denies the token but still spells it would be counted as a false correction. Do not write that token into any lane file, and do not edit the counter.
Report: .ufo/waves/round-36/w2/out/CritC1Forbidden.md"""),
    ("CritC1Noop", "critic", "calibration", f"""# Target
The C1 do-nothing control.
# Task
Run python3 {LANE}/tools/round36-statement-audit.py --repo {LANE} --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6. Paste the output line and the exit code. Say whether the do-nothing state meets the target. If it does, the counter is wrong. Do not edit the counter.
Report: .ufo/waves/round-36/w2/out/CritC1Noop.md"""),
    ("CritC2OldId", "critic", "coverage", f"""# Target
The cited_new rule in {LANE}/tools/round36-coverage-audit.py.
# Task
Read score(). Say whether an entry citing S006, which is already present at base e5a8ececf3d60fd53b36bb74299693a29e8f74b6, can set cited_new to 1. Verify S006 is present at base by reading the base blob with git -C {LANE} show e5a8ececf3d60fd53b36bb74299693a29e8f74b6:corpus/SOURCES.md. Paste the C2 selftest line. Do not construct files in the lane corpus.
Report: .ufo/waves/round-36/w2/out/CritC2OldId.md"""),
    ("CritC2Outside", "critic", "coverage", f"""# Target
The heading rule in {LANE}/tools/round36-coverage-audit.py.
# Task
Read block_names(). Say whether a mention of knowledge/sglang-native-route-deprecation.md outside the heading '## Coverage map — round 36 addition' sets named to 1. Run the C2 selftest and paste the line and exit code. Do not create that heading in {LANE}/corpus/README.md.
Report: .ufo/waves/round-36/w2/out/CritC2Outside.md"""),
    ("MutC1Blob", "mutation-tester", "calibration", f"""# Target
The pinned lesson blob in {LANE}/tools/round36-statement-audit.py.
# Task
Make a sandbox clone of the lane in your seat directory (git clone --no-local {LANE} <your-dir>/clone, or a copy of the working tree plus a git init; a clone is preferred). In the clone only, change corpus/lessons/round-35.md so its blob differs from the pinned constant, commit it, and run the counter against that clone with --tip pointing at the new commit. Paste the output line. State which field flipped and whether met went False. Do not touch the real lane repo.
Report: .ufo/waves/round-36/w2/out/MutC1Blob.md"""),
    ("MutC1Keep", "mutation-tester", "calibration", f"""# Target
The R35-KEEP tracked-path check in {LANE}/tools/round36-statement-audit.py.
# Task
In a sandbox clone in your seat directory only, add one of the two r35 ScribeGate HTML files to the index (git add) and commit it, then run the counter against that clone with --tip at the new commit. Paste the output line. Say whether R35-KEEP fails once either HTML path is tracked. Do not touch the real lane repo.
Report: .ufo/waves/round-36/w2/out/MutC1Keep.md"""),
    ("MutC2NoId", "mutation-tester", "coverage", f"""# Target
The cited_new rule in {LANE}/tools/round36-coverage-audit.py.
# Task
In a sandbox clone in your seat directory only, add a knowledge entry that cites an S-id which is absent from that clone's corpus/SOURCES.md, then run the counter against the clone with --tip at a commit carrying the entry. Paste the output line. Say whether cited_new stays 0. Do not touch the real lane repo.
Report: .ufo/waves/round-36/w2/out/MutC2NoId.md"""),
    ("MutEntryWord", "mutation-tester", "quality", f"""# Target
The <=25-word located-quote rule that governs every new SOURCES row.
# Task
In your seat directory, take the drafted row pair in {LANE}/.ufo/waves/round-36/assimilation/append-block.md and the drafted entry in {LANE}/.ufo/waves/round-36/assimilation/sglang-native-route-deprecation.md. Count the whitespace-delimited words of each located quote in the entry. Then write a scratch variant of one quote that is 26 words long and show that a length check at 25 rejects it. State the count of each real quote and whether both rows would pass a 25-word check. Do not write into the lane corpus.
Report: .ufo/waves/round-36/w2/out/MutEntryWord.md"""),
    ("RevQ224", "reviewer", "calibration", f"""# Target
Quarantine row S224 in {KNOW}/.ufo/waves/corpus-expansion-1/absent-defect-register.md, URL https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/
# Task
Fetch the URL. Say whether the page contains check_health, and say whether it contains the words render-only or the phrase always return 200. Quote at most 25 words from the health handler you find. Verdict: present, absent, or quote-not-located. State what you measured. Do not edit the register and do not append a row.
Report: .ufo/waves/round-36/w2/out/RevQ224.md"""),
    ("RevQ202", "reviewer", "calibration", f"""# Target
Quarantine row S202 in {KNOW}/.ufo/waves/corpus-expansion-1/absent-defect-register.md, URL https://docs.docker.com/reference/compose-file/services/
# Task
Fetch the URL. Locate the register's quoted span about service_healthy and as indicated by healthcheck. Quote at most 25 words from the page. Verdict: present, absent, or unreachable. Say whether the quoted span is on the page you read. Do not edit the register and do not append a row.
Report: .ufo/waves/round-36/w2/out/RevQ202.md"""),
    ("RevQ210", "reviewer", "calibration", f"""# Target
Quarantine row S210 in {KNOW}/.ufo/waves/corpus-expansion-1/absent-defect-register.md, URL https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide
# Task
Fetch the URL. Record the HTTP status. Say whether the page contains the literal text Page Not Found, and whether it contains sglang.launch_server. Verdict: present, absent, or unreachable. State what you measured. Do not edit the register and do not append a row.
Report: .ufo/waves/round-36/w2/out/RevQ210.md"""),
    # --- build / verify seats (13 of 32) ---
    ("RevS328", "revenger", "coverage", f"""# Target
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx
# Task
Fetch the URL. Record the HTTP status and today's access date. Count occurrences of get_model_info and of the route /model_info. Locate the route-list line and give its line number. Quote at most 25 words from a sentence on the page, with the line number. Compare what you measured against the drafted row S328 in {LANE}/.ufo/waves/round-36/assimilation/append-block.md: does the drafted anchor and scope cell match what you found? Do not append a source row and do not edit the lane corpus.
Report: .ufo/waves/round-36/w2/out/RevS328.md"""),
    ("RevS329", "revenger", "coverage", f"""# Target
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
# Task
Fetch the URL. Record the HTTP status. Locate the deprecation warning for /get_model_info and give its line numbers. Quote at most 25 words. Say whether /model_info is the replacement named in that warning, and whether the file registers a route at /model_info. Compare against the drafted row S329 in {LANE}/.ufo/waves/round-36/assimilation/append-block.md: does the drafted anchor match what you found? Do not append a source row and do not edit the lane corpus.
Report: .ufo/waves/round-36/w2/out/RevS329.md"""),
    ("RevQ211", "revenger", "calibration", f"""# Target
Quarantine row S211 in {KNOW}/.ufo/waves/corpus-expansion-1/absent-defect-register.md, URL https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md
# Task
Fetch the URL. Record the HTTP status you observe. Say whether the token still-live occurs anywhere in the page text you read. Verdict: present, absent, or unreachable. Do not copy a prior lesson's classification into your verdict line; state what you measured. Do not edit the register and do not append a row.
Report: .ufo/waves/round-36/w2/out/RevQ211.md"""),
    ("RevQ230", "revenger", "calibration", f"""# Target
Quarantine row S230 in {KNOW}/.ufo/waves/corpus-expansion-1/absent-defect-register.md, URL https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
# Task
Fetch the URL. Say whether the register's quoted sentence is present, and quote it in at most 25 words with line numbers. Verdict: present, absent, or unreachable. State whether the row's URL is the same URL the lane's drafted row S329 in {LANE}/.ufo/waves/round-36/assimilation/append-block.md uses, and say what that means for appending both. Do not edit the register.
Report: .ufo/waves/round-36/w2/out/RevQ230.md"""),
    ("RevEntry", "reviewer", "quality", f"""# Target
The drafted entry {LANE}/.ufo/waves/round-36/assimilation/sglang-native-route-deprecation.md and the drafted rows {LANE}/.ufo/waves/round-36/assimilation/append-block.md
# Task
For each drafted row: does every S-id it cites resolve in the census mirror {LANE}/.ufo/waves/round-36/assimilation/validate/corpus/SOURCES.md? Does any cell contain a literal or escaped pipe? Is the recheck cell a valid ISO date, an Nd value or a symbolic cadence? Is the used-by cell exactly the admitted entry that cites the row? Does the entry cite only sources that appear in its own source lines? Is every located quote 25 words or fewer? List each finding with the cell and its text. Do not edit any lane file.
Report: .ufo/waves/round-36/w2/out/RevEntry.md"""),
    ("RevConsider", "reviewer", "quality", f"""# Target
{LANE}/considerthese/2026-10-24.md proposals 2, 3 and 4, and {LANE}/corpus/QUALITY.md
# Task
The file says its suggestions are proposals only and that it is not acting on any of them. Proposal 1 is already recorded as criterion KQ44 in corpus/QUALITY.md. Say which of proposals 2, 3 and 4 is still unimplemented, and quote the proposal sentence you rely on. Check corpus/QUALITY.md for any criterion that already covers a daily re-open of each new SOURCES quote at its cited line; name the nearest criteria and say why they do not cover it. Say what evidence would ground that proposal in this lane. Do not edit considerthese/ or corpus/QUALITY.md.
Report: .ufo/waves/round-36/w2/out/RevConsider.md"""),
    ("ExecGuard", "executor", "quality", f"""# Target
The id-collision guard at {LANE}/.ufo/waves/round-36/assimilation/guard/
# Task
In your seat directory only, build a scratch registry with an indented row (two leading spaces) whose id is S002 and a scratch staged file whose id is S002. Show that the column-zero extraction pattern yields an EMPTY collision list and that the 0-3 leading-space pattern yields a NONEMPTY collision list. Then re-run the real check: extract ids from {LANE}/corpus/SOURCES.md and from {KNOW}/merge/kama/SOURCES.append.md with the 0-3 space pattern and report the two id counts and the collision list. Paste every command and its output. Do not write into the lane registry and do not write into the campaign tree.
Report: .ufo/waves/round-36/w2/out/ExecGuard.md"""),
    ("ExecValidate", "executor", "quality", f"""# Target
The census mirror {LANE}/.ufo/waves/round-36/assimilation/validate/corpus/SOURCES.md
# Task
Run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file {LANE}/.ufo/waves/round-36/assimilation/validate/corpus/SOURCES.md. Paste the exit code and the final line, and count the warning lines. Say whether the two drafted rows S328 and S329 are present in that mirror and whether the mirror differs from {LANE}/corpus/SOURCES.md by exactly those two rows. Do not modify {LANE}/corpus/SOURCES.md.
Report: .ufo/waves/round-36/w2/out/ExecValidate.md"""),
    ("ExecCensusLane", "executor", "quality", f"""# Target
The lane census.
# Task
Run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root {FLEET} kama. Paste the exit code and the final ok line, and count the rows with grep -cE '^\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|' against {LANE}/corpus/SOURCES.md. Do not modify corpus/SOURCES.md.
Report: .ufo/waves/round-36/w2/out/ExecCensusLane.md"""),
    ("ExecC1", "executor", "calibration", f"""# Target
{LANE}/tools/round36-statement-audit.py
# Task
Run the counting command at tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 and then with --selftest. Paste both output lines and both exit codes. Do not edit the tool.
Report: .ufo/waves/round-36/w2/out/ExecC1.md"""),
    ("ExecC2", "executor", "coverage", f"""# Target
{LANE}/tools/round36-coverage-audit.py
# Task
Run the counting command at tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 and then with --selftest. Paste both output lines and both exit codes. Do not edit the tool.
Report: .ufo/waves/round-36/w2/out/ExecC2.md"""),
    ("ScribeLesson", "scribe", "calibration", f"""# Target
Four correction rows for the round-36 lesson, drafted in your seat directory only.
# Task
Read the L1's draft at {LANE}/.ufo/waves/round-36/assimilation/correction-lines.md and the committed sources it cites: {LANE}/corpus/lessons/round-35-verifier-spotcheck.md, {LANE}/.ufo/waves/round-35/w1/out/ScoutQuarantineS211.md, {LANE}/corpus/lessons/round-35.md. Write your own four lines, one per line, each starting R35-S211:, R35-WORDS:, R35-MIRROR:, R35-KEEP: — the R35-S211 line must name ScoutQuarantineS211.md, state that still-live is absent, and state the 200 status; the R35-WORDS line must say 20 words; the R35-MIRROR line must say mixed, 11 and 84; the R35-KEEP line must name all seven leftover paths and the classes seat-log-flush, overwrite-not-committed, mixed-mirror-not-committed, helper-skipped and the size 1066624. No line may contain a token the counter forbids for the S211 row. Save the four lines to {LANE}/.ufo/waves/round-36/w2/out/ScribeLesson/correction-lines.txt. Do not write corpus/lessons/round-36.md.
Report: .ufo/waves/round-36/w2/out/ScribeLesson.md"""),
    ("ScribeRows", "scribe", "coverage", f"""# Target
Two scratch registry rows, drafted in your seat directory only.
# Task
Read the L1's draft at {LANE}/.ufo/waves/round-36/assimilation/append-block.md and the schema of the lane registry {LANE}/corpus/SOURCES.md. Write your own two rows in the same 11-column schema, ids S328 and S329: recheck cell 90d, no literal or escaped pipe in any cell, used-by exactly corpus/knowledge/sglang-native-route-deprecation.md, status mined, opened 2026-10-24, tier A. Save them to {LANE}/.ufo/waves/round-36/w2/out/ScribeRows/rows.md. Do not append them to corpus/SOURCES.md.
Report: .ufo/waves/round-36/w2/out/ScribeRows.md"""),
    ("ScribeEntry", "scribe", "coverage", f"""# Target
The round-36 knowledge entry, drafted in your seat directory only.
# Task
Re-read the two URLs the L1 opened this round: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx and https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py . Fetch each, record the HTTP status, and write your own entry at {LANE}/.ufo/waves/round-36/w2/out/ScribeEntry/sglang-native-route-deprecation.md. Use your own words. Cite only those two URLs, by the source ids S328 and S329. Keep every located quote at 25 words or fewer and give its line number. Do not copy the staged package files under {KNOW}. Do not write into corpus/.
Report: .ufo/waves/round-36/w2/out/ScribeEntry.md"""),
    ("ScoutCoverage", "scout", "coverage", f"""# Target
{LANE}/corpus/README.md and the lane's own knowledge index.
# Task
Read corpus/README.md. Say whether the coverage map already names any entry about a published native route that differs from the engine's current route, and quote the closest line if one exists. Read {LANE}/corpus/knowledge/runtime-health-surface-matrix.md and {LANE}/corpus/knowledge/sglang-docs-version-pinning.md if they exist. Say whether the ground the drafted entry covers is already held, or is new coverage-map ground. Do not edit any file and do not fetch anything.
Report: .ufo/waves/round-36/w2/out/ScoutCoverage.md"""),
    ("ConnScope", "connector", "adjacency", f"""# Target
Sibling PROVINCE.md files under {FLEET} for kake, kumitate, kengaku and kama itself.
# Task
Say whether "a published documentation route name that the engine has deprecated" is inside kama's province, or belongs to a sibling. Cite the sibling line you rely on with file and line number. Say what the sibling overlap is and whether the drafted entry crosses it. Do not edit any sibling repo and do not write any file.
Report: .ufo/waves/round-36/w2/out/ConnScope.md"""),
]


def main() -> None:
    items = []
    for name, role, axis, prompt in ITEMS:
        items.append({"name": name, "role": role, "prompt": prompt, "axes": [axis]})
    spec = {
        "wave": "round-36-w2",
        "reportDir": ".ufo/waves/round-36/w2/out",
        "maxLanes": 32,
        "context": CONTEXT,
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"wrote {OUT} items={len(items)}")


if __name__ == "__main__":
    main()
