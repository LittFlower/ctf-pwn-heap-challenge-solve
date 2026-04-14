# Heap Address Leaks

Use this file when the heap phase is plausible but the remaining blocker is still "where do heap, libc, PIE, or stack addresses come from in-band?"

If the notes say `single-shot show`, `one-shot show`, or `仅一次show`, keep the leak plan in this corridor and bias toward one-read unsorted / largebin disclosure or partial stdio leaks instead of long multi-read grooming.

## What this file is for

- Pick the smallest leak that unlocks the current heap route.
- Keep heap, libc, PIE, and stack leaks separate.
- Distinguish true in-band leaks from local-only visibility such as `/proc`, debugger state, or `io.libs()`.

## Repo-backed anchors

The local `how2heap` tree does not have a single "leak tutorial", but these files commonly anchor the first in-band address recovery step:

- `decrypt_safe_linking`: local `>= 2.32` heap-pointer recovery example when freed metadata is mangled
- `unsorted_bin_attack`: `0ctf 2016 zerostorage` for libc pointers surfacing from unsorted state
- `large_bin_attack`: `0ctf 2018 heapstorm2` when the route already needs largebin state and can often recover libc from the same corridor
- `house_of_water`: `37c3 Potluck Tamagoyaki` for metadata-side libc surfacing on modern leakless or low-leak routes

Treat those as leak-routing anchors, not as proof that the final exploit must reuse the same family.

## Family map

This corridor is split by the cheapest in-band address class to recover first, and the quick routing map below is the fastest way to choose the next file or proof target.

## First-pass leak families

### Freed tcache metadata

Use when:
- freed tcache chunks can be shown or reread
- the target libc is old enough that metadata still yields useful heap structure directly
- the first proof target is a heap leak, not a libc leak

Modern note:
- on `2.32+`, expect mangled pointers instead of raw `fd`
- if you can read the mangled value, compare against `how2heap-safe-linking.md`

### Unsorted / largebin pointers

Use when:
- a chunk can be freed out of tcache and later shown
- the first proof target is a libc leak
- chunk size or bin state already escapes tcache

Practical split:
- unsorted when one clean `fd` / `bk` read is enough
- largebin when the route already needs largebin sorting anyway

### Metadata-side libc surfacing

Use `house_of_water`, `tcache_relative_write`, or other metadata routes when:
- direct leak primitives are weak or one-shot
- but metadata control can place a libc pointer into a readable region

This is the modern "leak by steering metadata" branch.

### Pointer router leaks

Use when:
- a stale slot table, global pointer array, or other router can be repointed
- `stdout`, `stderr`, `environ`, or another pointer-bearing object is already live

This is often cheaper than a full FSOP setup and may recover stack or libc directly.

### Stdio partial leaks

Use when:
- stdout or stderr fields are writable or partially corruptible
- one-shot libc disclosure matters more than a full endgame

Treat these as leak routes first, not necessarily final execution routes.

## Decision rules

- If the current primitive already reaches a known-address router, prefer `stdout`, `stderr`, or `environ` leaks before growing a heavier heap chain.
- If the only readable heap metadata is mangled, open `how2heap-safe-linking.md` before abandoning the leak.
- If the route already requires largebin or unsorted state, prefer leaking from that same state instead of inventing a second leak mechanism.
- If the source material says `single-shot show`, assume the leak budget is one useful read and rank largebin, unsorted, or partial-stdout routes ahead of longer heap-only grooming plans.
- If the only available addresses come from `/proc`, debugger memory, `ptrace`, or helper-library metadata, label the route local-only and keep searching for an in-band replacement.

## Reporting language

When you report the route, say which address class was recovered first:

- heap leak
- libc leak
- PIE leak
- stack leak
- pointer-router leak

That phrasing is more reusable than saying only "got a leak."
