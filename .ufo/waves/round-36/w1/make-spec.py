#!/usr/bin/env python3
"""Write the round-36 v1 wave spec. Does not dispatch."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w1/spec.json")
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
kama lane, round 36, attempt 1, one v1 wave. The L1 (Kimi fresh L1) holds the canonical planner seat. A planner role is never a swarm role.

# Lane and bounds
Lane repo: /home/vgpnk/Projects/shokunin/kama-shokunin. Your one allowed report write is the absolute path named by your Report trailer: /home/vgpnk/Projects/shokunin/kama-shokunin/<that relative path>. Scratch files go only in your seat directory /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-36/w1/out/<YourSeatName>/. Never mutate the fleet repo /home/vgpnk/Projects/shokunin, any sibling lane, the lane jj state, or the lane Git index. Never run git add/commit/stash/checkout/switch/reset/pull/push and never run a mutating jj command. Read-only git is permitted. Never write into /home/vgpnk/Projects/shokuknow. Never edit MISSION.md, corpus/SOURCES.md, SCORECARD.md, LOG.md, or considerthese/. Never read secrets or credentials. No endpoint-admin actions and no service restoration.
Every Report: trailer path is relative to /home/vgpnk/Projects/shokunin/kama-shokunin — write it at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path>. Never message agent://all. You are a leaf. Do not spawn subagents.

# Frozen claims (do not retarget)
C1 calibration 7 -> 7. Predicate: A frozen r35 routed statement is corrected iff corpus/lessons/round-36.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the correction row does not contain the token 429, and the r35 lesson blob and the r35 fleet report blob are unchanged.
Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
C2 coverage 9 -> 9. Predicate: The round-36 coverage block names knowledge/sglang-native-route-deprecation.md, that file exists, and it cites an S-id present in corpus/SOURCES.md at the tip and absent at base e5a8ececf3d60fd53b36bb74299693a29e8f74b6; none of those three hold at that base.
Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
Do-nothing controls already printed met False. Do not change either predicate.

# Frontier
Theme: a published native route name is not the engine's current route. Candidate admit: one lane-written entry corpus/knowledge/sglang-native-route-deprecation.md citing only sources you re-open. Candidate reject: the round-5 campaign-local proposal file, and hosted-health-route-configuration.md (remote platform; kake). Staged package is read-only. Quarantine rows are not appendable until you hand-check them. considerthese is operator-authored: mine, never edit.

# Tooling
You may install or upgrade tools that help the task — read /home/vgpnk/.omp/agent/RULES.md first. Install via uv tool, npx, or an official binary in ~/.local/bin. Pacman guard: ALL pacman transactions are PAUSED host-wide. Never run pacman.
"""

ITEMS = [
    ("ReviewC1Predicate", "reviewer", "calibration", f"""# Target
{LANE}/tools/round36-statement-audit.py and {LANE}/.ufo/waves/round-36/preregistration.json
# Task
Read both. Say whether the predicate sentence is byte-identical in both. Run the counting command at tip {BASE} and paste the line and exit code. Say whether a missing lesson can meet the target. Do not edit the counter.
Report: .ufo/waves/round-36/w1/out/ReviewC1Predicate.md"""),
    ("ReviewWordCount", "reviewer", "calibration", f"""# Target
The S327 quote in {LANE}/corpus/lessons/round-35.md
# Task
Extract the sentence between Quote: and the closing quote. Count whitespace-delimited words. State the count. Say whether the same paragraph's recorded count matches. Do not edit the lesson.
Report: .ufo/waves/round-36/w1/out/ReviewWordCount.md"""),
    ("ReviewS211", "reviewer", "calibration", f"""# Target
{LANE}/.ufo/waves/round-35/w1/out/ScoutQuarantineS211.md and {LANE}/corpus/lessons/round-35-verifier-spotcheck.md
# Task
State whether the seat report records a successful fetch and whether still-live is absent. State the HEAD status the spot-check records. Say what a round-36 correction row must not restate. Do not edit either file and do not append a source row.
Report: .ufo/waves/round-36/w1/out/ReviewS211.md"""),
    ("ReviewLeftovers", "reviewer", "calibration", f"""# Target
git status --porcelain in {LANE}
# Task
List the seven porcelain paths. Classify each as seat-log flush, report overwrite, mixed mirror, or helper-skipped HTML. Say which must not be committed. Do not delete or commit anything.
Report: .ufo/waves/round-36/w1/out/ReviewLeftovers.md"""),
    ("ReviewC2Heading", "reviewer", "coverage", f"""# Target
{LANE}/tools/round36-coverage-audit.py
# Task
Read the heading constant and the cited_new rule. Run the selftest and paste its line and exit code. Say whether a citation of S006, which exists at the base, can meet the target. Do not edit the counter.
Report: .ufo/waves/round-36/w1/out/ReviewC2Heading.md"""),
    ("CriticC1Noop", "critic", "calibration", f"""# Target
C1 do-nothing control {LANE}/.ufo/waves/round-36/controls/c1-noop.out
# Task
Re-run python3 {LANE}/tools/round36-statement-audit.py --repo {LANE} --tip {BASE}. Paste the line and exit code. Say whether this control meets the target. If it does, the counter is wrong. Do not edit the counter.
Report: .ufo/waves/round-36/w1/out/CriticC1Noop.md"""),
    ("CriticC2OldId", "critic", "coverage", f"""# Target
C2 kill rule: an S-id already present at {BASE} must not count.
# Task
Read score() in {LANE}/tools/round36-coverage-audit.py. Construct no files in the lane corpus. Say whether citing S006 inside the round-36 heading would set cited_new. Paste the selftest line from {LANE}/.ufo/waves/round-36/controls/c2-selftest.out and re-run the selftest.
Report: .ufo/waves/round-36/w1/out/CriticC2OldId.md"""),
    ("CriticProvince", "critic", "adjacency", f"""# Target
{KNOW}/merge/kama/knowledge/corpus/knowledge/hosted-health-route-configuration.md and {LANE}/PROVINCE.md
# Task
Say whether that staged entry is local endpoint health or a remote platform field. Name the owning lane if it is out of province. Give a flip condition. Do not copy the file into the lane.
Report: .ufo/waves/round-36/w1/out/CriticProvince.md"""),
    ("MutC1Token", "mutation-tester", "calibration", f"""# Target
The C1 false-correction arm in {LANE}/tools/round36-statement-audit.py
# Task
Run --selftest and paste the line. In your seat directory only, show that a correction row containing the forbidden token fails. Do not write that token into corpus/lessons. Do not edit the counter.
Report: .ufo/waves/round-36/w1/out/MutC1Token.md"""),
    ("MutC2Outside", "mutation-tester", "coverage", f"""# Target
The C2 outside-heading arm.
# Task
Re-run the C2 selftest. State the outside_met value. Say whether a mention of the entry path outside '## Coverage map — round 36 addition' counts. Do not create that heading in corpus/README.md.
Report: .ufo/waves/round-36/w1/out/MutC2Outside.md"""),
    ("MutBlob", "mutation-tester", "calibration", f"""# Target
Pinned blobs in {LANE}/tools/round36-statement-audit.py
# Task
Run git rev-parse {BASE}:corpus/lessons/round-35.md and git -C {FLEET} rev-parse HEAD:.ufo/reports/round-35/kama.md. Compare each to the constants. Say what the counter does if either blob differs. Do not rewrite either file.
Report: .ufo/waves/round-36/w1/out/MutBlob.md"""),
    ("MutKeepTracked", "mutation-tester", "calibration", f"""# Target
The R35-KEEP tracked-path check.
# Task
Run git -C {LANE} ls-tree -r --name-only {BASE} and say whether either ScribeGate HTML path or assimilation/validate/ is tracked. Say whether committing them would fail R35-KEEP. Do not add them.
Report: .ufo/waves/round-36/w1/out/MutKeepTracked.md"""),
    ("ScoutDocs", "scout", "coverage", f"""# Target
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx
# Task
Fetch the URL. Record the HTTP status and access date. Count occurrences of get_model_info and of the route /model_info. Quote at most 25 words from a sentence on the page, with the line number. Compare to {LANE}/.ufo/waves/round-36/assimilation/opened-2026-10-24.md. Do not append a source row.
Report: .ufo/waves/round-36/w1/out/ScoutDocs.md"""),
    ("ScoutEngine", "scout", "coverage", f"""# Target
https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py
# Task
Fetch the URL. Record the HTTP status. Locate the deprecation warning for /get_model_info. Quote at most 25 words and give the line numbers. Say whether /model_info is the replacement named in that warning. Do not append a source row.
Report: .ufo/waves/round-36/w1/out/ScoutEngine.md"""),
    ("ScoutQ200", "scout", "calibration", f"""# Target
Quarantine row S200 in {KNOW}/.ufo/waves/corpus-expansion-1/absent-defect-register.md, URL https://arxiv.org/abs/2312.07104
# Task
Fetch the URL. Say whether the register quote cell is a sentence on the page or a class label. Verdict: present, absent, or unreachable. Do not edit the register and do not append a row.
Report: .ufo/waves/round-36/w1/out/ScoutQ200.md"""),
    ("ScoutQ202", "scout", "calibration", f"""# Target
Quarantine row S202, URL https://docs.docker.com/reference/compose-file/services/
# Task
Fetch the URL. Locate the register quote if you can. Verdict: present, absent, or unreachable. Say whether an admitted entry this round cites it. Do not append a row.
Report: .ufo/waves/round-36/w1/out/ScoutQ202.md"""),
    ("ScoutQ206", "scout", "calibration", f"""# Target
Quarantine row S206, URL https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/
# Task
Fetch the URL. Record the HTTP status. Say whether the page is reachable and whether the register quote locates. Verdict: present, absent, or unreachable. Do not append a row.
Report: .ufo/waves/round-36/w1/out/ScoutQ206.md"""),
    ("ScoutQ210", "scout", "calibration", f"""# Target
Quarantine row S210, URL https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide
# Task
Fetch the URL. Record the HTTP status. Say whether sglang.launch_server is on the page. Verdict: present, absent, or unreachable. Do not append a row.
Report: .ufo/waves/round-36/w1/out/ScoutQ210.md"""),
    ("ScoutQ211", "scout", "calibration", f"""# Target
Quarantine row S211, URL https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md
# Task
Fetch the URL. Record the HTTP status you observe. Say whether the token still-live occurs on the page. Verdict: present, absent, or unreachable. Do not copy a prior lesson classification into the verdict line. Do not append a row.
Report: .ufo/waves/round-36/w1/out/ScoutQ211.md"""),
    ("ScoutQ224", "scout", "calibration", f"""# Target
Quarantine row S224, URL https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/
# Task
Fetch the URL. Say whether the page contains check_health and whether it contains the words render-only. Verdict: present, absent, or quote-not-located. Do not append a row.
Report: .ufo/waves/round-36/w1/out/ScoutQ224.md"""),
    ("ScoutQ230", "scout", "calibration", f"""# Target
Quarantine row S230, same URL as the engine source above.
# Task
Fetch https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py. Say whether the deprecation sentence is present, and quote it in at most 25 words with line numbers. This is the hand-check that decides whether the row may be adopted. Do not edit the register.
Report: .ufo/waves/round-36/w1/out/ScoutQ230.md"""),
    ("ScoutConsider", "scout", "quality", f"""# Target
{LANE}/considerthese/2026-10-24.md proposal 2, and corpus/QUALITY.md
# Task
Say whether proposal 2 (re-open each new SOURCES quote at its cited location) is already a QUALITY criterion. Quote the proposal sentence. Do not edit considerthese. Name KQ44 so a later criterion does not reuse that id.
Report: .ufo/waves/round-36/w1/out/ScoutConsider.md"""),
    ("ScoutMatrix", "scout", "coverage", f"""# Target
{LANE}/corpus/knowledge/runtime-health-surface-matrix.md and corpus/SOURCES.md row S006
# Task
Say whether the matrix or S006 already records that /get_model_info is deprecated in favour of /model_info. If it does, the new entry is not new ground. Quote the line. Do not edit the matrix.
Report: .ufo/waves/round-36/w1/out/ScoutMatrix.md"""),
    ("ConnSibling", "connector", "adjacency", f"""# Target
Sibling PROVINCE.md files under {FLEET} for kake, kumitate, and kengaku.
# Task
Say whether a SGLang native-route deprecation note is inside kama's province or belongs to a sibling. Cite the sibling line. Do not edit any sibling repo.
Report: .ufo/waves/round-36/w1/out/ConnSibling.md"""),
    ("ScribeEntry", "scribe", "coverage", f"""# Target
A draft entry, written only in your seat directory.
# Task
After you re-read {LANE}/.ufo/waves/round-36/assimilation/opened-2026-10-24.md, draft corpus/knowledge/sglang-native-route-deprecation.md in your seat directory. Cite only the two URLs opened there. Use your own words. Do not copy the staged amendment files. Do not write into corpus/.
Report: .ufo/waves/round-36/w1/out/ScribeEntry.md"""),
    ("ScribeRows", "scribe", "coverage", f"""# Target
Two scratch registry rows for the docs URL and the engine URL.
# Task
Draft two 11-column rows in your seat directory. Recheck cell must be 90d. No pipe characters inside cells. used-by must be corpus/knowledge/sglang-native-route-deprecation.md. status mined. opened 2026-10-24. Ids S328 and S329. Do not append them to corpus/SOURCES.md.
Report: .ufo/waves/round-36/w1/out/ScribeRows.md"""),
    ("ScribeLesson", "scribe", "calibration", f"""# Target
Four correction lines for the round-36 lesson, drafted in your seat directory.
# Task
Draft one line each starting R35-S211:, R35-WORDS:, R35-MIRROR:, and R35-KEEP:. The S211 line must cite ScoutQuarantineS211.md, state that still-live is absent, and state HEAD 200. It must not contain the forbidden token. The words line must say 20 words. The mirror line must say mixed, 11, and 84. The keep line must name the seven porcelain paths and the classes seat-log-flush, overwrite-not-committed, mixed-mirror-not-committed, helper-skipped, and the size 1066624. Do not write corpus/lessons/round-36.md.
Report: .ufo/waves/round-36/w1/out/ScribeLesson.md"""),
    ("ExecC1", "executor", "calibration", f"""# Target
{LANE}/tools/round36-statement-audit.py
# Task
Run the noop command and the selftest. Paste both lines and both exit codes into the report. Do not edit the tool.
Report: .ufo/waves/round-36/w1/out/ExecC1.md"""),
    ("ExecC2", "executor", "coverage", f"""# Target
{LANE}/tools/round36-coverage-audit.py
# Task
Run the base command at tip {BASE} and the selftest. Paste both lines and both exit codes. Do not edit the tool.
Report: .ufo/waves/round-36/w1/out/ExecC2.md"""),
    ("ExecCollision", "executor", "quality", f"""# Target
{LANE}/.ufo/waves/round-36/assimilation/guard/
# Task
Re-run the indent-guard commands in your seat directory: a scratch registry with an indented S002 row and a staged file containing S002. Show that a column-zero pattern misses the collision and the 0-3 space pattern catches it. Do not edit the lane registry.
Report: .ufo/waves/round-36/w1/out/ExecCollision.md"""),
    ("ExecCensus", "executor", "quality", f"""# Target
The census script /home/vgpnk/Projects/shokunin/scripts/sources-census.sh
# Task
Run validate --root {FLEET} kama. Paste the exit code and the final ok line. Do not modify corpus/SOURCES.md.
Report: .ufo/waves/round-36/w1/out/ExecCensus.md"""),
    ("RevengerBounds", "revenger", "adjacency", f"""# Target
Write boundary for this wave.
# Task
Confirm you did not read a secret file, did not edit MISSION.md, did not run an endpoint-admin command, and did not mutate jj or the git index. List the commands you ran. Say whether the seven r35 leftovers are still uncommitted.
Report: .ufo/waves/round-36/w1/out/RevengerBounds.md"""),
]


def main() -> None:
    items = []
    for name, role, axis, prompt in ITEMS:
        items.append({"name": name, "role": role, "prompt": prompt, "axes": [axis]})
    spec = {
        "wave": "round-36-w1",
        "reportDir": ".ufo/waves/round-36/w1/out",
        "maxLanes": 32,
        "context": CONTEXT,
        "items": items,
    }
    OUT.write_text(json.dumps(spec, indent=1) + "\n")
    print(f"wrote {OUT} items={len(items)}")


if __name__ == "__main__":
    main()
