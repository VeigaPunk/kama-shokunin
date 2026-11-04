# Superseded — do not apply

These two files were the critic's F1/F2 correction against the census bytes `a82cad11…`
(tip `73597158`):

- `waived=` omitted unless a waiver was used (so a no-waiver verdict keeps
  `not_evaluated=<n> total=<t>` contiguous and the freeze's literal appears);
- the explanation line prefixed `CENSUS_EXIT` (exactly one `HOST_CENSUS`-prefixed line).

The wave integration at `af6eb6c2` (census `44bebd67…`) implements the same two changes
with the prefix `CENSUS_NOT_EVALUATED` and rewrites the `SKILL.md:1690` exit map. Applying
this patch on top would conflict and is unnecessary. Kept as the reasoning record only.
