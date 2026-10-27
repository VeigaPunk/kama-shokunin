# Proposed ledger rows for the round-50 integration (seat X5Digest2)

Measured on a scratch clone of the lane (`git clone --shared`), fixture commits listed in
`matrix.txt`; the lane's own tree was not written except this out directory.

## 1. The six values the round introduces: no digest-ledger row is required

| Value | Kind | Class at the build + draft paragraph | Load-bearing evidence |
|---|---|---|---|
| freeze `601c8889f33d1797c712feb753974c20cf891264` | 40-hex object id | `lane_oid` (hexrun-census) | `git -C <clone> cat-file -t 601c8889…` → `commit`; `git merge-base --is-ancestor 601c8889… 97c864be…` exit 0 |
| build `97c864bead3ee4a2f629574e77263d33834ec98a` | 40-hex object id | `lane_oid` (hexrun-census) | `git cat-file -t 97c864be…` → `commit` |
| maps page sha256 `e7cdf0ff1c8d8d87e5c92e529a09270945ca3b7cafb8e823a7ca3d294f3c16a2` | 64-hex digest | `blob` (digest-ledger) | `git cat-file -p 97c864be…:.ufo/waves/round-50/c1/proc_pid_maps.5.txt \| sha256sum` → `e7cdf0ff…` |
| prctl page sha256 `906bbe5cc7e38c02a82bb60ff3b7e0d1cfb21089a1a24f00f045fb1b86edb1e4` | 64-hex digest | `blob` (digest-ledger) | same command on `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt` → `906bbe5c…` |
| CommonMark excerpt sha256 `2dbd3f25b72d95ad2653bfcd9af704d7400a027ff0ed3e81e0391c3284c66d73` | 64-hex digest | `blob` (digest-ledger) | same command on `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt` → `2dbd3f25…` |
| server digest `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | 64-hex digest | `external`, row already present | `registry/digest-ledger.tsv:16`; `sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server` → `35ac50fb…` |

Nothing becomes `unknown`. Measured: digest-ledger at the build is `unknown=0` (exit 0) and at
the build plus the draft SCORECARD/LOG paragraph it is `tokens=133 blob=117 … unknown=0`
(exit 0); the three page digests are the `+3` blobs. The server digest adds no token because
round 47/48 already cite it (`LOG.md:2323`, `corpus/SOURCES.md:241`), and `tokens` counts
distinct digests, not citations (`tools/digest-ledger.py:117-119`).

Caveat on the `blob` class: the three page digests are explained by their committed text copies
being reachable from the scanned revision, not by those files still existing at HEAD — removing
them in a descendant fixture commit left the class `blob` and `unknown=0` (`matrix.txt`, rev
`44c325cc…`). Only a history rewrite that drops the blobs would turn them `unknown`
[INFERENCE: not measured, and not something an append-only lane does].

## 2. One hexrun-census row is needed — for a round-49 citation, not a round-50 value

The build already reports one unexplained run (`tokens=1858 distinct=305 … unknown=1`, exit 1;
`.ufo/waves/round-50/measured/hexrun-build.out:2`): the fleet-repo report commit cited at
`corpus/lessons/round-49-verifier-spotcheck.md:21`. It is not a lane object (a lane clone has no
such object) and carries no ledger row. Proposed text is `proposed-hexrun-ledger-row.tsv`
(header plus one row, appended to `registry/hexrun-ledger.tsv`); the `evidence` cell points at
`evidence/f8cdb853aaff29393faeb0b6d4c2a2296778b698.json` (verbatim `gh api
repos/VeigaPunk/shokunin/commits/<sha>` output, exit 0, sha echoed, which contains both the token
and the repo cell text) with the command transcript beside it as `.cmd.txt`.

The evidence file must land in the same commit as the row: `hexrun-census.py` accepts an
`upstream` row only when the `evidence` path is a blob at the scanned revision whose bytes
contain the token and the `repo` cell text (`tools/hexrun-census.py:248-272`). Measured: with
row plus evidence, the census reports `upstream_ok=95 … unknown=0`, exit 0, at both the
build-plus-paragraph fixture (`fe959a4d…`) and the post-build HEAD integration shape
(`22e0154b…`).

## 3. Controls that show either counter can fail

* `760902e5…` — a fabricated 64-hex keeping the `e7cdf0ff` prefix (`…000`), a random 64-hex and a
  random 40-hex: digest-ledger `wrong_unflagged=1 unknown=1` exit 1; hexrun-census `unknown=2`
  exit 1.
* `efb53b72…` — the same six values written only in the item's abbreviated form
  (`e7cdf0ff…`): both counters are byte-identical to the paragraph fixture
  (`tokens=133`/`133`, `distinct=307`/`307`, same exits). Abbreviated citations are invisible to
  both (`tools/digest-ledger.py:35-38` scope note, `tools/hexrun-census.py:71-72`).
