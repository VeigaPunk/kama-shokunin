# Line-count-preserving variants: every edit keeps the tool's line numbers
# above `def main` unchanged, so the counter's replayed forge patches
# (forge-A/B, fuzz 3) still land on the same hunks.
import sys, ast
sys.path.insert(0, '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof/exp')
import drive
from drive import base_text, CHILD, HOP_SRC, run_variant
ARGV_CLOSE = "        '-c', str(args.ctx), '-t', str(args.threads),\n    ]\n"
ENV_ANCHOR = "                        'LLAMA_ARG_THREADS', 'XDG_CACHE_HOME')}\n"
MAIN = "def main(argv=None):\n"
for a in (ARGV_CLOSE, ENV_ANCHOR, MAIN, CHILD):
    assert base_text.count(a) == 1, a[:50]

def build(suffix='', defs='', env_extra='', child=None):
    t = base_text
    t = t.replace(ARGV_CLOSE, ARGV_CLOSE[:-len("    ]\n")] + "    ]" + suffix + "\n", 1)
    if env_extra:
        t = t.replace(ENV_ANCHOR, ENV_ANCHOR[:-1] + " | {" + env_extra + "}\n", 1)
    if child:
        t = t.replace(CHILD, child, 1)
    if defs:
        t = t.replace(MAIN, defs + MAIN, 1)
    return t

SH_ARGV = "; receipt['argv'] = ['/bin/sh', '-c', ' '.join(__import__('shlex').quote(x) for x in receipt['argv']) + ' ; :']"
PORT_PRE = "; import socket as _sk; _s = _sk.socket(); _s.bind(('127.0.0.1', 0)); alt_port = _s.getsockname()[1]; _s.close()"
MODEL_PRE = "; _alt = os.path.join(os.path.abspath(args.work), 'alt-model.gguf'); os.makedirs(os.path.abspath(args.work), exist_ok=True); shutil.copyfile(args.model, _alt)"
PRESET_DEF = '''def _write_preset(args):
    """Router-mode preset: the same model under the alias (no argv pin)."""
    p = os.path.join(os.path.abspath(args.work), 'preset.ini')
    os.makedirs(os.path.abspath(args.work), exist_ok=True)
    with open(p, 'w') as f:
        f.write(f'[{args.alias}]\\nmodel = {os.path.abspath(args.model)}\\nc = {args.ctx}\\nt = {args.threads}\\n')
    return p


'''
HOP_DEF = "exec(" + repr(HOP_SRC) + ")\n\n\n"
V = {}
V['B1_dup_port_same'] = lambda: build("; receipt['argv'] = receipt['argv'] + ['--port', str(port)]")
V['B2_dup_port_other'] = lambda: build(PORT_PRE + "; receipt['argv'] = receipt['argv'] + ['--port', str(alt_port)]")
V['B3_short_model_copy'] = lambda: build(MODEL_PRE + "; receipt['argv'] = receipt['argv'] + ['-m', _alt]")
V['B4_short_alias'] = lambda: build("; receipt['argv'] = receipt['argv'] + ['-a', 'other-alias']")
V['B5_extra_flag_benign'] = lambda: build("; receipt['argv'] = receipt['argv'] + ['--no-slots']")
V['C1_sh_exec'] = lambda: build("; receipt['argv'] = ['/bin/sh', '-c', 'exec ' + ' '.join(__import__('shlex').quote(x) for x in receipt['argv'])]")
V['C2_sh_hop_nofix'] = lambda: build(SH_ARGV, defs=HOP_DEF)
V['C2_sh_hop_pidfix'] = lambda: build(SH_ARGV, defs=HOP_DEF, child="        proc = _HopProc(proc); receipt['child_pid'] = proc.pid\n")
V['R1_router_preset_argv'] = lambda: build("; _p = _write_preset(args); receipt['argv'] = receipt['argv'] + ['--models-preset', _p]", defs=PRESET_DEF)
V['E1_env_extra'] = lambda: build(env_extra="'LLAMA_ARG_NO_WEBUI': '1'")

if __name__ == '__main__':
    for n in sys.argv[1:]:
        text = V[n]()
        ast.parse(text)
        assert text.count('\n') >= base_text.count('\n')
        run_variant(n, text)
