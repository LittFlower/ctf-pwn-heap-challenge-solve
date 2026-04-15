# how2heap Bin Write Primitives

Use this file when the route clusters around unsorted bin, smallbin, largebin, or tcache-stash-assisted bin behavior and the main question is whether the first proof target is a returned pointer or an allocator write.

If the source material is still using old mixed-bin names such as `house_of_storm`, open `how2heap-legacy-writeup-labels.md` first, then return here to split write-first, return-first, and mixed behavior correctly.

If the notes use spaced forms such as `house of lore`, treat them as the same smallbin fake-chunk-return family described here and keep the split focused on first stable allocator effect rather than naming style.

## The split that matters

Do not group these together as "bin attack":

- `unsorted_bin_attack`
- `unsorted_bin_into_stack`
- `house_of_lore`
- `large_bin_attack`
- `tcache_stashing_unlink_attack`
- `house_of_storm`

The right split is based on the first stable allocator outcome: large-value write, chosen-pointer return, or mixed write-and-return behavior.

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors for this corridor:

- `unsorted_bin_attack`: `0ctf 2016 zerostorage`
- `large_bin_attack`: `0ctf 2018 heapstorm2`
- `tcache_stashing_unlink_attack`: HITCON `2019 one punch man`
- `house_of_storm`: local historical example exists, but the README table gives no challenge anchor

Treat those as routing anchors, not as license to transplant old bin geometry into a different libc.

## Family map

### `unsorted_bin_attack`

Use when:
- a freed unsorted chunk's `bk` can be overwritten
- the first proof target is a large allocator-managed value written to a target
- the chunk size stays outside tcache or tcache is otherwise bypassed

This is a write primitive first. In practice it often prepares later routes such as `global_max_fast` changes or other setup writes.

### `unsorted_bin_into_stack`

Use when:
- a freed unsorted chunk's metadata can be rewritten
- the first proof target is a nearly-arbitrary returned pointer rather than a plain write
- the target fake chunk is already at a known writable location

This is the unsorted-bin "return a fake chunk" branch, not the write-large-value branch.

### `house_of_lore`

Use when:
- the route depends on smallbin freelist corruption
- the first proof target is a chosen-pointer return
- you can satisfy the smallbin hardening checks on both `bk` and the staged fake list

This is the canonical smallbin-return family, especially when the end point is stack or another fake chunk.

### `large_bin_attack`

Use when:
- a chunk can reach largebin and you retain a post-free metadata write into that largebin-resident chunk, usually via UAF, overlap, or stale edit
- that post-free write reaches `bk_nextsize` or equivalent nextsize geometry
- the first proof target is a large-value write to a target
- the version is modern enough that you must satisfy the post-`2.30` insertion checks

This is a write primitive first. Treat nextsize ordering and repair steps as the deciding constraints.

Do not route here just because a chunk can be sorted into largebin. Without attacker-controlled post-free mutation of the largebin chunk metadata, modern `large_bin_attack` is not live.

Practical consequence:
- the written value is the heap address of the chunk being inserted, so target selection and carrier-chunk design are often the same problem
- if the final route is `apple2` or another FILE pivot, prefer layouts where the inserted chunk already holds the fake FILE or points into the same controlled heap object
- when only one arbitrary write exists, ask whether the largebin write can both retarget `_IO_list_all` and deliver a ready-to-trigger fake FILE base in one step
- if the challenge only exposes largebin-sized real chunks and lacks an arbitrary-allocation primitive, consider using the largebin write on `mp_.tcache_bins` to widen the valid tcache range, then convert a normal same-size free into out-of-range tcache poisoning

`_mp.tcache_bins` branch:
- treat it as a corridor change, not as the finish
- primitive 1 proves the write to `mp_.tcache_bins`
- primitive 2 proves that a chunk of the chosen largebin size now enters an out-of-range tcache bin and can be poisoned
- plan at least two same-size frees in that OOB bin, because widening `tc_idx` validity does not create a second node for you
- remember that `tcache_get` clears `e->key`, so target choice must survive the zero write at `target+0x8`

Single-write co-design checklist:
- a largebin-resident chunk `A` is writable after it reaches largebin
- the same write that edits `A->bk_nextsize` can also forge or finalize a later inserted chunk `B`
- `A` and `B` land in the same largebin index
- freeing or sorting `B` triggers the largebin write
- the written heap address is already the base, or a stable interior pointer, of the staged fake FILE carrier
- the carrier survives until `exit`, flush, or another stdio walk

### `tcache_stashing_unlink_attack`

Use when:
- a smallbin chunk's `bk` is writable
- `calloc` or stash movement is available
- the first proof target mixes both effects: stash-assisted write plus fake-chunk return

This is not just `house_of_lore` with a different name. The stash motion is part of the primitive.

### `house_of_storm`

Use when:
- the route is historical and combines unsorted plus largebin UAF state
- the first proof target is an arbitrary return from mixed bin state

Treat this as an old mixed-bin route. On modern libc, use it mainly as a version warning and conceptual ancestor.

## Decision rules

- If the first stable claim is "allocator writes a libc or heap pointer into my target," bias toward `unsorted_bin_attack` or `large_bin_attack`.
- If the only available arbitrary write is a `largebin attack` and the intended finish is FILE-based, design the fake FILE carrier before choosing the largebin target. `_IO_list_all` should ideally be rewritten to a chunk you already control.
- If the first stable claim is "malloc returns my fake chunk," bias toward `unsorted_bin_into_stack` or `house_of_lore`.
- If `calloc` is a required part of the trigger and smallbin-to-tcache movement is doing real work, bias toward `tcache_stashing_unlink_attack`.
- If the route needs a chunk to hit largebin before anything interesting happens, bias away from unsorted and smallbin routes immediately.
- If the route is old `< 2.29` mixed-bin folklore, compare against `house_of_storm` only after checking whether a simpler unsorted or largebin split already explains it.

## Heap-fengshui note for `largebin_attack`

On modern one-write routes, do not think of `largebin_attack` as just "write heap pointer somewhere."

Instead split it into two linked questions:

1. which writable target should receive the inserted chunk address
2. how do you shape that inserted chunk so the written heap address is already useful

For FILE-based routes such as `house_of_apple2`, this often means:

- use the stale or overlapping write on largebin chunk `A` to modify `bk_nextsize`
- use that same write window to forge or finish chunk `B`
- later free or sort `B` so largebin insertion writes `B`'s heap address into `_IO_list_all`
- treat `B` as the fake FILE carrier, not as a disposable trigger chunk

## Version guidance

- `< 2.29`: unsorted-bin return and older mixed-bin routes are more plausible.
- `2.30+`: modern `large_bin_attack` must satisfy the extra nextsize and `bk` checks.
- `2.26+`: if tcache is present, remember that many unsorted or smallbin examples only become reachable after filling or bypassing tcache first.
- Modern targets often demote historical unsorted-bin return tricks and promote largebin or stash-assisted routes.

## Reporting language

When you report the route, say which of these was proved first:

- unsorted-bin large-value write
- unsorted-bin fake-chunk return
- smallbin fake-chunk return
- largebin nextsize write
- stash-assisted write-and-return

That phrasing is more reusable than saying only "bin attack."
