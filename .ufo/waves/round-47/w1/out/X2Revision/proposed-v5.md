# Proposed v5 model provenance (NOT applied — advisory for round 48)

Frozen files (`tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, the round-47
counters) are untouched. Everything below is a proposal keyed to the current text.

## The gap

`provenance.model.url` is recorded verbatim (tools/kama-llamacpp-live.py:1385) and the
round-47 receipts record `https://huggingface.co/ggml-org/models-moved/resolve/main/...`
(.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json:394). `main` is a moving ref: on this
path it served three byte strings (`047bf464…` at 688f41dd, `68c694e7…` at 22027b1a,
`270cba1b…` at 96f460f9 and later). The sha256 guard is sound — a moved ref is refused
before extraction — but a moved ref turns a replay into a refusal (exit 2) instead of a
reproduction, and the receipt does not say which revision it meant.

Measured today: pinned URL -> replay match=True exit 0 (3/3 receipts, 11/11 checks); the
same receipt with the URL pointed at 22027b1a -> `digest-mismatch` exit 2.

## Change 1 — tools/kama-llamacpp-live.py (schema kama-llamacpp-live/v5)

Require the recorded URL to be revision-pinned and derive the commit from it. Insert after
the digest validation loop (currently tools/kama-llamacpp-live.py:1362-1367):

```python
    model_commit = None
    if args.model_url:
        m = re.search(r'/resolve/([0-9a-f]{40})(?:/|$)', args.model_url)
        if not m:
            parser.error('--model-url must be a revision-pinned hub URL '
                         '(.../resolve/<40-hex-commit>/<path>), not a branch ref')
        model_commit = m.group(1)
```

and at the provenance block (currently line 1385):

```python
            'model': {'url': args.model_url, 'sha256': args.model_sha256,
                      'commit': model_commit},
```

Contract text for the docstring (line 20 area): v5 adds
`provenance.model.commit` (40 lowercase hex, derived from the `/resolve/<commit>/` segment
of `provenance.model.url`); the tool exits 2 at setup when the model URL is not pinned.
`--selftest` receipts use a `file://` URL, so the check is applied only when
`--model-url` starts with `https://`; the selftest asserts the two refusal cases
(branch-URL -> exit 2, pinned-URL -> commit recorded).

## Change 2 — tools/kama-live-replay.py (accepts v5, still reads v4)

In `provenance()` (tools/kama-live-replay.py:68-83), after the digest equality check:

```python
    commit = mdl.get("commit")
    if rec.get("schema") == "kama-llamacpp-live/v5":
        if not (isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit)):
            raise Refused("provenance-bad-commit")
        if f"/resolve/{commit}/" not in need["model.url"]:
            raise Refused("provenance-url-revision-differs-from-commit")
```

`LIVE_SCHEMA` becomes a set `{"kama-llamacpp-live/v4", "kama-llamacpp-live/v5"}` and
`compare()` compares `provenance.model.commit` when both sides have one. Offline selftest
adds: missing commit, short commit, URL-revision/commit mismatch (each exit 2 with the
named reason). No network is needed for any of these.

## Change 3 — one-line SOURCES anchor

See `SOURCES-anchor.md` in this directory; S039 (corpus/SOURCES.md:51) already carries the
same identity, so either append `; deliverable URL: <pinned>` to its anchor cell or add the
new S488 row.

## Why derive instead of a `--model-commit` flag

One source of truth: a flag can disagree with the URL; the `/resolve/<commit>/` segment
cannot. It also keeps the caller's argv unchanged apart from the URL they already pass, and
the refusal is deterministic and offline (no HEAD request, no new network dependency in the
live tool).
