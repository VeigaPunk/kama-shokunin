# SC05Quarantine — kama quarantine slice re-derivation (round 64, wave b)

Seat: SC05Quarantine (leaf scout; no subagent dispatch). Axis: operability.
Item: derive the kama quarantine slice at today's bytes from the shokuknow
absent-defect register, report row count and change vs round 63, and check one
row not already checked in round 63. Read-only; nothing written or executed
inside `/home/vgpnk/Projects/shokuknow`; no lane source edited; no commit.

## 1. Derivation (verbatim recipe, cwd = fleet root, file read by absolute path)

```
R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}' "$R"
```

Output (7 lines, all class `payload-absent`):

```
 S200   `payload-absent`
 S202   `payload-absent`
 S206   `payload-absent`
 S210   `payload-absent`
 S211   `payload-absent`
 S224   `payload-absent`
 S230   `payload-absent`
```

Register sha256 at today's bytes (for future drift checks):
`5afe1810a6c3d62f37987b575a954f5b1197daa23005d4bb2f1d982f64bad833`.
Per-lane totals table in the register also says `kama | 7` (register line 245).

## 2. Changed vs round 63? — NO

Round 63 (`corpus/lessons/round-63.md` §Gate, "staged `merge/kama/` quarantine
slice" row; seat reports `.ufo/waves/round-63/w1/SC04QuarantineA.md` and
`SC05QuarantineB.md`) checked exactly these 7 ids: SC04QuarantineA took
S200/S202/S206/S210, SC05QuarantineB took S210/S211/S224/S230 (overlap S210,
disclosed there; union = all seven).

- Row count: 7 today vs 7 in round 63 — unchanged.
- Membership: identical id set {S200, S202, S206, S210, S211, S224, S230} — unchanged.
- Classes: all `payload-absent` both times — unchanged.
- Quote text: byte-matches the round-63 receipts for every row I could compare
  (S200/S202/S206/S210 quoted in SC04QuarantineA's table, S211/S224/S230 in
  SC05QuarantineB's; all equal today's register cells, including S202's
  trailing space and S211's `still-live` hyphenation).

**Consequence for the item:** the set "rows not already checked in round 63"
is empty. All seven rows carry round-63 Gate verdicts (4 absent → S200, S210,
S211, S224; 3 present → S202, S206, S230). I did not fabricate an "unchecked"
row; instead I took the one row whose round-63 evidence was explicitly left
incomplete and finished it at today's bytes (§3), plus the full quote-text
comparison above as today's-bytes confirmation of the other six.

## 3. The one row finished: S200 (round 63 left a companion unresolved)

Why this row: SC04QuarantineA's verdict on S200 was **absent**, but its §Caveats
records the companion check `api.semanticscholar.org/graph/v1/paper/ARXIV:2312.07104`
returning HTTP 429 twice — "Unresolved; not needed for the verdict". That is the
only sub-check anywhere in the seven rows that round 63 did not complete.

Fetched today (receipts in `out/SC05Quarantine/`, scratch copies hashed):

- Cited source `https://arxiv.org/abs/2312.07104` → HTTP 200, 43,012 bytes,
  sha256 `8d98899fd0314583726da896c216b9d146f59e8d51ec2678582c8a7c7daa4884`.
- Register quote `DOI not in Semantic Scholar`: 0 case-insensitive hits in the
  raw HTML; the token sequence `not in` occurs 0 times. The text layer carries
  only "References & Citations SciX Google Scholar Semantic Scholar export
  BibTeX citation Loading..." (nav labels) and
  "https://doi.org/10.48550/arXiv.2312.07104 … arXiv-issued DOI via DataCite".
- Companion `.../paper/DOI:10.48550/arXiv.2312.07104` → HTTP 404,
  `{"error":"Paper with id DOI:10.48550/arXiv.2312.07104 not found"}` —
  reproduces SC04QuarantineA's observation.
- Companion `.../paper/ARXIV:2312.07104` → HTTP 429 again today, including one
  retry after 40 s backoff (`429` body "Too Many Requests…"). Round 63's gap
  stays a host-side rate limit, not a resolved lookup: receipts now 4 × 429
  across two rounds.

Verdict for S200 at today's bytes: **absent** — the quote is in none of the
cited source's bytes (fabrication class per the register's own definition),
independently agreeing with round 63. Standing caveat (unchanged from SC04):
`DOI not in Semantic Scholar` reads as a census lookup note, and the DOI-key
404 keeps its *status* plausible; but as register text it is still absent from
the cited source. New datum this round: the ARXIV-key endpoint is still 429ing,
so any future S200 correction should cite the DOI-key 404, not the ARXIV key.

## 4. Bounds and tools

- No process ran with cwd inside `/home/vgpnk/Projects/shokuknow`; the register
  was read (awk/`sha256sum`) by absolute path from the fleet root; nothing
  written there.
- No git/jj mutation anywhere except none at all this seat; no clone needed
  (no counter or lane code executed); no pacman transaction; no tool installed
  or upgraded (curl, awk, grep, sha256sum, python3 stdlib only).
- Scratch root `/fast/scratch/hyaku/kama-r64/b/SC05Quarantine` removed after
  receipts were copied to `out/SC05Quarantine/` (`s200-arxiv.html`,
  `s200-arxiv.sha256`, `s200-ss-doi.json`, `s200-ss-arxiv.json`,
  `s200-ss-arxiv-retry.json`, `register-today.sha256`, `slice-today.txt`).

quarantine kama r64: rows=7 unchanged=7/7 unchecked=0; S200 re-fetched absent (quote 0 hits; SS DOI-key 404, ARXIV-key 429×2 today)
