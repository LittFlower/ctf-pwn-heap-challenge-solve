# how2heap Mmap Overlap

Use this file when the route looks like overlap, but the relevant chunks are large enough to be mmapped and the real mechanism is `munmap` plus later reclamation, not ordinary bin reuse.

## The split that matters

Do not collapse this into normal heap overlap families:

- `mmap_overlapping_chunks`
- `overlapping_chunks`
- `overlapping_chunks_2`

`mmap_overlapping_chunks` is an overlap neighbor, but it lives under mmap-chunk rules rather than unsorted-bin or consolidation rules.

## Repo-backed anchors

The local `README.md` records this corridor as:

- `mmap_overlapping_chunks`: local mmap-overlap example with no challenge anchor in the README table

Treat it as a routing anchor, not as proof that ordinary heap-bin overlap logic still applies.

## Family map

### `mmap_overlapping_chunks`

Use when:
- the target allocations are large enough to cross the mmap threshold
- the corruption reaches an mmap chunk's `size` or `prev_size`
- the first proof target is that freeing one mmap chunk `munmap`s a larger region that a later huge allocation reclaims with overlap

What the local example actually proves:
- mmap chunks are reclaimed with `munmap`, not pushed into bins
- corrupting mmap-chunk metadata can cause a later `free` to release a broader mmapped region
- a later large `malloc` can reclaim that region and overlap a previously unmapped pointer range

Typical hidden conditions:
- page-aligned mmap chunk size
- request size must remain above the post-free mmap threshold to stay on the mmap path
- stale pointers into unmapped memory are unreadable until the region is reclaimed

## Decision rules

- If the corruption target is an mmap chunk, leave ordinary unsorted-bin overlap families immediately.
- If the route depends on backward consolidation, `prev_inuse`, or unsorted-bin reuse, this is not the mmap family; go back to `how2heap-overlap-nullbyte.md`.
- If the route depends on the top chunk, `sysmalloc`, or arena routing rather than explicit mmap chunks, go to `how2heap-wilderness-and-arena.md`.

## Reporting language

When you report the route, say which of these was proved first:

- mmap chunk metadata corruption
- oversized `munmap` reclaim
- huge-allocation overlap after reclaim

That phrasing is more reusable than saying only "mmap overlap."
