#!/usr/bin/env python3
"""Write the round-36 v1 wave-3 spec (falsify the draft landing bytes). Does not dispatch.

Wave 3 is a third wave, not a replacement: every item attacks a byte that
wave 1 and wave 2 did not have in front of them — the draft lesson, the
draft entry, the two drafted registry rows, the drafted QUALITY criterion
and the draft README block, now written into the lane working tree by the
L1. The items are distinct from wave 1's and wave 2's items.
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/spec.json")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
KNOW = "/home/vgpnk/Projects/shokuknow"
BASE = "e5a8ececf3d60fd53b36bb74299693a29e8f74b6"
L = f"{LANE}/corpus/lessons/round-36.md"
E = f"{LANE}/corpus/knowledge/sglang-native-route-deprecation.md"
R = f"{LANE}/corpus/README.md"
Q = f"{LANE}/corpus/QUALITY.md"
S = f"{LANE}/corpus/SOURCES.md"

CONTEXT = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Goal
kama lane, round 36, wave 3: falsify the draft landing bytes. The L1 (Kimi fresh L1) holds the canonical planner seat. Wave 1 and wave 2 already ran; wave 3 attacks bytes they never saw — the draft lesson, entry, registry rows, QUALITY criterion and README block the L1 has just written into the lane working tree.

# Lane and bounds
Lane repo: /home/vgpnk/Projects/shokunin/kama-shokunin. Your one allowed report write is the absolute path named by your Report trailer: /home/vgpnk/Projects/shokunin/kama-shokunin/<that relative path>. Scratch files go only in your seat directory /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w3/out/<YourSeatName>/. Never mutate the fleet repo /home/vgpnk/Projects/shokunin, any sibling lane, the lane jj state, or the lane Git index. Never run git add/commit/stash/checkout/switch/reset/pull/push and never run a mutating jj command. Read-only git is permitted. Never write into /home/vgpnk/Projects/shokuknow. Never edit any corpus file, SCORECARD.md, LOG.md, or considerthese/. Never read secrets or credentials. No endpoint-admin actions and no service restoration. A git-writing check runs on a sandbox clone in your seat directory, never in the lane.
Every Report: trailer path is relative to /home/vgpnk/Projects/shokunin/kama-shokunin — write it at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path>. Never message agent://all. You are a leaf. Do not spawn subagents.

# Finish early
Your seat has a hard bound. When you have your answer, write the report and stop. Do not re-derive a fact twice; do not attempt a second fetch of a URL you already fetched. Report measured results separately from inference.

# Frozen claims (do not retarget)
C1 calibration 7 -> 7. Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>
C2 coverage 9 -> 9. Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>
Do-nothing controls already printed met False. Do not change either predicate.

# Draft bytes under attack (working tree, read-only)
Lesson draft: /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-36.md
Entry draft: /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/sglang-native-route-deprecation.md
Registry rows draft: the last two data rows of /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md (ids S328 and S329)
QUALITY draft: the last criterion block of /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md (KQ45)
README draft: the last heading block of /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md (## Coverage map — round 36 addition)

# Tooling
You may install or upgrade tools that help the task — read /home/vgpnk/.omp/agent/RULES.md first. Install via uv tool, npx, or an official binary in ~/.local/bin. Pacman guard: ALL pacman transactions are PAUSED host-wide. Never run pacman.
"""

ITEMS = [
    ("RevLessonGate", "reviewer", "calibration", f"""# Target
{L}
# Task
Read the lesson draft. For every row in its ## Gate quarantine table: does it name a URL, a verdict, a reason and a flip condition? Count the rows. For each of the four ## Corrections rows, list the exact tokens the C1 counter requires and say whether the row has each. Answer in a table. Do not edit the lesson.
Report: .ufo/waves/round-36/w3/out/RevLessonGate.md"""),
    ("RevLessonQuotes", "reviewer", "calibration", f"""# Target
The located quotes in {L}
# Task
For every quote in the lesson draft, count its whitespace-delimited words and say whether it is 25 words or fewer. Give the count for each. Also check the two registry rows' quotes. Do not edit any file.
Report: .ufo/waves/round-36/w3/out/RevLessonQuotes.md"""),
    ("RevEntryBytes", "reviewer", "coverage", f"""# Target
{E}
# Task
Read the entry draft. Re-fetch its two source URLs and check each located quote against the bytes you fetched: quote text, line number, and word count. Say for each quote whether it is present at the stated line. Do not edit the entry.
Report: .ufo/waves/round-36/w3/out/RevEntryBytes.md"""),
    ("RevRowsBytes", "reviewer", "coverage", f"""# Target
The S328 and S329 rows at the end of {S}
# Task
Read both rows. For each: count the pipe-delimited columns, check no cell contains a literal or escaped pipe, check the recheck cell is a valid ISO date or an Nd value or a symbolic cadence, check the used-by cell names exactly the entry path, check the opened cell, and check the anchor cell's quote sits at the cited line in the fetched source. Report a defect list. Do not edit the registry.
Report: .ufo/waves/round-36/w3/out/RevRowsBytes.md"""),
    ("RevQualBytes", "reviewer", "quality", f"""# Target
The KQ45 block at the end of {Q}
# Task
Read it. Say whether any earlier criterion in that file already covers checking a new SOURCES row's quote at its cited anchor. Name the two nearest earlier criteria and say why they do not. Check that the motivating lesson names a measured fact with a file path. Do not edit QUALITY.md.
Report: .ufo/waves/round-36/w3/out/RevQualBytes.md"""),
    ("RevReadmeBytes", "reviewer", "coverage", f"""# Target
The last heading block of {R}
# Task
Read it. Count how many times the string knowledge/sglang-native-route-deprecation.md appears inside the block that starts at the heading '## Coverage map — round 36 addition' and ends at the next '## '. State the count. Say whether the block's table row names the entry exactly once. Do not edit README.md.
Report: .ufo/waves/round-36/w3/out/RevReadmeBytes.md"""),

    ("RevLeftovers", "reviewer", "calibration", f"""# Target
The seven r35 leftovers.
# Task
Run git -C {LANE} status --porcelain. List the seven paths that were the r35 leftovers and say whether each is still uncommitted. Name the class of each: seat-log flush, report overwrite, mixed mirror, or helper-skipped HTML. Say whether committing any of them would break the C1 R35-KEEP arm. Do not add, commit or delete anything.
Report: .ufo/waves/round-36/w3/out/RevLeftovers.md"""),
    ("RevMisroot", "reviewer", "quality", f"""# Target
The fleet root working tree.
# Task
Run git -C {FLEET} status --porcelain. For every untracked file at the fleet root, read its first 40 lines and say whether it names kama or round-36. Report any file that does. Do not move, copy or delete anything.
Report: .ufo/waves/round-36/w3/out/RevMisroot.md"""),

    ("CritC1Sound", "critic", "calibration", f"""# Target
The soundness of the C1 counter.
# Task
Construct, in your seat directory only, a candidate R35-S211 correction row that satisfies every string predicate the counter checks but states a false fact. Run the counter's own score() on it. Report whether the counter accepts the false row. If it does, say what a do-nothing counter cannot reach here and what extra check the counter would need. Do not write that row into any lane file and do not edit the counter.
Report: .ufo/waves/round-36/w3/out/CritC1Sound.md"""),
    ("CritC2Junk", "critic", "coverage", f"""# Target
The soundness of the C2 counter.
# Task
In a sandbox clone in your seat directory only, add a knowledge entry that cites an S-id which is absent from the registry, and a README block that names the entry path. Run the C2 counter there with --tip at a commit carrying both. Paste the output line and say whether cited_new stays 0 and named is 1. Do not touch the real lane repo.
Report: .ufo/waves/round-36/w3/out/CritC2Junk.md"""),
    ("MutLessonRow", "mutation-tester", "calibration", f"""# Target
The C1 counter's reaction to a damaged correction row.
# Task
Make a sandbox clone of the lane in your seat directory. In the clone only, delete the R35-WORDS row from corpus/lessons/round-36.md, commit, and run the C1 counter against that clone with --tip at the new commit. Paste the output line. Then restore the row and change one word of it, commit, and run the counter again. Paste both lines and say which field caught each damage. Do not touch the real lane repo.
Report: .ufo/waves/round-36/w3/out/MutLessonRow.md"""),
    ("MutRowPipe", "mutation-tester", "quality", f"""# Target
The census parser's handling of a pipe inside a cell.
# Task
In your seat directory only, copy the lane registry, insert a literal pipe inside one cell of a copied data row, and run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file against your copy. Paste the exit code and the finding. Say whether the census catches the broken column count. Do not modify the lane registry.
Report: .ufo/waves/round-36/w3/out/MutRowPipe.md"""),
    ("MutQuote26", "mutation-tester", "quality", f"""# Target
The 25-word bound on a located quote.
# Task
In your seat directory, take the located quote in the S329 registry row and write a scratch variant of it that is 26 words long. Count both. State which passes a 25-word check and which does not, and name the check a gate would have to apply to catch it. Do not edit any lane file.
Report: .ufo/waves/round-36/w3/out/MutQuote26.md"""),

    ("RevQ202", "reviewer", "calibration", f"""# Target
Quarantine row S202: https://docs.docker.com/reference/compose-file/services/
# Task
Fetch the URL once. Say whether the page carries the span about service_healthy and 'as indicated by healthcheck'. Quote at most 25 words. Verdict: present, absent, or unreachable. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevQ202.md"""),
    ("RevQ206", "reviewer", "calibration", f"""# Target
Quarantine row S206: https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/
# Task
Fetch the URL once. Record the HTTP status. Say whether the page carries the span about vLLM/SGLang and /v1/models. Verdict: present, absent, or unreachable. State what you measured. Do not append a row.
Report: .vof/waves/round-36/w3/out/RevQ206.md""".replace("/.vof/", "/.ufo/")),
    ("RevQ210", "reviewer", "calibration", f"""# Target
Quarantine row S210: https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide
# Task
Fetch the URL once. Record the HTTP status. Say whether the page contains the literal text 'Page Not Found' and whether it contains sglang.launch_server. Verdict: present, absent, or unreachable. State what you measured. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevQ210.md"""),
    ("RevQ211", "reviewer", "calibration", f"""# Target
Quarantine row S211: https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md
# Task
Fetch the URL once. Record the HTTP status. Say whether the token still-live occurs anywhere in the page text you read. Verdict: present, absent, or unreachable. State what you measured. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevQ211.md"""),
    ("RevQ224", "reviewer", "calibration", f"""# Target
Quarantine row S224: https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/
# Task
Fetch the URL once. Say whether it contains check_health, whether it contains 'render-only', and whether it contains 'always return 200'. Verdict: present, absent, or quote-not-located. State what you measured. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevQ224.md"""),
    ("RevQ230", "reviewer", "calibration", f"""# Target
Quarantine row S230: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
# Task
Fetch the URL once. Say whether the deprecation sentence for /get_model_info is present and give its line numbers. Quote at most 25 words. Verdict: present, absent, or unreachable. State what you measured. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevQ230.md"""),
    ("RevDrift174", "reviewer", "quality", f"""# Target
Registry row S174: https://git-scm.com/docs/git-blame
# Task
Fetch the URL once. Find the sentence that begins 'Annotates each line'. Quote it in at most 25 words. Compare it word for word with the quote the row carries, and say whether the row's quote is byte-exact. State the difference. Do not edit the registry.
Report: .ufo/waves/round-36/w3/out/RevDrift174.md"""),
    ("RevDrift192", "reviewer", "quality", f"""# Target
Registry row S192: https://developers.openai.com/api/reference/resources/chat/index.md
# Task
Fetch the URL once. Say whether the row's quoted sentence about Structured Outputs and json_schema occurs in the bytes you fetched. If it does not, say whether the page's body is present in the fetched bytes at all, and give the reason you would record for the row: drift, or a source that cannot be read by a plain fetch. Do not edit the registry.
Report: .ufo/waves/round-36/w3/out/RevDrift192.md"""),
    ("RevDrift193", "reviewer", "quality", f"""# Target
Registry row S193, which quotes tools/gate-registry-check.py at c4c46ad5b87d8b63f03e200a7b13eb8eeff46279
# Task
Run git -C {LANE} show c4c46ad5b87d8b63f03e200a7b13eb8eeff46279:tools/gate-registry-check.py and find the sentence the row quotes. Give its line number and its exact bytes. Say whether the row's quote is byte-exact or normalized. Do not edit the registry or the tool.
Report: .ufo/waves/round-36/w3/out/RevDrift193.md"""),
    ("RevS328", "revenger", "coverage", f"""# Target
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx
# Task
Fetch the URL once. Record the HTTP status. Count occurrences of get_model_info and of the route /model_info. Give the line number of the route-list entry and of the worked example. Quote at most 25 words from line 6. Compare every number you measured with the S328 row and the entry draft. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevS328.md"""),
    ("RevS329", "revenger", "coverage", f"""# Target
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
# Task
Fetch the URL once. Record the HTTP status. Give the line numbers of the route registrations for /get_model_info and /model_info, and of the deprecation warning. Quote the warning in at most 25 words. Compare with the S329 row and the entry draft. Do not append a row.
Report: .ufo/waves/round-36/w3/out/RevS329.md"""),
    ("ExecCensusEnd", "executor", "quality", f"""# Target
The lane census at the working-tree state.
# Task
Run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root {FLEET} kama. Paste the exit code and the final ok line. Count the data rows in {S}. Do not modify the registry.
Report: .ufo/waves/round-36/w3/out/ExecCensusEnd.md"""),
    ("ExecCounters", "executor", "calibration", f"""# Target
The two counters.
# Task
Run both counting commands with --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6 and paste both output lines and both exit codes. Then say, from the counters' own code, what tip value would make each command read the draft bytes. Do not edit the tools.
Report: .ufo/waves/round-36/w3/out/ExecCounters.md"""),
    ("ExecSweep", "executor", "quality", f"""# Target
The fleet-root misroot sweep for round 36.
# Task
Run git -C {FLEET} status --porcelain with no pathspec. For every untracked file, read its first 40 lines and say whether it names kama or round-36. List every file that does. Do not move, copy or delete anything.
Report: .ufo/waves/round-36/w3/out/ExecSweep.md"""),
    ("ScribeQual", "scribe", "quality", f"""# Target
A QUALITY criterion draft in your seat directory only.
# Task
Read the KQ45 block at the end of {Q} and the drift evidence the L1 measured on S174, S192 and S193. Write your own criterion text into {LANE}/.ufo/waves/round-36/w3/out/ScribeQual/quality-draft.md. It must separate drift from a source that cannot be fetched. Then say whether your text and the L1's text say the same thing, and name any difference. Do not edit QUALITY.md.
Report: .ufo/waves/round-36/w3/out/ScribeQual.md"""),
    ("ScribeLog", "scribe", "calibration", f"""# Target
A LOG.md entry draft in your seat directory only.
# Task
Read {LANE}/LOG.md and its last entry for the house style. Then read the draft lesson {L} and the two counters' outputs. Draft the round-36 LOG.md entry into {LANE}/.ufo/waves/round-36/w3/out/ScribeLog/log-draft.md: what the round claimed, what it measured, what it landed and where the evidence sits. Use the house style and cite paths. Do not edit LOG.md.
Report: .ufo/waves/round-36/w3/out/ScribeLog.md"""),
    ("ScoutTally", "scout", "quality", f"""# Target
The round's wave record.
# Task
Read {LANE}/.ufo/waves/round-36/w1/out/seat-exit-codes.json and {LANE}/.ufo/waves/round-36/w2/out/seat-exit-codes.json. Report for each wave: seats dispatched, seats that exited 0, seats killed at the seat bound, the role mix, and the attack-role count (reviewer, critic, mutation-tester, labrat). Report the round total and the round's attack-role share. Say whether the floor of 32 seats and 25 percent attack roles is met. Do not edit anything.
Report: .ufo/waves/round-36/w3/out/ScoutTally.md"""),
    ("ConnScope2", "connector", "adjacency", f"""# Target
The drafted entry's wording against sibling provinces.
# Task
Read {E}. Read the PROVINCE.md of kama, kake, kumitate and kengaku under {FLEET}. Say whether the entry's subject — a documentation route name that the engine has deprecated — is inside kama's province. Cite the line you rely on from each sibling you checked. Say whether the entry crosses into a sibling's province. Do not edit any repo.
Report: .ufo/waves/round-36/w3/out/ConnScope2.md"""),
    ("SentFinal", "sentinel", "adjacency", f"""# Target
The round's write boundary.
# Task
List every command you ran. Confirm you read no secret file, edited no file outside your seat directory, ran no endpoint-admin command, and ran no mutating git or jj command in the lane. Say whether the seven r35 leftovers are still uncommitted. Say whether anything a kama round-36 seat wrote is sitting at the fleet root.
Report: .ufo/waves/round-36/w3/out/SentFinal.md"""),
]


def main() -> None:
    items = []
    for name, role, axis, prompt in ITEMS:
        items.append({"name": name, "role": role, "prompt": prompt, "axes": [axis]})
    spec = {
        "wave": "round-36-w3",
        "reportDir": ".ufo/waves/round-36/w3/out",
        "maxLanes": 32,
        "context": CONTEXT,
        "items": items,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"wrote {OUT} items={len(items)}")


if __name__ == "__main__":
    main()
