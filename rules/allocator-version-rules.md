# Allocator Version Rules

These rules cover glibc-version facts that must be resolved before choosing a technique or finish.

## Version first

- Identify the exact libc when possible from shipped files, loader-libc pairs, symbols, Docker image metadata, or package hints.
- If the exact version is unclear, keep a short candidate set. Do not guess.
- Read `references/version-delta.md` before committing to any technique family with version-sensitive behavior.

## Version-sensitive constraints

- Treat tcache presence, safe-linking, bin-count rules, and consolidation behavior as first-class constraints.
- Record whether late-2.27+ key checks, 2.31 count behavior, and safe-linking alter the intended route.
- Treat tcache ownership as thread-local allocator state. If helper threads call `malloc` or `free`, record which thread owns the freed chunk before planning same-size reuse or poisoning.
- Treat hook availability as a compatibility fact, not a default finish.
- Prefer modern FILE, stdout or stderr recovery, or exit-linked routes when hook-based finishes are no longer sound.

## how2heap mapping

- Check the exact `glibc_<version>/technique.c` example first.
- If the exact file is missing, compare the nearest older and newer versions and identify the allocator rule that changed.
- Treat technique absence in local `how2heap` as a warning that the pattern may no longer be sound for that version.
- Copy invariants and version constraints from `how2heap`, not old prose or outdated writeups.
- For off-by-null overlap, distinguish an official family breakpoint from a local layout breakpoint. A custom leakless geometry may fail on a newer libc because padding, heap-top placement, or tcache-metadata warmup changed even when the maintained `poison_null_byte` example still works.

## Route-selection rules

- If there is no direct `free`, prioritize top-chunk or `sysmalloc` paths before overfitting to bin attacks.
- If `calloc` is reachable, consider stash-dependent routes that benefit from zeroing or stash movement.
- If there is no heap leak on `2.32+`, avoid plain `tcache_poisoning` unless safe-linking can be decoded or bypassed.
- If a target uses worker threads, do not assume a freed chunk is reusable from the main thread just because a stale alias exists. Plan same-thread reuse, a main-thread re-free, or a route that forces the chunk out of that thread's tcache first.
- If the hard part is the finish rather than the first primitive, route early through `references/leak-and-endgame-map.md`.
- Once the heap phase yields overlap, arbitrary allocation, leak, or arbitrary write, pivot into the binary-specific finish instead of extending heap grooming for its own sake.
