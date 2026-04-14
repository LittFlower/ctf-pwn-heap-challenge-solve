# how2heap Freelist Primitives

Use this file when the candidate set clusters around fastbin, tcache, or tcache-metadata abuse and the main question is which freelist primitive the challenge actually proves first.

If the source material is still speaking in old labels such as `tcache_dup` or `house_of_io`, open `how2heap-legacy-writeup-labels.md` first, then return here for the corridor-specific split.

If the notes say `tcache dup`, treat that wording as the same obsolete duplicate-return label as `tcache_dup` and verify the libc window before trusting it literally.

If the writeup or notes say `house_of_kauri` or describe a stash-assisted fastbin-to-tcache double free, keep the route in this corridor first even though the maintained local tree does not ship those names as direct files.

If the notes say `house_of_atum`, treat that wording as a fastbin-to-tcache writeback route whose first useful effect is usually metadata reach near `chunk-0x10`, not plain chosen-pointer return.

If the notes say `tcache_perthread_struct` hijack or `tcache_perthread_struct劫持`, treat that wording as a metadata-control route first, then split it into `house_of_io`, `house_of_water`, `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, or `tcache_relative_write`.

If the notes use spaced forms such as `house of botcake`, `house of water`, or `house of io`, treat them as the same freelist families described here and keep the split focused on key-check bypass versus metadata-side control.

If the notes say `fastbin reverse into tcache`, treat that wording as the same fastbin-to-tcache writeback route described here and keep the split focused on allocator-managed metadata writes rather than chosen-pointer return.

## The split that matters

Do not group all of these together as "tcache poisoning":

- `fastbin_dup`
- `fastbin_dup_into_stack`
- `fastbin_dup_consolidate`
- `tcache_dup`
- `tcache_poisoning`
- `house_of_botcake`
- `fastbin_reverse_into_tcache`
- `house_of_io`
- `house_of_water`
- `tcache_metadata_poisoning`
- `tcache_metadata_hijacking`
- `tcache_relative_write`

The right split is based on the first stable allocator outcome: duplicate return, chosen-pointer return, large-value write, or metadata control.

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors or version cues for this corridor:

- `fastbin_dup_into_stack`: `9447 search-engine`, `0ctf 2017 babyheap`
- `house_of_water`: `37c3 Potluck Tamagoyaki`
- `house_of_botcake`: described as the route that makes `tcache_dup` work again on newer libc
- `tcache_dup`: obsolete `2.26-2.28` example in the local tree
- `house_of_io`: local example exists for `2.31-2.33`, but the README table gives no challenge anchor

Treat those as routing anchors, not as permission to reuse the old exploit shape unchanged.

## Family map

### Fastbin duplication family

Use `fastbin_dup` / `fastbin_dup_into_stack` / `fastbin_dup_consolidate` when:
- the primitive is true double free or freed-`fd` control in a fastbin-sized chunk
- the first proof target is duplicate reuse or near-arbitrary return
- the version is still old enough that the family exists locally

Split them by first proof target:
- duplicate live pointer -> `fastbin_dup`
- nearly arbitrary pointer / stack-like target -> `fastbin_dup_into_stack`
- duplicate return via top-chunk interplay -> `fastbin_dup_consolidate`

### Plain tcache poisoning

Use `tcache_poisoning` when:
- you control a freed tcache entry's `next`
- the first proof target is a chosen-pointer return
- on `2.32+`, a heap leak or valid protected-pointer computation is available

### Historical `tcache_dup`

Use `tcache_dup` when:
- the target is the old `2.26-2.28` window where the obsolete example still applies
- the first proof target is duplicate return from a tcache double free, not a modern key-check bypass
- the writeup or exploit notes are clearly inheriting an old `tcache_dup` label

Treat this as the historical ancestor of later tcache double-free routes. On newer libc, the same intent usually reappears as `house_of_botcake` or another bypass rather than raw `tcache_dup`.

### Double-free-bypass tcache routes

Use `house_of_botcake` when:
- the route wants tcache poisoning
- but direct double free is blocked by key checks
- and overlap, consolidation, or stale reuse can reinsert the victim into tcache

The first proof target is usually "victim can be freed into tcache again without tripping the key check," not the final poisoned return.

Use `house_of_kauri` when:
- a stale pointer can be freed twice only because the chunk size class is changed between the two frees
- the first proof target is "one physical chunk lands in two different tcache entries" rather than immediate chosen-pointer return
- the route is really a size-class-change bypass for the tcache key check

Use stash-assisted fastbin-to-tcache double-free notes when:
- the matching tcache bin can be filled first
- a fastbin-sized chunk can still be double-freed underneath that full tcache bin
- later stash or refill behavior converts the fastbin duplicate into a tcache-side chosen-pointer route

Treat both as bypass shapes inside the same branch:
- size-class change / stale pointer reuse -> `house_of_kauri`
- fill tcache, double-free in fastbin, then restage through stash/refill -> stash-assisted fastbin-to-tcache path
- overlap or consolidation that reinserts the victim into tcache -> `house_of_botcake`

### Fastbin-to-tcache writeback

Use `fastbin_reverse_into_tcache` when:
- a freed fastbin chunk's `fd` is writable
- the first proof target is not a returned pointer but a large allocator-managed value written into a target slot
- later tcache refill behavior is part of the exploit surface

This is closer to an allocator-side write primitive than to classic pointer-return poisoning.

Use `house_of_atum` when:
- the writeup frames the goal as reaching `chunk-0x10` or directly rewriting `prev_size` / `size`
- the real engine is still fastbin-to-tcache restaging rather than a standalone overlap family
- the target libc sits in the older tcache window where `entries[idx]` / `count[idx]` behavior still makes that metadata reach practical

Treat it as an alias route inside the same branch: `house_of_atum` names the metadata-reach outcome, while `fastbin_reverse_into_tcache` names the allocator motion that makes it happen.

### Leakless metadata-side control

Use `house_of_io`, `house_of_water`, `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, or `tcache_relative_write` when:
- raw freelist poisoning is blocked or leakless operation matters more than a simple chosen-pointer return
- the real exploit surface is `tcache_perthread_struct` or tcache-derived metadata writes

Split them by what you control first:
- historical UAF into the tcache management struct itself on `2.31-2.33` -> `house_of_io`
- metadata takeover through overlap / fake metadata staging -> `house_of_water`
- direct overwrite into `tcache_perthread_struct` -> `tcache_metadata_poisoning`
- post-`2.42` overflow into later-initialized tcache metadata -> `tcache_metadata_hijacking`
- out-of-range `tc_idx` style relative write foundation -> `tcache_relative_write`

## Decision rules

- If the first stable claim is "malloc returns the same fastbin chunk twice," stay in the fastbin duplication family.
- If the first stable claim is "malloc returns a chosen pointer from tcache," bias toward `tcache_poisoning` unless key checks force `house_of_botcake`.
- If the source material says `tcache_dup`, verify the libc is really in the obsolete `2.26-2.28` window before keeping that label.
- If the source material says `house of botcake`, `house of water`, or `house of io`, normalize the spacing first and keep the route in this freelist corridor.
- If the source material says `fastbin reverse into tcache`, normalize it into `fastbin_reverse_into_tcache` before comparing it with overlap or plain poisoning routes.
- If the source material says `house_of_kauri`, translate it into a size-class-change tcache double-free bypass before comparing it with `house_of_botcake`.
- If the source material says `house_of_atum`, translate it into fastbin-to-tcache writeback before comparing it with overlap or pure poisoning families.
- If the source material says `tcache_perthread_struct` hijack, keep it in the metadata-control branch before comparing it with plain chosen-pointer return.
- If the route needs a full tcache bin before the double free becomes useful, keep it in the double-free-bypass branch first instead of collapsing it into plain `tcache_poisoning`.
- If the first stable claim is "allocator writes a heap pointer or large counter into my target," bias toward `fastbin_reverse_into_tcache` or `tcache_relative_write`, not plain poisoning.
- If the route is blocked specifically on protected-pointer math or production, leave this file and open `how2heap-safe-linking.md`.
- If the challenge has no heap leak on `2.32+`, bias away from raw `tcache_poisoning` and toward `house_of_water` or other metadata-side routes.
- If the source material says `house_of_io`, treat it as a historical tcache-metadata route, not as a FILE / FSOP endgame.
- If the route depends on fake non-main arena state, leave this file and open `how2heap-wilderness-and-arena.md`.

## Version guidance

- `< 2.43`: the fastbin duplication family may still be live; verify the exact version directory first.
- `2.26-2.28`: `tcache_dup` is still a historical candidate; later tcache hardening forces you toward `house_of_botcake`-style bypasses or other modern routes.
- Late `2.27+`: key-check bypasses split into stale-size-class tricks, fastbin-to-tcache restaging, or overlap/consolidation restaging instead of raw `tcache_dup`.
- `2.31-2.33`: `house_of_io` is a historical metadata-control reference for arbitrary return through the tcache management struct.
- `2.32+`: safe-linking changes plain `tcache_poisoning` from "overwrite `fd`" into "supply a correct protected pointer."
- `2.42+`: `tcache_metadata_hijacking` matters because tcache metadata may no longer sit at the top of the heap.
- Modern leakless routes usually favor metadata control over naive freelist corruption.

## Reporting language

When you report the route, say which of these was proved first:

- duplicate fastbin return
- chosen-pointer return from freelist poisoning
- key-check bypass into second tcache free
- allocator writeback into target metadata
- direct tcache-metadata control

That phrasing is more reusable than saying only "freelist primitive."
