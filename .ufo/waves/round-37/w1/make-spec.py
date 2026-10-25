#!/usr/bin/env python3
"""Write the round-37 v1 wave-1 spec. Does not dispatch."""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-37/w1/spec.json")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = "6a4afdfe48b0b54239d127761d21a5cf21b5b0ea"
W = ".ufo/waves/round-37/w1/out"

CONTEXT = """/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Goal
kama lane, round 37, attempt 1, v1 wave 1 (build + first falsifiers). The L1 holds the canonical planner seat. A planner role is never a swarm role.

# Lane and bounds
Lane repo: /home/vgpnk/Projects/shokunin/kama-shokunin. Your one allowed report write is the absolute path named by your Report trailer: /home/vgpnk/Projects/shokunin/kama-shokunin/<that relative path>. Scratch files go only in your seat directory /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-37/w1/out/<YourSeatName>/. Never mutate the fleet repo /home/vgpnk/Projects/shokunin, any sibling lane, the lane jj state, or the lane Git index — a seat's stray `jj commit` parked this lane's working copy last round; never run git add/commit/stash/checkout/switch/reset/pull/push and never run a mutating jj command (commit, new, describe, squash, rebase, abandon, bookmark, undo, op restore/revert, git push/fetch) anywhere. Read-only git is permitted. Never write into /home/vgpnk/Projects/shokuknow (read-only package). Never delete, move or "clean" anything in the fleet repo outside your own report path. Never edit MISSION.md, corpus/SOURCES.md, SCORECARD.md, LOG.md, corpus/lessons/round-36*.md, or considerthese/. Never read secrets or credentials. Every `Report:` trailer path is relative to /home/vgpnk/Projects/shokunin/kama-shokunin — write it at /home/vgpnk/Projects/shokunin/kama-shokunin/<that path>. Never message agent://all. You are a leaf. Do not spawn subagents. Read-only `curl` HTTP GET of the exact URLs named in your item is authorized for this wave's source-reopening; nothing else.

# Frozen claims (do not retarget)
C1 calibration 7 -> 7. Predicate: A frozen r36-spotcheck routed statement is corrected iff corpus/lessons/round-37.md contains a correction row naming its id, the counter re-derives the cited committed-byte fact, the row carries no wrong-id restatement that its own statement forbids, and the r36 lesson blob and the r36 fleet report blob are unchanged.
Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round37-statement-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>
C2 coverage 9 -> 9. Predicate: The round-37 coverage block names each of knowledge/kv-cache-reclamation-models.md, knowledge/prefix-cache-reuse-models.md and knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md, every one of those files exists in corpus/knowledge/, and each cites an S-id present in corpus/SOURCES.md at the tip and absent at base 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea; none of those three holds at that base.
Counting command: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round37-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip <full-commit>
Do-nothing controls already printed met False (receipts in .ufo/waves/round-37/controls/). Do not change either predicate.

# Frontier
Theme (one only): engine internals that shape what a served endpoint answers — KV-cache reclamation and prefix-cache reuse models in vLLM and SGLang. Candidate admits: the three knowledge files in the frozen C2 predicate, adapted from the read-only package /home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/ and citing only rows the lane re-opened this round. Candidate rejects: other staged entries — judge each on PROVINCE.md (local serving/endpoint health) and QUALITY.md. Staged package is read-only; never run a campaign tool. considerthese is operator-authored: mine, never edit.

# Tooling
You may install or upgrade tools that help the task — read /home/vgpnk/.omp/agent/RULES.md first. Install via uv tool, npx, or an official binary in ~/.local/bin. Pacman guard: ALL pacman transactions are PAUSED host-wide. Never run pacman.
"""


def item(name, role, prompt, axes):
    return {"name": name, "role": role, "prompt": prompt, "axes": axes}


ITEMS = [
    item("ReviewC1Predicate", "reviewer",
         "# Target\n" + LANE + "/tools/round37-statement-audit.py and " + LANE + "/.ufo/waves/round-37/preregistration.json\n"
         "# Task\nRead both. Say whether the C1 predicate sentence is byte-identical in both files. Run the counting command at tip " + BASE + " and paste the line and exit code. Say whether a missing lessons/round-37.md can meet the target. Do not edit the counter.\nReport: " + W + "/ReviewC1Predicate.md", ["calibration"]),
    item("ReviewC2Predicate", "reviewer",
         "# Target\n" + LANE + "/tools/round37-coverage-audit.py and " + LANE + "/.ufo/waves/round-37/preregistration.json\n"
         "# Task\nRead both. Say whether the C2 predicate sentence is byte-identical in both. Run the counting command at tip " + BASE + " and paste the line and exit code. Say whether a name outside the round-37 heading can count. Do not edit the counter.\nReport: " + W + "/ReviewC2Predicate.md", ["coverage"]),
    item("MutD1", "mutation-tester",
         "# Target\nThe R36-D1 legs in " + LANE + "/tools/round37-statement-audit.py\n"
         "# Task\nShow .ufo/waves/round-36/census-end.out is absent at " + BASE + " (git cat-file -e fails) but exists on disk with a 'kama\\tok' tail line. In your seat dir, construct a row that would pass D1 without the file being tracked; say whether the counter rejects it. Do not edit the counter or commit the file.\nReport: " + W + "/MutD1.md", ["calibration"]),
    item("MutD2", "mutation-tester",
         "# Target\nThe R36-D2A/D2B legs and " + "/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md\n"
         "# Task\nFrom the staged file, extract the ids of rows whose source cell names native_api.mdx and the ids of rows naming http_server.py. State whether a D2B correction row containing S359 passes the counter's forbidden check, and whether a row missing 'miswritten' passes D2A. Do not edit anything.\nReport: " + W + "/MutD2.md", ["calibration"]),
    item("MutD3", "mutation-tester",
         "# Target\nThe R36-D3 legs and " + LANE + "/.ufo/waves/round-36/w3/out/seat-exit-codes.json\n"
         "# Task\nRe-derive from committed bytes: which seats have rc=1, and do ScribeLog/seat.log and RevQ206/seat.log contain 'rate_limit' and '429'? Say whether a correction row naming six rc=143 seats instead would pass or fail. Do not edit anything.\nReport: " + W + "/MutD3.md", ["calibration"]),
    item("CriticC1Sound", "critic",
         "# Target\nThe whole C1 predicate: does it over-credit?\n# Task\nAttack: can a correction row pass holds() while asserting a false fact? Check each of the four holds() branches for a substring that can appear without the fact being true (e.g. D2A 'miswritten' + 'S371' + 'native_api' all appear but the mapping claim is inverted). Say which legs are re-derivation and which are shape-only, and name the weakest leg. Do not edit the counter.\nReport: " + W + "/CriticC1Sound.md", ["calibration"]),
    item("CriticD3Accounting", "critic",
         "# Target\nThe D3 correction belongs in the round-37 fleet report (lane write scope), not only in the lesson.\n# Task\nRead " + LANE + "/corpus/lessons/round-36-verifier-spotcheck.md §6 item 3 and " + LANE + "/.ufo/waves/round-36/w3/out/seat-exit-codes.json. Say what the report must name (seats, rc, last error text) to satisfy the routing, and whether putting the same accounting in lessons/round-37.md is sufficient or also needed in the report. Do not edit anything.\nReport: " + W + "/CriticD3Accounting.md", ["calibration"]),
    item("ReviewAppend", "reviewer",
         "# Target\nAppend-only discipline: the r36 lesson blob and the fleet r36 report blob must stay unchanged.\n# Task\nRun git -C " + LANE + " rev-parse master:corpus/lessons/round-36.md and git -C /home/vgpnk/Projects/shokunin rev-parse HEAD:.ufo/reports/round-36/kama.md; compare with LESSON_BLOB and REPORT_BLOB constants in tools/round37-statement-audit.py. State whether both match. Do not edit anything.\nReport: " + W + "/ReviewAppend.md", ["calibration"]),
    item("ScoutGate", "scout",
         "# Target\nStaged-id bookkeeping for the C2 admissions.\n# Task\nFrom /home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md extract the staged rows S330, S333, S334, S335, S346, S347 and S363 (full row text). Re-derive: grep -oE '^ {0,3}\\|[[:space:]]*S[0-9]{3,}' on the lane corpus/SOURCES.md and on the staged file; sort; comm -12 → confirm zero collisions. Re-derive the kama quarantine slice with the awk -F'|' recipe in the round prompt §10 (register at /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md): list every kama row's id. Report row texts, the collision check output, and the slice. Do not edit anything.\nReport: " + W + "/ScoutGate.md", ["coverage"]),
    item("ConnSibling", "connector",
         "# Target\nSibling-overlap scan: does engine KV-cache/prefix-cache internals belong to kama (local serving & endpoint health) or to kengaku (model eval) or kumitate (orchestration tooling)?\n# Task\nRead " + LANE + "/PROVINCE.md, /home/vgpnk/Projects/shokunin/kengaku-shokunin/PROVINCE.md and /home/vgpnk/Projects/shokunin/kumitate-shokunin/PROVINCE.md (headers and Refuses/Owns sections only). State which lane owns engine-internal scheduling/KV docs and why the boundary rule 'what a served endpoint answers' does or does not cover it. Do not edit anything.\nReport: " + W + "/ConnSibling.md", ["adjacency"]),
    item("RevengerIntent", "revenger",
         "# Target\nWhy do the three C2 entries belong in this lane's corpus at all?\n# Task\nRead the three staged entries in /home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/{kv-cache-reclamation-models.md,prefix-cache-reuse-models.md,prefix-cache-reuse-models-amendment-2026-10-23.md} and " + LANE + "/corpus/README.md coverage map + Known gaps. Say whether the map already covers KV-cache/eviction/prefix-reuse ground, and reconstruct what gap these entries close for the endpoint-health question. Do not edit anything.\nReport: " + W + "/RevengerIntent.md", ["coverage"]),
    item("ScoutConsider", "scout",
         "# Target\n" + LANE + "/considerthese/2026-10-24.md self-improvement proposals.\n# Task\nList the four proposals. For each, say whether it was already implemented (cite the KQ id in " + LANE + "/corpus/QUALITY.md or other landed artifact). For proposal 3 (prepared-not-dispatched ledger), locate the evidence it names: the committed-but-never-run wave under .ufo/waves/round-32/w1/ or round-33 — list the spec path and seat count. Propose the grounded criterion text for one still-unimplemented proposal. Do not edit considerthese or QUALITY.md.\nReport: " + W + "/ScoutConsider.md", ["calibration"]),
    item("ReviewFrontier", "reviewer",
         "# Target\nDoes " + LANE + "/corpus/README.md already cover KV-cache reclamation or prefix-cache reuse?\n# Task\nGrep the README coverage map, Frontier, and Known gaps for KV, eviction, prefix, radix, scheduler, batching. State exactly which rows (if any) cover the ground the three C2 entries occupy, and what 'uncovered' means for the claim. Do not edit anything.\nReport: " + W + "/ReviewFrontier.md", ["coverage"]),
    item("CriticReject", "critic",
         "# Target\nCandidate rejects for the assimilation set: staged entries that must NOT be adopted this round.\n# Task\nEvaluate /home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/{cross-literate-endpoint-venues.md,openai-compat-host-vendor-contracts.md,hosted-health-route-configuration-amendment-2026-10-23-r4.md} against " + LANE + "/PROVINCE.md (local serving/endpoint health) and " + LANE + "/corpus/QUALITY.md. For each: adopt or reject, with reason and flip condition. At least one reject is required by the contract; name the strongest reject.\nReport: " + W + "/CriticReject.md", ["adjacency"]),
    item("ReviewQuality", "reviewer",
         "# Target\n" + LANE + "/corpus/QUALITY.md tail — KQ44, KQ45.\n# Task\nRead the last two criterion blocks. Draft text for a new criterion KQ46 'a foreign or staged id range cited in a lesson is a claim: re-derive every id against the named artifact before citing it; a copied range that misnames ids is a correction target, never a citation' — tighten or object to that wording with reasons. Motivating lesson: round-36-verifier-spotcheck.md §6 item 2 (five misattributed staged ids). Do not edit QUALITY.md.\nReport: " + W + "/ReviewQuality.md", ["calibration"]),
    item("ScribeEntries", "scribe",
         "# Target\nDrafts of the three C2 knowledge entries, adapted from staged bytes.\n# Task\nCopy the three staged files into your seat dir (never into corpus/knowledge/). Rewrite each: source: lines point at the lane's adopted ids S330, S333, S334, S335, S346, S347, S363 with the URLs; verified-at: 2026-10-25; recheck: 90d with a runnable command; ground: line states the coverage-map gap honestly (do not copy a frontier label that does not exist). Keep every factual claim verbatim from staged bytes; delete any claim a source does not support. Emit drafts under your seat dir plus a one-line summary per file.\nReport: " + W + "/ScribeEntries.md", ["coverage"]),
    item("ScribeLesson", "scribe",
         "# Target\nSkeleton of " + LANE + "/corpus/lessons/round-37.md (draft in your seat dir only, never at the corpus path).\n# Task\nDraft sections: ## Corrections — round 37 (rows R36-D1/R36-D2A/R36-D2B/R36-D3 following the r36 correction-row style, with the counter's re-derived facts), ## Gate (candidates/admitted/rejected placeholders, each new-row URL+access-date+≤25-word quote placeholders), ## Mistakes (class id-drift; evidence corpus/lessons/round-36-verifier-spotcheck.md §6 item 2; captured-by QUALITY.md; fix KQ46), ## Wave evidence. Leave placeholders clearly marked. Do not write the real file.\nReport: " + W + "/ScribeLesson.md", ["calibration"]),
    item("ExecValidate", "executor",
         "# Target\nScratch-mirror validation of the SOURCES append block (no real append).\n# Task\nBuild in your seat dir: copy " + LANE + "/corpus/SOURCES.md, append the normalized rows for S330, S333, S334, S335, S346, S347, S363 (status mined, recheck 90d, used-by the three corpus/knowledge/ paths, no pipe in any cell), then run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file <your mirror> and paste exit code + findings. The rows must sit inside the ## Registry table (r36's E12 trap). Report the command output verbatim. Do not touch the real corpus/SOURCES.md.\nReport: " + W + "/ExecValidate.md", ["coverage"]),
    item("ExecCollision", "executor",
         "# Target\nCollision-guard re-proof and real-id check.\n# Task\nRe-run in your seat dir: the 0-3-space extractor over lane corpus/SOURCES.md and over staged SOURCES.append.md; comm -12 → paste output (expect empty). Build the indented-row fixture (a scratch registry with '  | S330 |') and show the guard catches the collision. Also verify no staged row for S330/S333/S334/S335/S346/S347/S363 shares a URL already in the lane registry (E04 within-scope duplicate URL risk): list each staged row's URL and grep the lane SOURCES.md for it. Paste all outputs.\nReport: " + W + "/ExecCollision.md", ["coverage"]),
    item("FetchS330", "scout",
         "# Target\nhttps://docs.vllm.ai/en/v0.19.1/usage/v1_guide/\n# Task\nOne read-only curl GET (follow redirects, save bytes to your seat dir). Record HTTP status, bytes, effective URL. Locate quotes: 'treats both prompt and output tokens the same way' and 'enabled by default whenever possible' — state the section/heading each sits under and quote ≤25 words verbatim. State whether the page carries a version marker. Do not append a row.\nReport: " + W + "/FetchS330.md", ["coverage"]),
    item("FetchS333", "scout",
         "# Target\nhttps://docs.sglang.io/docs/advanced_features/radix_eviction_policy\n# Task\nOne read-only curl GET, save bytes. Record status/bytes. Locate 'the lowest score is evicted first' and the eviction-candidate conditions (evictable leaves, unlocked, shadowed child). Quote ≤25 words verbatim with its section. Note whether the page carries a version pin. Do not append a row.\nReport: " + W + "/FetchS333.md", ["coverage"]),
    item("FetchS334", "scout",
         "# Target\nhttps://docs.sglang.io/docs/advanced_features/session_radix_cache\n# Task\nOne read-only curl GET, save bytes. Record status/bytes. Locate 'session references are soft protection, not memory pins' — quote ≤25 words verbatim with its section. Say whether the page says referenced KV can still be evicted. Do not append a row.\nReport: " + W + "/FetchS334.md", ["coverage"]),
    item("FetchS335", "scout",
         "# Target\nhttps://arxiv.org/abs/2312.07104\n# Task\nRead-only curl GET of the abs page AND the HTML full text (arxiv.org/abs/2312.07104v1), save both. Record status/bytes of each. Locate 'A node is evictable if its reference counter is zero' and the LRU-eviction/caching statements. Quote ≤25 words verbatim with the section name. Do not append a row.\nReport: " + W + "/FetchS335.md", ["coverage"]),
    item("FetchS346", "scout",
         "# Target\nhttps://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md\n# Task\nOne read-only curl GET of the raw file (raw.githubusercontent.com same path) — record status/bytes. Locate §6.4 and the file-level map lines naming mem_cache/radix_cache.py (RadixCache) and managers/schedule_policy.py (SchedulePolicy). Quote ≤25 words verbatim. Note the source is a community write-up (tier B at most, never A). Do not append a row.\nReport: " + W + "/FetchS346.md", ["coverage"]),
    item("FetchS347", "scout",
         "# Target\nhttps://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html\n# Task\nOne read-only curl GET, save bytes. Record status/bytes. Locate 'hash-based approach', the Note-2 collision-free caveat + SHA256 advice, and the Eviction (LRU) section. Quote ≤25 words verbatim per item with its anchor. Do not append a row.\nReport: " + W + "/FetchS347.md", ["coverage"]),
    item("FetchS363", "scout",
         "# Target\nhttps://docs.vllm.ai/en/v0.32.0/design/prefix_caching/\n# Task\nOne read-only curl GET, save bytes. Record status/bytes. Locate the Note-2 sentence 'As of v0.11, the default hashing algorithm is sha256' and the --prefix-caching-hash-algo flag. Quote ≤25 words verbatim with its anchor. Do not append a row.\nReport: " + W + "/FetchS363.md", ["coverage"]),
    item("ReviewS330Claims", "reviewer",
         "# Target\nClaim-vs-source check for S330's planned row content.\n# Task\nFrom the staged SOURCES.append.md S330 row and the kv-cache-reclamation-models.md entry, list every claim attributed to S330 (token budget spans prompt and output; chunked prefill on by default; FCFS-or-priority via --scheduling-policy). After FetchS330 lands its page: state whether each claim is supported, unsupported, or absent — if the seat output is not yet available, run the same curl yourself (one GET allowed).\nReport: " + W + "/ReviewS330Claims.md", ["coverage"]),
    item("ReviewSGLangClaims", "reviewer",
         "# Target\nClaim-vs-source check for S333/S334/S335.\n# Task\nList the claims the staged entry attributes to the three SGLang sources (evictable-leaf rule, lowest-score-first, LRU tie-break, ref-counter-zero evictability, soft-protection-not-pins, session_id labels references only). For each claim, name which source must carry it and whether the staged row's quote supports it; flag any claim that rests only on the community source S346.\nReport: " + W + "/ReviewSGLangClaims.md", ["coverage"]),
    item("ReviewPrefixClaims", "reviewer",
         "# Target\nClaim-vs-source check for S347/S363.\n# Task\nList the claims: hash-based approach; block keyed by own tokens + prefix ancestry; full blocks only; collision caveat + SHA256 advice at v0.9.0; sha256 default as of v0.11; --prefix-caching-hash-algo. For each say which staged source row backs it and whether the v0.9.0-vs-v0.32.0 version split is correctly described. Flag portability problems (vLLM-only conclusions applied to SGLang).\nReport: " + W + "/ReviewPrefixClaims.md", ["coverage"]),
    item("CriticTheme", "critic",
         "# Target\nThe round's theme boundary: 'engine internals that shape what a served endpoint answers'.\n# Task\nAttack it: is KV-cache reclamation inside kama's province (endpoint health semantics) or creeping into model-quality/serving-performance territory the Refuses list bars? Does the lane's boundary rule ('is the thing at this baseURL the model this config believes it is, right now') cover why a request is rejected/re-prefilled? Give the narrowest honest statement of the theme that stays in province.\nReport: " + W + "/CriticTheme.md", ["adjacency"]),
    item("CriticEntries", "critic",
         "# Target\nFalsify the draft entries' claims before they land.\n# Task\nAfter ScribeEntries emits drafts: for each draft, find one sentence that a cited source does NOT support or that over-claims (e.g. 'a reader can act on this' beyond the page). Also check the staged claim 'session_id ... every request must still carry its full intended prompt' against FetchS334's page. Report each found defect with the draft line and the source gap.\nReport: " + W + "/CriticEntries.md", ["coverage"]),
    item("ScoutRegister", "scout",
         "# Target\nThe kama slice of the absent-defect register — re-derivation only.\n# Task\nRe-run the §10 awk recipe over /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md for lane kama. List the seven ids and their class cells. Cross-check against " + LANE + "/corpus/lessons/round-36.md's recorded verdicts (S202/S206/S230 present; S200/S210/S211 absent; S224 not-located). Report agreement or disagreement. No fetches needed.\nReport: " + W + "/ScoutRegister.md", ["calibration"]),
    item("ReviewSchema", "reviewer",
         "# Target\nFleet-schema conformance of the normalized append rows.\n# Task\nRead CORPUS.md's 11-column contract (fleet /home/vgpnk/Projects/shokunin/CORPUS.md §SOURCES.md). Check each normalized row ExecValidate builds (or the staged rows S330/S333/S334/S335/S346/S347/S363 if the mirror is not yet up): 11 cells, no literal or escaped |, kind/tier/status enums valid, community never tier-A, anchor not a bare homepage. Report each violation found with the offending cell.\nReport: " + W + "/ReviewSchema.md", ["coverage"]),
    item("ScribeKQ46", "scribe",
         "# Target\nFinal text for QUALITY.md criterion KQ46 (draft in your seat dir only).\n# Task\nUsing ReviewQuality's draft and the spotcheck item (corpus/lessons/round-36-verifier-spotcheck.md §6 item 2), write the KQ46 table row in QUALITY.md's exact style (ID | Admit only when | Reject or limit when | Motivating lesson). Also draft a short heading line '## Criterion added — round 37: ...'. Do not edit QUALITY.md.\nReport: " + W + "/ScribeKQ46.md", ["calibration"]),
    item("ExecMisroot", "executor",
         "# Target\nFleet-root misroot sweep, early pass.\n# Task\nRun git -C /home/vgpnk/Projects/shokunin status --porcelain (no pathspec). List every untracked path that names kama or round-37 (check file contents). For each: say whether it belongs to this lane's round and must be copied into the lane under the same relative path. Do not move or delete anything; report only.\nReport: " + W + "/ExecMisroot.md", ["calibration"]),
    item("ReviewQuorum", "reviewer",
         "# Target\nRound evidence quorum check.\n# Task\nRead the r36 verifier spotcheck's §7 admission line and the prompt §2 admission rule. List what this round must still produce for admission beyond the two counters (Gate ≥1 admit + ≥1 reject, mistakes row, sourced claim, census exit 0, sources opened with quotes, D3 naming in the report). Report a checklist the L1 can close against.\nReport: " + W + "/ReviewQuorum.md", ["calibration"]),
    item("ScribeAppend", "scribe",
         "# Target\nDraft the normalized SOURCES append block (in your seat dir only).\n# Task\nFrom staged rows S330, S333, S334, S335, S346, S347, S363: produce fleet-schema rows — status mined; opened 2026-10-25; recheck 90d; used-by exactly the corpus/knowledge/ paths that cite them (S330/S333/S334/S335/S346 → kv-cache-reclamation-models.md; S347 → prefix-cache-reuse-models.md; S363 → prefix-cache-reuse-models-amendment-2026-10-23.md); teaches/scope/anchor carried from staged cells minus campaign prose; no | in any cell. Emit the block as text plus a per-row note of what you changed from the staged cell.\nReport: " + W + "/ScribeAppend.md", ["coverage"]),
]

SPEC = {
    "wave": "round-37-w1",
    "reportDir": W,
    "maxLanes": 64,
    "context": CONTEXT,
    "items": ITEMS,
}


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(SPEC, indent=1))
    print(f"wrote {OUT} items={len(ITEMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
