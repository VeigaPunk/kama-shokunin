# Appended errata: round-50 closure routed defects R1, R4, R5 (draft)

seat: T7Errata (round-51 leaf seat, wave a2w1)
date: 2026-10-27
lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
round-50 base: `26ecba64ad6fb571d09074b07202d1618a46ecd1`
round-50 measured / results: `8370e39cc9a0589b831a724b00e6fa4a6293e52f` (`239` rows)
round-50 lane tip (closure endpoint): `5a1e29a14669521982843fd249583bf8ba755a51`
round-51 base: `57a2e25bf702b03aa61f9265e968cf68058ecb82`
round-51 build / build-fix / build-fix 2: `b6bed925b032ac2c19b63ef4af358ebdd5922c26`, `73bf2a7a17104a62a3e442912c8776cbd8dedbd5`, `138af25b963450b6520794995605fa7dbbcd87e0`
round-51 lane tip at the time of this seat: `4eca4892acca6ca4072a0a6fad577d0dd78a5dda`
closure source for the three routes: `corpus/lessons/round-50-verifier-spotcheck.md:113,116,117`

This file is a **draft**. Nothing here was applied to the lane: `corpus/SOURCES.md`, `corpus/lessons/round-50.md` and `corpus/lessons/round-51.md` are untouched by this seat. Each erratum gives what was said, what is true, the command that shows it, and a ready-to-paste text. Raw command output: `r1-rows.out`, `r4-counter.out`, `r5-s498.out` beside this file.

Where the text should land: `corpus/lessons/round-51.md` `## Errata (round-50 closure routed defects)` (`:37-41`) already holds a one-line draft of all three. The three entries below are the verified text for those lines; the only substantive correction to the existing draft is in E-R5 ("immutable" is not what the A-row rule says).

---

## E-R1 — round-50 report row count: said 237 → 240, true 236 → 239

**What was said.** `/home/vgpnk/Projects/shokunin/.ufo/reports/round-50/kama.md:61`, under `## Sources & frontier` (`:59`):

> `- **Row count** (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md`): **237 → 240**.`

**What is true.** The cited command prints **236** at the round-50 base `26ecba64` and **239** at the round-50 lane tip `5a1e29a1`; also 239 at the measured commit `8370e39c` and at the round-51 base `57a2e25b`. The delta the report claims (3) is right, both endpoints are one high. The number 240 first appears at the round-51 build `b6bed925`, which adds S499 — it is not a count at any round-50 rev.

**The command.**

```
$ for r in 26ecba64ad6fb571d09074b07202d1618a46ecd1 5a1e29a1 8370e39c b6bed925 57a2e25b 4eca4892; do
    printf '%s ' "$r"; git show $r:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'; done
26ecba64ad6fb571d09074b07202d1618a46ecd1 236
5a1e29a1 239
8370e39c 239
b6bed925 240
57a2e25b 239
4eca4892 240
$ git diff --stat 26ecba64 5a1e29a1 -- corpus/SOURCES.md
 corpus/SOURCES.md | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
$ git diff 26ecba64 5a1e29a1 -- corpus/SOURCES.md | grep -cE '^-\|[[:space:]]*S[0-9]{3,}'
0
```

The round-50 table changes are in `97c864be` (the three S496–S498 additions) and `3d42897b` (the S498 tick-parity edit); neither deletes a `| S###` row line (`r1-rows.out`). Therefore 236 + 3 additions = 239, and all the round-50 endpoint states read 236 or 239, not 237 or 240.

**Ready-to-paste text.**

> **R1 (closed).** The round-50 report's `Row count` line reads 237 → 240. The command it cites prints **236 → 239** at the round-50 base `26ecba64` and the round-50 lane tip `5a1e29a1`: `git show <rev>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`. The delta (3: S496–S498, no removed row line) was right; both endpoints were one high. 240 is the count at the round-51 build `b6bed925`, after S499.

---

## E-R4 — Gate reject 2 credits the counter with the live tool's O_NOFOLLOW/fstat open

**What was said.** `corpus/lessons/round-50.md:27` (Gate, second reject bullet, the one on a maps inode without the file hash):

> `- **Reject a maps inode without the file hash.** A host copy of the model path would match the inode but not `MODEL_SHA`; the counter re-opens the pathname O_NOFOLLOW, fstat-checks dev/inode, then hashes. Flip: never.`

**What is true.** The reject decision stands — an inode without a hash does not identify the model bytes — but the mechanism belongs to `tools/kama-llamacpp-live.py`, not to the counter.

- Counter `tools/round50-replay-bind-audit.py` `mapped_model()` (`:309-340`): takes `(dev, inode, pathname)` from `/proc/<pid>/maps` (`:319-327`), then `st = os.stat(path)` (`:330`) — which follows symlinks — compares dev/inode (`:333`) and a size bound (`:335`), then `sha_file(path) == MODEL_SHA` (`:337`). `sha_file()` opens **by path** in a second open (`:129-137`, `open(path, "rb")` at `:132`). Neither `O_NOFOLLOW` nor `fstat` occurs anywhere in the counter (`grep` over the file: no match).
- The O_NOFOLLOW + fstat + fd-hash path is `tools/kama-llamacpp-live.py` `model_mapping()` (`:678-746`): `os.open(want, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)` (`:704`), `os.fstat(fd)` with dev/inode/regular-file checks (`:709-713`), sha256 read from that fd (`:717-726`).
- `corpus/lessons/round-50.md:12` (the Claims entry) already attributes O_NOFOLLOW/fstat to `kama-llamacpp-live.py` correctly; only `:27` misattributes it.

**Residual limit this erratum leaves open.** Because the counter stats by path and hashes by a second open of that same path, a replacement of the path's target between `:330` and `:337` would hash bytes the dev/inode comparison did not accept. The closure's option (make the counter open once with O_NOFOLLOW and hash the fstat-checked fd) is not taken: the counter is frozen and the C1 counter for round 51 keeps the round-50 `mapped_model()` bytes. Recorded as a stated limit, not a repair.

**The command.**

```
$ grep -n 'O_NOFOLLOW\|fstat' tools/round50-replay-bind-audit.py
$ echo $?
1                     # no match in the counter
$ sed -n '330p;337p' tools/round50-replay-bind-audit.py
            st = os.stat(path)
        if sha_file(path) == MODEL_SHA:
$ grep -n 'os.O_NOFOLLOW\|os.fstat' tools/kama-llamacpp-live.py
704:        fd = os.open(want, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
709:        st = os.fstat(fd)
```

**Ready-to-paste text.**

> **R4 (closed in wording).** `corpus/lessons/round-50.md:27` says "the counter re-opens the pathname O_NOFOLLOW, fstat-checks dev/inode, then hashes". That is `tools/kama-llamacpp-live.py` `model_mapping()` (`:678-746`; `os.open` O_NOFOLLOW `:704`, `os.fstat` `:709`). The counter `tools/round50-replay-bind-audit.py` `mapped_model()` uses `os.stat(path)` (`:330`, follows symlinks) and then hashes by path in a second open (`sha_file(path)` `:337`, `open(path)` `:132`). The reject stands; only its reason was misattributed. Left open as a stated limit of the frozen counter: the stat→open window means the hashed bytes are not the fstat-checked fd.

---

## E-R5 — S498's teaches quote elides the source's parenthetical fence characters, unmarked

**What was said.** `corpus/SOURCES.md:251`, cell 7 (`teaches`), unchanged at HEAD:

> `"A code fence is a sequence of at least three consecutive backtick characters or tildes." — so a section scanner must not treat a `## ` line inside a fence as a heading`

**What is true.** CommonMark 0.31.2 §4.5 reads:

> "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~)."

The two parenthetical literals `(`)` and `(~)` were dropped with no `...` or `[…]` marking the omission (a side effect of the tick-parity rebuild, `corpus/lessons/round-50.md` Mistakes #1, commit `3d42897b`). The claim the quote supports — a `## ` line inside a fence is content, not a heading — is unaffected.

**The command.** Two independent reads agree: the committed section copy and a fresh fetch of the page.

```
$ sed -n '5,8p' .ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt
A code fence is a sequence
of at least three consecutive backtick characters (`) or
tildes (~).  (Tildes and backticks cannot be mixed.)
$ curl -sSL https://spec.commonmark.org/0.31.2/ | sha256sum
c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d  -
# tags stripped, whitespace collapsed, from the fetched page:
'A code fence is a sequence of at least three consecutive backtick characters ( ` ) or tildes ( ~ ). (Tildes and backticks cannot be mixed.)'
```

The fetched page's sha256 equals the full-page sha256 the committed section copy records on its line 1 (`c85f56cc…0f0d`), so the committed copy is the live text.

**Correction to the existing round-51 draft.** `corpus/lessons/round-51.md:41` justifies leaving the row alone with "The row is immutable outside status/recheck/used-by (A-row)". That is not what the A-row rule says. Under `tools/append-only-audit.py` v6 (`:9-16`), `permitted` covers a deleted registry row that **the same commit still holds** with every cell except status/recheck/used-by byte-equal; a row whose `teaches` cell changes is a **graded in-place edit**, not an allowed one. The lane's own ledger shows exactly that for this row: `registry/append-only-disclosures.tsv` has `3d42897b  corpus/SOURCES.md  d0c8b17e80551a96fa5a538352cec799d5fe3263669c7be3fd3f54dc820c7a3f  1  in-place-edit  deleted in place by: round-50: build-fix - S498 row markdown tick parity …`, and `d0c8b17e…` is the sha256 of the CR-stripped `| S498 …` line at `97c864be` (recomputed, `r5-s498.out`). So the row can be corrected in place; the lane records the correction in the erratum for source hygiene and disclosure, not because the row is immutable.

**Separator (part of R5).** The S498 build removed the blank line before `## Paths`; it is back from `b6bed925` on. Observed: `97c864be`, `3d42897b`, `5a1e29a1` → NOBLANK; `b6bed925`, `4eca4892` → blank.

**The command (separator).**

```
$ for r in 97c864be 3d42897b 5a1e29a1 b6bed925 4eca4892; do printf '%s ' "$r";
    git show $r:corpus/SOURCES.md | awk '/^## Paths/{print (prev=="" ? "blank" : "NOBLANK")} {prev=$0}'; done
97c864be NOBLANK
3d42897b NOBLANK
5a1e29a1 NOBLANK
b6bed925 blank
4eca4892 blank
```

**Ready-to-paste text.**

> **R5 (closed by erratum).** S498's `teaches` cell (`corpus/SOURCES.md:251`) quotes §4.5 as "A code fence is a sequence of at least three consecutive backtick characters or tildes." The source reads "… backtick characters (`) or tildes (~)."; both parenthetical literals were dropped without an ellipsis by the tick-parity rebuild (`3d42897b`). Correct quote, elisions marked: "A code fence is a sequence of at least three consecutive backtick characters … or tildes …". The scanner claim is unaffected, and the row may be corrected in place — v6 grades that as an in-place edit (as it already did for this very line at `3d42897b`, ledger key `d0c8b17e…`); the correction is recorded here instead, not because the row is immutable. The blank separator before `## Paths`, removed by the same build, is back from `b6bed925`.

---

## Verification limits of this draft

- Row counts and diffs were read from `git show <rev>:corpus/SOURCES.md` in the lane; no working-tree state, no counter run, no clone, no lane mutation.
- The two round-51 claim counters were **not** run by this seat; nothing here asserts a `met` value. This seat ran no llama-server and started no service.
- R4's residual stat→hash window is reported from the source text; no exploit was attempted or demonstrated.
- E-R5's source re-read is one HTTPS fetch of `spec.commonmark.org` (sha256 above) plus the committed section copy; no archive was downloaded.
