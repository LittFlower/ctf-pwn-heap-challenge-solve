# Primitive to Technique Map

## Quick filters

- Unknown libc version: recover it before picking a technique.
- No heap leak on `2.32+`: avoid plain `tcache_poisoning` unless you also have metadata-side control, pointer recovery, or a safe-linking bypass.
- No direct `free`: prioritize top chunk or `sysmalloc`-style paths.
- Only null-byte off-by-one: start with `poison_null_byte` or `house_of_einherjar`.
- Only fake free on attacker-controlled memory: start with `house_of_spirit` or `tcache_house_of_spirit`.
- `calloc` reachable: consider `fastbin_reverse_into_tcache`.
- One-shot `show`: prefer single-chunk unsorted or large-bin leaks, or stdout-based leak plans.
- Need code execution more than allocator novelty: open `references/leak-and-endgame-map.md` early.

## Mapping table

| Observed primitive | Best first candidates | Typical version window | Hidden conditions that usually decide it |
| --- | --- | --- | --- |
| Stale slot points to freed heap struct containing data pointer plus callback, vtable, or function pointer | Same-size tcache or fastbin reuse to overwrite the stale struct, then trigger the existing call site | Broad; easiest with tcache `2.26+`, no safe-linking issue if not poisoning `fd` | Need allocation order that returns the freed struct as writable user content, a valid call target such as PLT or a leaked libc address, and a later action that calls through the stale field. |
| UAF on freed tcache chunk plus heap leak | `tcache_poisoning`, `safe_link_double_protect` | `2.26+`, especially `2.32+` | Need correct protected-next calculation once safe-linking exists. |
| UAF on freed tcache chunk without heap leak | `house_of_water`, `tcache_metadata_poisoning`, `tcache_relative_write` | Mostly `2.32+` | Need metadata reach, offset writes, or a tolerable brute-force budget. |
| Need tcache double free but key checks block it | `house_of_botcake`, `house_of_kauri`, `tcache stash with fastbin double free` | Late `2.27+` | Need stale pointer, size-class change, or the ability to fill and drain tcache. |
| Double free or freed-fd control in fastbin | `fastbin_dup`, `fastbin_dup_into_stack`, `fastbin_dup_consolidate` | `< 2.43` | Verify the family still exists in the target version directory. |
| Need fastbin write-back into tcache metadata | `fastbin_reverse_into_tcache` | Modern stash-enabled targets | `calloc` or a clean stash trigger makes this path easier. |
| Off-by-one null into next chunk size | `poison_null_byte`, modern off-by-null overlap, `house_of_einherjar` | Broad; `2.29+` needs extra scaffolding | Watch fake-size equality, 0x100 alignment, and unlink conditions. |
| Overflow into `prev_size` or `prev_inuse` | `unsafe_unlink`, `house_of_einherjar`, `overlapping_chunks` | Broad, but exact version matters | Works only if backward consolidation and fake-chunk checks can be satisfied. |
| Overflow or UAF on unsorted, large, or small bin metadata | `unsorted_bin_attack`, `large_bin_attack`, `house_of_lore`, `tcache_stashing_unlink_attack` | Version specific | Exact bin state, sort order, and `target+0x18` writability decide feasibility. |
| Can corrupt `bk_nextsize` after a chunk reaches large bin | Modern `large_bin_attack` | `2.30+`, especially newer libc | Usually needs a heap leak and a repair step before reusing the chunk. |
| Arbitrary free or fake free of attacker memory | `house_of_spirit`, `tcache_house_of_spirit` | Pre-tcache and tcache variants | Simplest route when the program frees attacker-controlled addresses or fake headers. |
| Heap overflow into tcache metadata area | `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, `house_of_water` | `2.26+`, with a new angle at `2.42+` | Good when direct safe-linking bypass is harder than reaching metadata. |
| Need leakless modern tcache control | `house_of_water`, `house_of_rust`, `safe_link_double_protect` | Mostly `2.32+` | Use only when simpler leak-based plans are blocked. |
| No `free`, but top chunk size or control exists | `house_of_tangerine`, `sysmalloc_int_free`, old `house_of_force` | Modern / pre-`2.29` | Require enough allocation volume and usually 0x1000 top-chunk alignment. |
| Need a modern FSOP finish after arbitrary write or large-bin control | `house of apple2`, `house of cat`, `house of emma` | Mostly `2.34+` | Choose by trigger surface, FILE-field control, and point-guard or stderr constraints. |

## Escalation path

- If the first candidate fails on a consistency check, identify the exact check and re-open the nearest same-name file in a newer version directory.
- If the challenge has both a leak and an overwrite, favor the chain that turns them into a stable allocator primitive first. Only then pivot into code execution.
- If the target libc is `2.34+`, expect malloc hooks to be gone. Plan an endgame that does not depend on them.
- If the challenge exposes only semantic operations such as `add`, `delete`, `edit`, and `show`, rewrite them into allocator transitions before reasoning about a technique.

## Typical solver order

1. Recover version and mitigations.
2. Recover what bin sizes are reachable from the menu.
3. Decide whether the bug gives leak, write, free, or overlap first.
4. Choose one candidate technique family.
5. Recreate the smallest possible versioned PoC.
6. Only after the PoC is stable, integrate the binary-specific control flow.
