# SrcPythonDecode — candidate SOURCES rows for C1 decode faults (round 23)

Scribe seat `CloseKama22.SrcPythonDecode`. Draft only: `corpus/SOURCES.md` was NOT edited.
Access date for every source below: **2026-10-21**.

## Sources opened

| URL (opened) | Page title shown | Version observed |
|---|---|---|
| https://docs.python.org/3.14/library/subprocess.html | `subprocess — Subprocess management — Python 3.14.9 documentation` | 3.14 series URL; render says 3.14.9 (not a 3.14.8 pin) |
| https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode (rendered at `/3.14/builtins/stdtypes.html`) | `Built-in Types — Python 3.14.9 documentation` | 3.14 series URL; render says 3.14.9 |

Both are the same series-URL caveat as S087/S088: the 3.14 URL floats across micro releases; the quoted text is what the 3.14.9 render shows.

## Located quotes (verbatim, markdown stripped)

- **Q1** — subprocess, §Frequently Used Arguments, paragraph beginning "If *encoding* or *errors* are specified, or *text* is true": "are opened in text mode using the specified encoding and errors or the io.TextIOWrapper default" (15 words).
- **Q2** — subprocess, §Frequently Used Arguments, paragraph beginning "If text mode is not used": "If text mode is not used, stdin, stdout and stderr will be opened as binary streams. No encoding or line ending conversion is performed." (24 words).
- **Q3** — subprocess, §Frequently Used Arguments, "Changed in version 3.3" note (scope: `universal_newlines=True` only): "the class uses the encoding locale.getpreferredencoding(False) instead of locale.getpreferredencoding()" (9 words).
- **Q4** — stdtypes, §bytes.decode(encoding, errors), errors paragraph: "If 'strict' (the default), a UnicodeError exception is raised." (9 words).

## Draft rows (11 columns, matching the live header)

The live table header has 11 columns (`id … used-by`; census NF=13 with delimiters). The task brief said "12-column"; I followed the live header. See Discrepancies.

```
| S089 | Python subprocess text-mode decoding — https://docs.python.org/3.14/library/subprocess.html | docs | A | Python 3.14-series subprocess: when child output is decoded versus passed through as bytes; not the audit's error policy | §Frequently Used Arguments: text-mode paragraph and binary-mode paragraph, plus Changed in 3.3 note; page titled "subprocess — Subprocess management — Python 3.14.9 documentation", opened 2026-10-21; series URL, not a 3.14.8 pin | With text=True and no encoding=, output is decoded by the io.TextIOWrapper default the page names but does not spell out; without text mode no encoding or newline conversion happens, so decoding is the caller's choice. | queued | 2026-10-21 | on-release | — |
| S090 | Python bytes.decode errors default — https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode | docs | A | Python 3.14-series bytes.decode default error handler; strict raises rather than substituting characters; not any caller's verdict policy | §bytes.decode(encoding, errors), errors paragraph; page titled "Built-in Types — Python 3.14.9 documentation", opened 2026-10-21; series URL, not a 3.14.8 pin | With the default errors='strict', undecodable bytes raise UnicodeError instead of being replaced, so the caller must catch it to choose a verdict; what an uncaught exception becomes is the caller's behavior, not the docs'. | queued | 2026-10-21 | on-release | — |
```

Note on URL form: the brief gave `https://docs.python.org/3.14/library/stdtypes.html#bytes.decode`, but the page lives at `/3.14/builtins/stdtypes.html` (the fetch redirected/rendered there; the canonical is `/3/builtins/stdtypes.html`). The row above uses the `builtins/` path that was actually opened. L1 should choose one and keep it stable.

## Gate

- **S089** — URL: https://docs.python.org/3.14/library/subprocess.html — access 2026-10-21 — quote (Q1, 15 words): "are opened in text mode using the specified encoding and errors or the io.TextIOWrapper default" — located §Frequently Used Arguments, text-mode paragraph.
  Supports fault **(a)** (`logOutputEncoding=ISO-8859-1` + non-ASCII subject → UnicodeDecodeError traceback) and fault **(b)** (invalid UTF-8 in a committed report → traceback): base 4fe9339f `tools/report-landing-audit.py` line 89–91 calls `subprocess.run(..., capture_output=True, text=True, env=...)` with no `encoding=`, so decoding is the io.TextIOWrapper default and `except OSError` (line 92) does not catch a decode error. Supports the direction "bytes mode" via Q2 (24 words, same page): "No encoding or line ending conversion is performed."
- **S090** — URL: https://docs.python.org/3.14/builtins/stdtypes.html#bytes.decode — access 2026-10-21 — quote (Q4, 9 words): "If 'strict' (the default), a UnicodeError exception is raised." — located §bytes.decode, errors paragraph.
  Supports fault **(a)** and **(b)**: the audit's strict UTF-8 decode of git output (working tree `proc.stdout.decode("utf-8")` at line 110, its `UnicodeDecodeError` caught at lines 111–113) relies on this default raising rather than substituting. The docs do not say what the audit should do with the exception; that is own-work.

Fault coverage not supported by these two rows: **(c)** `git replace`, **(d)** fabricated `refs/replace/`, **(e)** promisor lazy fetch executing `core.sshCommand`. Those need git-docs rows (see Leads); none drafted here.

## Duplicates and overlaps

- **Source-level duplicate (S089):** the URL https://docs.python.org/3.14/library/subprocess.html is already registered twice: **S044** (anchor `Popen.returncode`/`Popen.wait`, page titled 3.14.8, status mined) and **S064** (anchor `CompletedProcess.returncode`, status mined). S089 cites a different anchor (text-mode decoding), so it is a new claim, not a copy. Rule 2 forbids editing S044/S064 to add an anchor. If L1 prefers one row per URL, S089 must be folded into a new row, not into S044/S064 in place. Flagged, not resolved.
- **No duplicate for S090:** `grep stdtypes|bytes\.decode|UnicodeError|TextIOWrapper|getpreferredencoding` over `corpus/SOURCES.md` returns only the S044/S064 subprocess rows and the S087/S088 open/os rows (no decode row).
- **Adjacent, not duplicate:** S075/S087 (open raises OSError) and S076/S088 (os errors) cover file-open errors, not decoding.
- **Next ID:** S088 is the last live row; S089 and S090 are the next unused IDs at read time. Sibling SrcGit* seats are drafting rows concurrently; if one takes S089 or S090 first, L1 renumbers at integration (IDs are never reused once written).

## Discrepancies and observations (for L1)

1. **Column count:** the brief says 12 columns; `corpus/SOURCES.md` header and CORPUS census (`NF!=13` check) say 11 data columns. Used 11.
2. **Base vs working tree differ:** base blob `4fe9339f:tools/report-landing-audit.py` `git()` uses `text=True` (line 89–91). The lane checkout's working-tree file at read time uses `capture_output=True` with bytes and an explicit `decode("utf-8")` at lines 101–113. The fault mapping above uses the **base** blob. L1 should confirm which tree the round judges.
3. **Probe consistency (not rerun):** the base-blob mechanism (text=True, no encoding, only `OSError` caught) is consistent with the user-reported traceback for faults (a) and (b). I did not rerun the probe.
4. **Catch-site note:** the working-tree `UnicodeDecodeError` catches are at lines 111–113 (git output) and 212 and 223 (source-table load), each wrapped as `EvalError` — a refusal, not a verdict. Whether the base tree's `text=True` path reaches the same catch for fault (b) is what that fault tests; not verified here.

## Did NOT verify

- The 3.14.8 render of either page (only the 3.14.9 render was opened today). Quotes are checked against today's render only.
- `io.TextIOWrapper` default encoding (`locale.getencoding()` / `locale.getpreferredencoding`) — the subprocess page names the default but does not define it; that needs the `io` or `locale` page, not opened here.
- `UnicodeDecodeError` as a subclass of `UnicodeError` — the stdtypes page says UnicodeError; the subclass relation is on the `exceptions` page, not opened.
- Behavior of the audit at base (no execution performed); all statements about the audit are read from source text.

## Leads (unopened; not rows)

- Python `io` / `locale` docs for the TextIOWrapper default encoding under text=True (would support S089's "default" claim directly).
- Python `exceptions` page for UnicodeDecodeError ⊂ UnicodeError.
- Git `git-config` for `i18n.logOutputEncoding` (fault a) and `git-replace` for `refs/replace/` and `--no-replace-objects` (faults c, d).
- Git `git-config` / `gitprotocol` pages for `remote.<name>.promisor` and `core.sshCommand` lazy-fetch behavior (fault e). Use `example.invalid` in any fixture; no network host.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/SrcPythonDecode.md` (this report).

No installs or tool upgrades performed. No subagents spawned. `corpus/SOURCES.md` untouched.
