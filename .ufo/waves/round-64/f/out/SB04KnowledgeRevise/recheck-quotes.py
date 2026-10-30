#!/usr/bin/env python3
"""Re-open every source cited by process-bound-listener.md (wave f, SB04) and
check every quoted sentence used by the entry; re-derive every counter line
number the entry cites.

Usage: python3 .ufo/waves/round-64/f/out/SB04KnowledgeRevise/recheck-quotes.py
Exit 0 iff every quote is OK.

Sources re-opened live (curl-equivalent, stdlib only):
  S529 man7 proc_pid_fd(5)      S530 man7 proc_pid_stat(5)
  S531 man7 proc_pid_environ(5) S532 man7 proc_pid_cmdline(5)
  S533 man7 proc_pid_status(5)  S534 man7 namespaces(7)
  S495/S499 man7 proc_pid_exe(5) S496 man7 proc_pid_maps(5)
  S049 raw kernel Documentation/networking/proc_net_tcp.rst @ v7.2
Held text copies (S495/S496/S499) are read from the lane at COMMIT.
The counter is read with `git show COMMIT:tools/round64-c1-counter.py`
(the lane is never written, never committed).
"""
import hashlib
import re
import subprocess
import sys
import urllib.request
from html.parser import HTMLParser

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
COMMIT = '23b3fdb1a925129a9961cf551f6d40bf251602cb'
MAN = 'https://man7.org/linux/man-pages/man5/{}.5.html'
NS7 = 'https://man7.org/linux/man-pages/man7/namespaces.7.html'
PAGES = {'fd': 'proc_pid_fd', 'stat': 'proc_pid_stat',
         'environ': 'proc_pid_environ', 'cmdline': 'proc_pid_cmdline',
         'status': 'proc_pid_status', 'exe': 'proc_pid_exe',
         'maps': 'proc_pid_maps'}
TCP_RAW = ('https://raw.githubusercontent.com/torvalds/linux/v7.2/'
           'Documentation/networking/proc_net_tcp.rst')
TCP_SHA = 'a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a'


class Text(HTMLParser):
    BLOCK = ('p', 'pre', 'dt', 'dd', 'h1', 'h2', 'h3', 'li', 'br', 'div', 'tr')

    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0

    def handle_starttag(self, t, a):
        if t in ('script', 'style'):
            self.skip += 1
        if t in self.BLOCK:
            self.out.append('\n')

    def handle_endtag(self, t):
        if t in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def norm(s):
    return re.sub(r'\s+', ' ', s)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'kama-recheck/1'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


# (page key, quote) - every sentence the entry quotes verbatim.
QUOTES = [
    ('fd', 'For sockets, that inode can be used to find more information in '
           'one of the files under /proc/net/.'),
    ('fd', 'A readlink(2) call on this file returns a string in the format:'),
    ('fd', 'Permission to dereference or read (readlink(2)) the symbolic '
           'links in this directory is governed by a ptrace access mode '
           'PTRACE_MODE_READ_FSCREDS check'),
    ('fd', 'In a multithreaded process, the contents of this directory are '
           'not available if the main thread has already terminated'),
    ('stat', 'If the check denies access, then the field value is displayed '
             'as 0.'),
    ('stat', 'The PID of the parent of this process.'),
    ('stat', 'The time the process started after system boot.'),
    ('stat', 'Since Linux 2.6, the value is expressed in clock ticks '
             '(divide by sysconf(_SC_CLK_TCK)).'),
    ('environ', 'This file contains the initial environment that was set '
                'when the currently executing program was started via '
                'execve(2).'),
    ('environ', 'this file will not reflect those changes.'),
    ('environ', 'PR_SET_MM_ENV_START'),
    ('cmdline', 'processes have the freedom to override the memory region '
                'and break assumptions about the contents or format of the '
                '/proc/pid/cmdline file.'),
    ('cmdline', 'Think of this file as the command line that the process '
                'wants you to see.'),
    ('cmdline', 'If, after an execve(2), the process modifies its argv '
                'strings, those changes will show up here.'),
    # S533 - the new bind_trace / bind_state observations
    ('status', 'TracerPid  PID of process tracing this process (0 if not '
               'being  traced).'),
    ('status', 'State Current state of the process. One of "R (running)", '
               ' "S (sleeping)", "D (disk sleep)", "T (stopped)", "t  '
               '(tracing stop)", "Z (zombie)", or "X (dead)".'),
    ('exe', 'This symbolic link can be dereferenced normally; attempting to '
            'open it will open the executable.'),
    ('exe', "If the pathname has been unlinked, the symbolic link will "
            "contain the string ' (deleted)' appended to the original "
            "pathname."),
    ('exe', 'Permission to dereference or read (readlink(2)) this symbolic '
            'link is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS '
            'check'),
    ('maps', 'dev is the device (major:minor); inode is the inode on that '
             'device.'),
    ('maps', 'The pathname field will usually be the file that is backing '
             'the mapping.'),
    ('maps', 'If the mapping is file-backed and the file has been deleted, '
             'the string " (deleted)" is appended to the pathname.'),
    ('maps', '0 indicates that no inode is associated with the memory region'),
]
NS_QUOTES = [
    'If two processes are in the same namespace, then the device IDs and '
    'inode numbers of their /proc/pid/ns/xxx symbolic links will be the same',
    'Each process has a /proc/pid/ns/ subdirectory containing one entry',
]
HELD = [  # held text copies of S495 / S496 / S499 at the verified-at commit
    ('.ufo/waves/round-49/c1/proc_pid_exe.5.txt',
     'This symbolic link can be dereferenced normally; attempting to open it '
     'will open the executable.'),
    ('.ufo/waves/round-51/c1/proc_pid_exe.5.txt',
     'This symbolic link can be dereferenced normally; attempting to open it '
     'will open the executable.'),
    ('.ufo/waves/round-50/c1/proc_pid_maps.5.txt',
     'dev is the device (major:minor); inode is the inode on that device.'),
    ('.ufo/waves/round-50/c1/proc_pid_maps.5.txt',
     'The pathname field will usually be the file that is backing the '
     'mapping.'),
]
TCP_QUOTES = [
    'Note that these interfaces are deprecated in favor of tcp_diag.',
    'implemented by tcp4_seq_show() in net/ipv4/tcp_ipv4.c and '
    'tcp6_seq_show() in net/ipv6/tcp_ipv6.c, respectively.',
]
# the counter line anchors the entry cites, re-derived at COMMIT
FUNCS = ['listeners', 'holder_pids', 'stat_fields', 'ppid_chain', 'read_maps',
         'file_set', 'ns_of', 'holder_record', 'collect', 'grade_binding',
         'expected_argv', 'holders_signature', 'probe_fails', 'score',
         'draw_requests', 'probe', 'reference_run', 'pid_gone', 'kill_if_same',
         'witness_run']
CHECKS = ['bind_listener', 'bind_holders', 'bind_exe', 'bind_argv',
          'bind_env', 'bind_ns', 'bind_trace', 'bind_state', 'bind_maps',
          'bind_ancestry', 'hold_fresh', 'bind_stable', 'bind_claim',
          'bind_ref_files', 'teardown_observed', 'receipt_req',
          'receipt_ref_text', 'receipt_ref_usage']

total = ok = 0
texts = {}
for key, page in PAGES.items():
    url = MAN.format(page)
    body = fetch(url)
    print(f'fetch {url} bytes={len(body)} '
          f'sha256={hashlib.sha256(body).hexdigest()}')
    p = Text()
    p.feed(body.decode('utf-8', 'replace'))
    texts[key] = norm(''.join(p.out))
for key, q in QUOTES:
    total += 1
    hit = norm(q) in texts[key]
    ok += hit
    print(f"{'OK  ' if hit else 'MISS'} man:{key} {q[:80]}")

body = fetch(NS7)
print(f'fetch {NS7} bytes={len(body)} '
      f'sha256={hashlib.sha256(body).hexdigest()}')
p = Text()
p.feed(body.decode('utf-8', 'replace'))
ns_text = norm(''.join(p.out))
for q in NS_QUOTES:
    total += 1
    hit = norm(q) in ns_text
    ok += hit
    print(f"{'OK  ' if hit else 'MISS'} ns7 {q[:80]}")

body = fetch(TCP_RAW)
dig = hashlib.sha256(body).hexdigest()
print(f"fetch {TCP_RAW} bytes={len(body)} sha256={dig} "
      f"{'matches S049 raw sha' if dig == TCP_SHA else 'DIFFERS from S049 raw sha'}")
lines = body.decode('utf-8', 'replace').splitlines()
for needle in ('deprecated in favor', 'tcp6_seq_show()', '46: 010310AC:9C4C'):
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    print(f'S049 line of {needle!r}: {hits}')
t = norm(body.decode('utf-8', 'replace'))
for q in TCP_QUOTES:
    total += 1
    hit = norm(q) in t
    ok += hit
    print(f"{'OK  ' if hit else 'MISS'} S049 {q[:80]}")

for path, q in HELD:
    total += 1
    try:
        raw = subprocess.run(['git', '-C', LANE, 'show', f'{COMMIT}:{path}'],
                             capture_output=True, check=True).stdout.decode(
                                 'utf-8', 'replace')
        hit = norm(q) in norm(raw)
    except subprocess.CalledProcessError:
        hit = False
    ok += hit
    print(f"{'OK  ' if hit else 'MISS'} held@{COMMIT[:8]} "
          f"{path.split('/')[-1]} {q[:70]}")

ctl = subprocess.run(['git', '-C', LANE, 'show',
                      f'{COMMIT}:tools/round64-c1-counter.py'],
                     capture_output=True, check=True).stdout.decode('utf-8')
m = re.search(r'EXPECT_FAMILIES = \{(.*?)\n\}', ctl, re.S)
fam = eval('{' + m.group(1) + '}')
print(f'counter declares controls={sum(fam.values())} families={len(fam)}')
print('counter line anchors at %s:' % COMMIT[:8])
for name in FUNCS:
    hit = [i + 1 for i, ln in enumerate(ctl.splitlines())
           if ln.startswith(f'def {name}(')]
    print(f'  def {name:<18} line {hit[0] if hit else "NOT FOUND"}')
for name in CHECKS:
    hit = [i + 1 for i, ln in enumerate(ctl.splitlines())
           if f"'{name}'" in ln and 'fails.add' in ln
           or ln.strip().startswith(f"out['{name}']")]
    print(f'  check {name:<18} line {hit[0] if hit else "NOT FOUND"}')
tool = subprocess.run(['git', '-C', LANE, 'show',
                       f'{COMMIT}:tools/kama-completion-live.py'],
                      capture_output=True, check=True).stdout
print('tool sha256 at %s: %s' % (
    COMMIT[:8], hashlib.sha256(tool).hexdigest()))
print(f'quotes OK={ok}/{total}')
sys.exit(0 if ok == total else 1)
