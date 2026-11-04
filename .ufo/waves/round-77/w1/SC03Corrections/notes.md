# SC03Corrections — round 77 w1

Axes: calibration and freshness; append-only preservation is the guard.

## Behavior and gates

- D1 closed: added the missing selfrecord coverage row and appended the historical Frontier correction. At c2aa7fb2: 49 files, 41 mapped, 8 unmapped; the new row leaves 7 of that population unmapped. Annotated entry cells are included.
- D3 closed: appended one correcting block in LOG §Round 76 and one in round-76.md; the committed findings partition 31 pre-cutoff + 6 post-cutoff = 37. Five post-cutoff findings are SCORECARD events; the sixth is c2aa7fb2 SOURCES.
- D4 closed: round-76 lesson Gate now retains the exact S498 sentence, S548 access date 2026-11-04 and located command receipt, plus S498 used-by old→new. Explicit historical-revision own-work replay returns SELFRECORD_FACTS claims=8 mismatches=0 corrected=5 unbacked=0, exit 0.
- D6 applied, not discarded: appended the draft withdrawal in LOG §Round 76 only, repaired pointer to .ufo/waves/round-76/measured/after/gate-selftest.out. Existing §Round 75 correction remains untouched. Historical pass=18 is unbacked; retained round-76 pass=21 is not a new selftest execution.

## Touched surfaces

/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md
/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-76.md
/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/*.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/notes.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections.md

All historical destination bytes remain; additions only (including insertion of an additional Gate subsection). No product code or SCORECARD edits.

## Provenance

Read the complete frozen plan before edits. Base: cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7. Read-only lane command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` → 7d60e2ab58866a0366937d61c9712483be57b36e, exit 0. Freeze discovery: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --diff-filter=A --format='%H %s' -- plans/round-77-claims.md` → same commit, adds the plan, exit 0. Plan unchanged.

## Commands, outcomes, and absolute receipt paths

Each receipt carries its exact runnable command, stdout/stderr, and exit. Before/baseline and after commands are identical except the explicitly repaired receipt-blob revision and coverage-parser correction below.

### Initial before

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/before-coverage.out
Command: `python3 -c 'import subprocess,re; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; tree=subprocess.check_output(["git","-C",L,"ls-tree","-r","--name-only","c2aa7fb2","corpus/knowledge/"],text=True).splitlines(); text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/README.md"],text=True); mapped=set(re.findall(r"^\| `((?:knowledge/)[^`]+)` \|",text,re.M)); missing=sorted(set(p.removeprefix("corpus/") for p in tree)-mapped); print("COVERAGE_AT_C2AA7FB2 files=%d mapped=%d unmapped=%d"%(len(tree),len(mapped),len(missing))); print("\n".join(missing)); current=open(L+"/corpus/README.md").read(); now=set(re.findall(r"^\| `((?:knowledge/)[^`]+)` \|",current,re.M)); print("COVERAGE_INDEX_AFTER unmapped=%d selfrecord_rows=%d"%(len(set(p.removeprefix("corpus/") for p in tree)-now),current.count("| `knowledge/selfrecord-fact-binding.md` |")))'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/before-postcutoff.out
Command: `python3 -c 'import subprocess,re,collections; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:.ufo/waves/round-76/measured/after/append-exempt.out"],text=True); rows=re.findall(r"^APPEND_EXEMPT_FINDING unaccounted ([0-9a-f]{40}) (\S+)",text,re.M); cutoff="10f37171fb696c542586cbee96ea4a509ab74afc"; post=[(h,p) for h,p in rows if subprocess.run(["git","-C",L,"merge-base","--is-ancestor",h,cutoff]).returncode==1]; print("POSTCUTOFF pre=%d post=%d total=%d sum=%d"%(len(rows)-len(post),len(post),len(rows),len(rows)-len(post)+len(post))); print("\n".join(h+" "+p for h,p in post))'`
Exit: 1

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/before-quote.out
Command: `python3 -c 'import re,subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=open(L+"/.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html").read(); q="The content of a code fence is treated as literal text, not parsed as inlines."; print("S498_QUOTE "+q); assert q in re.sub(r"\s+"," ",text); old=subprocess.check_output(["git","-C",L,"show","b06cc612:corpus/SOURCES.md"],text=True); new=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/SOURCES.md"],text=True); print("S498_USED_BY_OLD "+next(s for s in old.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip()); print("S498_USED_BY_NEW "+next(s for s in new.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip())'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/before-logtally.out
Command: `python3 -c 'import subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:.ufo/waves/round-76/measured/after/gate-selftest.out"],text=True); print(text,end=""); assert "PRE_REPORT_SELFTEST pass=21 fail=0" in text and "exit=0" in text; r=subprocess.run(["git","-C",L,"grep","-l","PRE_REPORT_SELFTEST pass=18","c9ab73d8","--",".ufo/waves/round-75"],capture_output=True,text=True); print("ROUND75_PASS18_RECEIPTS=%d search_exit=%d"%(len(r.stdout.splitlines()),r.returncode)); assert r.returncode==1'`
Exit: 1

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/before-ownwork.out
Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round76-selfrecord-facts.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 461d2adbf2b3fe596a53cb392e2bc6e82af79bfb`
Exit: 0

### Corrected baseline

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/baseline-coverage.out
Command: `python3 -c 'import subprocess,re; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; tree=subprocess.check_output(["git","-C",L,"ls-tree","-r","--name-only","c2aa7fb2","corpus/knowledge/"],text=True).splitlines(); text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/README.md"],text=True); mapped=set(re.findall(r"^\| `((?:knowledge/)[^`]+)`[^|]*\|",text,re.M)); missing=sorted(set(p.removeprefix("corpus/") for p in tree)-mapped); print("COVERAGE_AT_C2AA7FB2 files=%d mapped=%d unmapped=%d"%(len(tree),len(mapped),len(missing))); print("\n".join(missing)); current=open(L+"/corpus/README.md").read(); now=set(re.findall(r"^\| `((?:knowledge/)[^`]+)`[^|]*\|",current,re.M)); print("COVERAGE_INDEX_AFTER unmapped=%d selfrecord_rows=%d"%(len(set(p.removeprefix("corpus/") for p in tree)-now),current.count("| `knowledge/selfrecord-fact-binding.md` |")))'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/baseline-postcutoff.out
Command: `python3 -c 'import subprocess,re,collections; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7:.ufo/waves/round-76/measured/after/append-exempt.out"],text=True); rows=re.findall(r"^APPEND_EXEMPT_FINDING unaccounted ([0-9a-f]{40}) (\S+)",text,re.M); cutoff="10f37171fb696c542586cbee96ea4a509ab74afc"; post=[(h,p) for h,p in rows if subprocess.run(["git","-C",L,"merge-base","--is-ancestor",h,cutoff]).returncode==1]; print("POSTCUTOFF pre=%d post=%d total=%d sum=%d"%(len(rows)-len(post),len(post),len(rows),len(rows)-len(post)+len(post))); print("\n".join(h+" "+p for h,p in post))'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/baseline-quote.out
Command: `python3 -c 'import re,subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=open(L+"/.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html").read(); q="The content of a code fence is treated as literal text, not parsed as inlines."; print("S498_QUOTE "+q); assert q in re.sub(r"\s+"," ",text); old=subprocess.check_output(["git","-C",L,"show","b06cc612:corpus/SOURCES.md"],text=True); new=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/SOURCES.md"],text=True); print("S498_USED_BY_OLD "+next(s for s in old.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip()); print("S498_USED_BY_NEW "+next(s for s in new.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip())'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/baseline-logtally.out
Command: `python3 -c 'import subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7:.ufo/waves/round-76/measured/after/gate-selftest.out"],text=True); print(text,end=""); assert "PRE_REPORT_SELFTEST pass=21 fail=0" in text and "exit=0" in text; r=subprocess.run(["git","-C",L,"grep","-l","PRE_REPORT_SELFTEST pass=18","c9ab73d8","--",".ufo/waves/round-75"],capture_output=True,text=True); print("ROUND75_PASS18_RECEIPTS=%d search_exit=%d"%(len(r.stdout.splitlines()),r.returncode)); assert r.returncode==1'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/baseline-ownwork.out
Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round76-selfrecord-facts.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 461d2adbf2b3fe596a53cb392e2bc6e82af79bfb`
Exit: 0

### After edits

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-coverage.out
Command: `python3 -c 'import subprocess,re; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; tree=subprocess.check_output(["git","-C",L,"ls-tree","-r","--name-only","c2aa7fb2","corpus/knowledge/"],text=True).splitlines(); text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/README.md"],text=True); mapped=set(re.findall(r"^\| `((?:knowledge/)[^`]+)`[^|]*\|",text,re.M)); missing=sorted(set(p.removeprefix("corpus/") for p in tree)-mapped); print("COVERAGE_AT_C2AA7FB2 files=%d mapped=%d unmapped=%d"%(len(tree),len(mapped),len(missing))); print("\n".join(missing)); current=open(L+"/corpus/README.md").read(); now=set(re.findall(r"^\| `((?:knowledge/)[^`]+)`[^|]*\|",current,re.M)); print("COVERAGE_INDEX_AFTER unmapped=%d selfrecord_rows=%d"%(len(set(p.removeprefix("corpus/") for p in tree)-now),current.count("| `knowledge/selfrecord-fact-binding.md` |")))'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-postcutoff.out
Command: `python3 -c 'import subprocess,re,collections; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7:.ufo/waves/round-76/measured/after/append-exempt.out"],text=True); rows=re.findall(r"^APPEND_EXEMPT_FINDING unaccounted ([0-9a-f]{40}) (\S+)",text,re.M); cutoff="10f37171fb696c542586cbee96ea4a509ab74afc"; post=[(h,p) for h,p in rows if subprocess.run(["git","-C",L,"merge-base","--is-ancestor",h,cutoff]).returncode==1]; print("POSTCUTOFF pre=%d post=%d total=%d sum=%d"%(len(rows)-len(post),len(post),len(rows),len(rows)-len(post)+len(post))); print("\n".join(h+" "+p for h,p in post))'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-quote.out
Command: `python3 -c 'import re,subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=open(L+"/.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html").read(); q="The content of a code fence is treated as literal text, not parsed as inlines."; print("S498_QUOTE "+q); assert q in re.sub(r"\s+"," ",text); old=subprocess.check_output(["git","-C",L,"show","b06cc612:corpus/SOURCES.md"],text=True); new=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/SOURCES.md"],text=True); print("S498_USED_BY_OLD "+next(s for s in old.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip()); print("S498_USED_BY_NEW "+next(s for s in new.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip())'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-logtally.out
Command: `python3 -c 'import subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7:.ufo/waves/round-76/measured/after/gate-selftest.out"],text=True); print(text,end=""); assert "PRE_REPORT_SELFTEST pass=21 fail=0" in text and "exit=0" in text; r=subprocess.run(["git","-C",L,"grep","-l","PRE_REPORT_SELFTEST pass=18","c9ab73d8","--",".ufo/waves/round-75"],capture_output=True,text=True); print("ROUND75_PASS18_RECEIPTS=%d search_exit=%d"%(len(r.stdout.splitlines()),r.returncode)); assert r.returncode==1'`
Exit: 0

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-ownwork.out
Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round76-selfrecord-facts.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 461d2adbf2b3fe596a53cb392e2bc6e82af79bfb`
Exit: 0

### Additional focused checks

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-table-rows.out
Command: `python3 -c 'import re; p="/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md"; print("SELFRECORD_TABLE_ROWS=%d"%len(re.findall(r"^\| `knowledge/selfrecord-fact-binding\.md` \|",open(p).read(),re.M)))'`
Exit: 0; SELFRECORD_TABLE_ROWS=1.

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-wordcount.out
Command: `python3 -c 'print(len("The content of a code fence is treated as literal text, not parsed as inlines.".split()))'`
Exit: 0; 15.

## Failures, corrections, and known limits

Initial postcutoff and logtally measurements incorrectly requested receipt blobs at their measured-header revision c2aa7fb2; those receipts were introduced later. Exact failed stderr follows (also retained in initial before receipts):

```text
fatal: path '.ufo/waves/round-76/measured/after/append-exempt.out' exists on disk, but not in 'c2aa7fb2'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import subprocess,re,collections; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:.ufo/waves/round-76/measured/after/append-exempt.out"],text=True); rows=re.findall(r"^APPEND_EXEMPT_FINDING unaccounted ([0-9a-f]{40}) (\S+)",text,re.M); cutoff="10f37171fb696c542586cbee96ea4a509ab74afc"; post=[(h,p) for h,p in rows if subprocess.run(["git","-C",L,"merge-base","--is-ancestor",h,cutoff]).returncode==1]; print("POSTCUTOFF pre=%d post=%d total=%d sum=%d"%(len(rows)-len(post),len(post),len(rows),len(rows)-len(post)+len(post))); print("\n".join(h+" "+p for h,p in post))
                                                                                            ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 473, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               **kwargs).stdout
               ^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 578, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', '-C', '/home/vgpnk/Projects/shokunin/kama-shokunin', 'show', 'c2aa7fb2:.ufo/waves/round-76/measured/after/append-exempt.out']' returned non-zero exit status 128.
```

```text
fatal: path '.ufo/waves/round-76/measured/after/gate-selftest.out' exists on disk, but not in 'c2aa7fb2'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:.ufo/waves/round-76/measured/after/gate-selftest.out"],text=True); print(text,end=""); assert "PRE_REPORT_SELFTEST pass=21 fail=0" in text and "exit=0" in text; r=subprocess.run(["git","-C",L,"grep","-l","PRE_REPORT_SELFTEST pass=18","c9ab73d8","--",".ufo/waves/round-75"],capture_output=True,text=True); print("ROUND75_PASS18_RECEIPTS=%d search_exit=%d"%(len(r.stdout.splitlines()),r.returncode)); assert r.returncode==1
                                                                             ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 473, in check_output
    return run(*popenargs, stdout=PIPE, timeout=timeout, check=True,
           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
               **kwargs).stdout
               ^^^^^^^^^
  File "/usr/lib/python3.14/subprocess.py", line 578, in run
    raise CalledProcessError(retcode, process.args,
                             output=stdout, stderr=stderr)
subprocess.CalledProcessError: Command '['git', '-C', '/home/vgpnk/Projects/shokunin/kama-shokunin', 'show', 'c2aa7fb2:.ufo/waves/round-76/measured/after/gate-selftest.out']' returned non-zero exit status 128.
```

Repaired both derivations to read committed receipt bytes at sealed base cc6e1d3c, while preserving their historical header revisions and ancestry cutoff; all corrected derivations exit 0.

Initial coverage regex required a bare first cell, missing the annotated runtime-health-surface-processes row, and reported 9 gaps. Corrected baseline admits annotations and reports 8 gaps. The command embedded in README includes that correction. Its auxiliary selfrecord_rows substring count rises to 2 after the command text itself is added; this is not a table-row census. The separate anchored after-table-rows.out establishes exactly one actual table row.

This seat initially hand-counted the S498 quote as 17 and wrongly disputed the closure count. The error is retained and explicitly superseded inside Gate by a 15-word correction, re-derived with split().

The first edit invocation failed before applying anything: `TypeError: tool.edit(...) expects a dict of arguments (got str)`. Read the schema, refreshed anchors, then applied the append-only patch successfully.

Historical gate receipt includes an inner diagnostic `PRE_REPORT round=70 arms=9 failed=1 uncommitted=0`; the outer recorded selftest summary is PRE_REPORT_SELFTEST pass=21 fail=0, exit=0. No claim is made that the diagnostic is an independently passing gate.

No new live source fetch; retained CommonMark bytes checked. No pre-report gate, judge, commit, push, stash, checkout, switch, reset, add, jj mutation, fixture repo, endpoint probe, service change, install, or external runtime invoked. No subagents dispatched. D2 and D5 and the overall round-77 C1/C2/C3 acceptance belong to other seats/L1.

Scratch: /fast/scratch/hyaku/kama-r77/SC03Corrections was created only for the final word-count command, TMPDIR exported, and removed by EXIT trap. Other probes only read lane data and wrote the named receipts through the file tool. No tree left behind.

Tools installed/updated: none.

## Self-evaluation

Accuracy 4/5: initial receipt-revision, cell-parser, and quote-count mistakes are disclosed and corrected; retained historical receipt evidence is not fresh gate execution. Completeness 4/5: D1/D3/D4/D6 complete; full round acceptance deliberately not graded here. Clarity 4/5: exact commands are long but replayable. Actionability 4/5: L1 can integrate the uncommitted append-only edits; no passing gate is implied. Conciseness 4/5: detailed failures and repeated command provenance are retained for audit. Overall 4.0/5. Improvement priorities: use mechanical word counts before filing, distinguish receipt-introduction revision from measurement headers, and parse full table cells. User agreement self-check: evidence and limitations are explicit, not a claimed canonical verdict.
