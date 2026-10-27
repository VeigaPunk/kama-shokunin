#!/usr/bin/env python3
"""One archive case, one process: call the frozen verifier once and instrument it.

The verifier is imported from the lane tool verbatim (no edits, no reimplementation).
Instrumentation answers the seat question "is the refusal before any hash of the
member": every hashlib.sha256() instance the verifier creates is counted with the
bytes fed to it (instance 0 is the archive digest, instances >= 1 are member
digests), and tarfile.TarFile.extractfile is wrapped so a member read is visible.

Usage: measure_case.py --tool <path> --spec <case.json>
Prints one JSON object on stdout.
"""
import argparse
import hashlib
import importlib.util
import json
import resource
import sys
import tarfile
import time
import traceback

REAL_SHA256 = hashlib.sha256
REAL_EXTRACTFILE = tarfile.TarFile.extractfile
REAL_NEXT = tarfile.TarFile.next


def load_tool(path):
    spec = importlib.util.spec_from_file_location('kama_live_under_probe', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class HashProxy:
    def __init__(self, ledger):
        self._h = REAL_SHA256()
        self._entry = {'index': len(ledger), 'bytes': 0}
        ledger.append(self._entry)

    def update(self, data):
        self._entry['bytes'] += len(data)
        self._h.update(data)

    def hexdigest(self):
        return self._h.hexdigest()

    def digest(self):
        return self._h.digest()

    def copy(self):
        clone = object.__new__(HashProxy)
        clone._h = self._h.copy()
        clone._entry = self._entry
        return clone


class ReadProxy:
    def __init__(self, fh, ledger):
        self._fh = fh
        self._ledger = ledger

    def read(self, *a):
        data = self._fh.read(*a)
        self._ledger['member_bytes_read'] += len(data)
        return data

    def __getattr__(self, name):
        return getattr(self._fh, name)


def sha256_factory(ledger):
    def make(data=None, **kwargs):
        proxy = HashProxy(ledger)
        if data:
            proxy.update(data)
        return proxy
    return make


def run(tool_path, spec):
    mod = load_tool(tool_path)
    ledger = []
    reads = {'extractfile_calls': 0, 'member_bytes_read': 0}
    walks = {'next_calls': 0, 'max_offset': 0, 'last_tell': 0}

    def extract(self, member, *a, **k):
        reads['extractfile_calls'] += 1
        fh = REAL_EXTRACTFILE(self, member, *a, **k)
        return fh if fh is None else ReadProxy(fh, reads)

    def next_(self):
        walks['next_calls'] += 1
        try:
            return REAL_NEXT(self)
        finally:
            walks['max_offset'] = max(walks['max_offset'], getattr(self, 'offset', 0))
            try:
                walks['last_tell'] = self.fileobj.tell()
            except Exception:
                pass

    hashlib.sha256 = sha256_factory(ledger)
    tarfile.TarFile.extractfile = extract
    tarfile.TarFile.next = next_
    try:
        t0 = time.perf_counter()
        try:
            got = mod.verify_archive_member(
                spec['archive'], spec['archive_sha256'], spec['member'],
                spec['server_sha256'], spec['server_size'])
            outcome = {'result': 'accepted', 'returned': list(got)}
        except mod.SetupError as exc:
            outcome = {'result': 'refused', 'token': exc.code}
        except BaseException as exc:  # an internal fault is a finding, not a refusal
            outcome = {'result': 'fault', 'error': f'{type(exc).__name__}: {exc}',
                       'traceback': traceback.format_exc().splitlines()[-4:]}
        elapsed = round(time.perf_counter() - t0, 3)
    finally:
        hashlib.sha256 = REAL_SHA256
        tarfile.TarFile.extractfile = REAL_EXTRACTFILE
        tarfile.TarFile.next = REAL_NEXT
    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    archive_hashes = [e for e in ledger if e['index'] == 0]
    member_hashes = [e for e in ledger if e['index'] >= 1]
    return dict(spec, **outcome, seconds=elapsed, peak_rss_kb=rss_kb,
                hash_instances=len(ledger),
                archive_hash_bytes=archive_hashes[0]['bytes'] if archive_hashes else 0,
                member_hash_instances=len(member_hashes),
                member_hash_bytes=sum(e['bytes'] for e in member_hashes),
                member_hashed_before_verdict=bool(member_hashes),
                extractfile_calls=reads['extractfile_calls'],
                member_bytes_read=reads['member_bytes_read'],
                tar_walk=walks)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--tool', required=True)
    ap.add_argument('--spec', required=True)
    args = ap.parse_args(argv[1:])
    with open(args.spec) as fh:
        spec = json.load(fh)
    print(json.dumps(run(args.tool, spec), sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
