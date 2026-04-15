# Primitive to Technique Map

Use this file when the observed bug or allocator primitive is already mostly clear and you need the shortest path from that fact pattern to a first candidate set.

If the source material is still dominated by noisy writeup labels, mixed cheatsheet wording, or corridor uncertainty, start with `how2heap-selector.md` first.

If you only need a static inventory of local `how2heap` families and the version breakpoints that shape them, open `how2heap-taxonomy.md` instead.

## Quick filters

- Unknown libc version: recover it before picking a technique.
- No heap leak on `2.32+`: avoid plain `tcache_poisoning` unless you also have metadata-side control, pointer recovery, or a safe-linking bypass.
- No direct `free`: prioritize top chunk or `sysmalloc`-style paths.
- Address leak path unclear: open `heap-address-leaks.md` before adding a second heap primitive just to chase bases.
- Fastbin / tcache family unclear: open `how2heap-freelist-primitives.md` before ranking `fastbin_dup*`, `tcache_poisoning`, `house_of_botcake`, or metadata-side routes such as `house_of_water`.
- Safe-linking handling unclear: open `how2heap-safe-linking.md` before forcing plain `tcache_poisoning` on `2.32+`.
- Unsorted / smallbin / largebin family unclear: open `how2heap-bin-attacks.md` then `how2heap-bin-write-primitives.md` before ranking `unsorted_bin_attack`, `house_of_lore`, `large_bin_attack`, `tcache stash unlink`, or other stash-assisted routes.
- Wilderness / arena family unclear: open `how2heap-wilderness-and-arena.md` before ranking `house_of_force`, `house_of_orange`, `house_of_tangerine`, `sysmalloc_int_free`, or fake-arena routes.
- Fake-free family unclear: open `how2heap-fake-free-primitives.md` before ranking `house_of_spirit` against `tcache_house_of_spirit`.
- Historical or community writeup label unclear: open `how2heap-legacy-writeup-labels.md` before trusting names such as `offbynull-heap`, `tcache_dup`, `house_of_io`, `house_of_roman`, or `house_of_storm`.
- Challenge says `offbynull-heap`: open `offbynull-heap.md` before turning the bug label into `poison_null_byte` or `house_of_einherjar`.
- No heap leak plus null-byte overlap goal: bias `poison_null_byte` before `house_of_einherjar`.
- Only null-byte off-by-one: start with `poison_null_byte` or `house_of_einherjar`.
- Null-byte or overlap family unclear: open `how2heap-overlap-nullbyte.md` before ranking `poison_null_byte`, `house_of_einherjar`, or the older overlap files.
- `calloc` reachable: consider `fastbin_reverse_into_tcache`.
- One-shot `show`: prefer single-chunk unsorted or large-bin leaks, or stdout-based leak plans.
- Need code execution more than allocator novelty: open `references/leak-and-endgame-map.md` early.

## Mapping table

| Observed primitive | Best first candidates | Typical version window | Hidden conditions that usually decide it |
| --- | --- | --- | --- |
| Stale slot points to freed heap struct containing data pointer plus callback, vtable, or function pointer | Same-size tcache or fastbin reuse to overwrite the stale struct, then trigger the existing call site | Broad; easiest with tcache `2.26+`, no safe-linking issue if not poisoning `fd` | Need allocation order that returns the freed struct as writable user content, a valid call target such as PLT or a leaked libc address, and a later action that calls through the stale field. |
| UAF on freed tcache chunk plus heap leak | `tcache_poisoning`, `safe_link_double_protect` | `2.26+`, especially `2.32+` | Need correct protected-next calculation once safe-linking exists. |
| Old `tcache_dup` writeup label or raw tcache double free in the obsolete window | `tcache_dup`, then `house_of_botcake` if the libc is newer | `2.26-2.28` for direct `tcache_dup` | Verify the target really predates the later double-free checks; otherwise translate the label into a modern bypass family instead of copying the old route. |
| UAF reaches the tcache management struct itself and the writeup says `house_of_io` or `tcache_perthread_struct` hijack | `house_of_io`, `house_of_water`, then modern metadata-control routes if the libc is newer | `2.31+`, with `house_of_io` concentrated on `2.31-2.33` | Treat the name as a tcache-metadata route, not as libio / FILE corruption despite the misleading label. Decide whether the first stable effect is direct metadata control, arbitrary return, or a later libc leak pivot. |
| UAF on freed tcache chunk without heap leak | `house_of_water`, `tcache_metadata_poisoning`, `tcache_relative_write` | Mostly `2.32+` | Need metadata reach, offset writes, or a tolerable brute-force budget. |
| Primitive is live, but in-band address recovery is still missing | `heap-address-leaks.md`, then the route's current primitive family | Broad | Decide whether heap, libc, PIE, or stack is the cheapest leak to recover first. |
| Protected-pointer handling is the real blocker on a modern freelist route | `how2heap-safe-linking.md`, then `decrypt_safe_linking`, `safe_link_double_protect`, or metadata-side routes | `2.32+` | Decide whether to recover the pointer, synthesize it, or avoid forging it through metadata control. |
| Need tcache double free but key checks block it | `house_of_botcake`, `house_of_kauri`, `tcache stash with fastbin double free` | Late `2.27+` | Need stale pointer, size-class change, or the ability to fill and drain tcache. |
| Double free or freed-fd control in fastbin | `fastbin_dup`, `fastbin_dup_into_stack`, `fastbin_dup_consolidate` | `< 2.43` | Verify the family still exists in the target version directory. |
| Need fastbin write-back into tcache metadata | `fastbin_reverse_into_tcache` | Modern stash-enabled targets | `calloc` or a clean stash trigger makes this path easier. |
| Historical leakless chain mixes fake fastbins, unsorted-bin attack, and relative overwrites | `house_of_roman` | `< 2.29`, especially old hook-era libc | Treat it as a bundled old chain with brute-force cost, not as a clean primitive family to copy into newer targets. |
| Fastbin / tcache / metadata freelist route still ambiguous | `how2heap-freelist-primitives.md`, then exact fastbin or tcache file | Broad | Decide whether the first proof target is duplicate return, chosen-pointer return, large-value write, or metadata control. |
| Unsorted / smallbin / largebin route still ambiguous | `how2heap-bin-attacks.md`, then `how2heap-bin-write-primitives.md`, then exact bin file | Broad | Use the repo-backed first cut before deciding whether the first proof target is a write, a chosen-pointer return, or stash-assisted mixed behavior. |
| Null-byte off-by-one, no heap leak, overlap first | `offbynull-heap.md`, then `poison_null_byte`, then `how2heap-overlap-nullbyte.md` | Broad; `2.29+` needs fake-chunk scaffolding, `2.43` may need warmup / alignment re-check | Need repaired residual `fd` / `bk`, fake `size == prev_size`, a consolidation free that bypasses tcache, and alignment that makes the partial-null repair land on the fake chunk. |
| Off-by-one null into next chunk size | `offbynull-heap.md`, then `poison_null_byte`, modern off-by-null overlap, or `house_of_einherjar` | Broad; `2.29+` needs extra scaffolding | Decide whether the first proof target is overlap only or a later chosen-pointer return; watch fake-size equality, 0x100 alignment, and unlink conditions. |
| Huge allocations are mmapped and overlap depends on corrupting mmap-chunk metadata before `munmap` | `how2heap-mmap-overlap.md`, then `mmap_overlapping_chunks` | Broad when the allocation crosses the mmap threshold | This is not ordinary unsorted-bin overlap; page alignment, `mmap_threshold`, and reclaiming unmapped space decide feasibility. |
| Overflow into `prev_size` or `prev_inuse` | `unsafe_unlink`, `house_of_einherjar`, `overlapping_chunks`, `overlapping_chunks_2` | Broad, but exact version matters | Works only if backward consolidation and fake-chunk checks can be satisfied. Use `how2heap-overlap-nullbyte.md` to split modern null-byte paths from historical overlap-first paths. |
| Overflow or UAF on unsorted, large, or small bin metadata | `unsorted_bin_attack`, `large_bin_attack`, `house_of_lore`, `tcache_stashing_unlink_attack` | Version specific | Exact bin state, sort order, `target+0x18` writability, and whether the writeup's `tcache stash unlink` wording is really describing stash-assisted writeback or a returned fake chunk decide feasibility. |
| Can corrupt `bk_nextsize` after a chunk reaches large bin | Modern `large_bin_attack` | `2.30+`, especially newer libc | Requires a post-free metadata write into the largebin-resident chunk, usually via UAF, overlap, or stale edit; usually also needs a heap leak and a repair step before reusing the chunk. |
| Arbitrary free or fake free of attacker memory | `how2heap-fake-free-primitives.md`, then `house_of_spirit` or `tcache_house_of_spirit` | Pre-tcache and tcache variants | Decide whether free reaches tcache directly, whether the tcache bin must be saturated first, and whether classic nextsize sanity is required. |
| Heap overflow into tcache metadata area | `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, `house_of_water` | `2.26+`, with a new angle at `2.42+` | Good when direct safe-linking bypass is harder than reaching metadata. |
| Need leakless modern tcache control | `house_of_water`, `house_of_rust`, `safe_link_double_protect` | Mostly `2.32+` | Use only when simpler leak-based plans are blocked. |
| No `free`, but top chunk size or control exists | `house_of_tangerine`, `sysmalloc_int_free`, old `house_of_force`, `house_of_orange` when the finish is stdio-facing | Modern / pre-`2.29` for the older houses | Require enough allocation volume, usually 0x1000 top-chunk alignment, and a real trigger surface if the route is drifting toward Orange-era IO pivoting instead of pure wilderness control. |
| Need fake non-main arena or arena-list control | `house_of_mind_fastbin`, `house_of_gods`, then `how2heap-wilderness-and-arena.md` | Mostly old libc | The first proof target is arena routing or `thread_arena` control, not ordinary returned-pointer reuse. |
| Need a modern FSOP or exit-linked finish after arbitrary write or large-bin control | `house of apple2`, `house of cat`, `house of emma`, `house of banana`, `house of kiwi` | Mostly `2.34+` | Choose by trigger surface, FILE-field control, whether `link_map` / fini-style surfaces are already reachable, and whether kiwi is only a trigger helper through the shipped-libc assert path rather than the finish itself. |

## Escalation path

- If the first candidate fails on a consistency check, identify the exact check and re-open the nearest same-name file in a newer version directory.
- If the challenge has both a leak and an overwrite, favor the chain that turns them into a stable allocator primitive first. Only then pivot into code execution.
- If the target libc is `2.34+`, expect malloc hooks to be gone. Plan an endgame that does not depend on them.
- If the challenge exposes only semantic operations such as `add`, `delete`, `edit`, and `show`, rewrite them into allocator transitions before reasoning about a technique.

## Typical solver order

1. Recover version and mitigations.
2. Recover what bin sizes are reachable from the menu.
3. Decide whether the bug gives leak, write, free, or overlap first.
4. Choose one candidate technique family. Use `how2heap-selector.md` for the first cut, then the specialized selector that matches the corridor: `how2heap-legacy-writeup-labels.md`, `heap-address-leaks.md`, `offbynull-heap.md`, `how2heap-overlap-nullbyte.md`, `how2heap-mmap-overlap.md`, `how2heap-fake-free-primitives.md`, `how2heap-freelist-primitives.md`, `how2heap-safe-linking.md`, `how2heap-bin-attacks.md`, `how2heap-bin-write-primitives.md`, or `how2heap-wilderness-and-arena.md`.
5. Recreate the smallest possible versioned PoC.
6. Only after the PoC is stable, integrate the binary-specific control flow.
