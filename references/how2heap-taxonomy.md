# how2heap Taxonomy

Use this file as the static catalog: what families exist in the local tree, which examples belong together, and which version breakpoints usually kill or revive them.

If the source material is still noisy, label-heavy, or corridor-ambiguous, start with `how2heap-selector.md` instead.

If the observed bug or allocator primitive is already known and you only need the first candidate list, use `primitive-version-map.md` instead.

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
  Use `how2heap-freelist-primitives.md` when the real question is which fastbin / tcache first proof target the challenge exposes.

- Tcache poisoning and metadata control:
  `tcache_dup`, `tcache_poisoning`, `house_of_botcake`, `house_of_io`, `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, `tcache_relative_write`, `safe_link_double_protect`, `house_of_water`
  Use when the challenge centers on UAF, double free, freed-chunk edits, or modern tcache metadata abuse.
  Treat `tcache_perthread_struct` hijack wording as an entry into this corridor, then split it into historical `house_of_io`, modern metadata takeover, or leakless metadata-side control.
  Use `house-water-and-stash-fengshui.md` when `house_of_water` is blocked on helper-bin sizes, fake metadata placement, or `2.42+` tcache metadata drift.
  Use `how2heap-freelist-primitives.md` when plain poisoning, key-bypass poisoning, and metadata-side control are all plausible.

- Fake-free and House of Spirit routes:
  `house_of_spirit`, `tcache_house_of_spirit`
  Use when the program can free attacker-controlled memory or a forged chunk header and the real question is whether the fake chunk should enter classic fastbin logic or tcache directly.
  Use `how2heap-fake-free-primitives.md` when fake-free admission is the main proof target.

- Smallbin, unsorted bin, and large bin write primitives:
  `house_of_lore`, `unsorted_bin_attack`, `unsorted_bin_into_stack`, `large_bin_attack`, `tcache_stashing_unlink_attack`, `house_of_storm`
  Treat spaced writeup labels such as `tcache stash unlink` as the same stash-assisted mixed-bin family.
  Use when you can corrupt `fd`/`bk`, sort chunks through unsorted or large bins, or turn bin insertion into a write.
  Use `how2heap-bin-attacks.md` for the repo-backed first cut, then `how2heap-bin-write-primitives.md` for the write-vs-return split.
  Use `house-water-and-stash-fengshui.md` when the branch is TSU, TSU+, or TSU++ and the blocker is smallbin tail position, tcache count, or fake target layout.
  Use `how2heap-bin-write-primitives.md` when the real question is whether the first proof target is a write or a returned fake chunk.

- Historical mixed relative-overwrite chains:
  `house_of_roman`
  Use when an old pre-`2.29` target mixes fake fastbins, unsorted-bin writes, and relative overwrites into a leakless or low-leak endgame rather than proving one clean modern primitive.
  Treat this as a historical combined chain, not as the default answer when a modern target merely mentions "leakless heap."

- Backward consolidation and overlap:
  `unsafe_unlink`, `house_of_einherjar`, `poison_null_byte`, `overlapping_chunks`, `overlapping_chunks_2`
  Use when you can fake `prev_size`, clear `prev_inuse`, inject a fake chunk, or create overlap via size corruption.
  Use `how2heap-overlap-nullbyte.md` when the real question is which overlap / null-byte subfamily matches the first proof target.

- Mmap overlap variants:
  `mmap_overlapping_chunks`
  Use when the target allocations are large enough to be mmapped and the overlap comes from corrupting mmap-chunk size metadata before `munmap`, not from ordinary bin reuse.
  Treat this as an overlap neighbor with different allocator rules: page alignment, `mmap_threshold`, and reclaiming unmapped space matter more than unsorted-bin or tcache state.

- Top chunk and heap growth paths:
  `house_of_force`, `house_of_orange`, `house_of_tangerine`, `sysmalloc_int_free`
  Use when the challenge lets you corrupt the wilderness, influence heap growth, or reach `_int_free` on the top chunk without a normal `free`.

- Arena and non-main-arena routes:
  `house_of_mind_fastbin`, `house_of_gods`
  Use when the primitive depends on fake `heap_info`, forged arena state, `NON_MAIN_ARENA`, or arena-list hijack rather than ordinary bin reuse.
  Use `how2heap-wilderness-and-arena.md` when wilderness and arena routes are adjacent candidates.

- Safe-linking recovery or bypass support:
  `decrypt_safe_linking`, `safe_link_double_protect`
  Use when modern glibc blocks raw pointer corruption and you need to recover or synthesize protected pointers.
  Use `how2heap-safe-linking.md` when the real question is whether to recover the pointer, synthesize it leaklessly, or avoid raw pointer forging through metadata control.

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
  - Need to decide whether the first stable outcome is overlap or a chosen-pointer return; that split often decides `poison_null_byte` versus `house_of_einherjar`.
  - Need to decide whether the first stable outcome is duplicate return, chosen-pointer return, allocator writeback, freed wilderness, or fake-arena write.
- Copy the state transition into the challenge's menu semantics. Do not copy raw offsets until they are re-derived under the challenge's chunk sizes.

## Using this repo well

- Start from the exact version directory if it exists.
- If the exact version is missing, compare the nearest older and newer files with the same technique name.
- Use `how2heap-selector.md` for the first family cut, then `how2heap-overlap-nullbyte.md` when the route lives in the overlap / off-by-null corridor.
- Use `how2heap-legacy-writeup-labels.md` first when the source material is still using old community names rather than allocator-first language.
- Use `offbynull-heap.md` first when the source material literally names the bug `offbynull-heap` or `off-by-null`, then drop into `how2heap-overlap-nullbyte.md` for the allocator-family split.
- Use `how2heap-mmap-overlap.md` when the route depends on mmap-sized allocations, `munmap`, and later huge-allocation reclamation rather than normal bin reuse.
- Use `primitive-version-map.md` and the nearest family reference when the source material still uses historical labels such as `tcache_dup`, `house_of_io`, `house_of_roman`, or `house_of_storm`.
- Use `heap-address-leaks.md` when the route is bottlenecked on in-band address recovery rather than primitive selection.
- Use `how2heap-fake-free-primitives.md` when the route starts from freeing attacker-controlled non-heap memory or forged chunk headers.
- Use `how2heap-freelist-primitives.md` when the route lives in fastbin / tcache / metadata freelists.
- Use `how2heap-safe-linking.md` when the route lives in protected-pointer recovery, synthesis, or avoidance.
- Use `how2heap-bin-attacks.md` when the route needs a repo-backed entry for unsorted / smallbin / largebin / stash families.
- Use `how2heap-bin-write-primitives.md` when the route lives in unsorted / smallbin / largebin / stash behavior.
- Use `how2heap-wilderness-and-arena.md` when the route lives in top chunk, `sysmalloc`, or fake-arena logic.
- Use absence as evidence: if a technique is gone in later directories, assume a mitigation or consistency check matters until proven otherwise.
- Keep the `how2heap` philosophy in the exploit: prove one allocator primitive at a time with concrete state checks.
- Remember that `how2heap` mostly stops at allocator behavior. Pair it with `references/leak-and-endgame-map.md` when the remaining challenge is leak recovery, no-`free` routing, or modern FSOP. If the source labels really say `_fileno`, stdin/stdout arbitrary read/write, or old `FSOP`, route through `references/libio-stdio-primitives.md` before assuming a modern Apple-family or generic endgame split.
