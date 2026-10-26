#!/usr/bin/env python3
"""Build the two proposed patches from the frozen lane files (read-only copy)."""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
S = os.environ["S"]
BASE = os.path.join(S, "patch")


def edit(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:80])
        s = s.replace(old, new)
    open(path, "w").write(s)


def stage(name):
    for side in ("orig", "new"):
        d = os.path.join(BASE, side, "tools")
        os.makedirs(d, exist_ok=True)
        shutil.copy2(os.path.join(LANE, "tools", name), os.path.join(d, name))
    return (os.path.join(BASE, "orig", "tools", name),
            os.path.join(BASE, "new", "tools", name))


def diff(name, out):
    p = subprocess.run(["diff", "-u",
                        "--label", f"a/tools/{name}", os.path.join(BASE, "orig", "tools", name),
                        "--label", f"b/tools/{name}", os.path.join(BASE, "new", "tools", name)],
                       capture_output=True, text=True)
    assert p.returncode == 1, p.returncode
    open(out, "w").write(p.stdout)
    print(f"{out}: {len(p.stdout.splitlines())} lines")


def replay_patch():
    _o, new = stage("kama-live-replay.py")
    edit(new, [
        ("Network: https only, for the two recorded URLs. Writes only under --work and J.",
         "Network: https only (a redirect must stay on https; file:// is accepted\n"
         "only with --allow-file-urls, which the selftest uses). Writes only under\n"
         "--work and J; a refusal always writes J."),
        ("CHUNK = 1 << 20",
         "CHUNK = 1 << 20\nMAX_BYTES = 1 << 30   # per-url download cap (asset 22 MB, model 1.2 MB)"),
        ("def fetch(url, dest, timeout=120):",
         "def fetch(url, dest, timeout=120, allow_file=False, max_bytes=MAX_BYTES):"),
        ('    """Download url to dest (https or file://; file:// only for the selftest)."""',
         '    """Download url to dest (https; file:// only with allow_file). At most\n'
         '    max_bytes are read, a redirect that leaves https is refused, and the\n'
         '    partial .part file is removed on any failure."""'),
        ('    if not (url.startswith("https://") or url.startswith("file://")):',
         '    if not (url.startswith("https://")\n'
         '            or (allow_file and url.startswith("file://"))):'),
        ('    with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as fh:\n'
         '        shutil.copyfileobj(r, fh, CHUNK)\n'
         '    os.replace(tmp, dest)',
         '    try:\n'
         '        with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb") as fh:\n'
         '            final = r.geturl() or url\n'
         '            if url.startswith("https://") and not final.startswith("https://"):\n'
         '                raise Refused(f"redirect-left-https:{final}")\n'
         '            n = 0\n'
         '            while True:\n'
         '                chunk = r.read(CHUNK)\n'
         '                if not chunk:\n'
         '                    break\n'
         '                n += len(chunk)\n'
         '                if n > max_bytes:\n'
         '                    raise Refused(f"download-too-large:{url}:>{max_bytes}")\n'
         '                fh.write(chunk)\n'
         '        os.replace(tmp, dest)\n'
         '    except BaseException:\n'
         '        try:\n'
         '            os.unlink(tmp)\n'
         '        except OSError:\n'
         '            pass\n'
         '        raise'),
        ("def acquire(url, sha, dest):", "def acquire(url, sha, dest, allow_file=False):"),
        ("    fetch(url, dest)\n", "    fetch(url, dest, allow_file=allow_file)\n"),
        ("def replay(receipt_path, work, live=DEFAULT_LIVE, timeout=600):",
         "def replay(receipt_path, work, live=DEFAULT_LIVE, timeout=600, allow_file=False):"),
        ('        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"], archive)',
         '        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"],\n'
         '                                                 archive, allow_file=allow_file)'),
        ('        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"], model)',
         '        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"],\n'
         '                                               model, allow_file=allow_file)'),
        ('        tree = os.path.join(work, "server")',
         '        tree = os.path.join(work, "server")\n'
         '        # fresh tree: a reused --work must never supply the member that runs\n'
         '        shutil.rmtree(tree, ignore_errors=True)'),
        ('        res["inputs"].update({"archive": archive, "model": model, "server": server})',
         '        # the binary may run only if it is the binary the receipt recorded\n'
         '        want = (rec.get("server") or {}).get("sha256")\n'
         '        got = sha256_file(server)\n'
         '        res["inputs"]["member_sha256"] = got\n'
         '        if isinstance(want, str) and HEX64.fullmatch(want) and got != want:\n'
         '            raise Refused(f"member-digest-mismatch:{need[\'server.member\']}:"\n'
         '                          f"want={want}:got={got}")\n'
         '        res["inputs"].update({"archive": archive, "model": model, "server": server})'),
        ('    except (OSError, ValueError, tarfile.TarError, subprocess.TimeoutExpired, urllib.error.URLError) as exc:\n'
         '        res["refused"] = f"could-not-run:{type(exc).__name__}:{exc}"\n'
         '        return res, 2',
         '    except (OSError, ValueError, tarfile.TarError, subprocess.TimeoutExpired, urllib.error.URLError) as exc:\n'
         '        res["refused"] = f"could-not-run:{type(exc).__name__}:{exc}"\n'
         '        return res, 2\n'
         '    except Exception as exc:\n'
         '        # e.g. http.client.IncompleteRead: a refusal, never the exit-1\n'
         '        # "ran and differs" code or a traceback with no J\n'
         '        res["refused"] = f"could-not-run:{type(exc).__name__}:{exc}"\n'
         '        return res, 2'),
        ('    d = tempfile.mkdtemp(prefix="klr-st-", dir=root)',
         '    os.makedirs(root, exist_ok=True)\n'
         '    d = tempfile.mkdtemp(prefix="klr-st-", dir=root)'),
        ('            res, code = replay(rp, os.path.join(d, f"w-{len(cases)}"), live=live)',
         '            res, code = replay(rp, os.path.join(d, f"w-{len(cases)}"), live=live,\n'
         '                               allow_file=True)'),
        ('        run("absent-member", receipt(**{"provenance.server.member": "build/bin/nope"}), 2, "member-absent")',
         '        run("absent-member", receipt(**{"provenance.server.member": "build/bin/nope"}), 2, "member-absent")\n'
         '        run("member-digest-mismatch", receipt(**{"server.sha256": "0" * 64}), 2,\n'
         '            "member-digest-mismatch")'),
        ('    ap.add_argument("--scratch", help="selftest root (default TMPDIR)")',
         '    ap.add_argument("--scratch", help="selftest root (default TMPDIR)")\n'
         '    ap.add_argument("--allow-file-urls", action="store_true",\n'
         '                    help="accept file:// provenance URLs (offline replay)")'),
        ('    res, code = replay(a.receipt, a.work, a.live, a.timeout)',
         '    res, code = replay(a.receipt, a.work, a.live, a.timeout, a.allow_file_urls)'),
        ('    with open(a.out, "w") as fh:',
         '    os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)\n'
         '    with open(a.out, "w") as fh:'),
    ])
    diff("kama-live-replay.py", os.path.join(BASE, "proposed-kama-live-replay.diff"))


def counter_patch():
    _o, new = stage("round47-live-replay-audit.py")
    edit(new, [
        ('ASSET_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"',
         'ASSET_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"\n'
         'MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/main/"\n'
         '             "tinyllamas/stories260K.gguf")\n'
         'MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"'),
        ('    if not str(mdl.get("url") or "").startswith("https://"):\n'
         '        probs.append(f"provenance.model.url {mdl.get(\'url\')!r}")',
         '    if mdl.get("url") != MODEL_URL:\n'
         '        probs.append(f"provenance.model.url {mdl.get(\'url\')!r}")\n'
         '    if mdl.get("sha256") != MODEL_SHA:\n'
         '        probs.append(f"provenance.model.sha256 {mdl.get(\'sha256\')!r}")'),
        ('def run_replay(tree, receipt, work, outj, env, timeout=1200):\n'
         '    try:\n'
         '        p = subprocess.run([sys.executable, os.path.join(tree, REPLAY), "--receipt", receipt,\n'
         '                            "--work", work, "--out", outj], capture_output=True, text=True,\n'
         '                           env=env, cwd=tree, timeout=timeout)\n'
         '    except subprocess.TimeoutExpired:\n'
         '        return None, None, "timeout"\n'
         '    try:\n'
         '        with open(outj) as fh:\n'
         '            j = json.load(fh)\n'
         '    except (OSError, ValueError):\n'
         '        j = None\n'
         '    return p.returncode, j, (p.stdout[-400:] + " | " + p.stderr[-400:]).replace("\\n", " ")',
         'def run_replay(tree, receipt, work, outj, env, timeout=1200):\n'
         '    argv = [sys.executable, os.path.join(tree, REPLAY), "--receipt", receipt,\n'
         '            "--work", work, "--out", outj]\n'
         '    try:\n'
         '        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,\n'
         '                                text=True, env=env, cwd=tree, start_new_session=True)\n'
         '    except OSError as exc:\n'
         '        return None, None, f"could-not-start:{exc}"\n'
         '    try:\n'
         '        out, err = proc.communicate(timeout=timeout)\n'
         '    except subprocess.TimeoutExpired:\n'
         '        # the replay tool, the live tool and llama-server share this new\n'
         '        # session; kill the group so nothing outlives the counter and\n'
         '        # races the scratch removal below\n'
         '        try:\n'
         '            os.killpg(proc.pid, signal.SIGKILL)\n'
         '        except OSError:\n'
         '            pass\n'
         '        proc.communicate()\n'
         '        return None, None, "timeout"\n'
         '    try:\n'
         '        with open(outj) as fh:\n'
         '            j = json.load(fh)\n'
         '    except (OSError, ValueError):\n'
         '        j = None\n'
         '    return proc.returncode, j, (out[-400:] + " | " + err[-400:]).replace("\\n", " ")'),
        ("import shutil\nimport subprocess",
         "import shutil\nimport signal\nimport subprocess"),
    ])
    diff("round47-live-replay-audit.py", os.path.join(BASE, "proposed-round47-counter.diff"))


if __name__ == "__main__":
    shutil.rmtree(BASE, ignore_errors=True)
    replay_patch()
    counter_patch()
