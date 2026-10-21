VERDICT: confirm - Registry row, round-18 cite token, and pinned blob SHA-256 match exactly.

- `registry/required-citations.json:52-56`: `id` is `r18-falsify-validation`; `rev` is `101f3991d3570bc9350fbf9c5561f4be1185699d`; `path` is `.ufo/waves/round-18/falsify/validation.json`; `sha256` is `5644346ed0d9b543e1934b4ee32cf7c287bd12d0aed67594bf1201f9e4cbcf5c`; `doc` is `corpus/lessons/round-18.md`.
- `corpus/lessons/round-18.md:463` has the matching token: `cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/falsify/validation.json, sha256=5644346ed0d9b543e1934b4ee32cf7c287bd12d0aed67594bf1201f9e4cbcf5c)`. Its revision, path, and digest agree with the registry, and it is in the registry-bound document.
- From the repository root, `git show 101f3991d3570bc9350fbf9c5561f4be1185699d:.ufo/waves/round-18/falsify/validation.json | sha256sum` returned `5644346ed0d9b543e1934b4ee32cf7c287bd12d0aed67594bf1201f9e4cbcf5c`, exactly the registered/token digest.

No mismatch observed. Registry and document were not modified.