# Largebin Geometry Checklist

Use this when a heap plan depends on:
- forging a fake chunk from an overlapping/UAF-controlled write
- largebin insertion or largebin attack
- making one write serve two roles at once, such as modifying `A->bk_nextsize` while also forging `B`

The point is to solve the geometry before guessing the grooming.

## 1. Write the real chunk-size formulas

Start from allocator truth, not menu labels.

For each menu allocation kind, record:
- requested size
- resulting chunk size
- bin class after `free`

If the challenge exposes only a few sizes, derive their relations explicitly.

Typical useful relations:
- difference between two adjacent size classes
- whether `2*y-z` leaves a valid tail such as `0x20` or `0x30`
- whether `2*y-2*x` gives the gap needed to place a fake header
- whether a different menu knob yields a cleaner real-chunk same-bin pair than the current fake-chunk plan

Do this before trying brute-force scripts.

## 2. Separate the two models

Track both:
- stale-handle model
  - which indices still point into old chunks after `free`
  - which stale pointers can still be used by `edit`, `show`, or `free`
- physical-chunk model
  - which chunks are actually allocated or free
  - what chunk boundaries glibc will trust

Most wrong turns come from conflating these two models.

## 3. Build the invariant table

For every candidate overlap, write:

| Field | Required value | Write source | Offset from edit base | Consumed by |
| --- | --- | --- | --- | --- |
| `A->bk_nextsize` | target address or target-0x20 | stale edit into `A` | `?` | largebin insertion |
| `B.prev_size` | if needed | stale edit into fake `B` | `?` | `_int_free` / consolidation |
| `B.size` | fake size or pre-coalesce size | stale edit into fake `B` | `?` | `_int_free` |
| `B.end` | real chunk boundary | derived | n/a | `_int_free` |

If two fields overlap, stop and decide one of:
- the same 8-byte value is valid for both roles
- the layout is impossible

Do not continue with a vague “maybe glibc will accept it”.

## 4. Solve the fake-size story

Ask which of these is true:
- `B.size == target bin size` immediately
- `B.size + forward_tail == target bin size` after forward consolidation
- `B.size` enters one bin first and later coalesces/splits into the real target

Write the exact equation.

Examples:
- `fake_size + 0x30 = target_size`
- `2*y-z = 0x30`
- `boundary - fake_header = fake_size`

If the plan relies on later coalescing, identify the exact tail chunk and why it survives until `free(B)`.

## 5. Check the `free(B)` conditions

Before testing the full exploit, verify:
- `B` header is aligned
- `B.size` is at least `MINSIZE`
- `B.end` lands exactly on a real chunk boundary
- the next chunk metadata seen by `_int_free` is coherent
- if forward consolidation is required, the next chunk is free with the exact expected size
- if backward consolidation must not happen, `prev_inuse` remains consistent

Use allocator-check language, not “it crashed”.

## 6. Check the largebin conditions

For largebin attack chains, verify separately:
- `A` really leaves unsorted and enters largebin before the attack trigger
- the forged or coalesced `B` enters the same largebin index as `A`
- nextsize ordering assumptions hold
- the write target matches glibc's largebin insertion write site
- whether a same-bin write can be achieved with two real chunks before attempting fake-`B` geometry

If you hit:
- `largebin double linked list corrupted (nextsize)`
  - re-check nextsize ordering and chain invariants first
  - for glibc `2.30+`, also re-check whether the chosen `B` is really the smaller same-bin insertion case from the modern largebin pattern
- `double free or corruption (!prev)`
  - re-check fake boundary landing and consolidation expectations
- `invalid pointer`
  - re-check header alignment, fake size, and exact boundary

## 7. Prefer equation-driven searches

If you need automation, search only layouts satisfying your equations.

Good search predicates:
- `A.size == target_A`
- `B.size == target_B` or `B.size + tail == target_A`
- `offset(A->bk_nextsize) < edit_width`
- `offset(B.size) < edit_width`
- stale handle exists for edit base
- stale handle exists for `free(B)`
- `A` and `B` end up in the same largebin index

Bad search strategy:
- enumerate random alloc/free histories and hope one “looks right”

## 8. Minimal proof order

Prove these in order:
1. `free(B)` survives.
2. `A` is in largebin when expected.
3. `free(B)` or later insertion makes `B`/coalesced `B` land in the same bin.
4. the intended largebin write occurs.
5. only then continue to FSOP / house / ROP.

If step `n` fails, return to the invariant table instead of extending the exploit script.
