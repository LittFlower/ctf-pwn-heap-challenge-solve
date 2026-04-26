# how2heap Wilderness And Arena

Use this file when the route depends on top chunk behavior, `sysmalloc` freeing the wilderness, or fake-arena / non-main-arena handling rather than ordinary bin reuse.

If the notes say `no free` or `无 free`, keep the route in this corridor first and decide whether the real branch is `house_of_tangerine`, `sysmalloc_int_free`, an old `house_of_force`, or fake-arena state.

If the notes use spaced forms such as `house of force` or `house of orange`, treat them as the same wilderness-facing routes described here and keep the split focused on first stable allocator effect rather than naming style.

If the notes say `house of tangerine`, treat that wording as the same no-`free` wilderness route as `house_of_tangerine` and verify that the top-chunk / wilderness transition really exists before trusting the label literally.

## The split that matters

This group is not one family. Separate:

- top-chunk steering for an arbitrary later return
- `sysmalloc` freeing the old wilderness when normal `free` is absent
- historical wilderness-to-FSOP chains
- fake non-main arena and arena-hijack routes

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors or version cues for this corridor:

- `house_of_force`: Boston Key Party `2016 cookbook`, BCTF `2016 bcloud`
- `house_of_orange`: HITCON `2016 houseoforange`
- `house_of_tangerine`: PicoCTF `2024 high frequency troubles`
- `sysmalloc_int_free`: local modern transition primitive with no challenge anchor in the README table
- `house_of_mind_fastbin`: local arena-routing example with no challenge anchor in the README table
- `house_of_gods`: local old-libc arena-hijack example with no challenge anchor in the README table

Treat those as routing anchors, not as permission to copy an old wilderness or arena chain into a different libc.

## Family map

### `house_of_force`

Use when:
- the target is old enough (`< 2.29`)
- you can overwrite the top chunk size directly
- the first proof target is evil-size arithmetic that moves `malloc` to a chosen destination

This is the historical "wilderness becomes gigantic, then one evil malloc walks to target" route.

### `sysmalloc_int_free`

Use when:
- direct `free` is absent or limited
- but you can corrupt the top chunk size while heap growth is still reachable
- the first proof target is that `sysmalloc` frees the old wilderness into a real bin

Treat this as the transition primitive behind later routes like Orange and Tangerine, not as the final exploit by itself.

### `house_of_tangerine`

Use when:
- the challenge is modern and no ordinary `free` is needed
- top-chunk corruption plus later allocations can force `sysmalloc` to free the wilderness
- the final goal is a tcache-style chosen-pointer return
- size algebra can make `(new_top_size - FENCEPOST) & MALLOC_MASK` land in a later reusable tcache or smallbin size
- after `sysmalloc`, you still have an adjacent OOB, UAF, or stale edit that reaches the freed wilderness entry
- on `2.32+`, you also have a heap leak or another safe-linking-compatible way to produce the poisoned pointer

Treat this as `sysmalloc_int_free` plus a second proof obligation: the old wilderness must not only get freed, it must become a reachable tcache-poison bridge that can return a chosen pointer.

The first stable proof target is usually "freed wilderness became a poisonable small tcache-sized chunk," not FSOP or a generic unsorted leak.

Version notes:
- `2.26-2.31`: original tcache window. Once the freed wilderness really lands in a tcache-usable size and remains writable, ordinary tcache poisoning is the usual finish.
- `2.32-2.41`: the route is still live, but safe-linking turns the heap leak or metadata-side bypass into an explicit prerequisite.
- `2.42+`: re-check the maintained local `house_of_tangerine` example instead of copying a `2.39`-era script. The landing target may need valid chunk metadata, and the released wilderness may not reach tcache the same way older notes expect.
- `2.43`: the maintained example removes the helper `free(malloc(...))` trick by repeating the wilderness-free cycle and then allocating once more to move the released smallbin chunks into tcache.

### `house_of_orange`

Use when:
- the target is truly old enough for the classic abort / `_IO_list_all` path
- the wilderness can be freed into unsorted
- and the finish is an old-school FSOP chain

Treat this as historical. On modern libc, Orange is mostly a lineage reference for "wilderness freed by `sysmalloc`" rather than a drop-in plan.
If Orange still looks live on an old target, open `libio-stdio-primitives.md` before inheriting generic `FSOP` notes so `_IO_list_all`, `_fileno`, and historical `_IO_str_*` subroutes do not get collapsed together.

### `house_of_mind_fastbin`

Use when:
- a chunk can be freed with the `NON_MAIN_ARENA` bit set
- a fake `heap_info` / fake arena is reachable
- the first proof target is a fastbin write into an offset of the forged arena

This is an arena-routing primitive, not ordinary fastbin duplication.

### `house_of_gods`

Use when:
- the libc is old enough for arena hijacking (`< 2.27`)
- you have the unsorted-bin write-after-free plus leak budget it expects
- the first proof target is control of `thread_arena` or `main_arena.next`, not a simple returned pointer

This is the deeper arena-hijack branch, not just a top-chunk trick.

## Decision rules

- If no direct `free` exists and the route still wants a later returned pointer, compare `sysmalloc_int_free` and `house_of_tangerine` before anything else.
- If all you have proved is that `sysmalloc` freed the old wilderness into a reusable bin, keep the route named `sysmalloc_int_free` until you also prove the tcache-poison bridge.
- If the target is old and the plan is "one evil malloc walks the top chunk to my destination," bias toward `house_of_force`.
- If the route frees the old wilderness and then pivots into modern tcache poisoning or another chosen-pointer return, bias toward `house_of_tangerine`.
- If the route frees the old wilderness and then pivots into historical `_IO_list_all` FSOP, bias toward `house_of_orange`, then reopen `libio-stdio-primitives.md` so old `_IO_str_*`, `_fileno`, and live-stream field routes do not collapse into one label.
- If the route depends on `NON_MAIN_ARENA`, fake `heap_info`, or `thread_arena`, stay in the arena branch: `house_of_mind_fastbin` or `house_of_gods`.

## Version guidance

- `< 2.29`: `house_of_force` is still a real candidate.
- `< 2.26`: classic `house_of_orange` is historically relevant; later libc changes kill the old abort path.
- `>= 2.26`: if the wilderness route is still live, prefer `sysmalloc_int_free` and `house_of_tangerine` over Orange-era assumptions.
- `2.32+`: for classic Tangerine-style tcache poisoning, heap leak or safe-linking-compatible metadata control is no longer optional.
- `2.42+`: validate target-chunk metadata and post-free tcache transfer behavior against the maintained local example before trusting older writeups.
- `< 2.27`: arena-hijack routes like `house_of_gods` remain candidates; later versions require much more skepticism.

## Reporting language

When you report the route, say which of these was proved first:

- evil-size top-chunk walk
- old wilderness freed by `sysmalloc`
- wilderness-to-tcache poisoning bridge
- fake non-main arena write
- arena-list / `thread_arena` hijack

That phrasing is more reusable than saying only "top chunk attack."
