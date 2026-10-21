VERDICT: confirm - registry row c2-official-stdout exactly matches its cite token and the git-show bytes; no mismatch in rev, path, sha256, or doc binding.

# Row under inspection
registry/required-citations.json:16-22 (lane /home/vgpnk/Projects/shokunin/kama-shokunin):
- id: c2-official-stdout
- rev: 1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e
- path: .ufo/waves/round-18/runs/c2-survivors.stdout
- sha256: ea2e3e0258346410a04cef27a79c1ec0bbe1fd8ce8db13e683da327950cf272d
- doc: corpus/lessons/round-18.md

# Evidence (commands run read-only in the lane; no mutations)
1. Rev exists and is a commit: `git cat-file -t 1b85a24e` -> commit;
   `git log -1 --format='%H %ci %s'` -> "2026-10-21 02:38:35 -0300 round-18: measured
   pass on eb78788b, recovery receipts, scorecard and log". Ancestor of HEAD
   92b146253fd3a8c4bfade94c909dc63b13d6f4a8 (`git merge-base --is-ancestor` exit 0).
2. Path exists at rev: `git show 1b85a24e:.ufo/waves/round-18/runs/c2-survivors.stdout`
   exit 0; `git cat-file -s` -> 249095 bytes.
3. Digest: `git show 1b85a24e:<path> | sha256sum` ->
   ea2e3e0258346410a04cef27a79c1ec0bbe1fd8ce8db13e683da327950cf272d — exact match to
   the row sha256.
4. Doc binding: token at corpus/lessons/round-18.md:423 (bullet :422):
   `cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/c2-survivors.stdout, sha256=ea2e3e0258346410a04cef27a79c1ec0bbe1fd8ce8db13e683da327950cf272d)`.
   Rev, path, and sha256 each equal the row values; registry `doc` names the file that
   holds the token. Exactly one occurrence of this digest in the doc, also at HEAD tip
   (`git show HEAD:corpus/lessons/round-18.md | grep -c <digest>` -> 1).
5. Lane copy freshness: working-tree .ufo/waves/round-18/runs/c2-survivors.stdout
   sha256 = ea2e3e02… (same); `cmp` pinned-vs-worktree exit 0; blob id at rev equals
   blob id at HEAD (7bdf80232696fe26fbfb93e4376f88460ab2abcd both) — no tip drift.
6. Corroboration: run record .ufo/waves/round-18/runs/commands.json:691-693 records
   stdout_sha256 ea2e3e02… for the c2-survivors run (measured_commit eb78788b); frozen
   calibration evidence .ufo/waves/round-20/runs/0957ce61/citation-count.stdout:39-47
   lists this row status "ok" with observed_sha256 equal to the pin.
7. Cleanliness: `git status --porcelain` over registry/required-citations.json,
   tools/citation-provenance.py, corpus/lessons/round-18.md and the cited stdout is
   empty (all tracked, unmodified at HEAD). Round-19's "registry untracked" observation
   no longer holds at HEAD 92b14625.

LSP note: item is JSON/Markdown evidence verification; no language server answers
these files, and every check above is a git-object/digest fact, so text and sha256
evidence is direct measurement, not a semantic fallback.

Mismatch found: none.

# Residual risk / verification gaps
- Pin integrity verified (rev/path/digest/doc token), not generation provenance: that
  the stdout bytes were produced by survivors.py at measured commit eb78788b rests on
  commands.json:691-693 and round-19 receipts; rerunning was out of scope and would
  mutate the lane.
- Known adjacent defect, out of my item scope: citation-provenance.py exit-code
  contract (exit 1 for unreadable doc vs docstring "exit 2 for unusable registry/docs/
  git") — round-19/falsify/advice/CitationTokens.md finding 2; not re-tested here.
- Future rewrites of round-18.md or the registry silently move line numbers; the token
  and row currently agree byte-for-byte at HEAD 92b14625.

No installs or tool updates performed. Scratch /tmp/kama-r20-CitationC2OfficialStdout
removed before return. Registry and documents untouched.
