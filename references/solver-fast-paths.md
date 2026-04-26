# Solver Fast Paths

Use this file when a first-pass heap solve still has too many live branches.

Goal: reduce the challenge to one corridor quickly, then open the narrower reference set instead of reading half of `references/`.

## The first eight questions

1. Is there a real `free`, or is the surface fundamentally `no free`?
2. Does the write land on chunk user data, chunk metadata, or a live libc/application object such as `FILE`?
3. Is the corruption budget only one null byte, or do you control full qwords?
4. Do you have UAF / double free / freed-`fd` reach, or only an overflow?
5. After a chunk becomes free, can you still mutate its metadata?
6. Do you get one useful read (`single-shot show`) or a reusable leak primitive?
7. Do worker threads allocate or free the chunks that matter?
8. Does the draft route still depend on `/proc`, debugger state, `io.libs()`, or copied local offsets?

If question 8 is yes, the route is still a draft, not a finished solve.

## Fast routing matrix

| First strong signal | Open first | What to prove next |
| --- | --- | --- |
| No direct `free`, but top chunk can be corrupted | `how2heap-wilderness-and-arena.md`, `primitive-version-map.md`, `version-delta.md` | Whether this is only `sysmalloc_int_free`, or a full `house_of_tangerine`-style chosen-pointer bridge |
| Only one null byte / backward consolidation / `offbynull-heap` wording | `offbynull-heap.md`, `how2heap-overlap-nullbyte.md`, `version-delta.md` | Whether the first stable result is overlap only or a later chosen-pointer return |
| UAF / double free / freed `fd` / tcache metadata reach | `how2heap-freelist-primitives.md`, `how2heap-safe-linking.md`, `version-delta.md` | Whether the first stable result is duplicate return, chosen-pointer return, or metadata control |
| Unsorted / smallbin / largebin / stash wording | `how2heap-bin-attacks.md`, `how2heap-bin-write-primitives.md`, `largebin-geometry-checklist.md` | Whether the first stable result is a write, fake-chunk return, or stash-assisted mixed effect |
| Live `FILE`, `_fileno`, stdin/stdout, wide stream, `_codecvt` | `libio-object-corruption.md`, `libio-stdio-primitives.md`, `leak-and-endgame-map.md` | Which exact later libc helper consumes the corrupted state |
| One-shot `show` or only one useful read | `heap-address-leaks.md`, `leak-and-endgame-map.md` | Which single leak buys the most: heap, libc, PIE, or stack |
| Worker thread owns a target free or allocation | `threaded-allocator-pitfalls.md`, `leak-and-endgame-map.md` | Whether the route truly has a same-thread reuse or a proved cross-thread bridge |
| Primitive is stable, but finish is unclear | `leak-and-endgame-map.md`, `house-of-apple2.md`, `output-contract.md` | Which endgame matches the real trigger surface and stays remotely viable |

## Stop-reading rules

- Do not read both the overlap corridor and the freelist corridor unless the observed primitive really spans both.
- Do not open Apple-family or generic FILE endgames just because the word `FSOP` appears in notes. Split live-stdio routes first.
- Do not call a no-`free` route `house_of_tangerine` until the freed wilderness becomes a reachable tcache-poison or chosen-pointer bridge.
- Do not route to `large_bin_attack` just because a chunk reaches largebin. You still need a post-free metadata write.
- Do not keep reading heap-family docs when the writable surface is already a live `FILE` or another libc object.

## First-pass deliverable

Before leaving first-pass routing, write down:

- exact bug primitive
- exact libc or candidate set
- cheapest missing address class
- first proof target
- one rejected corridor and the allocator fact that killed it

If you cannot fill those five items, stay in routing mode instead of jumping to exploit scripting.
