# how2heap Overlap / Null-Byte Families

Use this file when the route lives in the overlap, off-by-null, backward-consolidation, or fake-chunk corridor and the main question is which nearby `how2heap` family actually matches the primitive.

If the challenge or writeup literally labels the bug `offbynull-heap`, open `how2heap-legacy-writeup-labels.md`, then `offbynull-heap.md`, then return here for the deeper family split.

If the notes use spaced forms such as `house of einherjar`, treat them as the same null-byte fake-chunk-return family described here and keep the split focused on first stable allocator outcome rather than naming style.

If the notes say `unsafe unlink`, treat that wording as the same backward-consolidation / fake-chunk corridor and then decide whether the real route is historical nonadjacent consolidation, null-byte fake-chunk return, or another overlap-first branch.

## The split that matters

Do not group these four files together just because they all end in overlap:

- `poison_null_byte`
- `house_of_einherjar`
- `overlapping_chunks`
- `overlapping_chunks_2`

The right split is based on the first stable allocator claim.

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors for this corridor:

- `poison_null_byte`: PlaidCTF `2015 plaiddb`, BalsnCTF `2019 PlainNote`
- `house_of_einherjar`: SECCON `2016 tinypad`
- `overlapping_chunks`: hack.lu CTF `2015 bookstore`, Nuit du Hack `2016 night-deamonic-heap`

`overlapping_chunks_2` has no challenge anchor in the current README table, so treat it as the historical neighbor for size-rewrite-driven overlap, not as the default answer to a modern off-by-null label.

## Family map

### `poison_null_byte`

Use when:
- a single null byte is enough to clear or shrink the next chunk metadata
- the real goal is backward consolidation into a forged free chunk
- the first proof target is overlap, not an immediate chosen-pointer return

What the local modern example actually does:
- parks a fake chunk inside a reclaimed largebin chunk
- repairs `fd` / `bk` via residual largebin pointers
- uses an off-by-null into the victim size field
- frees the victim so backward consolidation unlinks the fake chunk and places the merged result in unsorted

Typical hidden conditions:
- fake chunk `size == next_chunk->prev_size`
- unlink checks must be repaired before the consolidation free
- low two-byte rewrite assumptions can force heap alignment or padding

### `house_of_einherjar`

Use when:
- the bug is still a null-byte off-by-one
- you know or can recover the fake chunk address
- the overlap is only a bridge to a stronger primitive such as tcache poisoning or chosen-pointer return

What the local modern example actually does:
- places a fake chunk at a known address
- clears `prev_inuse` in the next chunk with one null byte
- writes a fake `prev_size` that points backward to the fake chunk
- fills tcache so the free reaches unsorted-style consolidation
- mallocs from the overlapped region, then uses that overlap to poison tcache

Typical hidden conditions:
- heap leak or equivalent known fake-chunk base
- fake `fd` / `bk` must satisfy unlink checks
- modern safe-linking constraints move the finish toward protected-pointer-aware poisoning

### `overlapping_chunks`

Use when:
- you can free a chunk first
- then overwrite that freed chunk's size while it sits in unsorted
- and later request a larger allocation that is still served from the corrupted free chunk

What the local historical example actually proves:
- a freed unsorted chunk can be re-issued at an inflated size
- the new allocation overlaps a later still-live chunk

Typical hidden conditions:
- this family is essentially historical for `< 2.29`
- the overwrite is a full size-field corruption, not a one-byte consolidation trick

### `overlapping_chunks_2`

Use when:
- the overwrite lands on the size of an in-use next chunk
- then freeing an earlier chunk makes glibc believe a farther free chunk is adjacent
- the first proof target is nonadjacent consolidation producing overlap

What the local historical example actually proves:
- a forged next-chunk landing can make one `free` create a larger merged free region that wrongly covers an in-use middle chunk

Typical hidden conditions:
- exact boundary landing
- coherent next-chunk metadata
- again, treat this as historical `< 2.29` material unless the target libc is old enough

## Decision rules

- If the only writable byte is a null byte and you do not yet have a known fake-chunk base, compare `poison_null_byte` before `house_of_einherjar`.
- If the solve already has a heap leak and the real goal is a controlled later `malloc` result, bias toward `house_of_einherjar`.
- If the overwrite is a full size rewrite on a chunk already in unsorted, bias toward `overlapping_chunks`.
- If the overwrite changes where a later `free` thinks the next chunk begins, bias toward `overlapping_chunks_2`.

## Version guidance

- `2.29+`: expect extra scaffolding or outright dead ends for `overlapping_chunks` and `overlapping_chunks_2`.
- Modern libc: `poison_null_byte` and `house_of_einherjar` remain the primary null-byte family, but they now depend on stricter fake-chunk and tcache behavior.
- When the exact version has both `poison_null_byte` and `house_of_einherjar`, use the stronger finish requirement to choose:
  - overlap validation -> `poison_null_byte`
  - chosen-pointer / poisoning bridge -> `house_of_einherjar`

## Reporting language

When you report the route, say which of these was proved first:

- backward-consolidation overlap
- chosen-pointer return from a fake-chunk route
- unsorted-size inflation overlap
- nonadjacent consolidation overlap

That phrasing is more reusable than saying only "null-byte overlap."
