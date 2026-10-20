VERDICT: confirm — every S044 cell and the lesson Gate quote re-open true at 54a2926; two non-falsifying notes (teaches paraphrase, receipt still cites `/3/`).

# ReopenS044 — round 17 FALSIFY, S044 cell-by-cell

Seat: `KamaR17.ReopenS044` (scout, leaf). Target: `corpus/SOURCES.md:56` and
`corpus/lessons/round-17.md:66`, at lane tip
`54a29268e2083caa2b1e0d54ee1e7d90961302f3` (`git rev-parse HEAD` returns that
commit; clone `git status --porcelain` empty). The row's bytes are identical in
the clone and the worktree: both `sed -n 56p corpus/SOURCES.md | sha256sum` give
`d043936388a1aaed2e026bf5c54ffe5f10b1bf4e18f3d332dffda2688a4d68f0`. S044 is
absent at round start `cff9e62` (`git show cff9e62:corpus/SOURCES.md | grep -c
S044` → `0`, exit 1) and appears only in 54a2926 (`git log -S S044` shows one
commit), so the append-only baseline is intact.

## What I attacked

The landed row, not the build draft:

> `| S044 | Python `subprocess` — `Popen.returncode` (Python 3.14) — https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode | docs | A | meaning of a child return code as observed by kama's Python 3.14 harness; not llama.cpp exit semantics | §`Popen.returncode` and §`Popen.wait`, page titled Python 3.14.8 documentation (host interpreter 3.14.8; `/3/` now serves 3.15) | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." `None` means not terminated at the last `poll()` or `wait()`, so liveness must be polled fresh before signalling. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-17.md |`

and the Gate row `corpus/lessons/round-17.md:66`:

> `| Negative returncode = death by signal N | admit (S044) | https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode "A negative value -N indicates that the child was terminated by signal N (POSIX only)." |`

The row was re-opened on 2026-10-20 with `curl -sS` to
`/tmp/ReopenS044-subprocess314.html` (exit 0, 207127 bytes, sha256
`c10390303d0ff3b346e563fa8c1403f3743e286747d6dfbfba7798467799d7ea`) and the
`/3/` page to `/tmp/ReopenS044-subprocess3.html` (exit 0, title 3.15.0).

## Cell-by-cell

| Cell | Verdict | Evidence |
|---|---|---|
| `id` | agree | `S044` is unique; the contract duplicate-id census prints nothing (`sort \| uniq -d \| wc -l` → `0`). |
| `source` | agree | https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode resolves (HTTP 200, curl exit 0); title is `subprocess — Subprocess management — Python 3.14.8 documentation` (`<title>` at raw HTML line 20). Title, URL and row label agree. |
| `kind` | agree | `docs` is in the contract enum (`SOURCES-CONTRACT-v1.md` kind list); this is Python's official documentation, not a spec, paper or source tree. |
| `tier` (for scope) | agree | Tier A covers "official docs" (`SOURCES-CONTRACT-v1.md` §Shape); the scope explicitly limits it to "meaning of a child return code as observed by kama's Python 3.14 harness; not llama.cpp exit semantics". A is scoped, not global. |
| `scope` | agree | The negative-code meaning is a Python `subprocess` fact; the row expressly does not claim llama.cpp exit semantics. The harness use is `Popen` returncode in `tools/kama-llamacpp-live.py`. |
| `anchor` | agree | `id="subprocess.Popen.returncode"` at raw HTML line 1169 and `id="subprocess.Popen.wait"` at line 1009; page title says 3.14.8 (line 20); `python3 -VV` is `Python 3.14.8`; `/3/` title is `Python 3.15.0 documentation` (line 20). All four anchor-cell claims are true. |
| `teaches` | agree, with caveat | The quoted sentence is verbatim at the anchor (raw HTML line 1176; also under `CompletedProcess.returncode` at line 364). The `None` sentence is a paraphrase, not a quote: the page says "A `None` value indicates that the process hadn't yet terminated at the time of the last method call." and "Initially `None`, `returncode` is set by a call to the `poll()`, `wait()`, or `communicate()` methods". The row narrows this to `poll()`/`wait()` and does not mention `communicate()` or the initial-`None` case. Within the row's harness scope that narrowing is correct: the tool uses `poll()` (lines 632, 754) and `wait()` (789, 798), never `communicate()`. The final clause "so liveness must be polled fresh before signalling" is an operational inference, implemented at lines 632/754, not a sentence on the page. See note 1. |
| `status` | agree | `mined` requires at least one citing `used-by` path; both listed paths cite S044. |
| `opened` | agree | `2026-10-20`; the Gate preamble says "All sources opened 2026-10-20." (`round-17.md:56`) and this re-open is the same date. |
| `recheck` | agree | `on-release` is an allowed cadence (`SOURCES-CONTRACT-v1.md` §Shape). Note the 3.14 page footer now reads "Last updated on Oct 20, 2026 (18:24 UTC)" — it can be regenerated intra-release; the quoted sentences are stable here (and per `ScoutPythonReturncode.md` across 3.12–3.15). |
| `used-by` | agree | Both paths exist and cite S044: `corpus/knowledge/llamacpp-loading-lifecycle.md:155` ("S044 (Python 3.14 `Popen.returncode`)") and `:180` ("terminated by signal N (POSIX only)." (S044)); `corpus/lessons/round-17.md:39` and `:66`. A grep of `corpus/knowledge/` and `corpus/lessons/` finds no other citing files. `corpus/README.md:238` also mentions S044, but it is neither a knowledge entry nor a lesson, so the contract does not require it in `used-by`. |
| row shape | agree | `awk -F'\|' ... 'S044'` → `NF=13`, no pipes inside any cell; census: 46 rows, `malformed=0`, duplicates `0`, enum/tier-inflation command prints nothing (exit 0), `used-by` existence check prints no missing path; histogram A=43 C=3, mined=36 queued=5 rejected=5, matching `SCORECARD.md` "rows 41 → 46". |

## Lesson `## Gate` quote

Agree. `corpus/lessons/round-17.md:66` quotes
"A negative value -N indicates that the child was terminated by signal N (POSIX only)."
— 15 whitespace-delimited words (≤25), verbatim on the page except for HTML
`<code>` markup and a line wrap (rendered text matches exactly), located at
`#subprocess.Popen.returncode` (raw HTML 1169–1176). The same sentence is also
under `CompletedProcess.returncode` (line 364), but the Gate's fragment resolves
to the `Popen` entry. The access date is in the section preamble
(`round-17.md:56`: "All sources opened 2026-10-20."). The quote grounds the
admitted claim "Negative returncode = death by signal N"; it does not quote the
`None` sentence (note 1).

## Version re-check (the one substantive trap)

- Host: `command -v python3` → `/usr/bin/python3` → `/usr/bin/python3.14`;
  `python3 -VV` → `Python 3.14.8 (main, Oct 2 2026, ...)`.
- `/3.14/library/subprocess.html`: title `Python 3.14.8 documentation`,
  fetched 2026-10-20T18:47:12Z, 207127 bytes, sha256 `c1039030…79d7ea`.
- `/3/library/subprocess.html`: title `Python 3.15.0 documentation`; the row's
  "`/3/` now serves 3.15" and the Gate's reject row are correct.
- The negative sentence is present on both pages; the 3.15 page at its
  `#subprocess.Popen.returncode` anchor says the same "A negative value -N
  indicates that the child was terminated by signal N (POSIX only)."

## Notes (not disagreements with the row cells)

1. **`teaches` is part quote, part paraphrase/inference.** The page's exact
   `None` wording is "hadn't yet terminated at the time of the last method
   call", and the preceding sentence lists `poll()`, `wait()` **and**
   `communicate()`. The row's "last `poll()` or `wait()`" is correct for this
   harness's calls but is not the page's wording, and "so liveness must be
   polled fresh before signalling" is a derived rule. The admitted Gate claim
   (negative = signal) is unaffected. If L1 wants strict source wording, use
   the page's "last method call" phrase or add the 18-word `None` sentence to
   the Gate quote. [INFERENCE] that the row's narrowing was intentional for the
   harness scope.
2. **Cross-artifact drift: the receipt pins `/3/`, not the row's `/3.14/`.**
   `tools/kama-llamacpp-live.py:60-61` sets `POPEN_RETURNCODE_DOC` to
   `https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode`,
   and `.ufo/waves/round-17/live/receipt-1.json` `checks[7].documented_by`
   reproduces that `/3/` URL. The row's anchor cell itself says `/3/` now serves
   3.15; the receipt therefore cites the moving branch, not the row's 3.14
   anchor. The sentence is identical on 3.15.0 (verified), so no predicate is
   unsupported, but the "sourced S044" binding is not version-pinned. The gate
   cannot catch this: `tests/llamacpp-live/check-receipt.py:644-646` only
   requires `documented_by` to be a non-empty string. Recommend updating the
   constant to `/3.14/` (and re-running the gate) or recording why `/3/` is
   intentional.
3. **S044 has no saved page/digest.** `.ufo/waves/round-17/sources/pins.json`
   contains only llama.cpp files (`server.cpp`, `server-context.cpp`,
   `server-http.cpp`, `README.md`, `server-queue.cpp`, `server-queue.h`); no
   Python docs entry exists. The knowledge supplement's blanket "sources
   re-fetched at the pinned commit and saved with digests" is true for
   S042/S043/S046 but not S044. The live quote is present now, but exact-byte
   identity with the page the author opened at 16:24:57Z cannot be proven: the
   page footer says it was last updated at 18:24 UTC. [INFERENCE] the page was
   regenerated after the commit; the S044 sentences are unchanged.

## Commands run (exit codes)

- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ReopenS044-clone && git -C /tmp/ReopenS044-clone checkout -q 54a2926…` — exit 0; `git rev-parse HEAD` printed the commit; `git status --porcelain` 0 lines.
- `awk -F'|' '/^\|…S044…/' corpus/SOURCES.md` — `NF=13`; no cell contains `|`.
- contract census: `grep -cE` → `46`; `NF!=13` malformed → `0`; `uniq -d | wc -l` → `0`; enum/tier-inflation awk → no output, exit 0; mined used-by existence loop → no missing path; histogram A=43 C=3, mined=36 queued=5 rejected=5.
- `sed -n 56p corpus/SOURCES.md | sha256sum` (clone and worktree) → `d0439363…68f0` both.
- `git log -S 'S044' -- corpus/SOURCES.md` → only `54a2926`; `git show cff9e62:corpus/SOURCES.md | grep -c S044` → `0` (exit 1, expected pre-round absence).
- `curl -sS --max-time 30 https://docs.python.org/3.14/library/subprocess.html -o /tmp/ReopenS044-subprocess314.html` — exit 0, 207127 bytes.
- `grep -n 'id="subprocess.Popen.returncode"'` → line 1169; `grep -n 'A negative value'` → lines 364 and 1176; `grep -n '<title>'` → 3.14.8.
- `curl -sS --max-time 30 https://docs.python.org/3/library/subprocess.html -o /tmp/ReopenS044-subprocess3.html` — exit 0; title line 20 → 3.15.0.
- `python3 -VV` — exit 0 → 3.14.8.
- Python matcher over the `Popen.returncode` `<dd>` — 15 words, `quote_in_section=True`.
- `grep -n S044` in `corpus/knowledge/` + `corpus/lessons/` — 4 hits in 2 files; `grep -rl S044` — only `llamacpp-loading-lifecycle.md` and `round-17.md`.
- `grep -n POPEN_RETURNCODE_DOC tools/kama-llamacpp-live.py` → lines 60-61 (`/3/`); receipt-1 `checks[7].documented_by` → `/3/`; `grep -n documented_by tests/llamacpp-live/check-receipt.py` → 644-646 non-empty check only.
- `date -u` → 2026-10-20T18:47:12Z; page footer → 18:24 UTC.
- `grep -in 'python\|subprocess\|docs.python' .ufo/waves/round-17/sources/pins.json` → no matches.

## Limitations

- No language server was applicable or available for a remote HTML documentation
  page or a Markdown registry table; I used HTTP fetch plus raw-text extraction,
  not `lsp` semantic queries. No `lsp` status was recorded because there is no
  server for these file types.
- S044 has no pinned page digest or saved copy (note 3), so I can prove the
  current page contains the quoted sentences, not that its bytes equal those the
  author opened. The row's anchor names the version (3.14.8), which the contract
  allows, but not the page's last-updated timestamp.
- I did not re-run the live harness, receipt gate or controls; this seat re-opens
  the source row and the Gate quote only. The C2 predicate replay is another
  seat's assignment.
- The `/3/` receipt drift (note 2) is outside the row's cells; I did not edit it.

## Installs

None. No package was installed or upgraded.

## Scratch

`/tmp/ReopenS044-clone`, `/tmp/ReopenS044-subprocess314.html` and
`/tmp/ReopenS044-subprocess3.html` are removed after this report; no lane file
other than this advice report was written.
