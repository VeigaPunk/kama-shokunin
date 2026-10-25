# CriticC1Sound — C1 over-credit review (does the counter earn "corrected"?)

**Verdict: yes, C1 over-credits, without upper bound in the row dimension.** The frozen
predicate is stronger than the instrument, and the gap is not a tradeoff — the counter can
report `false_corrections 0 / met True` while the lesson asserts the inverted mapping for all
four ids. The counter was not edited; every result below comes from importing
`tools/round37-statement-audit.py` and calling its own `score()`/`holds()`/`forbidden_in()`/
`rows_of()` with the real r36 bytes from the worktree and the real staged
`SOURCES.append.md`.

## 1. Counterexample (all four, one forged lesson)

Lesson text used (not written to the corpus path; scored in memory):

```
R36-D1: .ufo/waves/round-36/census-end.out was present at base and deleted at tip; its last line is a failure.
R36-D2A: S366 is the miswritten entry; S371 is fine and its native_api mapping is correct.
R36-D2B: S364, S365, S377 and S396 do not cite http_server.py; the http_server.py row is S388.
R36-D3: ScribeLog and RevQ206 did not fail; the 429 came from an unrelated provider call.
```

Result: `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True`
with per-branch `{'R36-D1': True, 'R36-D2A': True, 'R36-D2B': True, 'R36-D3': True}`.

Every line contradicts the frozen statement it is supposed to correct. D1 inverts base/tip
and "ends ok"; D2A inverts S371/S366 (the task's named counterexample); D2B asserts the four
ids do *not* cite `http_server.py`; D3 denies the two failures and re-attributes the 429.
The counter calls all four corrected because it never reads the claim, only token presence.

## 2. Leg classification (re-derivation vs shape-only)

"Re-derivation" = reads an artifact's bytes and checks the statement's fact. "Shape-only" =
checks that a token appears in the row; says nothing about truth or direction.

| Branch | Re-derivation legs | Shape-only legs | Wrong-id guard |
|---|---|---|---|
| R36-D1 (4 legs) | `census_base is None`; `census_tip is not None`; `"kama\tok" in census_tip` | `CENSUS_PATH in row` | none (`None`) |
| R36-D2A (5 legs) | `"native_api.mdx" in url371`; `"native_api.mdx" not in url366` | `"S371"`, `"native_api"`, `"miswritten"` in row | **none** — `forbidden_in` returns `None` |
| R36-D2B (6 legs) | compound `all("http_server.py" in (staged_url(s) or ""))` over S364/S365/S377/S396 | `"http_server.py"` + four ids in row | S359/S360/S372/S391 (matches spotcheck §6 exactly) |
| R36-D3 (6 legs) | `need` (both names present in exitcodes); `rc1 = count('"rc": 1') >= 2`; `rate` (`rate_limit` ∧ `429` in the two seat logs) | `"ScribeLog"`, `"RevQ206"`, `"429"` in row | `rc=0`, `rc=143` |

## 3. Substrings that appear without the fact being true

**D1 — `CENSUS_PATH in row` (weakest shape leg of D1).** The row only has to name the path. An
inverted row (present-at-base / failure-at-tip) passes. Also `"kama\tok" in census_tip` is a
substring, not the stated suffix "ends 'kama ok'": a census of
`kama\tok\t…` followed by `kama\tW04\tfailure: duplicate url` satisfies the leg while the
statement "ends kama ok" is false (verified `True`). Tab-vs-space also differs from the
statement text.

**D2A — the counterexample.** `"S371"`, `"native_api"`, `"miswritten"` are three independent
substrings, and `forbidden_in("R36-D2A", …)` returns `None`. So
`S366 is miswritten; S371 is fine and its native_api mapping is correct` passes. The
statement's own forbidden restatement ("not the lesson's S366") is checked only against the
*package* (`"native_api.mdx" not in url366`), never against the row. This is the branch with a
missing denylist while D2B and D3 both have one — an asymmetry, not a deliberate tradeoff.

**D2B — presence is not mapping.** A row with the four ids plus `http_server.py` passes even
when it asserts they do *not* cite it (`…do not cite http_server.py; the row is S388` passes —
S388 is not on the denylist). The denylist is line-scoped: `S359` on a dropped earlier line, or
in surrounding prose, escapes (`forbidden_in` on the picked line → `None`; line 1 carries
`S359`; prose `S359` → `None`).

**D3 — the rc binding is factually broken, not merely shape-only.**
`'"rc": 1'` is a prefix of `'"rc": 143'`. In the real
`.ufo/waves/round-36/w3/out/seat-exit-codes.json` (2 rows at `rc: 1`, 6 at `rc: 143`),
`count('"rc": 1')` is **8**. Consequence: setting ScribeLog and RevQ206 to `rc: 0` in the same
artifact still yields D3 `True` (verified), and a synthetic file `{rc:0, rc:0, rc:143, rc:143}`
also yields D3 `True` (verified). `need` only checks that the two *names* exist, not their rc;
`rc1` is not bound to any seat. The leg can therefore be true while the statement "records
ScribeLog and RevQ206 at rc=1" is false. The leg is also format-coupled: compact JSON
(`"rc":1`) makes it always 0 (fail-closed).

**Row identity — shape-only and unscoped.** `rows_of` accepts any line containing `<id>:`, in
any section, and the last matching line wins. Verified: the four rows placed as *quotes* under
`## Mistakes` (never a correction row) still give `met True`; a correct D2B line preceded by a
line carrying `S359` is scored on the clean last line, so the wrong-id restatement is never
seen. C2's kill_rule explicitly scopes names to `## Coverage map — round 37 addition`; C1 has
no analogous heading scoping.

## 4. Provenance defect inside the "re-derivation" legs

`staged_url` returns `cells[2]`, the whole content cell (description **and** URL), not the URL.
Verified: a staged `| S371 | native_api.mdx page superseded; actual: https://example.com/other.txt |`
satisfies D2A's fact legs although the URL is not `native_api.mdx`; the same construction
satisfies D2B's compound leg for S364. So the "re-derives the cited committed-byte fact" leg
can be satisfied by prose.

Separately, the D2A/D2B fact source is
`/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` — outside the lane repo, not
committed at the audited tip, and not pinned by any hash in the counter. The predicate's words
("cited committed-byte fact") are not what the counter checks. The report-blob leg reads
`git_blob(FLEET, "HEAD", …)` (moving ref, currently `7c060ea7b009`), not a pinned commit.

## 5. Weakest leg

- **Weakest single leg: `rc1 = exitcodes.count('"rc": 1') >= 2`.** It is the only leg in a
  *re-derivation* position that is provably true while its fact is false in the actual r36
  artifact (6× `rc: 143` supply the count), and it binds no seat.
- **Weakest branch: R36-D2A.** Three unanchored substrings, no denylist at all, while its own
  statement forbids `S366`.
- **Weakest-by-construction: `"miswritten" in row`.** Unanchored to any id; with D2A's missing
  denylist it can attach to `S366` and still pass.

## 6. Impacted axes

- **calibration (C1, 7 → 7):** the claimed predicate is met by construction, so a "corrected"
  claim can be won by a false correction row. Calibration cannot rise on this evidence.
- **provenance/grounding (indirect):** unpinned external `SOURCES.append.md` and `FLEET HEAD`
  are presented as committed-byte facts.
- **duplicate authority:** the preregistration statements, the predicate, and the counter now
  hold three different strengths; only the counter executes, and it is the weakest.

## 7. Smallest safe correction

Minimal, local to `holds`/`forbidden_in`/`staged_url`, each fail-closed on the current data:

1. `forbidden_in("R36-D2A")` → `("S366",)`. One branch, two lines; safe because S366 can never
   belong in a correct D2A row.
2. Replace `rc1` with a parse: `json.loads(exitcodes)` and require
   `all(r["rc"] == 1 for r in rows if r["name"] in ("ScribeLog","RevQ206"))` plus both names
   present. Removes the `rc: 143` and cross-seat over-credit.
3. `staged_url` → `re.search(r"https?://\S+", cell)` (return the URL token, not the cell), so
   description prose cannot satisfy the fact leg. Current rows all carry exactly one URL, so
   this changes no present result.
4. `holds` D1: `census_tip.rstrip("\n").splitlines()[-1].startswith("kama\tok")` — matches the
   statement's "ends" instead of any-line substring.

Steps 1–3 are the smallest set that removes the demonstrated over-credit; they are all
defects, not tradeoffs. Full soundness additionally needs the *row* to bind id→fact (e.g.
`S371[^\n]{0,80}native_api` and `S366` absent; heading-scoped row collection, forbidden scan
over the whole correction section). That anchoring is the genuine judgment call, because a
literal-adjacency regex constrains legitimate prose — it should be the canonical judge's
decision, not applied silently.

*No file other than this report was written; the counter was not edited; no vcs mutation was
run.*
