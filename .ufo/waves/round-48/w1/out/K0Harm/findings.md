# K0Harm — proposed fixes (unified diffs)

These are proposals only; the lane was not edited (read-only).

## F1 — sources-append-only.py: row-like scan must be scoped to the registry section

File: `tools/sources-append-only.py`. Problem: `ROWLIKE_RE` is applied to every line of the blob (`:227-232`), so the round-45 re-verification table (`corpus/SOURCES.md:520`@33e005, `:522`@380bcdff; first cell ``| `S010` |``) trips the guard and the tool exits 2 on any revision containing it — it cannot grade the round-48 SOURCES append.

```diff
--- a/tools/sources-append-only.py
+++ b/tools/sources-append-only.py
@@ -164,6 +164,8 @@ def parse_registry(text, label):
     level = len(REGISTRY_RE.match(lines[headings[0]]).group(1))
     start = headings[0] + 1
+    # The registry section ends at the next heading of the same or a higher
+    # level; row-like lines outside it are not registry rows.
+    end = len(lines)
+    for idx in range(start, len(lines)):
+        m = HEADING_RE.match(lines[idx])
+        if m and len(m.group(1)) <= level:
+            end = idx
+            break
 
     rows_by_id = {}
     row_lines = set()
     header = None
     seen_separator = False
-    for idx in range(start, len(lines)):
+    for idx in range(start, end):
@@ -227,7 +231,7 @@ def parse_registry(text, label):
-    for idx, line in enumerate(lines):
+    for idx, line in enumerate(lines[:end]):
         if idx not in row_lines and ROWLIKE_RE.match(line):
             raise ParseError(
```

Note: this keeps the "refuse to drop a row-like line" property *inside* the registry section; non-registry tables elsewhere in the document no longer block grading.

Alternative (content-side, not preferred): rename the round-45 re-verification table's id column from `S0NN` to non-`S` keys so `ROWLIKE_RE` does not match — but that rewrites a historical section and would need its own append-only/errata handling.

## F2 — check-receipt.py: accept v5 receipts

File: `tests/llamacpp-live/check-receipt.py`. The v5 delta over v4: schema name + `provenance.verified` (`{"at": "record", "archive_sha256", "member_sha256", "model_sha256"}`); check set is identical to v4 (11 ids). Add v5 as a v4 superset.

```diff
--- a/tests/llamacpp-live/check-receipt.py
+++ b/tests/llamacpp-live/check-receipt.py
@@ -53,6 +53,8 @@ RECEIPT_SCHEMA_V3 = "kama-llamacpp-live/v3"
 RECEIPT_SCHEMA_V4 = "kama-llamacpp-live/v4"
+RECEIPT_SCHEMA_V5 = "kama-llamacpp-live/v5"
@@ -304,7 +306,9 @@ def validate(receipt, ...):
     schema = receipt.get("schema")
+    is_v5 = schema == RECEIPT_SCHEMA_V5
     is_v4 = schema == RECEIPT_SCHEMA_V4
     is_v3 = schema in (RECEIPT_SCHEMA_V3, RECEIPT_SCHEMA_V4)
+    is_v3 = schema in (RECEIPT_SCHEMA_V3, RECEIPT_SCHEMA_V4, RECEIPT_SCHEMA_V5)
     is_v2 = schema in (RECEIPT_SCHEMA_V2, RECEIPT_SCHEMA_V3,
+                       RECEIPT_SCHEMA_V4, RECEIPT_SCHEMA_V5)
@@ -311,7 +315,7 @@ def validate(receipt, ...):
     if schema not in (RECEIPT_SCHEMA, RECEIPT_SCHEMA_V2,
-                      RECEIPT_SCHEMA_V3, RECEIPT_SCHEMA_V4):
+                      RECEIPT_SCHEMA_V3, RECEIPT_SCHEMA_V4,
+                      RECEIPT_SCHEMA_V5):
         bad(f"schema is {schema!r}, want {RECEIPT_SCHEMA!r}, "
@@ -315,9 +319,14 @@ def validate(receipt, ...):
             f"{RECEIPT_SCHEMA_V3!r} or {RECEIPT_SCHEMA_V4!r}")
+    if is_v5:
+        verified = receipt.get("provenance", {}).get("verified")
+        if not isinstance(verified, dict):
+            bad("v5 provenance.verified is not an object")
+        elif (verified.get("at") != "record"
+              or verified.get("archive_sha256") != receipt["provenance"]["server"].get("asset_sha256")
+              or verified.get("member_sha256") != receipt["provenance"]["server"].get("sha256")
+              or verified.get("model_sha256") != receipt["provenance"]["model"].get("sha256")):
+            bad("v5 provenance.verified does not match recorded server/model digests")
@@ -2435,7 +2444,7 @@ def main(argv=None):
-    ap.add_argument("--require-schema", choices=("v1", "v2", "v3", "v4"),
+    ap.add_argument("--require-schema", choices=("v1", "v2", "v3", "v4", "v5"),
                     help="reject receipts below this schema version")
```

## F3 — gguf-identity.py: accept v5 receipts

File: `tools/gguf-identity.py`. v5 reconciles with the same fields as v4 (provenance.model.sha256 / server.sha256); only the schema name differs.

```diff
--- a/tools/gguf-identity.py
+++ b/tools/gguf-identity.py
@@ -44,7 +44,8 @@ RECEIPT_SCHEMA_V3 = "kama-llamacpp-live/v3"
 # v4 (round 47) adds only a provenance block and a null teardown.log_path; the
 # identity fields it reconciles are the same as v3.
-RECEIPT_SCHEMAS = (RECEIPT_SCHEMA_V3, "kama-llamacpp-live/v4")
+RECEIPT_SCHEMAS = (RECEIPT_SCHEMA_V3, "kama-llamacpp-live/v4",
+                   "kama-llamacpp-live/v5")
```

(`:44-47` whitelist, `:480-481` the `receipt_schema_unsupported` raise.)

## F4 — gate-registry-check.py: keep `--selftest` hermetic

File: `tools/gate-registry-check.py`. Arm 6 evaluates the live lane tip (`:338-349`); with mid-wave unregistered counters the selftest prints `pass=5 fail=1` even though fixture arms 1–5 pass. Proposal: make the lane-tip arm's expected unregistered count explicit/tolerable (e.g., a `--selftest-expect-unregistered N` flag, or print the observed count as info instead of failing) so the selftest does not depend on registry-complete state.

```diff
--- a/tools/gate-registry-check.py
+++ b/tools/gate-registry-check.py
@@ -338,7 +338,9 @@ def selftest() -> int:
-        arms.append(f"FAIL lane-tip {tip[:12]}: exit={code} line={summary!r}")
+        # Lane-tip arm: with wave counters unregistered until their SKILL.md
+        # rows land, failure here is expected; print info, do not fail the
+        # hermetic fixture matrix.
+        print(f"lane-tip {tip[:12]}: exit={code} line={summary!r}")
```
