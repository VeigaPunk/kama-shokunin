# SimplifyHistoryCheck — CloseKama22.SimplifyHistoryCheck-2

**Verdict:** **holds** — batched `rev-parse` in `check_history_repo` is equivalent at 245a37f; grid and mutant profile match pristine. `resolve_branch` unchanged (already 1–2 calls; branch-before-tag needs the fallback).

**Clone:** `/tmp/kama-r23w2/CloseKama22.SimplifyHistoryCheck-2` @ `245a37f69628c2c6bb29bbf17897d8fb5946c857` (verified `git rev-parse HEAD`).

## Godspeed axes

| Axis | Move |
|------|------|
| Git subprocess count | 5 → 2 per `check_history_repo` (3× `rev-parse` + 2× `--git-path` → 2× `rev-parse`; config unchanged) |
| Refusal parity | Same `EvalError` strings and branches |
| Grid graded rows | 26/26 faults, 8/8 controls |
| Mutant kills | 22/24 killed; survivors M02, M20 (defensive-only, unchanged) |

## Proposed diff (`tools/report-landing-audit.py`)

```diff
diff --git a/tools/report-landing-audit.py b/tools/report-landing-audit.py
--- a/tools/report-landing-audit.py
+++ b/tools/report-landing-audit.py
@@ -428,20 +428,24 @@ def check_history_repo(repo):
     (shallow boundary, info/grafts), whose missing objects belong to a
     promisor remote (absence is not evidence there), or whose object names
     the 40-hex scanners cannot read (non-sha1 object format)."""
-    fmt = git(repo, "rev-parse", "--show-object-format").strip()
+    fmt, prefix, shallow = git(
+        repo, "rev-parse", "--show-object-format", "--show-prefix",
+        "--is-shallow-repository").splitlines()
     if fmt != "sha1":
         raise EvalError(f"{repo}: object format {fmt!r}, not sha1")
-    if git(repo, "rev-parse", "--show-prefix").strip():
+    if prefix:
         raise EvalError(f"{repo}: not a repository top level")
-    if git(repo, "rev-parse", "--is-shallow-repository").strip() != "false":
+    if shallow != "false":
         raise EvalError(f"{repo}: shallow repository")
-    for rel in ("info/grafts", "objects/pack"):
-        path = Path(repo, git(repo, "rev-parse", "--git-path", rel).strip())
-        if rel == "info/grafts" and os.path.lexists(path):
-            raise EvalError(f"{repo}: {path} rewrites history")
-        if rel == "objects/pack" and path.is_dir() and any(
-                p.suffix == ".promisor" for p in path.iterdir()):
-            raise EvalError(f"{repo}: partial clone (promisor pack)")
+    grafts, pack = git(repo, "rev-parse", "--git-path", "info/grafts",
+                       "--git-path", "objects/pack").splitlines()
+    path = Path(repo, grafts.strip())
+    if os.path.lexists(path):
+        raise EvalError(f"{repo}: {path} rewrites history")
+    pack_path = Path(repo, pack.strip())
+    if pack_path.is_dir() and any(p.suffix == ".promisor"
+                                  for p in pack_path.iterdir()):
+        raise EvalError(f"{repo}: partial clone (promisor pack)")
     for line in git(repo, "config", "--list", "--name-only").split("\n"):
```

`resolve_branch` (451–459 @ 245a37f): no smaller equivalent found without losing `refs/heads/` first (M18 / F12).

**Implementation note:** use `.splitlines()` on batched `rev-parse` stdout, not `.split("\n")`, so the trailing newline from `git()` does not add a fourth field.

## Evidence (diff applied in clone)

**Pristine @ 245a37f (baseline, for contrast):**

```
python tests/report-audit/repo-state-grid.py --arm current
→ exit 0; faults=26/26 controls=8/8 tracebacks=0 executed=0 timeouts=0 violations=0

python tests/report-audit/isolation-mutants.py
→ exit 0; mutants=24 killed=22 surviving=['M02-lazy-fetch', 'M20-log-sha-shape']
```

**With diff (`--current` absolute path to clone auditor):**

```
AUDIT=/tmp/kama-r23w2/CloseKama22.SimplifyHistoryCheck-2/tools/report-landing-audit.py
python tests/report-audit/repo-state-grid.py --arm current --current "$AUDIT"
→ exit 0; faults=26/26 controls=8/8 tracebacks=0 executed=0 timeouts=0 violations=0

python tests/report-audit/isolation-mutants.py   # clone tree = modified AUDIT
→ exit 0; mutants=24 killed=22 surviving=['M02-lazy-fetch', 'M20-log-sha-shape']
```

History-related mutants still killed: M12 (F10), M13 (F11), M14 (F06), M15 (F15), M16 (F21), M18 (F12), M22 (F23). M24/M25 kill with `grid=2` (could-not-evaluate) vs pristine `grid=1`; still `killed=True`.

## Tradeoffs

- Relies on Git emitting one line per batched `rev-parse` flag in argument order (observed git 2.x on this host: `sha1`, empty prefix, `false`; then two `--git-path` lines).
- Slightly less obvious than three named one-flag calls; docstring unchanged.

## Not verified

- Frozen arm regression (out of scope for this advice slice).
- Integration on git &lt; 2.45 floor beyond existing lane contract.
- Whether `config --list --name-only` could be folded further without new mutants/grid rows.

## Tooling installs

None.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/SimplifyHistoryCheck.md` (this report)
- Modified scratch only: `/tmp/kama-r23w2/CloseKama22.SimplifyHistoryCheck-2/tools/report-landing-audit.py` (not committed; lane checkout untouched)
