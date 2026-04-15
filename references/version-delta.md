# Version Delta

Use exact shipped libc whenever possible. Use this file to avoid applying an old heap habit to the wrong version.

## Distro anchors

- Ubuntu 16.04: glibc `2.23`
- Ubuntu 18.04: glibc `2.27`
- Ubuntu 20.04: glibc `2.31`
- Ubuntu 22.04: glibc `2.34`
- Ubuntu 24.04: glibc `2.39`

## Breakpoints

| Version window | What changes | Solver impact |
| --- | --- | --- |
| `2.23` | No tcache | Lean on classic fastbin, unsorted, unlink, overlap, and hook-era endgames. |
| `2.26` / `2.27` | Tcache appears | Re-check every old pre-tcache habit before copying a classic writeup. |
| Late `2.27+` | Tcache key checks appear in many targets | Do not assume direct tcache double free; plan to break key, change size class, or pivot through fastbin or overlap. |
| `2.29+` | Stronger `prev_size` and consolidation checks | Modern off-by-null, unlink, and einherjar flows need extra fake-chunk scaffolding. |
| `2.31+` | `counts[]` becomes `uint16_t`; `tcache_get` expects `count[idx] > 0` | Preserve or repair counts when poisoning metadata or faking a tcache entry. |
| `2.32+` | Safe-linking | Recover heap addresses, decode protected pointers, double-protect, or attack metadata instead of using raw `fd` writes. |
| `2.32+` | `tcache_get` clears `key` on pop | Expect `bk`-adjacent data to be clobbered when a poisoned tcache chunk is returned. |
| `2.34+` | `tcache_key` becomes randomized; malloc hooks are gone | Stop planning around heap-leak-via-key and stop defaulting to `__free_hook` or `__malloc_hook`. |
| `<= 2.35` | Local notes keep `__malloc_assert -> fflush(stderr)` alive | `house of kiwi` can still matter as a trigger surface. |
| `2.36+` | Local notes treat `fflush(stderr)` from `__malloc_assert` as gone | Do not assume `kiwi` triggerability without checking the shipped libc. |
| `2.37+` | Local notes treat classic `__malloc_assert` path as gone | Treat classic `kiwi` as dead unless the target ships an older patched build. |
| `2.39` | Local notes track newer stdout and IO_FILE layouts | Re-derive offsets for `apple`, `cat`, `snake`, and related IO routes instead of copying old offsets. |
| `2.42` | Local notes treat tcache semantics as changed again; `tcache_perthread_struct` may no longer sit at the heap top | Verify exact minor behavior before relying on a 2.42-only poisoning shortcut, and re-check whether `tcache_metadata_hijacking` or other metadata-side paths replaced older heap-top assumptions. Do not treat `2.42` alone as a hard `poison_null_byte` boundary unless the maintained example also breaks. |
| `2.43` | Maintained `how2heap` examples drop fastbin dup family; maintained `poison_null_byte` adds a tcache-metadata warmup before padding | If a plan depends on `fastbin_dup*`, verify exact version and check whether a newer substitute exists. For leakless off-by-null overlap, re-check low-byte alignment and fake-chunk landing after the warmup before inventing a new family split. |

## Endgame defaults by era

- `< 2.34`: Hooks may still exist, but only use them if the binary gives the right trigger.
- `2.34+`: Prefer FSOP, exit-linked targets, or ROP/context pivots.
- Modern IO: Prefer stable `apple2`-style execution routes before more brittle `cat` or `emma` variants.
