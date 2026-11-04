## diffs:round75-interpretation-pins.py
### A1-declared-flip
```diff
--- a
+++ b (mutant A1-declared-flip)
@@ -1 +1 @@
-    declared = sum(pin["observed"] == pin["declared"] for pin in pins)
+    declared = sum(pin["observed"] != pin["declared"] for pin in pins)
```
### A2-kill-rule-drop
```diff
--- a
+++ b (mutant A2-kill-rule-drop)
@@ -1 +1 @@
-    killed = sum(pin["mutant"] != pin["declared"] and pin["mutant_ok"] for pin in pins)
+    killed = sum(pin["mutant_ok"] for pin in pins)
```
### A3-finding-exit-to-0
```diff
--- a
+++ b (mutant A3-finding-exit-to-0)
@@ -1 +1 @@
-"exit": 0 if declared == killed == len(pins) else 1}+"exit": 0 if declared == killed == len(pins) else 0}```
### A4-clean-exit-to-1
```diff
--- a
+++ b (mutant A4-clean-exit-to-1)
@@ -1 +1 @@
-"exit": 0 if declared == killed == len(pins) else 1}+"exit": 1 if declared == killed == len(pins) else 0}```
### A5a-grade-one-pin
```diff
--- a
+++ b (mutant A5a-grade-one-pin)
@@ -1,2 +1,2 @@
          "mutant_name": "c1_f2c_literal_hex", "runs": results},
-    ])+    ][:1])```
### A5b-fake-P2-leg
```diff
--- a
+++ b (mutant A5b-fake-P2-leg)
@@ -1,3 +1 @@
-         "observed": pristine["exit"], "mutant": mutant["exit"],
-         "mutant_ok": mutant["exit"] == 1 and
-                       "RECEIPT_CLAIM_V2_FINDING stale-revision " in mutant["stdout"],
+         "observed": 0, "mutant": 1, "mutant_ok": True,
```
### A6-trust-P2-observed
```diff
--- a
+++ b (mutant A6-trust-P2-observed)
@@ -1 +1 @@
-         "observed": pristine["exit"], "mutant": mutant["exit"],
+         "observed": 0, "mutant": mutant["exit"],
```
### A7-oracle-declared-and-kill
```diff
--- a
+++ b (mutant A7-oracle-declared-and-kill)
@@ -1 +1 @@
-            ("declared-and-kill", clean["exit"] == 0), ("cheat-escaped", cheat_ok)]+            ("declared-and-kill", True), ("cheat-escaped", cheat_ok)]```
### A8-oracle-predicate
```diff
--- a
+++ b (mutant A8-oracle-predicate)
@@ -1 +1 @@
-("predicate", plan_predicate(repo) == PREDICATE),+("predicate", True),```
## diffs:round75-survivor-probe.py
### B1-killed-flip
```diff
--- a
+++ b (mutant B1-killed-flip)
@@ -1,3 +1,3 @@
-    killed = sum(row["mutant_exit"] == 1
+    killed = sum(row["mutant_exit"] != 1
                  and EXPECTED_ARMS.get(row["mutant"]) in row["failed_arms"]
                  for row in rows)
```
### B2-arm-check-drop
```diff
--- a
+++ b (mutant B2-arm-check-drop)
@@ -1,3 +1 @@
-    killed = sum(row["mutant_exit"] == 1
-                 and EXPECTED_ARMS.get(row["mutant"]) in row["failed_arms"]
-                 for row in rows)
+    killed = sum(row["mutant_exit"] == 1 for row in rows)
```
### B3-finding-exit-to-0
```diff
--- a
+++ b (mutant B3-finding-exit-to-0)
@@ -1 +1 @@
-            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 1,
+            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 0,
```
### B4-clean-exit-to-1
```diff
--- a
+++ b (mutant B4-clean-exit-to-1)
@@ -1 +1 @@
-            "exit": 0 if complete and pristine_exit == 0 and killed == 5 else 1,
+            "exit": 1 if complete and pristine_exit == 0 and killed == 5 else 0,
```
### B5-skip-pristine-verdict
```diff
--- a
+++ b (mutant B5-skip-pristine-verdict)
@@ -1 +1 @@
-        doc = grade(pristine.returncode, rows, MUTANTS)
+        doc = grade(0, rows, MUTANTS)
```
### B6-skip-mutant-leg
```diff
--- a
+++ b (mutant B6-skip-mutant-leg)
@@ -1 +1 @@
-            copy.write_text(original.replace(old, new, 1), encoding="utf-8")
+            copy.write_text(original, encoding="utf-8")
```
### B8-oracle-complete-kills
```diff
--- a
+++ b (mutant B8-oracle-complete-kills)
@@ -1 +1 @@
-        "complete-kills": grade(0, rows, MUTANTS)["exit"] == 0,
+        "complete-kills": True,
```
### B9-summary-line-hardcode
```diff
--- a
+++ b (mutant B9-summary-line-hardcode)
@@ -1 +1 @@
-    print("SURVIVORS2 mutants={mutants} killed={killed} escaped={escaped}".format(**doc))
+    print("SURVIVORS2 mutants=5 killed=5 escaped=0")
```
## diffs:round75-append-accepted.py
### C1-accepted-unconditional
```diff
--- a
+++ b (mutant C1-accepted-unconditional)
@@ -1,2 +1,2 @@
-        if not missing and key not in invalid:
+        if True:
             accepted += 1
```
### C2-unaccepted-zero
```diff
--- a
+++ b (mutant C2-unaccepted-zero)
@@ -1 +1 @@
-"unaccepted": len(pending) - accepted,+"unaccepted": 0,```
### C3-bad-rows-drop
```diff
--- a
+++ b (mutant C3-bad-rows-drop)
@@ -1,3 +1,3 @@
     def bad(kind, detail, key=None):
         nonlocal bad_rows
-        bad_rows += 1
+        bad_rows += 0
```
### C4-finding-exit-to-0
```diff
--- a
+++ b (mutant C4-finding-exit-to-0)
@@ -1 +1 @@
-    return int(bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))
+    return 0
```
### C5-clean-exit-to-1
```diff
--- a
+++ b (mutant C5-clean-exit-to-1)
@@ -1 +1 @@
-    return int(bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))
+    return int(not bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))
```
### C6-grade-one-event
```diff
--- a
+++ b (mutant C6-grade-one-event)
@@ -1 +1,2 @@
-    pending = {key: e for key, e in all_events.items() if e["undisclosed"] and e["status"] != "restored"}
+    _pending_all = {key: e for key, e in all_events.items() if e["undisclosed"] and e["status"] != "restored"}
+    pending = dict(list(_pending_all.items())[:1])
```
### C7-accept-any-row
```diff
--- a
+++ b (mutant C7-accept-any-row)
@@ -1,4 +1,7 @@
         entry = expected.get(row_key)
+        if entry is None and key in pending:
+            covered.add(row_key)
+            continue
         if entry is None or not re.fullmatch(r"[0-9a-f]{64}", digest):
             bad("hash-mismatch", detail, key)
             continue
```
### C8-bad-declarations-zero
```diff
--- a
+++ b (mutant C8-bad-declarations-zero)
@@ -1 +1 @@
-              "bad_rows": bad_rows, "bad_declarations": data["summary"]["bad_declarations"]}
+              "bad_rows": bad_rows, "bad_declarations": 0}
```
### C9-oracle-and-to-or
```diff
--- a
+++ b (mutant C9-oracle-and-to-or)
@@ -1 +1 @@
-        ok = actual == want and (finding is None or any(f["class"] == finding for f in result["findings"]))
+        ok = actual == want or (finding is None or any(f["class"] == finding for f in result["findings"]))
```