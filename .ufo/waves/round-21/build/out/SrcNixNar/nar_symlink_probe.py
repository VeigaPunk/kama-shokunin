#!/usr/bin/env python3
"""NAR symlink probe for kama round 21 (lane SrcNixNar). Stdlib only.

Encodes trees with an encoder written from the Nix Archive grammar at nix tag 2.34.1
(doc/manual/source/protocols/nix-archive/index.md, EBNF lines 16-35):
  str(s)       = int64_le(len(s)) + s + zero padding to a multiple of 8 bytes
  nar          = str("nix-archive-1") nar-obj
  symlink node = str("(") str("type") str("symlink") str("target") str(<link text>) str(")")

This is NOT Nix's own dumper: no Nix binary is installed on this host. It shows what the
grammar implies for a digest over a tree, and checks the grammar against a known-answer size.

Checks:
  1. known-answer: a root symlink "../lib/foo" encodes to exactly 128 bytes and parses back
     to the raw link text (not a resolved path).
  2. retargeting one soname-style symlink (dangling target name, no regular file changes)
     changes the NAR digest.
  3. the same retarget leaves a regular-files-only digest (install_tree-like) unchanged.
  4. changing only a regular file's mtime leaves the NAR digest unchanged (no timestamps).
Exit 0 when all checks pass, 1 otherwise.
"""
import hashlib
import os
import stat
import struct
import sys
import tempfile


def enc(b: bytes) -> bytes:
    return struct.pack('<Q', len(b)) + b + b'\x00' * ((8 - len(b) % 8) % 8)


def nar_node(path: str) -> bytes:
    st = os.lstat(path)
    if stat.S_ISLNK(st.st_mode):
        target = os.fsencode(os.readlink(path))  # raw link text, never resolved
        return enc(b'(') + enc(b'type') + enc(b'symlink') + enc(b'target') + enc(target) + enc(b')')
    if stat.S_ISREG(st.st_mode):
        out = enc(b'(') + enc(b'type') + enc(b'regular')
        if st.st_mode & stat.S_IXUSR:
            out += enc(b'executable') + enc(b'')
        with open(path, 'rb') as f:
            out += enc(b'contents') + enc(f.read())
        return out + enc(b')')
    if stat.S_ISDIR(st.st_mode):
        out = enc(b'(') + enc(b'type') + enc(b'directory')
        for name in sorted(os.listdir(path), key=os.fsencode):  # entries ordered by name bytes
            out += (enc(b'entry') + enc(b'(') + enc(b'name') + enc(os.fsencode(name))
                    + enc(b'node') + nar_node(os.path.join(path, name)) + enc(b')'))
        return out + enc(b')')
    raise ValueError(f'unsupported file type: {path}')


def nar(path: str) -> bytes:
    return enc(b'nix-archive-1') + nar_node(path)


def read_str(buf: bytes, pos: int):
    n = struct.unpack_from('<Q', buf, pos)[0]
    data = buf[pos + 8:pos + 8 + n]
    return data, pos + 8 + n + ((8 - n % 8) % 8)


def expect(buf: bytes, pos: int, tok: bytes) -> int:
    got, pos = read_str(buf, pos)
    if got != tok:
        raise ValueError(f'expected {tok!r} got {got!r}')
    return pos


def parse_root_symlink(buf: bytes):
    pos = expect(buf, 0, b'nix-archive-1')
    pos = expect(buf, pos, b'(')
    pos = expect(buf, pos, b'type')
    pos = expect(buf, pos, b'symlink')
    pos = expect(buf, pos, b'target')
    target, pos = read_str(buf, pos)
    pos = expect(buf, pos, b')')
    return target, pos


def regular_only_digest(root: str) -> str:
    rows = []
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            p = os.path.join(dirpath, name)
            st = os.lstat(p)
            if not stat.S_ISREG(st.st_mode):  # install_tree pins regular files only
                continue
            with open(p, 'rb') as f:
                digest = hashlib.sha256(f.read()).hexdigest()
            rows.append(f"{os.path.relpath(p, root)}\t{digest}\t{int(bool(st.st_mode & stat.S_IXUSR))}\n")
    return hashlib.sha256(''.join(sorted(rows)).encode()).hexdigest()


def make_tree(root: str, link_target: str) -> None:
    os.makedirs(os.path.join(root, 'lib'))
    with open(os.path.join(root, 'lib', 'libllama.so.0.0.1'), 'wb') as f:
        f.write(b'ELF-STUB\n')
    os.symlink(link_target, os.path.join(root, 'lib', 'libllama.so.0'))
    os.symlink('libllama.so.0', os.path.join(root, 'lib', 'libllama.so'))


def main() -> int:
    results = []
    with tempfile.TemporaryDirectory(prefix='kama-r21-nar-') as tmp:
        # 1. known-answer single symlink
        single = os.path.join(tmp, 'root-link')
        os.symlink('../lib/foo', single)
        buf = nar(single)
        target, end = parse_root_symlink(buf)
        ok1 = len(buf) == 128 and target == b'../lib/foo' and end == len(buf)
        print(f'bytes={len(buf)} parsed_target={target!r} consumed={end}')
        print('hex=' + buf.hex())
        results.append(('1 grammar known-answer (128 bytes = 24+16+16+16+16+24+16; raw target text)', ok1))

        # 2 and 3: retarget the soname symlink to a dangling name; regular files unchanged
        t1 = os.path.join(tmp, 't1')
        t2 = os.path.join(tmp, 't2')
        t3 = os.path.join(tmp, 't3')
        make_tree(t1, 'libllama.so.0.0.1')
        make_tree(t2, 'libllama.so.0.0.9')
        make_tree(t3, 'libllama.so.0.0.1')
        n1, n2, n3 = (hashlib.sha256(nar(p)).hexdigest() for p in (t1, t2, t3))
        r1, r2 = regular_only_digest(t1), regular_only_digest(t2)
        print(f'nar_sha256 t1={n1}')
        print(f'nar_sha256 t2={n2}')
        print(f'regular_only t1={r1}')
        print(f'regular_only t2={r2}')
        results.append(('2 NAR digest changes when a symlink is retargeted', n1 != n2))
        results.append(('3 regular-only digest blind to the same retarget', r1 == r2))

        # 4: mtime-only change on a regular file
        os.utime(os.path.join(t3, 'lib', 'libllama.so.0.0.1'), (0, 0))
        n3b = hashlib.sha256(nar(t3)).hexdigest()
        print(f'nar_sha256 t3(mtime-only)={n3b}')
        results.append(('4 NAR digest unchanged by mtime-only change', n1 == n3b))

    failed = 0
    for label, ok in results:
        print(('PASS ' if ok else 'FAIL ') + label)
        failed += 0 if ok else 1
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
