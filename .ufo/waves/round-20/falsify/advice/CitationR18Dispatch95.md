VERDICT: confirm - registry row r18-dispatch-95 matches its cite token and git show bytes exactly on rev, path, sha256, and doc binding; one retrospective-binding nuance noted below, not a defect.

## Row under inspection
- registry/required-citations.json:73-77 (unique row; only occurrence of "r18-dispatch-95" in the registry):
  id "r18-dispatch-95"; rev "c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d";
  path ".ufo/waves/round-18/build/dispatch-95.json";
  sha256 "59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744";
  doc "corpus/lessons/round-18.md".

## Revision and path (git, read-only)
- `git cat-file -t c6dc46f...` -> commit; `git rev-parse c6dc46f...^{commit}` -> same full SHA. Rev resolves.
- `git show c6dc46f...:.ufo/waves/round-18/build/dispatch-95.json` succeeds; blob starts
  `{"schema": "ufo-swarm-wave-dispatch-v1", ...}` — the round-18 refused dispatch payload.

## SHA-256 vs git show bytes
- sha256(`git show c6dc46f...:<path>`) = 59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744,
  171837 bytes. Exact match to the row's sha256. No mismatch.

## Worktree doc binding
- sha256(worktree .ufo/waves/round-18/build/dispatch-95.json) = same digest, 171837 bytes —
  worktree copy is byte-identical to the pinned blob.
- `git status --porcelain` on dispatch-95.json, registry, and round-18.md: empty (all clean).

## Cite-token match in doc
- corpus/lessons/round-18.md:466 (worktree): `- Refused payload: cite(c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d, .ufo/waves/round-18/build/dispatch-95.json, sha256=59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744)` —
  rev, path, and sha256 each byte-equal to the row. Prose usage at round-18.md:111 and :270
  ("dispatch-95.json ... is the refused payload") is consistent with the token's framing.
- Cross-references agree: .ufo/waves/round-20/build/out/R18CitationRows/tokens-fragment.md:4
  and build/advice/R18CitationRows.md:19 carry the identical token; frozen run evidence
  .ufo/waves/round-20/runs/0957ce61/citation-count.stdout:133-138 lists the same row bound to
  corpus/lessons/round-18.md.

## Nuance (observation, not a mismatch)
- The token is absent from corpus/lessons/round-18.md at rev c6dc46f (the doc exists there, but
  `git show c6dc46f...:corpus/lessons/round-18.md | grep "cite(c6dc46f"` is empty). `git log -S`
  dates the token's introduction to commit 33a6777 (round-20 evidence commit). The row schema
  pins only `doc` as a path — no doc rev — so the citation is retrospective by design: artifact
  pinned at its original rev, token added to the lesson later. Honest, and consistent with the
  lesson's own framing that dispatch-95.json is the refused (never-run) payload.

## Boundaries
- Read-only git inspection only (parent-clarified allowance); no registry or document modified;
  no installs; no scratch created; no subagent dispatch.
