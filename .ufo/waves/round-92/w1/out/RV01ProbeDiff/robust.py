#!/usr/bin/env python3
"""Pipeline robustness: awk-missing, SIGPIPE/pipefail exit codes, LC_ALL restoration."""
import os, subprocess, sys

SC = "/fast/scratch/hyaku/kama-r92/RV01ProbeDiff"
BIN = f"{SC}/bin"
os.makedirs(BIN, exist_ok=True)

def sh(rev, body, env_extra=None, path=None, label=""):
    env = dict(os.environ)
    env.pop("LANG", None); env.pop("LC_ALL", None)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run(["bash", "-c", f"source {SC}/h{rev}.sh\n" + body],
                       env=env, capture_output=True, timeout=120)
    print(f"[{label}] rc={p.returncode} out={p.stdout[:120]!r} err={p.stderr[:200]!r}")
    return p.returncode, p.stdout, p.stderr

print("== 1. awk missing (PATH has only python3+dirname) ==")
for f in ("python3", "dirname"):
    src = subprocess.run(["bash", "-c", "command -v " + f], capture_output=True, text=True).stdout.strip()
    dst = os.path.join(BIN, f)
    if not os.path.exists(dst):
        os.symlink(src, dst)
CTL = r"'a\x01b'"  # forces jstr slow path
for rev in ("B", "M2"):
    sh(rev, f'PATH={BIN} jstr {CTL}; echo "JSTR_RC=$?"', label=f"jstr-ctl-{rev}")
for rev in ("B", "M2"):
    sh(rev, f'PATH={BIN} served_persist "a,b\\x01c"; echo "SP_RC=$?"', label=f"sp-ctl-{rev}")

print("== 2. SIGPIPE: jstr output closed early by head -c 1 ==")
GEN = 's=$(printf "a%.0s" $(seq 1 5000000)); s="$s"$(printf "\\x01")'
for rev in ("B", "M2"):
    body = f'''
{GEN}
set -o pipefail
jstr "$s" | head -c 1 >/dev/null
echo "JSTR_PS=${{PIPESTATUS[0]}}"
'''
    env = dict(os.environ); env.pop("LANG", None); env.pop("LC_ALL", None)
    p = subprocess.run(["bash", "-c", f"source {SC}/h{rev}.sh\n" + body],
                       env=env, capture_output=True, timeout=120)
    print(f"[jstr-sigpipe-{rev}] rc={p.returncode} out={p.stdout!r} err={p.stderr[:150]!r}")

print("== 3. served_persist multiline 2MB: internal NR>1 exit vs base first-line read ==")
for rev in ("B", "M2"):
    env = dict(os.environ); env.pop("LANG", None); env.pop("LC_ALL", None)
    p = subprocess.run(["bash", "-c", f"source {SC}/h{rev}.sh\n"
                        + 'ml="$(printf "a\\n"; printf "x%.0s" $(seq 1 1000000); printf "\\n"; printf "y%.0s" $(seq 1 1000000))"\n'
                        + 'served_persist "$ml"; echo " SP_RC=$?"'],
                       env=env, capture_output=True, timeout=120)
    print(f"[sp-bigmultiline-{rev}] rc={p.returncode} out={p.stdout[:60]!r} err={p.stderr[:100]!r}")

print("== 4. served_persist multiline small under pipefail (status only) ==")
for rev in ("B", "M2"):
    sh(rev, 'set -o pipefail; served_persist $\'a\\nb,c\'; echo " RC=$?"', label=f"sp-smallml-{rev}")

print("== 5. LC_ALL / LANG restoration after jstr and served_persist ==")
for rev in ("B", "M2"):
    sh(rev, 'LC_ALL=en_US.UTF-8; s=$(jstr "x\\x01"); echo "LC_ALL_after=${LC_ALL-unset} LANG=${LANG-unset} out=$s"',
       label=f"lc-restore-{rev}")
for rev in ("B", "M2"):
    sh(rev, 'export LC_ALL=en_US.UTF-8; s=$(jstr "x"); echo "LC_ALL_after=${LC_ALL-unset}"', label=f"lc-exported-{rev}")
for rev in ("B", "M2"):
    sh(rev, 's=$(served_persist "a,b"); echo "LC_ALL_after=${LC_ALL-unset}"', label=f"lc-sp-{rev}")
print("== 6. jstr under set -e with awk missing mid-corpus: function exit vs output ==")
for rev in ("B", "M2"):
    sh(rev, f'PATH={BIN} v=$(jstr {CTL}) ; echo "ASSIGN_RC=$? v=$v"', label=f"jstr-cmdsub-{rev}")
