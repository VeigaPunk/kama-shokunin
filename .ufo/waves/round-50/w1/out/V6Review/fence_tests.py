#!/usr/bin/env python3
"""V6Review: unit tests of key()/fence_open()/fence_close()/sections() at the v5 tip."""
import importlib.util

spec = importlib.util.spec_from_file_location("aoa5", "/fast/scratch/hyaku/kama-r50/V6Review/audit-v5.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

fails = []
def check(name, got, want):
    ok = got == want
    print(f"{'pass' if ok else 'FAIL'} {name}: got {got!r}" + ("" if ok else f" want {want!r}"))
    if not ok:
        fails.append(name)

# --- key(): exactly one trailing CR removed (docstring F5)
check("key.lf", m.key(b"x"), b"x")
check("key.crlf", m.key(b"x\r"), b"x")
check("key.crcrlf-one-only", m.key(b"x\r\r"), b"x\r")
check("key.cr-only", m.key(b"\r"), b"")

# --- sections(): fence state machine (CommonMark 0.31.2 section 4.5)
S = m.sections
check("sec.basic-fake-heading-in-fence",
      S([b"## A", b"a", b"```", b"## B", b"b", b"```", b"c"]),
      ["## A"] * 7)
check("sec.unclosed-runs-to-eof",
      S([b"## A", b"~~~", b"## B", b"b"]),
      ["## A"] * 4)
check("sec.4-space-indent-is-not-a-fence",
      S([b"    ```", b"## B", b"b"]),
      [None, "## B", "## B"])
check("sec.tab-indented-close-does-not-close",
      S([b"```", b"\t```", b"## B", b"b"]),
      [None, None, None, None])
check("sec.longer-close-closes",
      S([b"```", b"x", b"````", b"## B", b"b"]),
      [None, None, None, "## B", "## B"])
check("sec.shorter-close-does-not-close",
      S([b"````", b"x", b"```", b"## B", b"b"]),
      [None] * 5)
check("sec.close-with-junk-does-not-close",
      S([b"````", b"x", b"```junk", b"## B", b"b"]),
      [None] * 5)
check("sec.close-with-info-does-not-close",
      S([b"```", b"```js", b"## B", b"b"]),
      [None] * 4)
check("sec.backtick-info-with-backtick-does-not-open",
      S([b"``` a ` b", b"## B", b"b"]),
      [None, "## B", "## B"])
check("sec.tilde-info-may-hold-backticks",
      S([b"~~~ ```", b"## B", b"b"]),
      [None, None, None])
check("sec.crlf-lines",
      S([b"## A\r", b"```\r", b"## B\r", b"b\r", b"```\r", b"c\r"]),
      ["## A"] * 6)
check("sec.3-space-open-2-space-close",
      S([b"   ```", b"  ```", b"## B", b"b"]),
      [None, None, "## B", "## B"])
check("sec.backtick-inside-tilde-fence-does-not-close",
      S([b"~~~", b"```", b"## B", b"```", b"~~~", b"## C", b"c"]),
      [None, None, None, None, None, "## C", "## C"])
check("sec.trailing-tab-after-close-run",
      S([b"```", b"```\t", b"## B", b"b"]),
      [None, None, "## B", "## B"])
check("sec.heading-cannot-open-fence",
      S([b"## A", b"```", b"## B", b"```", b"## C"]),
      ["## A", "## A", "## A", "## A", "## C"])
check("sec.4-space-open-tab-close-no",
      S([b"```", b"  \t```", b"## B", b"b"]),
      [None, None, None, None])
check("sec.four-tilde-open-three-tilde-close-no",
      S([b"~~~~", b"x", b"~~~", b"## B", b"b"]),
      [None] * 5)

# --- fence_open / fence_close details
check("open.4sp-none", m.fence_open(b"    ```"), None)
check("open.tab-none", m.fence_open(b"\t```"), None)
check("open.run-length", m.fence_open(b"`````"), (b"`", 5))
check("open.mixed-run-backticks-then-tilde", m.fence_open(b"````~"), (b"`", 4))
check("close.indent-4-false", m.fence_close(b"    ```", (b"`", 3)), False)
check("close.char-mismatch", m.fence_close(b"~~~", (b"`", 3)), False)

print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
raise SystemExit(1 if fails else 0)
