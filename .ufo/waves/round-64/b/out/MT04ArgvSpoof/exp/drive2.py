import sys
sys.path.insert(0, '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof/exp')
import drive
from drive import base_text, DEF_RUN, CHILD, FWD_SRC, HOP_SRC, run_variant
ARGV_ANCHOR = "        '-c', str(args.ctx), '-t', str(args.threads),\n    ]\n"
assert base_text.count(ARGV_ANCHOR) == 1
HEAD = 'import shlex as _shlex\n'

def build(argv_add='', pre='', post_child='', hop=False):
    t = base_text
    head = HEAD + ('exec(' + repr(HOP_SRC) + ')\n' if hop else '')
    t = t.replace(DEF_RUN, head + DEF_RUN, 1)
    t = t.replace(ARGV_ANCHOR, ARGV_ANCHOR + pre + argv_add, 1)
    if post_child:
        t = t.replace(CHILD, CHILD + post_child, 1)
    return t

V = {}
V['B1_dup_port_same'] = lambda: build("    receipt['argv'] = receipt['argv'] + ['--port', str(port)]\n")
V['B2_dup_port_other'] = lambda: build(
    "    receipt['argv'] = receipt['argv'] + ['--port', str(alt_port)]\n",
    pre="    import socket as _sk\n    _s = _sk.socket(); _s.bind(('127.0.0.1', 0)); alt_port = _s.getsockname()[1]; _s.close()\n")
V['B3_short_model_copy'] = lambda: build(
    "    receipt['argv'] = receipt['argv'] + ['-m', _alt_model]\n",
    pre="    _alt_model = os.path.join(os.path.abspath(args.work), 'alt-model.gguf')\n    os.makedirs(os.path.abspath(args.work), exist_ok=True)\n    shutil.copyfile(args.model, _alt_model)\n")
V['B4_short_alias'] = lambda: build("    receipt['argv'] = receipt['argv'] + ['-a', 'other-alias']\n")
V['B5_extra_flag_benign'] = lambda: build("    receipt['argv'] = receipt['argv'] + ['--no-slots']\n")
V['C1_sh_exec'] = lambda: build(
    "    receipt['argv'] = ['/bin/sh', '-c', 'exec ' + ' '.join(_shlex.quote(x) for x in receipt['argv'])]\n")
V['C2_sh_hop_nofix'] = lambda: build(
    "    receipt['argv'] = ['/bin/sh', '-c', ' '.join(_shlex.quote(x) for x in receipt['argv']) + ' ; :']\n")
V['C2_sh_hop_pidfix'] = lambda: build(
    "    receipt['argv'] = ['/bin/sh', '-c', ' '.join(_shlex.quote(x) for x in receipt['argv']) + ' ; :']\n",
    post_child="        proc = _HopProc(proc)\n        receipt['child_pid'] = proc.pid\n", hop=True)

if __name__ == '__main__':
    import ast
    names = sys.argv[1:] or list(V)
    for n in names:
        text = V[n]()
        ast.parse(text)
        run_variant(n, text)

ENV_ANCHOR = "                        'LLAMA_ARG_THREADS', 'XDG_CACHE_HOME')}\n"
assert base_text.count(ENV_ANCHOR) == 1
def build_env(line):
    t = build()
    return t.replace(ENV_ANCHOR, ENV_ANCHOR + line, 1)
V['R1_router_preset_argv'] = lambda: build(
    "    receipt['argv'] = receipt['argv'] + ['--models-preset', _preset]\n",
    pre="    _preset = os.path.join(os.path.abspath(args.work), 'preset.ini')\n    os.makedirs(os.path.abspath(args.work), exist_ok=True)\n    with open(_preset, 'w') as _pf:\n        _pf.write(f'[{args.alias}]\\nmodel = {os.path.abspath(args.model)}\\nc = {args.ctx}\\nt = {args.threads}\\n')\n")
V['E1_env_extra'] = lambda: build_env("        env['LLAMA_ARG_NO_WEBUI'] = '1'\n")
if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] in ('R1_router_preset_argv', 'E1_env_extra'):
    import ast
    for n in sys.argv[1:]:
        text = V[n](); ast.parse(text); run_variant(n, text)
