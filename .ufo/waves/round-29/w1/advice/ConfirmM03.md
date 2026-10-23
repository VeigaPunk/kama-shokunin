# ConfirmM03 — advice

Verdict for sid `SCORECARD.md:P:980355388a:0` (SCORECARD.md:192, token `MISSION.md:29`,
W = 1e41928aba2b81dd65ea75084918a7fadf453720): **confirmed-false**, observed `p:absent`.
Established without running the counter: `git cat-file -e W:MISSION.md` fails; the file
never existed on any lane ref (`git log --all -- MISSION.md` empty), so it was a dangling
pointer at writing time, not drift.

Intended referent: fleet-root `/home/vgpnk/Projects/shokunin/MISSION.md:29` —
`kama: { cwd: kama-shokunin/, axes: "operability + freshness (local model serving/endpoints)" }`.
Line 29 identical at fleet commit 84bade0 (pre-W). Corroborated inside the lane at W:
LOG.md:277 and LOG.md:518 cite `MISSION.md:29` for operability + freshness;
`.ufo/round-10/audit/stale-anchors.tsv` A16 already resolved the same bare pointer to
`../MISSION.md` (fleet root).

Correction-row cause (≤25 words): "Statement points to lane-root MISSION.md, which never
existed in the lane; the axes authority lives at fleet-root ../MISSION.md:29, invisible to
the lane-tree check." Observed value for the row: `p:absent`.

Note for sibling seats: bare `MISSION.md` pointers in lane files denote fleet-root
`../MISSION.md`; the counter intentionally cannot resolve `../` paths (in_lane), so any
statement whose only pointer is lane-root MISSION.md will read p:absent regardless of
fleet state.

Full evidence: `.ufo/waves/round-29/w1/out/ConfirmM03/verdict.json` and `REPORT.md`.
No tool installs; all commands read-only.
