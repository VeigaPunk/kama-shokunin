#!/usr/bin/env bash
# Supplementary read-only checks for matrix.md (writes evidence_extra.txt). Exit codes printed per step.
F=/home/vgpnk/Projects/shokunin
L=$F/kama-shokunin
OUT=$L/.ufo/waves/round-21/build/out/ClosureNotesSweep
M=$OUT/matrix.md
exec > >(tee "$OUT/evidence_extra.txt") 2>&1
step(){ printf '\n$ %s\n' "$1"; }
ok(){ echo "  -> exit=$?"; }

step "matrix rows (lines starting with an R-id)"; grep -c '^| R[0-9][0-9]-' "$M"; ok
for s in RESOLVED RESOLVED-BY-DISCLOSURE OPEN OPEN-DRAFT DECLARED-OPEN FLEET/OPERATOR PROBE-ANSWERED; do step "matrix status cell == $s"; grep -c "^| R[0-9][0-9]-[^|]* | [^|]* | [^|]* | $s |" "$M"; ok; done

step "draft a29bb84 files touched (stat)"; git -C "$L" show --stat --format= a29bb84 | cat; ok
step "SKILL.md at a29bb84: install-links mentions (0 = unregistered)"; git -C "$L" show a29bb84:SKILL.md | grep -c 'install-links'; ok
step "first commit: KQ23 in QUALITY.md"; git -C "$L" log --reverse --format='%h %s' -S'KQ23 ' -- corpus/QUALITY.md | sed -n '1p'; ok
step "first commit: models_alias_id in controls.py (k9-k14 family)"; git -C "$L" log --reverse --format='%h %s' -S'models_alias_id' -- tests/llamacpp-live/controls.py | sed -n '1p'; ok
step "first commit: except BaseException in kama-llamacpp-live.py"; git -C "$L" log --reverse --format='%h %s' -S'except BaseException' -- tools/kama-llamacpp-live.py | sed -n '1p'; ok
step "first commit: docs.python.org/3.14 subprocess link"; git -C "$L" log --reverse --format='%h %s' -S'docs.python.org/3.14/library/subprocess' -- tools/kama-llamacpp-live.py | sed -n '1p'; ok
step "first commit: round-18 lesson line-anchor qualification"; git -C "$L" log --reverse --format='%h %s' -S'Line-anchor qualification' -- corpus/lessons/round-18.md | sed -n '1p'; ok
step "first commit: residual PROVENANCE file"; git -C "$L" log --reverse --format='%h %s' -- .ufo/waves/round-18/residual/assignments.PROVENANCE.md | sed -n '1p'; ok
step "first commit: round-17 SKILL correction (routed by round-16 spot-check)"; git -C "$L" log --reverse --format='%h %s' -S'Round-17 correction (routed by' -- SKILL.md | sed -n '1p'; ok
step "lane HEAD still a29bb84 (read-only confirmation)"; git -C "$L" rev-parse --short HEAD; ok
echo; echo done
