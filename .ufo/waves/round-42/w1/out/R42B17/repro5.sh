#!/bin/bash
# R42B17 repro 5 — logs everything to $S/r5.log so a traceback cannot truncate the run
S=/fast/scratch/kama-r42/seats/R42B17
export TMPDIR=$S/tmp
TOOL=$S/clone/tools/digest-ledger.py
CNT=$S/clone/tools/round42-digest-audit.py
R=$S/r5
mkdir -p "$R/registry" "$S/tmp"
T=3333333333333333333333333333333333333333333333333333333333333333
exec >>"$S/r5.log" 2>&1

echo "===== D: row naming /proc/self/environ (tool hashes the verifier's own environment)"
python3 - "$TOOL" "$R" <<'PY'
import hashlib,os,subprocess,sys
tool,r=sys.argv[1],sys.argv[2]
env=dict(os.environ, R42B17_CANARY="hunter2-canary")
blob=("\0".join(f"{k}={v}" for k,v in env.items())+"\0").encode()
d=hashlib.sha256(blob).hexdigest()
open(os.path.join(r,"registry/digest-ledger.tsv"),"w").write(
  "digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n%s\texternal\ts\t/proc/self/environ\t\t\t\n"%d)
open(os.path.join(r,"doc.md"),"w").write(d+"\n")
p=subprocess.run([sys.executable,tool,"scan","--dir",r],capture_output=True,text=True,env=env)
print("exit=",p.returncode)
print(p.stdout.strip())
print("isfile(/proc/self/environ)=",os.path.isfile("/proc/self/environ"))
PY
echo "rc=$?"

echo "===== E: read-only check (tool writes nothing): tree snapshot around a full scan"
printf 'digest\tclass\tsubject\tpath\tcorrect\tverified-at\tnote\n' > "$R/registry/digest-ledger.tsv"
printf '%s\n' "$T" > "$R/doc.md"
find "$R" -type f | sort > "$S/before.txt"
python3 "$TOOL" scan --dir "$R" --details > "$S/e.out" 2>&1; echo "tool_exit=$?"
find "$R" -type f | sort > "$S/after.txt"
diff "$S/before.txt" "$S/after.txt" && echo "no files created/removed by the scan"
echo "--- /tmp and seat tmp dirs after the scan:"; ls -A "$S/tmp" | head

echo "===== F: counter --out to an unwritable directory"
( cd "$S/clone" && python3 "$CNT" --repo "$S/clone" --tip HEAD --seed 42 --out /proc/nope/x.out > "$S/f.out" 2> "$S/f.err"; echo "counter_exit=$?" )
echo "stdout=[$(head -c 200 "$S/f.out")]"
echo "stderr_tail=[$(tail -c 240 "$S/f.err" | tr '\n' '|')]"

echo "===== G: independent re-run of the C2 counter at the candidate tip (seed 42)"
( cd "$S/clone" && timeout 900 python3 "$CNT" --repo "$S/clone" --tip 3d9bd8d72366e281fab291874524130428ee423d --seed 42 > "$S/g.out" 2> "$S/g.err"; echo "counter_exit=$?" )
cat "$S/g.out"
echo "stderr=[$(head -c 200 "$S/g.err")]"
echo "left in TMPDIR: $(ls -A "$S/tmp" | wc -l)"
echo "===== done"
