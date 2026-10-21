# Boundary excerpt — correct authority for `<name>.promisor` files

URL: https://git-scm.com/docs/partial-clone#_design_details
Access date: 2026-10-21
HTTP: 200, 51,719 bytes, sha256 8a6493225f76dba8e5b1eb75234f7370e057ee87c11e07a2681dbf522b16c9ad
Section id: `_design_details` (not `_handling_missing_objects`, which is S099's anchor)

Verbatim (normalized whitespace, 23 words):

> These promisor packfiles consist of a "<name>.promisor" file with arbitrary
> contents (like the "<name>.keep" files), in addition to their "<name>.pack"
> and "<name>.idx" files.

Surrounding context, same section:

> To differentiate these cases, the local repository specially indicates such
> filtered packfiles obtained from promisor remotes as "promisor packfiles".

Purpose: record that `objects/pack/<name>.promisor` is defined by
partial-clone §Design Details, not by gitrepository-layout(5). This file is a
boundary note only; no registry row is proposed from it by this seat.
