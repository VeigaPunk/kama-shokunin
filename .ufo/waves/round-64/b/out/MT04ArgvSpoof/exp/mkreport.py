import json, re
S = '/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof'
def res(n):
    r = json.load(open(f'{S}/exp/result-{n}.json'))
    errs = [l for l in r['stderr'].splitlines() if l.startswith('error: live') or l.startswith('error: forge')]
    return r, errs
def L(n):
    r, errs = res(n)
    line = r['line']
    return f"`{n}` tip `{r['tip'][:12]}` exit {r['exit']}\n```\n{line}\n" + ''.join(e + '\n' for e in errs[:4]) + "```"
base = open(f'{S}/work/base.out').read().strip()
base2 = open(f'{S}/work/base2.out').read().strip()
tpl = open(f'{S}/exp/report.tpl').read()
names = ['A_exec','A_exec_fab','A_retitle','A_retitle_fab','B1_dup_port_same','B2_dup_port_other','B3_short_model_copy',
         'B6_dup_model_long_r3','B7_alias_comma_r3','B4_short_alias_r3','C1_sh_exec_r3','C2_sh_hop_nofix','C2_sh_hop_pidfix_r3',
         'B5_extra_flag_benign_r3','R1_router_preset_argv_r3','E1_env_extra_r3']
out = tpl.replace('@@BASE@@', base).replace('@@BASE2@@', base2)
for n in names:
    out = out.replace('@@L:' + n + '@@', L(n))
open('/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-64/b/MT04ArgvSpoof.md', 'w').write(out)
print(len(out.splitlines()), 'lines')
