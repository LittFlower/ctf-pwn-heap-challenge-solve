# Solver Benchmark Suite

Use this file when evaluating whether the skill actually routes real heap tasks well.

The goal is not to "solve many challenges" in one sitting. The goal is to measure whether the first-pass routing, proof-target selection, and finish selection are stable across common heap archetypes.

## What to measure

For each benchmark case, record:

- chosen first corridor
- first files opened after Always Read
- first proof target
- missing address classes written down or skipped
- whether the route stayed remotely viable

A routing change is good only if it reduces wrong turns without weakening proof obligations.

## Core benchmark set

Use at least 8 cases. Prefer one representative from each row.

| Archetype | Typical signals | Expected first corridor | Must-prove output |
| --- | --- | --- | --- |
| No-`free` wilderness | no delete, top-chunk overwrite, heap growth, `no free` notes | `how2heap-wilderness-and-arena.md` | Distinguish `sysmalloc_int_free` from a full `house_of_tangerine` bridge |
| Null-byte overlap | one-byte null, backward consolidation, `offbynull-heap`, `house_of_einherjar` notes | `offbynull-heap.md` + `how2heap-overlap-nullbyte.md` | Overlap-only vs chosen-pointer-return split |
| Freelist corruption | UAF, double free, freed `fd`, tcache-key issues | `how2heap-freelist-primitives.md` | Duplicate return vs chosen-pointer return vs metadata control |
| Safe-linking blocker | `2.32+`, protected next ptr, no raw heap leak | `how2heap-safe-linking.md` | Pointer recovery, synthesis, or metadata-side avoidance |
| Unsorted / largebin write | stale edit after free, `large bin attack`, unsorted wording | `how2heap-bin-attacks.md` + `how2heap-bin-write-primitives.md` | Prove post-free metadata mutation exists before naming the family |
| Live libio object | writable `FILE`, `_fileno`, stdout/stderr/stdin, `_codecvt`, wide stream | `libio-object-corruption.md` + `libio-stdio-primitives.md` | Name the exact later libc helper that consumes the corruption |
| Single useful leak | `single-shot show`, one read, one flush, partial stdout | `heap-address-leaks.md` | Pick the cheapest address class to recover first |
| Threaded ownership | worker thread frees or allocates the target chunk | `threaded-allocator-pitfalls.md` | Same-thread reuse or explicit cross-thread bridge |
| Direct stale-struct finish | freed object with callback, vtable, or function pointer | `solve-heap-challenge.md` first-pass + `leak-and-endgame-map.md` | Prove the direct call path beats heavier heap grooming |
| Local-only draft cleanup | exploit works only with `/proc`, debugger, or `io.libs()` | `leak-and-endgame-map.md` + `output-contract.md` | Replace each local-only base assumption with a target-derived step |

## Suggested local anchors

Use nearby public or local anchors only as route checks, not as exploit templates:

- `high frequency troubles` or local `house_of_tangerine.c` for no-`free` wilderness
- local `poison_null_byte.c` / `house_of_einherjar.c` for null-byte routing
- local `house_of_botcake.c`, `house_of_water.c`, `house_of_io.c` for freelist / metadata splits
- local `large_bin_attack.c`, `house_of_lore.c`, `tcache_stashing_unlink_attack.c` for bin routes
- any local note or challenge with writable `stdout`, `stdin`, `_fileno`, or `_codecvt`

## Pass / fail rubric

Mark a case as pass only if all are true:

- the first corridor matches the real primitive family
- no unnecessary second corridor was opened before the first proof target
- the first proof target is mechanical and version-aware
- remote-only blockers are stated explicitly instead of hidden behind local tooling

Mark as fail if any are true:

- the skill opened 3+ corridor references before naming one proof target
- it named a finish family before proving the allocator primitive
- it called a no-`free` route `house_of_tangerine` before proving the chosen-pointer bridge
- it defaulted to `/proc`, debugger memory, or `io.libs()` instead of naming the missing leak
- it treated a live `FILE` route as generic heap grooming for too long

## Regression discipline

Run this suite after:

- changing `SKILL.md` Common Tasks
- adding or renaming high-traffic references
- changing first-pass workflow questions
- adding a new family split that is supposed to save time on real solves

If two or more benchmark cases regress after a routing change, revert the routing idea or isolate it behind a narrower task entry instead of broadening the default path.
