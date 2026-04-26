# how2heap Selector

Use this file when the challenge clearly wants a local `how2heap` comparison, but the right family is not yet obvious from the bug label alone.

If the observed bug or allocator primitive is already mostly clear and you only need a first candidate list, use `primitive-version-map.md` instead.

If you only need the static local family catalog and version breakpoints, use `how2heap-taxonomy.md` instead.

## Purpose

- Start from the first stable allocator outcome, not from the most famous technique name.
- Use the local `how2heap` tree as a versioned behavior atlas.
- Keep overlap / null-byte routes separated by what the first proof target actually is: overlap, controlled return, or fake-free consolidation.
- Keep fake-free routes separated by allocator admission: direct tcache reuse versus classic fastbin admission with nextsize checks.

## Repo-backed first-pass signals

The current local `how2heap` tree records these challenge-facing anchors in `README.md`:

- `poison_null_byte`: PlaidCTF `2015 plaiddb`, BalsnCTF `2019 PlainNote`
- `house_of_einherjar`: SECCON `2016 tinypad`
- `overlapping_chunks`: hack.lu CTF `2015 bookstore`, Nuit du Hack `2016 night-deamonic-heap`
- `mmap_overlapping_chunks`: local mmap-overlap example with no challenge anchor in the README table
- `house_of_spirit`: hack.lu CTF `2014 OREO`
- `fastbin_dup_into_stack`: `9447 search-engine`, `0ctf 2017 babyheap`
- `tcache_dup`: obsolete local `2.26-2.28` tcache-double-free example
- `house_of_io`: local `2.31-2.33` tcache-metadata example with no challenge anchor in the README table
- `house_of_water`: `37c3 Potluck Tamagoyaki`
- `house_of_force`: Boston Key Party `2016 cookbook`, BCTF `2016 bcloud`
- `house_of_orange`: HITCON `2016 houseoforange`
- `house_of_tangerine`: PicoCTF `2024 high frequency troubles`
- `house_of_roman`: local historical mixed leakless chain with no challenge anchor in the README table
- `unsorted_bin_attack`: `0ctf 2016 zerostorage`
- `unsorted_bin_into_stack`: local historical unsorted-bin return example with no challenge anchor in the README table
- `house_of_lore`: local smallbin-return example with no challenge anchor in the README table
- `large_bin_attack`: `0ctf 2018 heapstorm2`
- `tcache_stashing_unlink_attack`: HITCON `2019 one punch man`
- `house_of_storm`: local historical mixed-bin return example with no challenge anchor in the README table
- `safe_link_double_protect`: `37c3 Potluck Tamagoyaki`

Treat those as family examples, not as permission to paste an old exploit shape into a new libc.
Only classic `house_of_spirit` has a challenge anchor in the current README table; use `tcache_house_of_spirit` as the same fake-free family's tcache-side variant.

## Selector table

| Observable challenge signal | First local files to open | First thing to prove | Hidden condition that usually decides it |
| --- | --- | --- | --- |
| Off-by-one null into the next chunk, and the first goal is a reusable overlap | `poison_null_byte`, `house_of_einherjar`, then `how2heap-overlap-nullbyte.md` | Whether clearing one byte gives a valid backward-consolidation story | Fake-size equality, unlink coherence, and modern tcache staging often matter more than the off-by-null itself |
| Off-by-one null into the next chunk, and the end goal wants `malloc` to return a chosen pointer | `house_of_einherjar`, then `poison_null_byte` for comparison | Whether you can build a known-address fake chunk and later reuse the overlap for poisoning | Heap leak or known fake-chunk address, tcache fill, and safe-linking compatibility |
| The notes say `house of einherjar` | `how2heap-overlap-nullbyte.md`, then `house_of_einherjar` | Whether the first stable result is the fake-chunk-return bridge rather than overlap-only validation | The spaced label usually names the same null-byte route, but the proof target still decides between Einherjar and poison-null-byte |
| The source material is using old community labels and you need to normalize them before routing | `how2heap-legacy-writeup-labels.md`, then the translated family doc | Which allocator corridor the old label actually maps to | Historical labels often bundle old libc assumptions or name the bug instead of the first stable primitive. |
| The challenge literally calls the bug `offbynull-heap` or `off-by-null`, but the allocator family is still unclear | `how2heap-legacy-writeup-labels.md`, then `offbynull-heap.md`, then `poison_null_byte` or `house_of_einherjar` | Whether the one-byte null proves overlap-first or fake-chunk-return-first | A bug label alone does not decide whether you need only overlap or a known fake-chunk base for a stronger finish |
| Program can `free` a pointer into stack, `.bss`, or another attacker-staged region | `house_of_spirit`, `tcache_house_of_spirit`, then `how2heap-fake-free-primitives.md` | Whether the fake chunk is admitted through tcache directly or must survive classic fastbin checks first | Tcache occupancy, size-class reachability, alignment, and whether a sane next fake chunk is required |
| The notes say `house of spirit` | `how2heap-fake-free-primitives.md`, then `house_of_spirit` or `tcache_house_of_spirit` | Whether the first stable result is fake chunk admission into tcache or through the older fastbin path | The spaced label names the family, but the real split is allocator admission, not naming style |
| Freed unsorted chunk size can be enlarged before a later allocation | `overlapping_chunks` | Whether one oversized allocation from unsorted overlaps a still-live neighbor | Usually only sound on `< 2.29`; confirm the old overlap family still exists in the target version window |
| Huge allocations are mmapped and the corruption lands on mmap-chunk `size` or `prev_size` | `how2heap-mmap-overlap.md`, then `mmap_overlapping_chunks` | Whether a corrupted mmap chunk can be `munmap`ped in a way that a later huge allocation reclaims overlapping space | This is mmap / `munmap` behavior, not ordinary heap-bin consolidation; page alignment and threshold behavior decide it |
| In-use next-chunk size can be overwritten before freeing an earlier chunk | `overlapping_chunks_2`, `unsafe_unlink`, then `how2heap-overlap-nullbyte.md` | Whether fake next-chunk landing causes nonadjacent consolidation without immediate abort | Boundary landing and `prev_inuse` / `prev_size` coherence |
| The notes say `unsafe unlink` | `how2heap-overlap-nullbyte.md`, then `unsafe_unlink` or nearby overlap files | Whether the first stable result is a historical nonadjacent-consolidation overlap or a modern fake-chunk / null-byte branch | The spaced label still belongs to the backward-consolidation corridor, not to generic bin or freelist routing |
| You have overlap already, but need to decide whether the family is "null-byte off-by-one" or "size rewrite overlap" | `how2heap-overlap-nullbyte.md` plus the exact versioned file | Which metadata word was truly attacker-controlled first | A single null-byte usually implies a consolidation-family proof; a full size rewrite usually implies a simpler overlap-first proof |
| The main blocker is still "where do the addresses come from?" rather than the primitive family itself | `heap-address-leaks.md` plus the route's current primitive file | Which address class is cheapest to recover in-band first | Heap-vs-libc-vs-stack leak budget usually decides the next move faster than naming a new technique |
| The notes say `single-shot show`, `one-shot show`, or `仅一次show` | `heap-address-leaks.md`, then the current unsorted / largebin / stdio route | Whether one useful read is enough for libc, heap, or stack recovery | A one-read budget usually rewards largebin, unsorted, or partial-stdout leaks over longer heap grooming, but only count partial-stdout if later output still flows through stdio rather than raw `write` / `send`. |
| The source material says `无 leak`, `no leak`, or `leakless heap` | `primitive-version-map.md`, then `leak-and-endgame-map.md` | Whether this is really a modern low-leak metadata route, a historical combined leakless chain, or just an unsolved leak problem wearing a name | The wording often overstates how leakless the route really is |
| The source material already says `house of banana`, `house of cat`, `house of emma`, or `house of kiwi` | `leak-and-endgame-map.md`, then the exact endgame helper or route | Whether the name is describing the real finish, only a trigger helper, or a version-incompatible historical route | Endgame labels often hide trigger-surface and version assumptions more than primitive-family assumptions |
| The source material says `_fileno`, stdin/stdout arbitrary read/write, or old `FSOP` | `libio-stdio-primitives.md`, then `heap-address-leaks.md` or `leak-and-endgame-map.md` | Whether the first stable effect is redirected fd use, partial-stdio leak, stdin-backed write, or a real historical `_IO_str_*` route | These labels usually describe stdio-field corruption directly and should be split before comparing Apple-family or generic endgame names. For `_fileno`, check early that the target fd is already open and that a later stdio helper still consumes the same live stream object. |
| UAF, double free, freed-`fd`, or tcache metadata corruption points toward a returned-pointer or metadata-control route | `how2heap-freelist-primitives.md` plus the exact fastbin / tcache file | Whether the first stable result is duplicate return, chosen-pointer return, or metadata control | Safe-linking, tcache key checks, and whether the route is leakless usually decide the branch |
| The source material says `tcache dup` | `how2heap-freelist-primitives.md`, then `tcache_dup` | Whether the name really belongs to the obsolete duplicate-return window or must be translated into a newer bypass family | The spaced label is the same old tcache-dup wording, not a separate modern primitive |
| The source material says `fastbin reverse into tcache` | `how2heap-freelist-primitives.md`, then `fastbin_reverse_into_tcache` | Whether the first stable result is allocator-managed metadata writeback instead of duplicate return or plain poisoning | The spaced label still belongs to the freelist corridor, but the writeback effect matters more than the name |
| The source material says `house of botcake`, `house of water`, or `house of io` | `how2heap-freelist-primitives.md`, then `house-water-and-stash-fengshui.md` for `house_of_water` layout details | Whether the first stable result is key-check bypass, chosen-pointer return, or direct metadata control | These spaced labels still belong to the fastbin/tcache corridor, not to generic FSOP or overlap routing |
| The writeup or challenge notes still use old tcache labels such as `tcache_dup` or `house_of_io` | `how2heap-freelist-primitives.md`, then `tcache_dup` or `house_of_io` | Whether the label really means obsolete duplicate return or a historical tcache-metadata route | Exact libc window decides whether the old label survives or must be translated into a modern metadata or bypass family |
| The notes say `tcache_perthread_struct` hijack or `tcache_perthread_struct劫持` | `how2heap-freelist-primitives.md`, then the metadata-side files | Whether the first stable result is direct tcache-metadata control instead of a chosen-pointer return | This wording usually names the metadata surface, not the exact family; split it into `house_of_io`, `house_of_water`, metadata poisoning, hijacking, or relative write |
| The source material says `house_of_kauri` or describes filling tcache before a fastbin double free becomes useful again | `how2heap-freelist-primitives.md`, then `house_of_botcake`, `fastbin_reverse_into_tcache`, or stash neighbors | Whether the first stable result is a second tcache free through size-class change, fastbin restaging, or overlap-assisted reinsertion | The bypass shape decides whether this stays a freelist route or spills into stash-assisted bin behavior |
| The source material says `house_of_atum` or frames the goal as reaching `chunk-0x10` to rewrite `prev_size` / `size` | `how2heap-freelist-primitives.md`, then `fastbin_reverse_into_tcache` | Whether the first stable result is allocator-managed metadata reach near the chunk header, not a plain chosen-pointer return | This label describes the metadata-reach outcome; the real route is still fastbin-to-tcache writeback |
| The source material says `house_of_roman` or "leakless heap" on an old hook-era libc | `primitive-version-map.md`, then `leak-and-endgame-map.md` and `house_of_roman` | Whether this is really the historical mixed chain or a simpler primitive wearing an old name | Relative-overwrite budget, hook-era libc, and brute-force tolerance decide whether Roman is still relevant |
| The route is clearly a modern tcache problem, but the real blocker is protected-pointer handling on `2.32+` | `how2heap-safe-linking.md` plus `decrypt_safe_linking`, `safe_link_double_protect`, or metadata-side files | Whether you can recover a mangled pointer, synthesize one, or avoid forging it entirely | Heap leak quality and metadata reach usually decide the branch |
| Freed-chunk `bk` / `fd`, nextsize, or stash motion points toward unsorted, smallbin, or largebin behavior | `how2heap-bin-attacks.md` then `how2heap-bin-write-primitives.md` plus the exact bin file | Whether the first stable result is a write or a returned fake chunk | Tcache bypass, nextsize checks, and whether `calloc` is required usually decide the branch |
| The notes say `large bin attack` or `unsorted bin attack` | `how2heap-bin-attacks.md`, then the exact unsorted or largebin file | Whether the first stable result is a write-first unsorted/largebin route or a return-first neighbor | These spaced labels still belong to the bin corridor, but the first stable effect decides the exact family |
| The notes say `house of lore` | `how2heap-bin-attacks.md`, then `how2heap-bin-write-primitives.md` and `house_of_lore` | Whether the first stable result is a smallbin fake-chunk return rather than a write-first unsorted or largebin route | The spaced label is still a smallbin-return family, not a generic bin attack keyword |
| The notes say `tcache stash unlink`, `tcache stash unlink+`, or `tcache stash unlink++` | `how2heap-bin-attacks.md`, then `how2heap-bin-write-primitives.md`, then `house-water-and-stash-fengshui.md` | Whether stash motion is only providing the write, fake-chunk return, or both fake return and a second libc-pointer write | These cheatsheet labels name the stash-assisted mixed-bin branch, not a generic tcache route |
| The notes say `no free` or `无 free` | `how2heap-wilderness-and-arena.md`, then `house_of_tangerine` or `sysmalloc_int_free` | Whether the first stable result comes from freeing the wilderness, steering heap growth, or old top-chunk abuse | This wording usually describes the allocator surface better than any single historical technique name |
| The notes say `house of tangerine` | `how2heap-wilderness-and-arena.md`, then `house_of_tangerine` | Whether the first stable result is the modern no-`free` wilderness transition rather than a generic top-chunk corruption story | The spaced label still belongs to the wilderness corridor, not to bin or freelist routing |
| The notes say `house of force` or `house of orange` | `how2heap-wilderness-and-arena.md`, then the exact wilderness-era file | Whether the first stable result is evil-size top-chunk steering, freed wilderness, or Orange-era IO pivoting | The spaced labels still belong to the wilderness corridor, not generic overlap or FSOP routing |
| No direct `free`, or the route clearly depends on top chunk growth, `sysmalloc`, `NON_MAIN_ARENA`, or fake arena handling | `how2heap-wilderness-and-arena.md` plus `house_of_tangerine`, `sysmalloc_int_free`, `house_of_force`, or arena files | Whether the first stable result is freed wilderness, evil-size walk, or fake-arena write | Exact version window matters more than the bug label here |

## Fast routing rules

- If the bug gives only one null byte, open `how2heap-overlap-nullbyte.md` immediately before ranking `poison_null_byte` against `house_of_einherjar`.
- If the source material says `house of einherjar`, open `how2heap-overlap-nullbyte.md` before trusting the spaced label literally.
- If the source material is speaking in old writeup labels, open `how2heap-legacy-writeup-labels.md` before trusting the label literally.
- If the challenge label itself says `offbynull-heap`, open `how2heap-legacy-writeup-labels.md`, then `offbynull-heap.md` before ranking `poison_null_byte` against `house_of_einherjar`.
- If the source material says `house of spirit`, open `how2heap-fake-free-primitives.md` before comparing it with overlap or poisoning families.
- If the primitive is fake free of attacker-controlled memory, open `how2heap-fake-free-primitives.md` before ranking overlap or poisoning families.
- If the first deterministic claim is "this free chunk can be re-served at a larger size", start from `overlapping_chunks`, not from the null-byte family.
- If the source material says `unsafe unlink`, keep it in the overlap/null-byte corridor before comparing it with bin or freelist families.
- If the chunks are mmap-sized and the overlap depends on `munmap` plus a later huge allocation, open `how2heap-mmap-overlap.md` before `mmap_overlapping_chunks`.
- If the first deterministic claim is "malloc will return a pointer near my fake chunk", bias toward `house_of_einherjar`.
- If the real blocker is address recovery, open `heap-address-leaks.md` before inventing a new heap family.
- If the source material says `single-shot show` or `仅一次show`, open `heap-address-leaks.md` before designing a multi-read leak plan.
- If the source material says `无 leak` or `leakless heap`, open `primitive-version-map.md` and `leak-and-endgame-map.md` before trusting the wording literally.
- If the source material already says `house of banana`, `house of cat`, `house of emma`, or `house of kiwi`, open `leak-and-endgame-map.md` before reopening primitive-family selection from scratch.
- If the source material says `_fileno`, stdin/stdout arbitrary read/write, or old `FSOP`, open `libio-stdio-primitives.md` before comparing Apple-family or generic endgame labels.
- If the source material says `tcache dup`, open `how2heap-freelist-primitives.md` before trusting it as a modern route.
- If the source material says `fastbin reverse into tcache`, open `how2heap-freelist-primitives.md` before mixing it with overlap or generic poisoning routes.
- If the source material says `house of botcake`, `house of water`, or `house of io`, open `how2heap-freelist-primitives.md` before comparing them with non-freelist families.
- If the source material says `house of water` and the route is stuck on offsets or fake metadata roles, open `house-water-and-stash-fengshui.md` before coding.
- If the route clusters around fastbin, tcache, or metadata freelists, open `how2heap-freelist-primitives.md` before ranking individual poisoning files.
- If the source material still says `tcache_dup` or `house_of_io`, open `how2heap-freelist-primitives.md` before trusting the historical label.
- If the source material says `tcache_perthread_struct` hijack, keep it in the metadata-control branch before comparing it with plain tcache poisoning.
- If the source material says `house_of_kauri` or describes a double free that only becomes useful after tcache fill/drain behavior, open `how2heap-freelist-primitives.md` before collapsing it into plain `tcache_poisoning`.
- If the source material says `house_of_atum`, open `how2heap-freelist-primitives.md` before mistaking the route for overlap or generic header corruption.
- If the source material still says `house_of_roman`, open `primitive-version-map.md` and `leak-and-endgame-map.md` before assuming a modern leakless route exists.
- If the route is blocked specifically on safe-linking math or protected-pointer production, open `how2heap-safe-linking.md` before forcing a poisoning family.
- If the route clusters around unsorted, smallbin, largebin, or stash-assisted writeback, open `how2heap-bin-attacks.md` before dropping into the deeper bin-write split.
- If the source material says `large bin attack` or `unsorted bin attack`, keep it in the bin corridor before comparing it with freelist or overlap routes.
- If the source material says `house of lore`, keep it in the bin corridor and compare it against other return-first smallbin or unsorted routes before inventing a write-first story.
- If the source material says `tcache stash unlink`, `tcache stash unlink+`, or `tcache stash unlink++`, treat it as the local `tcache_stashing_unlink_attack` branch and open `house-water-and-stash-fengshui.md` for the tcache-count and target-layout algebra before comparing it with generic tcache or smallbin labels.
- If the source material says `no free` or `无 free`, open `how2heap-wilderness-and-arena.md` before inventing a bin route that needs a `free` the binary never exposes.
- If the source material says `house of tangerine`, keep it in the wilderness corridor before widening it into older top-chunk folklore.
- If the source material says `house of force` or `house of orange`, keep it in the wilderness corridor before mixing it with generic overlap or endgame-only labels.
- If the route clusters around top chunk, heap growth, `sysmalloc`, or fake arena state, open `how2heap-wilderness-and-arena.md` before naming a technique.
- If the target version is `2.29+`, treat `overlapping_chunks` and `overlapping_chunks_2` as historical warnings until the exact allocator checks are revalidated.
- If the exact version directory contains both `poison_null_byte` and `house_of_einherjar`, compare them by first stable outcome:
  - overlap only -> `poison_null_byte`
  - controlled return / later tcache poison -> `house_of_einherjar`

## Practical reading order

1. Open the exact `glibc_<version>/technique.c` file when it exists.
2. Compare the nearest older and newer same-name files when it does not.
3. Open `offbynull-heap.md` first when the source material literally says `offbynull-heap` or `off-by-null`.
4. Open `how2heap-legacy-writeup-labels.md` first when the source material is using historical labels such as `offbynull-heap`, `tcache_dup`, `house_of_io`, `house_of_roman`, or `house_of_storm`.
5. Use `scripts/find_how2heap_examples.py` only after the primitive is stated in allocator terms.
6. Open `heap-address-leaks.md` when the route is bottlenecked on in-band heap/libc/stack recovery.
7. Open `how2heap-overlap-nullbyte.md` when the route depends on null-byte, `prev_inuse`, `prev_size`, or backward consolidation semantics.
8. Open `how2heap-fake-free-primitives.md` when the route depends on freeing attacker-controlled non-heap memory or fake chunk headers.
9. Open `how2heap-freelist-primitives.md` when the route depends on fastbin / tcache / metadata freelist behavior.
10. Open `how2heap-safe-linking.md` when the route depends on protected-pointer recovery, synthesis, or avoidance.
11. Open `how2heap-bin-attacks.md` when the route depends on unsorted / smallbin / largebin / stash semantics.
12. Open `house-water-and-stash-fengshui.md` when `house_of_water` or TSU/TSU+/TSU++ heap fengshui is the blocker.
13. Open `how2heap-wilderness-and-arena.md` when the route depends on wilderness growth, `sysmalloc`, or fake-arena behavior.
14. Open `how2heap-mmap-overlap.md` when the route depends on mmap-sized allocations, `munmap`, and later huge-allocation reclamation rather than normal bin reuse.
