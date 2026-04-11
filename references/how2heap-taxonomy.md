# how2heap Taxonomy

## What this repository actually is

- `how2heap` is a versioned collection of single-file PoCs, not a single linear tutorial.
- The stable structure is `glibc_<version>/technique.c`.
- Base files at repo root teach allocator basics: `first_fit.c`, `calc_tcache_idx.c`, `malloc_playground.c`.
- The `Makefile` supports versions `2.23`, `2.24`, `2.27`, and `2.31` through `2.43`.
- The important style cue is consistency: every PoC states prerequisites, performs a small number of allocator mutations, and ends with an assertion that proves the primitive.

## Family map

- Fastbin duplication and near-arbitrary return:
  `fastbin_dup`, `fastbin_dup_into_stack`, `fastbin_dup_consolidate`, `fastbin_reverse_into_tcache`
  Use when you control double free or freed-chunk forward pointers in fastbin-sized chunks.

- Tcache poisoning and metadata control:
  `tcache_poisoning`, `tcache_house_of_spirit`, `house_of_botcake`, `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, `tcache_relative_write`, `safe_link_double_protect`, `house_of_water`
  Use when the challenge centers on UAF, double free, freed-chunk edits, or modern tcache metadata abuse.

- Smallbin, unsorted bin, and large bin write primitives:
  `house_of_lore`, `unsorted_bin_attack`, `unsorted_bin_into_stack`, `large_bin_attack`, `tcache_stashing_unlink_attack`
  Use when you can corrupt `fd`/`bk`, sort chunks through unsorted or large bins, or turn bin insertion into a write.

- Fake chunk and backward consolidation:
  `unsafe_unlink`, `house_of_spirit`, `house_of_einherjar`, `poison_null_byte`, `overlapping_chunks`, `overlapping_chunks_2`
  Use when you can fake `prev_size`, clear `prev_inuse`, inject a fake chunk, or create overlap via size corruption.

- Top chunk and heap growth paths:
  `house_of_force`, `house_of_orange`, `house_of_tangerine`, `sysmalloc_int_free`
  Use when the challenge lets you corrupt the wilderness, influence heap growth, or reach `_int_free` on the top chunk without a normal `free`.

- Safe-linking recovery or bypass support:
  `decrypt_safe_linking`, `safe_link_double_protect`
  Use when modern glibc blocks raw pointer corruption and you need to recover or synthesize protected pointers.

## Version breakpoints that matter in practice

- `2.26` introduces tcache, and Ubuntu enables it starting with `2.27`. Pre-tcache habits from `2.23` and `2.24` do not transfer directly.
- `2.29` kills several classic top-chunk and overlap flows. Expect `house_of_force`, old unsorted-bin returns, and older overlap tricks to disappear or require new variants after this point.
- `2.30+` adds stricter large-bin insertion checks. Use the post-2.30 `large_bin_attack` variant instead of older writeups.
- `2.32+` introduces safe-linking and alignment-sensitive tcache poisoning. Heap leaks, pointer recovery, double-protect tricks, or metadata-side attacks become central.
- `2.42` adds `tcache_metadata_hijacking` because `tcache_perthread_struct` may no longer sit at the heap top. Heap overflow into metadata becomes a fresh path again.
- `2.43` removes the fastbin duplication family from the maintained examples. If a plan depends on `fastbin_dup*` or `house_of_mind_fastbin`, verify the exact version before spending time on it.

## How to read a technique file

- Read the opening prose first. It usually states the bug assumption, the version claim, and the patch that forced the current variant.
- Extract the invariant, not just the code. Examples:
  - Need one padding chunk before poisoning because of new tcache checks.
  - Need a heap leak because the protected next pointer is computed from the storage address.
  - Need the tcache bin filled before a free reaches unsorted or smallbin.
- Copy the state transition into the challenge's menu semantics. Do not copy raw offsets until they are re-derived under the challenge's chunk sizes.

## Using this repo well

- Start from the exact version directory if it exists.
- If the exact version is missing, compare the nearest older and newer files with the same technique name.
- Use absence as evidence: if a technique is gone in later directories, assume a mitigation or consistency check matters until proven otherwise.
- Keep the `how2heap` philosophy in the exploit: prove one allocator primitive at a time with concrete state checks.
- Remember that `how2heap` mostly stops at allocator behavior. Pair it with `references/leak-and-endgame-map.md` when the remaining challenge is leak recovery, no-`free` routing, or modern FSOP.
