VERDICT: partial — three draft rows (S051 Python exceptions, S052 pytest exit codes, S053 Automake 77/99) drafted from sources opened 2026-10-20; S053 is cited via the upstream 1.19 tarball because www.gnu.org timed out, and the pytest stable alias's version is not stated on its page.

# ScribeSourcesPython — round 18 draft report

Draft: `.ufo/waves/round-18/build/drafts/sources-python.md` (sha256 recorded by L1 on integration; no lane file other than this draft and this report was written).

## Behaviour / findings

1. **S051 Python 3.14 built-in exceptions** — opened https://docs.python.org/3.14/builtins/exceptions.html (rendered page "Built-in Exceptions — Python 3.14.8 documentation"; same bytes at /3.14/library/exceptions.html, sha256 766d785f…, 144074 bytes; accessed 2026-10-20).
   - Escapes `except Exception`: direct `BaseException` children `BaseExceptionGroup` (when it wraps non-Exception members), `GeneratorExit`, `KeyboardInterrupt`, `SystemExit`. Quote: "It inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception." (§SystemExit).
   - Caught by `except Exception`: `ExceptionGroup` (Exception subclass). Quote: "except Exception catches an ExceptionGroup but not BaseExceptionGroup." (§BaseExceptionGroup).
   - Unknown on this page: whether the interpreter ever raises bare `BaseException`; bare `except:` is not described.
2. **S052 pytest exit codes** — opened https://docs.pytest.org/en/stable/reference/exit-codes.html (markdown view and curl HTML copy, sha256 7a13d907…, 25597 bytes; accessed 2026-10-20).
   - Exit 1: "Tests were collected and run but some of the tests failed". Exit 5: "No tests were collected". Exit 3: "Internal error happened while executing tests". So "nothing collected" is distinct from failure, and the code is a public API via `pytest.ExitCode`.
   - Unknown: pytest version the `stable` alias denotes; the page does not state one. Host pytest is not installed (`import pytest` → ModuleNotFoundError), so nothing local confirms the codes.
3. **S053 GNU Automake 77/99** — the www.gnu.org URL timed out three times (curl, 60–100 s); the manual was opened as `automake-1.19/doc/automake.texi` from https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz (sha256 e3e2c2e3…, 1682600 bytes), lines 9774–9777 under `@node Scripts-based Testsuites` (line 9748). Quote: "an exit status of 77 a skipped test, an exit status of 99 a hard error". The installed Arch automake 1.19-1 info manual (`/usr/share/info/automake.info*.gz`, node Scripts-based Testsuites, concatenated line 8451–8479) carries the same sentence. Scope: default harness with no test protocol only.

## Gate for L1 (verification)

- The 11-column row shape matches S044's registry row (id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by); status `mined`, recheck `on-release` (existing recheck vocabulary).
- Gate rows use the lesson table shape (id | URL | accessed | quote | location), all quotes ≤25 words and copied from the opened files. Quote check was done with `grep` on the saved copies; the pytest Note sentence was seen only in the markdown view and is flagged in the draft.

## Installs / updates

- None. Host automake 1.19-1 pre-existed (`pacman -Q automake`); no pacman transaction was run (pacman pause honoured). Tools used: curl, tar, xz, zcat, python3 standard library (HTML-to-text extraction only).

## Limitations

- S053 cites the upstream manual by tarball; the live www.gnu.org HTML page was not opened this session.
- Python and pytest pages are dated only by their fetch date (Python footer: "Last updated on Oct 20, 2026 (20:36 UTC)"); pytest carries no date.
- Temp copies under /tmp were created by this seat for quote checks and removed in the final step.
