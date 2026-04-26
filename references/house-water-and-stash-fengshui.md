# House of Water and Stash Fengshui

Use this file when a route mentions `house_of_water`, `tcache stash unlink`,
`tcache stash unlink+`, or `tcache stash unlink++` and the blocker is heap layout
rather than the high-level technique name.

These families are easy to misroute because the same smallbin-to-tcache motion can
prove different outcomes:

- `tcache stash unlink`: allocator-managed libc write.
- `tcache stash unlink+`: fake chunk enters tcache and is returned by a later malloc.
- `tcache stash unlink++`: fake chunk return plus a libc write through the fake chunk's `bk`.
- `house_of_water`: leakless or low-leak tcache metadata control by turning tcache metadata into a smallbin node.

## Source Anchors

- Local how2heap: `glibc_2.27` and `glibc_2.31-2.40/tcache_stashing_unlink_attack.c`.
- Local how2heap: `glibc_2.32-2.43/house_of_water.c`.
- Upstream how2heap `house_of_water.c`: https://github.com/shellphish/how2heap/blob/master/glibc_2.36/house_of_water.c
- Corgi's House of Water article: https://corgi.rip/posts/leakless_heap_1/
- Technique survey for House of Rust/Water context: https://0x434b.dev/overview-of-glibc-heap-exploitation-techniques/

Treat these as behavior anchors. Rebuild the exact invariant table on the shipped
libc before using old offsets.

Local coverage note: the maintained local tree stops shipping
`tcache_stashing_unlink_attack.c` after `glibc_2.40`. Treat `2.41+` TSU plans as
needs-revalidation rather than assuming the older layout survived unchanged.

## Stash Unlink Core

`tcache_stashing_unlink_attack` is consumed during smallbin allocation, especially
through `calloc` or a malloc path that moves same-size smallbin chunks into tcache.

Common preconditions:

- A real smallbin-sized allocation class can be filled past tcache.
- At least one same-size chunk is already in smallbin and its `bk` is writable after free.
- The request that triggers the route avoids serving directly from tcache first, or tcache has been drained to the intended count.
- The target used as fake `bk` passes the unlink side effect: the location reached by `bck->fd = bin` is writable.
- For fake chunk return variants, the fake target is aligned and later allocation count actually reaches the staged tcache node.

Do not call it plain `house_of_lore`. The useful side effect is not only a smallbin
return; stash movement also writes through `bk` and links extra nodes into tcache.

## Stash Count Algebra

Let `T` be the number of chunks already in the target tcache bin immediately before
the triggering allocation, and let the vulnerable smallbin chain be counted from the
tail, because smallbin returns the oldest chunk first.

Use this checklist:

| Variant | Count rule | Corrupt | First stable result |
| --- | --- | --- | --- |
| `tcache stash unlink` | `T + position = 8` | `bk = write_target - 0x10` | `write_target` receives a libc/bin pointer through `bck->fd = bin` |
| `tcache stash unlink+` | `T + position = 7` | `bk = fake_chunk - 0x10` | fake chunk is linked into tcache and returned by a later same-size malloc |
| `tcache stash unlink++` | same as plus | `bk = fake_chunk - 0x10`, and `fake_chunk+0x8 = write_target - 0x10` | fake chunk return plus libc/bin pointer write to `write_target` |

Practical translation:

- If tcache is empty, the plain write variant usually corrupts the 8th smallbin node from the tail.
- If tcache is empty, plus and plus-plus usually corrupt the 7th smallbin node from the tail.
- If tcache already has entries, subtract that count from the position you corrupt.
- Keep at least two smallbin chunks when you need both a returned real chunk and a stashed fake target.

When the target write lands at `addr+0x10` in a writeup, normalize whether `addr`
means the fake `bk` pointer or the logical target address. In allocator terms the
side effect is `bck->fd = bin`.

## Stash Fengshui Template

A stable challenge plan usually needs this shape:

1. Allocate same-size chunks with guard chunks between any chunks that must stay separate.
2. Fill the target tcache bin or leave it with the exact count required by the variant.
3. Free the remaining same-size chunks out of tcache so they first enter unsorted.
4. Allocate a larger chunk to sort unsorted chunks into the smallbin for that size.
5. Drain tcache to the planned count.
6. Use UAF, overlap, or stale edit to overwrite the selected smallbin victim's `bk`.
7. Trigger stash movement with `calloc` or an equivalent allocation path.
8. For plus variants, allocate again until the fake chunk is returned.

Guard chunks matter because adjacent same-size frees can consolidate before they ever
become independent smallbin nodes.

## House of Water Core

Modern `house_of_water` converts a UAF or overlap into tcache metadata control without
requiring a direct heap leak. The maintained smallbin variant does this by making a
tcache metadata region behave as a fake smallbin chunk.

The recurring geometry is:

- Place a `relative_chunk` immediately after or near the tcache metadata area so its page/nibble relation matches the fake metadata target.
- Prepare `small_start`, `relative_chunk`, and `small_end` as same-size smallbin chunks, separated by guards.
- Create two larger tcache entries whose stored pointers overlap the headers or link fields of `small_start` and `small_end`.
- Free `small_end`, `relative_chunk`, and `small_start`, then sort them into one smallbin list.
- Partially overwrite `small_start->fd` and `small_end->bk` so the middle smallbin node becomes the fake chunk inside `tcache_perthread_struct`.
- Drain the same-size tcache bin, allocate through `small_start` and `small_end`, then receive a chunk overlapping tcache metadata.

The first proof target is not code execution. It is a returned allocation overlapping
`tcache_perthread_struct`, after which counts, entries, leak placement, or a later
safe-linking-aware route becomes the next stage.

## House of Water Version Notes

Local how2heap has three important shape groups:

| Version window | Maintained shape |
| --- | --- |
| `2.32-2.41` | Base smallbin variant. The examples use the `0x320` and `0x330` tcache bins as fake link helpers and return metadata near `metadata+0x210`. |
| `2.42` | `tcache_perthread_struct` size and placement changed. The example first misaligns metadata with a large allocation, uses `0x310` and `0x320` helper bins, and returns metadata near `metadata+0x280`. |
| `2.43` | The maintained example changes the warmup again: it uses `free(malloc(0x1e0))`, primes more `0x90` tcache entries, and redirects to a different page offset before returning metadata near `metadata+0x280`. |

Do not port `2.32-2.41` offsets into `2.42+`. Recompute:

- actual `tcache_perthread_struct` base and size
- page offset shared by the relative chunk and fake metadata node
- helper tcache-bin sizes used to create fake `fd` and `bk`
- number of same-size chunks needed to drain before smallbin servicing

## House of Water Proof Table

Before coding, write this invariant table:

| Field | Required value | Written by | Consumed by |
| --- | --- | --- | --- |
| `small_start->fd` | fake metadata smallbin node | UAF, overlap, or partial overwrite | smallbin unlink/stash walk |
| `small_end->bk` | same fake metadata smallbin node | UAF, overlap, or partial overwrite | smallbin unlink/stash walk |
| helper tcache entry A | pointer overlapping `small_start` link/header role | fake free or metadata staging | metadata-as-link construction |
| helper tcache entry B | pointer overlapping `small_end` link/header role | fake free or metadata staging | metadata-as-link construction |
| target tcache count | drained enough to force smallbin servicing | frees and allocations | final same-size malloc |

Reject the route if two roles require the same bytes to hold incompatible values.

## Routing Rules

- Use stash unlink when the direct primitive is `smallbin victim->bk` control and the goal is a libc write, fake return, or both.
- Use `house_of_water` when the direct primitive can arrange fake tcache metadata and the goal is leakless metadata control rather than a one-shot smallbin write.
- If the writeup says `TSU+` inside a larger chain such as House of Rust, classify only that step as stash-assisted fake return; the larger chain may still need largebin repair or stdout/FILE work.
- If the route relies on safe-linking bypass but never obtains a heap leak, prefer `house_of_water` or `safe_link_double_protect` over raw tcache poisoning.
- If the plan only writes a libc pointer but never returns or reads a useful object, report it as a setup primitive, not a complete leak or endgame.

## Common Failure Checks

- Wrong smallbin position: recompute from the tail and include the current tcache count.
- Tcache not drained: allocation returns a tcache chunk before smallbin stash ever runs.
- Missing `calloc` or equivalent path: the challenge's allocation path may not trigger the expected stash motion.
- Unwritable `bck->fd`: plus and plus-plus need the fake `bk` chain to survive the allocator write.
- Consolidation: missing guard chunks merge would-be smallbin nodes.
- `2.42+` House of Water offset drift: metadata base, helper size classes, and drain count must be version-specific.
