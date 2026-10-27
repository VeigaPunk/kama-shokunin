import os, subprocess, time, sys
D = os.getcwd()
child, non, aud = os.path.join(D,"child"), os.path.join(D,"libnonaudit.so"), os.path.join(D,"libaudit.so")
cases = [("control (no env vector)", {}),
         ("LD_PRELOAD=libnonaudit.so", {"LD_PRELOAD": non}),
         ("LD_AUDIT=libnonaudit.so (no la_version)", {"LD_AUDIT": non}),
         ("LD_AUDIT=libaudit.so (exports la_version)", {"LD_AUDIT": aud})]
for label, extra in cases:
    env = dict(os.environ); env.update(extra)
    p = subprocess.Popen([child], env=env, stderr=subprocess.PIPE, text=True)
    time.sleep(0.4)
    maps = open(f"/proc/{p.pid}/maps").read().splitlines()
    lib = list(extra.values())[0] if extra else non
    hits = [ln for ln in maps if lib in ln]
    p.kill(); err = p.communicate()[1].strip()
    print(f"case: {label}")
    print(f"  pid={p.pid} target={os.path.basename(lib)} mapped_rows={len(hits)}")
    for ln in hits[:3]: print(f"    {ln}")
    if err: print(f"  child stderr: {err.splitlines()[0][:160]}")
    print()
