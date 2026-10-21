# Evidence — git v2.56.0 `promisor-remote.c`, partialclonefilter-only promisor registration

Retrieved 2026-10-21 over official HTTPS only.

## Retrieval provenance

    curl -sS -o promisor-remote.c.v2.56.0 \
      https://raw.githubusercontent.com/git/git/v2.56.0/promisor-remote.c

- HTTP 200, content-length 36203
- sha256 `175e67e1b2cc62db1ead26007ba1e5502f9b585fd33dbc45b59f9876b34f9bca`
- `git hash-object -t blob promisor-remote.c.v2.56.0` = `43505d1e1ac8fd48cf185169ea76d92dc277ef01`
- GitHub contents API for `promisor-remote.c?ref=v2.56.0` reports the same blob sha `43505d1e1ac8fd48cf185169ea76d92dc277ef01` and size 36203.
- Annotated tag object: `https://api.github.com/repos/git/git/git/refs/tags/v2.56.0` → tag object `2478544319491bbd2a42cc57a83e3d2f4730a280`; dereferenced tag → tag `v2.56.0`, commit `a018953688f1b10bddf91bff8747068f5f4746a4`.
- Host `git --version` = `git version 2.56.0`.

## Anchor

File: `promisor-remote.c` at tag `v2.56.0`.
Function: `static int promisor_remote_config(const char *var, const char *value, const struct config_context *ctx UNUSED, void *data)`.
Lines 148–163 for the `partialclonefilter` branch; lines 152–154 for the quote.

Raw URL: https://raw.githubusercontent.com/git/git/v2.56.0/promisor-remote.c
Rendered anchor: https://github.com/git/git/blob/v2.56.0/promisor-remote.c#L148-L163

Exact quoted source (11 words, lines 152–154; indentation/newline normalized only):

    r = promisor_remote_lookup(config, remote_name, NULL);
    if (!r)
        r = promisor_remote_new(config, remote_name);

Full branch as fetched (line-numbered):

    148  if (!strcmp(subkey, "partialclonefilter")) {
    149      struct promisor_remote *r;
    150      char *remote_name = xmemdupz(name, namelen);
    151
    152      r = promisor_remote_lookup(config, remote_name, NULL);
    153      if (!r)
    154          r = promisor_remote_new(config, remote_name);
    155
    156      free(remote_name);
    157
    158      if (!r)
    159          return 0;
    160
    161      FREE_AND_NULL(r->partial_clone_filter);
    162      return git_config_string(&r->partial_clone_filter, var, value);
    163  }

Contrasting `promisor` branch (lines 134–147): `if (!git_config_bool(var, value)) return 0;` before creation — a false/missing boolean records nothing by that branch. Nothing in the `partialclonefilter` branch consults `remote.<name>.promisor`.

## Adjacent source facts (same file, cited separately)

- `promisor_remote_init()` runs `repo_config(r, promisor_remote_config, config)` at line 178; the registration is lazy, not load-time.
- `repo_has_promisor_remote()` lines 224–227 returns true for any registered entry, including one created only by `partialclonefilter`.
- `promisor_remote_get_direct()` line 310 calls `promisor_remote_init(repo)` before fetching.
- `fetch_objects()` lines 34–41 checks `NO_LAZY_FETCH_ENVIRONMENT` and returns -1 with `warning(_("lazy fetching disabled; some objects may not be available"))` before forking any fetch.
- `promisor_remote_new()` lines 75–82 refuses a remote name beginning with `/` (warning, returns NULL), so that edge config registers nothing.
- `repository_format_partial_clone` is only read at lines 180–190; this file does not set it.

## Files

- `promisor-remote.c.v2.56.0` — exact fetched bytes.
- `excerpt-config-callback.txt` — `nl -ba` excerpt lines 122–180.
- `SOURCES-candidate-row.md` — proposed registry row; registry NOT edited.

## Adjacent fetched files (official raw, same tag, 2026-10-21)

    https://raw.githubusercontent.com/git/git/v2.56.0/packfile.c   (58979 bytes)
    https://raw.githubusercontent.com/git/git/v2.56.0/setup.c      (83214 bytes)

- `is_promisor_object` is defined in `packfile.c:2061`, not `promisor-remote.c`;
  it calls `repo_has_promisor_remote(r)` at `packfile.c:2067` and then walks
  `ODB_FOR_EACH_OBJECT_PROMISOR_ONLY` (`packfile.c:2073-2074`).
- `extensions.partialclone` is parsed in `setup.c:622-626` and stored into
  `repo->repository_format_partial_clone` at `setup.c:1813-1814`;
  `promisor-remote.c` only reads that field, lines 180-190.
