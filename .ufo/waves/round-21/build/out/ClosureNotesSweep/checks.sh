#!/usr/bin/env bash
# ClosureNotesSweep evidence (read-only). Each check prints its command and exit code.
# Lane and fleet repos are only read (git show/cat-file/log, sed, grep -c, sha256sum).
# citation-provenance steps run in the scratch clone /tmp/kama-r21-ClosureNotesSweep/lane
# checked out at a29bb84; the lane checkout is not modified.
F=/home/vgpnk/Projects/shokunin
L=$F/kama-shokunin
C=/tmp/kama-r21-ClosureNotesSweep/lane
OUT=$L/.ufo/waves/round-21/build/out/ClosureNotesSweep
mkdir -p "$OUT"
exec > >(tee "$OUT/evidence.txt") 2>&1
step(){ printf '\n$ %s\n' "$1"; }
ok(){ echo "  -> exit=$?"; }

step "git -C lane rev-parse --short HEAD"; git -C "$L" rev-parse --short HEAD; ok
step "git -C lane log --oneline 7a6bc91..a29bb84"; git -C "$L" log --oneline 7a6bc91..a29bb84 | cat; ok

echo; echo "=== R20 closure: D1 unresolved full hash, D2 landed omissions ==="
step "git -C lane cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c (bad hash)"; git -C "$L" cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c 2>/dev/null; ok
step "git -C fleet cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c (bad hash)"; git -C "$F" cat-file -e 0957ce619789d13d894ef21bc863486bcb35b56c 2>/dev/null; ok
step "git -C lane cat-file -e 0957ce619789d13bb5779606078fa1498114d2c7 (correct hash)"; git -C "$L" cat-file -e 0957ce619789d13bb5779606078fa1498114d2c7; ok
step "git -C fleet log -- .ufo/reports/round-20/kama.md"; git -C "$F" log --format='%h %an %ad %s' --date=short -- .ufo/reports/round-20/kama.md | cat; ok
step "fleet round-20 report line 7 (bad hash)"; sed -n '7p' "$F/.ufo/reports/round-20/kama.md" | cut -c1-120; ok
step "fleet round-20 report lines 13-19 (Landed changes)"; sed -n '13,19p' "$F/.ufo/reports/round-20/kama.md" | cut -c1-100; ok
step "fleet report HEAD blob sha256 vs working-tree sha256"; git -C "$F" show HEAD:.ufo/reports/round-20/kama.md | sha256sum; sha256sum "$F/.ufo/reports/round-20/kama.md"; ok
step "splice: bad[1-15] vs correct[1-15]; bad[16-40] vs 33a6777[16-40]"; echo 0957ce619789d13d894ef21bc863486bcb35b56c | cut -c1-15; echo 0957ce619789d13bb5779606078fa1498114d2c7 | cut -c1-15; echo 0957ce619789d13d894ef21bc863486bcb35b56c | cut -c16-40; echo 33a6777866d0f63d894ef21bc863486bcb35b56c | cut -c16-40; ok
step "draft errata rows 3-7 (registry/report-landing-errata.tsv at a29bb84)"; git -C "$L" show a29bb84:registry/report-landing-errata.tsv | sed -n '3,7p' | cut -c1-110; ok

echo; echo "=== L0 questions in fleet root (tracked) ==="
step "git -C fleet ls-files --error-unmatch .ufo/l0-questions.md"; git -C "$F" ls-files --error-unmatch .ufo/l0-questions.md; ok
step "fleet L0 line 58 (kama round-16 fixture ratification)"; sed -n '58p' "$F/.ufo/l0-questions.md" | cut -c1-90; ok
step "fleet L0 line 68 (kama round-17 llama archive)"; sed -n '68p' "$F/.ufo/l0-questions.md" | cut -c1-90; ok
step "fleet L0 answer markers (count)"; grep -c 'L0 ANSWE' "$F/.ufo/l0-questions.md"; ok
step "fleet L0 answer markers (line numbers)"; grep -n 'L0 ANSWE' "$F/.ufo/l0-questions.md" | cut -c1-30; ok

echo; echo "=== host llama.cpp install facts (read-only) ==="
step "command -v llama-server"; command -v llama-server; ok
step "readlink -f ~/.local/bin/llama-server"; readlink -f "$HOME/.local/bin/llama-server"; ok
step "test -e /usr/bin/llama-server"; test -e /usr/bin/llama-server; ok
step "release archive present"; ls -l "$HOME/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz" | cut -c1-120; ok
step "compgen -G '/tmp/kama-r19-*' (empty = scratch removed)"; compgen -G '/tmp/kama-r19-*'; ok

echo; echo "=== R16 falsify verdicts recount from committed advice ==="
step "round-16 falsify advice file count"; ls "$L/.ufo/waves/round-16/falsify/advice" | wc -l; ok
step "round-16 falsify first-line VERDICT distribution (*.md)"; (cd "$L/.ufo/waves/round-16/falsify/advice" && for f in *.md; do l=$(head -n1 "$f"); case "$l" in VERDICT:*) echo "$l" | cut -d' ' -f2 | tr -d '[:punct:]';; *) echo NONCONFORMANT;; esac; done | sort | uniq -c); ok

echo; echo "=== R15/R16/R17 lane state at a29bb84 ==="
step "corpus/README.md:238 (S043-only exit-status pointer; no S047)"; git -C "$L" show a29bb84:corpus/README.md | sed -n '238p' | cut -c1-200; ok
step "corpus/README.md:230-232 (round-17 correction: OPTIONS only)"; git -C "$L" show a29bb84:corpus/README.md | sed -n '230,232p' | cut -c1-120; ok
step "SKILL.md:652-654 (verifier registrations, incl. --expect-install-tree-sha256)"; git -C "$L" show a29bb84:SKILL.md | sed -n '652,654p' | cut -c1-90; ok
step "controls.py:18-21 (six v2 checks with retained controls k9-k14)"; git -C "$L" show a29bb84:tests/llamacpp-live/controls.py | sed -n '18,21p' | cut -c1-90; ok
step "check-receipt.py:33-34 (exit map: 2 unreadable, 3 NOT-EVALUATED)"; git -C "$L" show a29bb84:tests/llamacpp-live/check-receipt.py | sed -n '33,34p'; ok
step "check-receipt.py:609-613 (exact argv re-derivation)"; git -C "$L" show a29bb84:tests/llamacpp-live/check-receipt.py | sed -n '609,613p' | cut -c1-100; ok
step "kama-llamacpp-live.py: count 'except BaseException'"; git -C "$L" show a29bb84:tools/kama-llamacpp-live.py | grep -c 'except BaseException'; ok
step "kama-llamacpp-live.py: count '/3/' docs link (expect 0)"; git -C "$L" show a29bb84:tools/kama-llamacpp-live.py | grep -c 'docs.python.org/3/'; ok
step "kama-llamacpp-live.py:59-61 (docs link now /3.14/)"; git -C "$L" show a29bb84:tools/kama-llamacpp-live.py | sed -n '59,61p' | cut -c1-100; ok
step "tools/sources-append-only.py tracked"; git -C "$L" ls-files -- tools/sources-append-only.py; ok
step "SOURCES.md S012 cross-source synthesis note"; git -C "$L" show a29bb84:corpus/SOURCES.md | grep -n 'cross-source synthesis' | cut -c1-90; ok
step "ollama-evidence-replay.md ordering precision (appended r16)"; git -C "$L" show a29bb84:corpus/knowledge/ollama-evidence-replay.md | grep -n 'Repair ordering precision' | cut -c1-90; ok
step "round-17 lesson M1 (S041 in-place) and M7 ('still no mechanical guard')"; git -C "$L" show a29bb84:corpus/lessons/round-17.md | sed -n '85p;90p' | cut -c1-140; ok
step "round-16 lesson M6/M7 rows"; git -C "$L" show a29bb84:corpus/lessons/round-16.md | sed -n '169,170p' | cut -c1-140; ok
step "round-17 spot-check: seven falsify seats not respawned"; git -C "$L" show a29bb84:corpus/lessons/round-17-verifier-spotcheck.md | sed -n '255,258p' | cut -c1-120; ok
step "fleet MISSION.md bucket map (route map item)"; sed -n '62,65p' "$F/MISSION.md" | cut -c1-100; ok
step "SHONEN [~] count (expect 4)"; git -C "$L" show a29bb84:SHONEN.md | grep -c '\[~\]'; ok

echo; echo "=== R18 / R19 / R20 carried items at a29bb84 ==="
step "round-18 lesson 316 (five-confirm text kept, append-only)"; git -C "$L" show a29bb84:corpus/lessons/round-18.md | sed -n '316p' | cut -c1-100; ok
step "round-18 lesson 387-389 (round-19 erratum)"; git -C "$L" show a29bb84:corpus/lessons/round-18.md | sed -n '387,389p' | cut -c1-100; ok
step "round-18 lesson 425-427 (round-20 correction of line-42 rewrite)"; git -C "$L" show a29bb84:corpus/lessons/round-18.md | sed -n '425,427p' | cut -c1-100; ok
step "round-18 lesson 441-449 (retrospective roster + S051 heading qualification)"; git -C "$L" show a29bb84:corpus/lessons/round-18.md | sed -n '441,449p' | cut -c1-100; ok
step "round-18 lesson 288-291 (deferred named debt: GateCaptureHashes, fresh mutants)"; git -C "$L" show a29bb84:corpus/lessons/round-18.md | sed -n '288,291p' | cut -c1-100; ok
step "round-18 lesson: mutant (b) exclusion lines"; git -C "$L" show a29bb84:corpus/lessons/round-18.md | grep -n 'mutant (b)' | cut -c1-90; ok
step "SOURCES.md S055 qualification and S051 clarification"; git -C "$L" show a29bb84:corpus/SOURCES.md | sed -n '218,219p;225,226p' | cut -c1-100; ok
step "SCORECARD.md 785-786 (mutant (b) excluded), 799-802 (deferred R18 plan), 809-811 (C2 erratum)"; git -C "$L" show a29bb84:SCORECARD.md | sed -n '785,786p;799,802p;809,811p' | cut -c1-110; ok
step "SCORECARD.md 853-855 (round-20 correction of round-19 record)"; git -C "$L" show a29bb84:SCORECARD.md | sed -n '853,855p' | cut -c1-100; ok
step "SCORECARD.md 919-922 (R20 planned frontier incl. symlinked soname identity)"; git -C "$L" show a29bb84:SCORECARD.md | sed -n '919,922p' | cut -c1-120; ok
step "round-19 lesson 109-111 (falsify-label appended correction)"; git -C "$L" show a29bb84:corpus/lessons/round-19.md | sed -n '109,111p' | cut -c1-100; ok
step "LOG.md 1176-1181 (round-20 correction of round-19 counts) and 1193-1196 (scratch removal)"; git -C "$L" show a29bb84:LOG.md | sed -n '1176,1181p;1193,1196p' | cut -c1-100; ok
step "round-20 lesson 81 (M7: 42-run counter not rerun)"; git -C "$L" show a29bb84:corpus/lessons/round-20.md | sed -n '81p' | cut -c1-260; ok
step "round-20 lesson 188-189 (declared limits: v3 scalars, timeout-reason precision)"; git -C "$L" show a29bb84:corpus/lessons/round-20.md | sed -n '188,189p' | cut -c1-120; ok
step "round-20 lesson 206-209 (S051 pointer correction)"; git -C "$L" show a29bb84:corpus/lessons/round-20.md | sed -n '206,209p' | cut -c1-110; ok
step "residual assignments + PROVENANCE tracked; census-after tracked; final-selftests tracked; clean rerun tracked"; git -C "$L" ls-files -- .ufo/waves/round-18/residual/assignments.PROVENANCE.md .ufo/waves/round-19/sources/census-after.txt .ufo/waves/round-19/evidence/final-selftests.txt .ufo/waves/round-20/build/out/SelftestsAtCommit/final-selftests-37bd4c5b.txt; ok
step "git log: census-after.txt first commit"; git -C "$L" log --format='%h %s' -- .ufo/waves/round-19/sources/census-after.txt | cat; ok
step "git log: final-selftests.txt commits (dirty-tree header)"; git -C "$L" log --format='%h %s' -- .ufo/waves/round-19/evidence/final-selftests.txt | cat; ok
step "final-selftests.txt line 1 (measured_tree header)"; git -C "$L" show a29bb84:.ufo/waves/round-19/evidence/final-selftests.txt | sed -n '1p'; ok
step "registry rows with id (expect 17)"; git -C "$L" show a29bb84:registry/required-citations.json | jq '[.. | objects | select(has("id"))] | length'; ok
step "registry r18-* rows (expect 13)"; git -C "$L" show a29bb84:registry/required-citations.json | jq -r '[.. | objects | select(has("id")) | .id | select(startswith("r18-"))] | length'; ok
step "install-tree-grid.py:85-91 (exit 1 counts as rejected only with INVALID stdout)"; git -C "$L" show a29bb84:tests/llamacpp-live/install-tree-grid.py | sed -n '85,91p'; ok
step "citation-provenance.py:300-302 (observed-digest selftest branch)"; git -C "$L" show a29bb84:tools/citation-provenance.py | sed -n '300,302p'; ok
step "run.py:5 hard-coded lane root (SentinalSecrets)"; git -C "$L" show a29bb84:.ufo/waves/round-18/runs/run.py | sed -n '5p' | cut -c1-130; ok
step "install_tree silent skips (GridDefaults / TreeDeterminism finding 3)"; git -C "$L" show a29bb84:tools/kama-llamacpp-live.py | sed -n '191,199p'; ok
step "draft install_links (TreeCap fix) with silent skip"; git -C "$L" show a29bb84:tools/kama-llamacpp-live.py | sed -n '205,223p'; ok
step "TreeDeterminism seat advice verdict line"; git -C "$L" show a29bb84:.ufo/waves/round-19/build/advice/TreeDeterminism.md | sed -n '1p' | cut -c1-160; ok

echo; echo "=== attribution: first commit carrying each resolution string ==="
step "R19 erratum in round-18 lesson"; git -C "$L" log -n1 --format='%h %s' -S'Erratum — round-19 routed defects' -- corpus/lessons/round-18.md; ok
step "R20 correction of line-42 rewrite"; git -C "$L" log -n1 --format='%h %s' -S'Round-20 correction — filed wording' -- corpus/lessons/round-18.md; ok
step "S055 revision qualification"; git -C "$L" log -n1 --format='%h %s' -S'S055 revision qualification' -- corpus/SOURCES.md; ok
step "SCORECARD C2 erratum (round 19, routed defect 3)"; git -C "$L" log -n1 --format='%h %s' -S'Erratum (round 19, routed defect 3)' -- SCORECARD.md; ok
step "SCORECARD round-20 correction of round-19 record"; git -C "$L" log -n1 --format='%h %s' -S'Round-20 correction of round-19 record' -- SCORECARD.md; ok
step "SKILL.md citation-provenance registration"; git -C "$L" log -n1 --format='%h %s' -S'citation-provenance' -- SKILL.md; ok
step "registry r18 rows"; git -C "$L" log -n1 --format='%h %s' -S'r18-retrospective-assignments' -- registry/required-citations.json; ok
step "citation-provenance observed-digest branch"; git -C "$L" log -n1 --format='%h %s' -S'observed-digest' -- tools/citation-provenance.py; ok
step "grid INVALID-only kill rule"; git -C "$L" log -n1 --format='%h %s' -S'startswith("INVALID ")' -- tests/llamacpp-live/install-tree-grid.py; ok
step "S012 cross-source synthesis note"; git -C "$L" log -n1 --format='%h %s' -S'cross-source synthesis' -- corpus/SOURCES.md; ok
step "replay ordering precision (appended)"; git -C "$L" log -n1 --format='%h %s' -S'Repair ordering precision' -- corpus/knowledge/ollama-evidence-replay.md; ok
step "R20 round-20 commits (subject round-20:)"; git -C "$L" log --format='%h %s' 37bd4c5..7a6bc91 | grep -c ' round-20:'; ok

echo; echo "=== citation provenance tool in scratch clone at a29bb84 ==="
step "citation-provenance.py (default run)"; (cd "$C" && python3 -B tools/citation-provenance.py); ok
step "citation-provenance.py --selftest"; (cd "$C" && python3 -B tools/citation-provenance.py --selftest); ok

echo; echo "done"
