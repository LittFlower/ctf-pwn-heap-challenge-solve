# how2heap Bin Attacks

Use this file when the challenge obviously lives in unsorted, smallbin, largebin, or stash-assisted bin logic and you want the repo-backed first cut before dropping into the deeper `how2heap-bin-write-primitives.md` split.

If the source material is still using old mixed-bin names such as `house_of_storm`, open `how2heap-legacy-writeup-labels.md` first, then return here for the repo-backed first cut.

If the notes say `tcache stash unlink`, `tcache stash unlink+`, or `tcache stash unlink++`, treat that wording as the local `tcache_stashing_unlink_attack` branch, then return here to decide whether the first stable effect is the write, the returned fake chunk, or both together. Open `house-water-and-stash-fengshui.md` when the blocker is the exact smallbin position, tcache drain count, or plus/plus-plus target layout.

If the notes use spaced forms such as `large bin attack`, `unsorted bin attack`, or `house of lore`, treat them as the same bin families described here and keep the split focused on write-first versus return-first behavior rather than naming style.

If the route clearly depends on same-size smallbin allocation, House of Lore, or smallbin-to-tcache stash movement, open `smallbin-techniques.md` before treating the issue as generic bin corruption.

## Repo-backed anchors

The local `how2heap` tree records these challenge-facing anchors in `README.md`:

- `unsorted_bin_attack`: `0ctf 2016 zerostorage`
- `unsorted_bin_into_stack`: local historical return-first unsorted example with no challenge anchor in the README table
- `house_of_lore`: local smallbin-return example with no challenge anchor in the README table
- `large_bin_attack`: `0ctf 2018 heapstorm2`
- `tcache_stashing_unlink_attack`: HITCON `2019 one punch man`
- `house_of_storm`: local mixed-bin historical example with no challenge anchor in the README table

Use these as family anchors, not as exploit templates.

## Family map

This corridor is still split by first stable effect, but the fastest usable form here is the quick routing table below.

## Quick split

| Observable signal | First local files to open | First thing to prove |
| --- | --- | --- |
| Freed unsorted chunk `bk` is writable and you mainly want a large write | `unsorted_bin_attack`, then `how2heap-bin-write-primitives.md` | allocator-managed large value lands on target |
| Freed unsorted chunk is being reshaped into a fake returned chunk | `unsorted_bin_into_stack`, then `how2heap-bin-write-primitives.md` | next `malloc` returns the fake region |
| Smallbin freelist corruption wants a chosen pointer | `house_of_lore`, then `smallbin-techniques.md` and `how2heap-bin-write-primitives.md` | smallbin hardening checks still pass while returning the staged fake chunk |
| Chunk must reach largebin before the write exists | `large_bin_attack`, then `how2heap-bin-write-primitives.md` | nextsize geometry and modern insertion checks hold |
| Old route mixes unsorted-bin and largebin UAF state into one return-first chain | `house_of_storm`, then `how2heap-bin-write-primitives.md` | the route is really a historical mixed-bin return, not a simpler unsorted or largebin split |
| `calloc` and smallbin-to-tcache stash motion are part of the exploit | `tcache_stashing_unlink_attack`, then `smallbin-techniques.md`, `house-water-and-stash-fengshui.md`, and `how2heap-bin-write-primitives.md` | stash movement creates the write, fake return side effect, or both |

## Decision rules

- If the first stable claim is a write, bias toward unsorted or largebin.
- If the first stable claim is a returned fake chunk, bias toward unsorted-into-stack or House of Lore.
- If both unsorted-bin and largebin UAF state are essential and the target is old `< 2.29`, compare against `house_of_storm` before overfitting a cleaner modern split.
- If `calloc` is mandatory, bias toward stash-assisted routes first.
- If the label is simply `smallbin attack`, split it through `smallbin-techniques.md` into fake return, unlink write, stash-assisted behavior, or backward-consolidation unlink before coding.
- If you still cannot decide after that split, open `how2heap-bin-write-primitives.md` and classify the route by write-first, return-first, or mixed behavior.
