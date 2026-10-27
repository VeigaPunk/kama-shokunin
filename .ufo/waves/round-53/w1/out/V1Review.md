Verdict: One actionable robustness defect in `verify_code`: a mapping entry with no path can be accepted as a root-owned host mapping.

## Finding — malformed mapping without `path` is verified as host code

Severity: medium (receipt contract validation / observability).

At `tools/kama-live-replay.py:321-335`, missing `path` becomes the literal string `"None"`; the host branch checks only `uid == 0`, after `opened` and string `sha256`, and appends that string to `host`. It does not require a path or verify host inode identity in the replay. The code's docstring at lines 308-311 claims every recorded mapping is a tree file or root-owned host file, which this entry does not establish.

Minimal reproduction (run from `/fast/scratch/hyaku/kama-r53/V1Review`):

```sh
python3 -c 'import importlib.util,tarfile,tempfile,os,json; p="lane/tools/kama-live-replay.py"; s=importlib.util.spec_from_file_location("r",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); a="a.tar"; t=tarfile.open(a,"w"); import io; x=tarfile.TarInfo("libx.so"); x.size=1; t.addfile(x,io.BytesIO(b"x")); t.close(); cm={"read":True,"mappings":[{"opened":True,"sha256":"0"*64,"uid":0},{"path":os.path.abspath("tree/libx.so"),"opened":True,"sha256":__import__("hashlib").sha256(b"x").hexdigest(),"uid":1}]}; print(json.dumps(m.verify_code(cm,a,"tree"),sort_keys=True))'
```

Output: `{"host": ["None"], "members": {"libx.so": "2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881"}, "verified": true}` and no mismatches. Thus the malformed entry is included in a successful `own_code` result despite not naming any file.

Proposed fix: reject entries unless `path` is a nonempty string (before string coercion / path classification); require the host path to be absolute and retain whatever host identity checks are part of the claim. Add a selftest case with a root-UID mapping lacking `path`, expecting replay failure.

## Other scoped checks

- `member_digests` (lines 290-302) compares exact tar member names and includes only regular members. A `./`-prefixed archive name will not match the normalized relative path requested by `verify_code`; it consequently fails as `not-a-member` rather than being accepted incorrectly. Duplicate regular members overwrite in archive iteration order (last digest wins); extraction behavior and the live path's digest must still agree for acceptance. Hardlinks and symlinks are not regular members and do not supply a digest; they cannot directly satisfy the member check.
- `verify_code` checks unreadable/hashless entries before path class, then verifies archive members by stream digest and allows root-owned paths outside the tree. A string UID (`"0"`) is rejected as foreign, consistent with the generated live receipt's integer UID; malformed non-dict list members are silently filtered rather than rejected, so completeness of a purported mappings list is not enforced. This is a second manifestation of permissive malformed-input handling, but the missing-path case above is the minimal demonstrated acceptance.
- The selftest fake tar extracts a `build/bin` tree and the fake live script locates `libfake.so` relative to the extracted executable, exercising the real relative tree layout. It covers absent, digest mismatch, foreign, non-member, unopened, and no-library conditions, but not missing-path entries, `./` member names, duplicate names, symlink, or hardlink members.
- No counter, network-dependent replay, or full selftest was run. No edits were made to lane files or counters.