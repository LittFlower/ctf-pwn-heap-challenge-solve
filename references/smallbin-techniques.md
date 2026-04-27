# Smallbin Techniques

Use this file when a route depends on same-size chunks being sorted into smallbin,
then returned, unlinked, or stashed into tcache.

Smallbin routes are often misnamed. Split them by the first stable allocator effect:

- `house_of_lore`: smallbin returns a staged fake chunk.
- smallbin unlink write: allocator writes `bin` through a corrupted `bk` target.
- `tcache_stashing_unlink_attack`: smallbin-to-tcache stash creates a write, fake return, or both.
- backward consolidation / `unsafe_unlink`: a free triggers `unlink_chunk` on a fake previous chunk; this is adjacent to smallbin but belongs to the overlap/unlink corridor.

## Local Anchors

- `glibc_2.23-2.43/house_of_lore.c`.
- `glibc_2.27` and `glibc_2.31-2.40/tcache_stashing_unlink_attack.c`.
- `glibc_2.23-2.43/unsafe_unlink.c` for adjacent backward-consolidation unlink, not ordinary smallbin return.
- `references/house-water-and-stash-fengshui.md` for TSU, TSU+, and TSU++ count algebra.

Treat local how2heap as the versioned behavior anchor. The file names are stable,
but tcache interaction and helper metadata differ by version.

## Core Smallbin Model

Smallbin chunks are doubly linked and exact-size. To use them in a CTF menu:

- Free same-size chunks only after tcache for that size is full, or drain/fill tcache deliberately.
- Prevent accidental consolidation with guard chunks.
- Sort chunks from unsorted into smallbin by making an allocation that cannot be served by the target unsorted chunk.
- Keep the physical chunk state separate from stale slot state; a stale slot is only useful if it can still edit or show the freed chunk metadata.
- Count from the smallbin tail when reasoning about returned order.

The key unlink side effect during smallbin allocation is:

```text
bck = victim->bk
check: bck->fd == victim
bin->bk = bck
bck->fd = bin
```

That check is the line between a plausible smallbin plan and a crash.

## Technique Split

| Technique shape | First proof target | Main write needed | Usual hidden condition |
| --- | --- | --- | --- |
| `house_of_lore` | later same-size malloc returns a fake region | smallbin victim `bk` points to staged fake list | fake `bk->fd == victim`, plus next fake node coherence |
| smallbin unlink write | `bck->fd = bin` writes a libc/bin pointer to a target | victim `bk = target - fd_offset` | target side is writable and the check still passes |
| TSU / TSU+ / TSU++ | stash movement writes, returns fake chunk, or both | selected smallbin node `bk` | exact tcache count and smallbin tail position |
| unsafe unlink neighbor | backward consolidation rewrites a pointer router | fake previous chunk `fd` / `bk` and next `prev_size` | fake chunk starts at a known pointer and passes `P->fd->bk == P`, `P->bk->fd == P` |

## House of Lore Checklist

Use `house_of_lore` when the goal is a chosen allocation from smallbin, usually into
stack, `.bss`, a slot table, or another staged fake chunk.

Proof obligations:

- One real victim chunk of the target size reaches smallbin.
- The victim's `bk` is editable after sorting into smallbin.
- The fake chunk at `victim->bk` has `fd` pointing back to the victim header.
- A second fake node exists so the following smallbin unlink or tcache-stash side effect does not crash.
- Tcache for the size is drained before the allocation that must consume smallbin.
- The returned fake pointer has enough writable logical size in the program's menu.

Version notes:

- `2.23-2.24`: no tcache drain is needed, but smallbin hardening still requires fake `fd` / `bk` coherence.
- `2.27+`: fill or drain tcache consciously; otherwise same-size malloc/free may never touch smallbin.
- `2.35+`: local how2heap adds an extra fake freelist to survive smallbin-to-tcache side effects. Do not copy older fake-stack layouts into newer libc without that extra staging.

## Smallbin Write Checklist

Use a smallbin write shape when the useful first effect is `bck->fd = bin`, not a
chosen returned pointer.

Checklist:

- Decide whether the target wants the bin pointer itself, a libc-like pointer leak, or only a non-zero marker.
- Place `victim->bk` so the allocator writes to the intended field.
- Ensure the object at `victim->bk` has an `fd` field that currently equals the victim header, or can be made to equal it.
- If the target is a real application object, check that the allocator's write does not clobber fields needed before the later trigger.

This is usually a setup primitive. Treat it as incomplete until it leads to a leak,
pointer router, fake return, or endgame.

## TSU Boundary

Use `tcache_stashing_unlink_attack` when smallbin allocation moves extra same-size
chunks into tcache and that stash movement is the exploitable behavior.

Quick split:

- Plain TSU: prove a libc/bin pointer write.
- TSU+: prove a fake chunk enters tcache and later malloc returns it.
- TSU++: prove fake return plus a second libc/bin pointer write.

Open `house-water-and-stash-fengshui.md` for the count equation. Do not duplicate
the count algebra here.

## Unsafe Unlink Boundary

Do not route every `fd` / `bk` corruption to smallbin.

Use the overlap/unlink corridor when:

- The route forges a previous free chunk inside a live chunk.
- The trigger is freeing the next chunk and backward consolidation.
- The target write comes from `unlink_chunk`, not from a same-size smallbin allocation.
- A known pointer, often a global slot, is overwritten into a pointer router.

Open `how2heap-overlap-nullbyte.md` or the exact `unsafe_unlink.c` example before
comparing it with House of Lore.

## Common Failure Checks

- Tcache intercepts the same-size allocation before smallbin is reached.
- Adjacent freed chunks consolidate because guard chunks were missing.
- The stale slot points to user data but the check needs the chunk header.
- Fake `fd` / `bk` values satisfy the first unlink but not the next one.
- The fake target is returned but the menu's tracked size or state bit blocks the follow-up write.
- A one-shot write to a fake stack chunk is treated as code execution before the real trigger is proved.

## Reporting Language

When reporting a smallbin route, name the first proof target:

- smallbin fake-chunk return
- smallbin unlink write
- stash-assisted write
- stash-assisted fake return
- backward-consolidation unlink

This prevents `smallbin attack` from hiding the actual proof obligation.
