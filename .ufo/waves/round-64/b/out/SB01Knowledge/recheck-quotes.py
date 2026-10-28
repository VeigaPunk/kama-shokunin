#!/usr/bin/env python3
"""Re-open each cited source and check every quoted sentence used by
process-bound-listener.md. Fetches live URLs (stdlib only), extracts text
from man7 HTML, checks the quotes with whitespace normalised, checks the
held text copies from the lane at the verified-at commit, and prints the
S049 anchors (raw line numbers, raw digest, blob-page size) and the number
of counter controls declared by the counter at that commit.

Usage: python3 .ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.py [--commit SHA]
Exit 0 iff every quote is OK.
"""
import hashlib, re, subprocess, sys, urllib.request
from html.parser import HTMLParser

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
COMMIT = 'f6a4ea9a8b5a876d685b08e7e582ec0723412a4a'
if '--commit' in sys.argv:
    COMMIT = sys.argv[sys.argv.index('--commit') + 1]
MAN = 'https://man7.org/linux/man-pages/man5/{}.5.html'
PAGES = {'fd': 'proc_pid_fd', 'stat': 'proc_pid_stat', 'environ': 'proc_pid_environ',
         'cmdline': 'proc_pid_cmdline', 'exe': 'proc_pid_exe', 'maps': 'proc_pid_maps'}
TCP_RAW = 'https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst'
TCP_BLOB = 'https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst'
TCP_SHA = 'a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a'


class Text(HTMLParser):
    BLOCK = ('p', 'pre', 'dt', 'dd', 'h1', 'h2', 'h3', 'li', 'br', 'div', 'tr')

    def __init__(self):
        super().__init__(); self.out = []; self.skip = 0

    def handle_starttag(self, t, a):
        if t in ('script', 'style'): self.skip += 1
        if t in self.BLOCK: self.out.append('\n')

    def handle_endtag(self, t):
        if t in ('script', 'style'): self.skip -= 1

    def handle_data(self, d):
        if not self.skip: self.out.append(d)


def norm(s):
    return re.sub(r'\s+', ' ', s)


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'kama-recheck/1'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


QUOTES = [
 ('fd', 'For sockets, that inode can be used to find more information in one of the files under /proc/net/.'),
 ('fd', 'A readlink(2) call on this file returns a string in the format:'),
 ('fd', 'Permission to dereference or read (readlink(2)) the symbolic links in this directory is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check'),
 ('fd', 'In a multithreaded process, the contents of this directory are not available if the main thread has already terminated'),
 ('stat', 'If the check denies access, then the field value is displayed as 0.'),
 ('stat', 'The PID of the parent of this process.'),
 ('stat', 'The time the process started after system boot.'),
 ('stat', 'Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK)).'),
 ('environ', 'This file contains the initial environment that was set when the currently executing program was started via execve(2).'),
 ('environ', 'this file will not reflect those changes.'),
 ('environ', 'PR_SET_MM_ENV_START'),
 ('cmdline', 'processes have the freedom to override the memory region and break assumptions about the contents or format of the /proc/pid/cmdline file.'),
 ('cmdline', 'Think of this file as the command line that the process wants you to see.'),
 ('cmdline', 'If, after an execve(2), the process modifies its argv strings, those changes will show up here.'),
 ('exe', 'This symbolic link can be dereferenced normally; attempting to open it will open the executable.'),
 ('exe', "If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname."),
 ('exe', 'Permission to dereference or read (readlink(2)) this symbolic link is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check'),
 ('maps', 'dev is the device (major:minor); inode is the inode on that device.'),
 ('maps', 'The pathname field will usually be the file that is backing the mapping.'),
 ('maps', 'If the mapping is file-backed and the file has been deleted, the string " (deleted)" is appended to the pathname.'),
 ('maps', '0 indicates that no inode is associated with the memory region'),
]
HELD = [  # held text copies of S495 / S496 / S499 at the verified-at commit
 ('.ufo/waves/round-49/c1/proc_pid_exe.5.txt', 'This symbolic link can be dereferenced normally; attempting to open it will open the executable.'),
 ('.ufo/waves/round-51/c1/proc_pid_exe.5.txt', 'This symbolic link can be dereferenced normally; attempting to open it will open the executable.'),
 ('.ufo/waves/round-50/c1/proc_pid_maps.5.txt', 'dev is the device (major:minor); inode is the inode on that device.'),
 ('.ufo/waves/round-50/c1/proc_pid_maps.5.txt', 'The pathname field will usually be the file that is backing the mapping.'),
]
TCP_QUOTES = [
 'Note that these interfaces are deprecated in favor of tcp_diag.',
 'implemented by tcp4_seq_show() in net/ipv4/tcp_ipv4.c and tcp6_seq_show() in net/ipv6/tcp_ipv6.c, respectively.',
]

total = ok = 0
texts = {}
for key, page in PAGES.items():
    url = MAN.format(page)
    body = fetch(url)
    print(f'fetch {url} bytes={len(body)} sha256={hashlib.sha256(body).hexdigest()}')
    p = Text(); p.feed(body.decode('utf-8', 'replace'))
    texts[key] = norm(''.join(p.out))
for key, q in QUOTES:
    total += 1; hit = norm(q) in texts[key]; ok += hit
    print(f"{'OK  ' if hit else 'MISS'} man:{key} {q[:80]}")

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
    total += 1; hit = norm(q) in t; ok += hit
    print(f"{'OK  ' if hit else 'MISS'} S049 {q[:80]}")

blob = fetch(TCP_BLOB)
print(f'fetch {TCP_BLOB} bytes={len(blob)} starts={blob[:15]!r} (blob page, not the .rst)')

for path, q in HELD:
    total += 1
    try:
        raw = subprocess.run(['git', '-C', LANE, 'show', f'{COMMIT}:{path}'],
                             capture_output=True, check=True).stdout.decode('utf-8', 'replace')
        hit = norm(q) in norm(raw)
    except subprocess.CalledProcessError:
        hit = False
    ok += hit
    print(f"{'OK  ' if hit else 'MISS'} held@{COMMIT[:8]} {path.split('/')[-1]} {q[:70]}")

ctl = subprocess.run(['git', '-C', LANE, 'show', f'{COMMIT}:tools/round64-c1-counter.py'],
                     capture_output=True, check=True).stdout.decode('utf-8')
m = re.search(r'EXPECT_FAMILIES = \{(.*?)\n\}', ctl, re.S)
fam = eval('{' + m.group(1) + '}')
print(f'counter declares controls={sum(fam.values())} families={len(fam)}')
print(f'quotes OK={ok}/{total}')
sys.exit(0 if ok == total else 1)
