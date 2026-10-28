import os, re, subprocess, sys, json, shutil, socket, time
S = '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof'
D = f'{S}/clone'
BASE = 'f6a4ea9a8b5a876d685b08e7e582ec0723412a4a'
sys.path.insert(0, f'{S}/exp')
from fwd_src import FWD_SRC, HOP_SRC
TOOL = f'{D}/tools/kama-completion-live.py'
base_text = subprocess.run(['git', '-C', D, 'show', f'{BASE}:tools/kama-completion-live.py'], capture_output=True, check=True).stdout.decode()

POP = "        proc = subprocess.Popen(\n            receipt['argv'], stdout=log_f,"
assert base_text.count(POP) == 1
HOLD_LINE = "        holders = _proc_holders(port)\n"
assert base_text.count(HOLD_LINE) == 1
CHILD = "        receipt['child_pid'] = proc.pid\n"
assert base_text.count(CHILD) == 1
DEF_RUN = "def run(args):\n"
assert base_text.count(DEF_RUN) == 1

PRE_FWD = ("        fwd_path = os.path.join(work, 'fwd.py')\n"
           "        with open(fwd_path, 'w') as _ff:\n"
           "            _ff.write(FWD_SRC)\n")

def popen_with(argv_expr, pre='', fabricate=False, hop=False):
    t = base_text
    head = 'import shlex as _shlex\n'
    if 'FWD' in argv_expr or 'fwd_path' in argv_expr or 'FWD_SRC' in pre:
        head += 'FWD_SRC = ' + repr(FWD_SRC) + '\n'
    if hop:
        head += 'HOP_SRC_CODE = ' + repr(HOP_SRC) + '\n'
    t = t.replace(DEF_RUN, head + DEF_RUN, 1) if head else t
    if hop:
        # define the hop class at module scope (exec'd source)
        t = t.replace(head + DEF_RUN, head + "exec(HOP_SRC_CODE)\n" + DEF_RUN, 1)
    newpop = pre + "        proc = subprocess.Popen(\n            " + argv_expr + ", stdout=log_f,"
    t = t.replace(POP, newpop, 1)
    if hop:
        t = t.replace(CHILD, "        proc = _HopProc(proc)\n" + CHILD, 1)
    if fabricate:
        t = t.replace(HOLD_LINE, "        holders = [{'pid': proc.pid, 'exe': server, 'exe_sha256': server_sha}]\n", 1)
    return t

def run_variant(name, text, extra_note=''):
    subprocess.run(['git', '-C', D, 'reset', '-q', '--hard', BASE], check=True)
    with open(TOOL, 'w') as f:
        f.write(text)
    subprocess.run(['git', '-C', D, 'add', '-A'], check=True)
    subprocess.run(['git', '-C', D, '-c', 'user.name=seat', '-c', 'user.email=seat@seat.invalid', 'commit', '-q', '--allow-empty', '-m', f'wip {name}'], check=True)
    tip = subprocess.run(['git', '-C', D, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    work = f'{S}/work/{name}'
    os.makedirs(work, exist_ok=True)
    r = subprocess.run([sys.executable, f'{D}/tools/round64-c1-counter.py', '--repo', D, '--tip', tip, '--work', work],
                       capture_output=True, text=True, cwd=f'{D}/tools', timeout=900)
    out = r.stdout.strip()
    err = r.stderr.strip()
    res = {'name': name, 'tip': tip, 'exit': r.returncode, 'line': out, 'stderr': err[:1500], 'note': extra_note}
    with open(f'{S}/exp/result-{name}.json', 'w') as f:
        json.dump(res, f, indent=1)
    print(f'== {name} tip={tip[:12]} exit={r.returncode}\n{out}\n{err[:900]}\n', flush=True)
    subprocess.run(['git', '-C', D, 'reset', '-q', '--hard', BASE], check=True)
    return res

def A_exec():
    argv = "['/bin/bash', '-c', 'exec -a \"$0\" \"$@\"', receipt['argv'][0], sys.executable, fwd_path, 'exec', *receipt['argv']]"
    return popen_with(argv, pre=PRE_FWD)
def A_retitle():
    argv = "[sys.executable, fwd_path, 'retitle', *receipt['argv']]"
    return popen_with(argv, pre=PRE_FWD)

def cmd_join():
    return "' '.join(_shlex.quote(x) for x in receipt['argv'])"

variants = {}
variants['A_exec'] = lambda: A_exec()
variants['A_exec_fab'] = lambda: A_exec().replace(HOLD_LINE, "        holders = [{'pid': proc.pid, 'exe': server, 'exe_sha256': server_sha}]\n", 1)
variants['A_retitle'] = lambda: A_retitle()
variants['A_retitle_fab'] = lambda: A_retitle().replace(HOLD_LINE, "        holders = [{'pid': proc.pid, 'exe': server, 'exe_sha256': server_sha}]\n", 1)
variants['B1_dup_port_same'] = lambda: popen_with("receipt['argv'] + ['--port', str(port)]")
variants['B4_short_alias'] = lambda: popen_with("receipt['argv'] + ['-a', 'other-alias']")
variants['B5_extra_flag_benign'] = lambda: popen_with("receipt['argv'] + ['--no-slots']")
variants['C1_bash_exec'] = lambda: popen_with("['/bin/bash', '-c', 'exec ' + " + cmd_join() + ", ]")
variants['C2_sh_hop_pidfix'] = lambda: popen_with("['/bin/sh', '-c', " + cmd_join() + " + ' ; :']", hop=True)
variants['C2_sh_hop_nofix'] = lambda: popen_with("['/bin/sh', '-c', " + cmd_join() + " + ' ; :']")


def _alt_port_pre():
    return ("        import socket as _sk\n"
            "        _s = _sk.socket(); _s.bind(('127.0.0.1', 0)); alt_port = _s.getsockname()[1]; _s.close()\n")
variants['B2_dup_port_other'] = lambda: popen_with("receipt['argv'] + ['--port', str(alt_port)]", pre=_alt_port_pre())
def _alt_model_pre():
    return ("        alt_model = os.path.join(work, 'alt-model.gguf')\n"
            "        shutil.copyfile(args.model, alt_model)\n")
variants['B3_short_model_copy'] = lambda: popen_with("receipt['argv'] + ['-m', alt_model]", pre=_alt_model_pre())
variants['C1_sh_exec'] = lambda: popen_with("['/bin/sh', '-c', 'exec ' + " + cmd_join() + "]")

if __name__ == '__main__':
    names = sys.argv[1:] or list(variants)
    for n in names:
        text = variants[n]()
        if 'exec ' in text and False:
            pass
        run_variant(n, text)
