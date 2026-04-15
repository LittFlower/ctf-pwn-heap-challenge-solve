---
name: ctf-pwn-heap-challenge-solve
description: >
  Use this skill when the user asks to "solve this heap challenge", "analyze this
  glibc heap exploit", "debug this largebin corruption", "map this UAF to a
  working technique", "route this double free", or "find a no-free or leakless
  heap path". Activate when the main task is a Linux glibc heap-pwn challenge
  and Codex must analyze use-after-free, double free, off-by-one/null overwrite,
  heap overflow into size or bin metadata, arbitrary free, overlap, leakless
  tcache abuse, no-free top-chunk paths, or modern FSOP / exit-linked heap
  chains, then recover allocator facts, prove one stable primitive, compare
  version-compatible how2heap families, and choose a leak or endgame route that
  matches the shipped libc and trigger surface.
---

# CTF Pwn Heap Challenge Solve

Version-aware workflow for glibc heap CTF challenges: normalize the surface,
prove one allocator primitive, then finish with a compatible leak or endgame.
Optimize for solving speed only when the same proof and validation standard is preserved.

## Always Read

These files apply to every heap-solving task. Read them first:
1. `rules/heap-solving-principles.md`
2. `rules/allocator-version-rules.md`
3. `rules/output-contract.md`

## Common Tasks

Each task lists the exact files to read before acting:

- First-pass challenge solve → read `references/challenge-observation-checklist.md`, `references/version-delta.md`, and `references/primitive-version-map.md`; follow `workflows/solve-heap-challenge.md`
- Select the nearest local `how2heap` family from challenge signals → read `references/how2heap-selector.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; use `scripts/find_how2heap_examples.py`
- Choose an in-band heap / libc / stack address leak route → read `references/heap-address-leaks.md`, `references/challenge-observation-checklist.md`, and `references/leak-and-endgame-map.md`; follow `workflows/solve-heap-challenge.md` or `workflows/choose-endgame.md`
- Translate historical or community writeup labels into current allocator families → read `references/how2heap-legacy-writeup-labels.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Translate an `offbynull-heap` bug label into the right allocator family → read `references/offbynull-heap.md`, `references/how2heap-overlap-nullbyte.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md` or `workflows/prove-primitive.md`
- Route leakless off-by-null overlap or modern `poison_null_byte` geometry → read `references/offbynull-heap.md`, `references/how2heap-overlap-nullbyte.md`, `references/version-delta.md`, and `references/largebin-geometry-checklist.md`; follow `workflows/prove-primitive.md`
- Route a largebin-only menu surface with overlap/UAF into `_mp.tcache_bins` overwrite and out-of-range tcache poisoning → read `references/how2heap-bin-write-primitives.md`, `references/how2heap-safe-linking.md`, `references/heap-address-leaks.md`, and `references/largebin-geometry-checklist.md`; follow `workflows/route-mp-tcache-bins-to-oob-tcache.md`
- Route fastbin / tcache / metadata-freelist labels, including `tcache_dup`, `tcache dup`, `house_of_io`, `house_of_botcake`, `house_of_kauri`, `fastbin reverse into tcache`, `house_of_atum`, `house_of_water`, or `tcache_perthread_struct` hijack → read `references/how2heap-freelist-primitives.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Normalize mixed cheatsheet labels that may span multiple corridors, such as `unsafe unlink`, `tcache dup`, `house_of_atum`, or `no leak` → read `references/how2heap-selector.md`, `references/how2heap-overlap-nullbyte.md`, `references/how2heap-freelist-primitives.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Route scenario-first cheatsheet cues such as `double free`, `single-shot show`, `no leak`, or `no free` into the right family → read `references/how2heap-selector.md`, `references/heap-address-leaks.md`, `references/how2heap-freelist-primitives.md`, and `references/how2heap-wilderness-and-arena.md`; follow `workflows/solve-heap-challenge.md`
- Translate historical mixed leakless labels such as `house_of_roman` → read `references/primitive-version-map.md`, `references/leak-and-endgame-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md` or `workflows/choose-endgame.md`
- Route unsorted / smallbin / largebin / stash labels, including `house_of_lore`, `large bin attack`, `unsorted bin attack`, `tcache stash unlink`, or `house_of_storm` → read `references/how2heap-bin-attacks.md`, `references/how2heap-bin-write-primitives.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md` or `workflows/prove-primitive.md`
  Treat `large_bin_attack` as live only after proving a post-free metadata write into the largebin-resident chunk, usually via UAF, overlap, or stale edit. Largebin residency alone is not a route.
- Route single-write `largebin attack` plus fake-FILE / `house_of_apple2` co-design → read `references/how2heap-bin-write-primitives.md`, `references/largebin-geometry-checklist.md`, `references/house-of-apple2.md`, and `references/leak-and-endgame-map.md`; follow `workflows/prove-primitive.md`, then `workflows/choose-endgame.md`
- Route constrained `house of apple` branches such as `_wide_data`-first or `_codecvt`-first FILE finishes → read `references/house-of-apple-family.md`, `references/house-of-apple2.md`, `references/libio-object-corruption.md`, and `references/leak-and-endgame-map.md`; follow `workflows/choose-endgame.md`
- Resolve null-byte overlap / backward-consolidation families such as `house_of_einherjar` → read `references/how2heap-overlap-nullbyte.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md` or `workflows/prove-primitive.md`
- Resolve mmap-overlap families for huge mmapped allocations → read `references/how2heap-mmap-overlap.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Resolve fake-free / House of Spirit families such as `house_of_spirit` → read `references/how2heap-fake-free-primitives.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md` or `workflows/prove-primitive.md`
- Resolve safe-linking / protected-pointer families → read `references/how2heap-safe-linking.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Resolve wilderness / top-chunk / fake-arena families such as `house_of_tangerine`, `house_of_force`, or `house_of_orange` → read `references/how2heap-wilderness-and-arena.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Heap-labeled target with writable `FILE` / libio object or wide-stream trigger → read `references/challenge-observation-checklist.md`, `references/libio-object-corruption.md`, and `references/leak-and-endgame-map.md`; follow `workflows/solve-heap-challenge.md`, then `workflows/choose-endgame.md`
- Threaded heap target or cross-thread tcache suspicion → read `references/challenge-observation-checklist.md`, `references/threaded-allocator-pitfalls.md`, and `references/leak-and-endgame-map.md`; follow `workflows/solve-heap-challenge.md`, then `workflows/choose-endgame.md` if the finish depends on same-size reuse or poisoning
- Prove or debug a heap primitive → read `references/largebin-geometry-checklist.md`, `references/gdb-mi-heap-proof-loop.md`, and `references/core-postmortem-validation.md`; follow `workflows/prove-primitive.md`
- Decode an allocator abort or corruption check → read `references/version-delta.md` and `references/gdb-mi-heap-proof-loop.md`; follow `workflows/debug-allocator-failure.md`
- Choose a leak, FSOP, or exit-linked finish, including `house_of_apple2`, `house_of_cat`, `house_of_emma`, `house_of_banana`, or `house_of_kiwi` style endgame labels → read `references/leak-and-endgame-map.md` and `references/house-of-apple2.md`; follow `workflows/choose-endgame.md`
- Audit a local-only known-base or debugger-assisted finish and convert it into an in-band leak route → read `references/challenge-observation-checklist.md`, `references/leak-and-endgame-map.md`, and `rules/output-contract.md`; follow `workflows/choose-endgame.md`
- Search local `how2heap` coverage → read `references/how2heap-taxonomy.md`; use `scripts/find_how2heap_examples.py`
- Record a new lesson after solving a challenge → read `references/gotchas.md`; follow `workflows/update-rules.md`
- Optimize this skill from live solve feedback → read `references/gotchas.md`, `workflows/update-rules.md`, and `workflows/maintain-docs.md`; follow `workflows/update-rules.md`, then `workflows/maintain-docs.md` if routing or file boundaries should change
- Reshape this skill when docs drift or bloat → read `workflows/maintain-docs.md`
- Other or unclear heap task → read the Always Read files, then pick the closest workflow above before improvising

## Known Gotchas

- Menu transport can invalidate the heap model. Verify fixed-width `read` plus `atoi` parsing before blaming chunk geometry.
- Fixed-width `read` does not imply a full-width write. Prove whether short sends return early or block; that difference can create a low-clobber transport or kill a planned overwrite.
- A heap label does not guarantee allocator gameplay. If the live writable object is `FILE` / libio state, switch to object-layout and trigger-path modeling before touching `how2heap`.
- Once `ELF.address` / `libc.address` is set in pwntools, `ELF.sym[...]` is already absolute. Re-adding the base yields non-canonical targets and fake primitive failures such as `EFAULT` on the final write.
- For Apple2 and other libio routes, do not start from inherited fake-FILE templates such as `stderr-0x10`, `fp+0x68`, or copied callback slots. Reverse the shipped libc consumer path first, then derive the exact indirect-call slot from that path.
- If `_wide_data` control is fragile but `_codecvt` is writable, do not force an Apple2 layout. Re-check whether an Apple3-style `_codecvt` route keeps more default FILE state intact.
- If only one largebin write exists, do not treat “overwrite `_IO_list_all`” and “place fake FILE” as separate tasks. The written heap address should usually already be the carrier chunk whose contents you control.
- If a largebin write targets `mp_.tcache_bins`, remember that widening the valid `tc_idx` range does not create a spare tcache entry. Plan the out-of-range poison with at least two same-size frees and account for `tcache_get` clearing `target+0x8`.
- Do not route to `large_bin_attack` just because a chunk can be sorted into largebin. Modern largebin write routes need attacker-controlled post-free metadata mutation on the largebin chunk, typically a UAF, overlap, or stale edit that reaches `bk_nextsize`.
- Keep slot/handle state separate from physical chunk state. A stale alias is not a live chunk.
- Leakless off-by-null overlap is usually `poison_null_byte`, not `house_of_einherjar`. If the route does not start with a known fake-chunk base and only needs overlap, prove backward-consolidation overlap first.
- If a stale slot table lives in `.bss` and can be retargeted through a heap primitive, treat it as a pointer router immediately. It may produce arbitrary known-address read/write, `environ` leaks, or a stack-return finish before any heavier FSOP plan.
- A pointer router is constrained by UI state too. Before planning follow-up `edit` or `show` calls through a repointed slot table, prove which slot still has non-zero tracked size and enough write width; the prettiest retarget can still be a logical no-op.
- Do not let `/proc`, a debugger, or `io.libs()` become the leak plan. They are acceptable for local validation, but a real solve still needs an in-band address-recovery route unless the challenge environment itself fixes the bases.
- Default to a remotely viable exploit path. Treat fixed local offsets, `/proc`, debugger memory, and same-host helper metadata as validation aids unless the challenge is explicitly local-only or the remote environment guarantees the same bases.
- Do not invent a `2.42` boundary for official `poison_null_byte`. Local how2heap coverage keeps the maintained `2.41` example working on `2.42`; `2.43` is where the official example adds a tcache-metadata warmup and may shift low-byte alignment assumptions.
- Before spending time on heavier exit-linked surfaces such as `__exit_funcs`, `tls_dtor_list`, or `link_map`, inventory whether clean exit already gives a stdio walk. Prefer the lower-assumption trigger first.
- Tcache is thread-local. If worker threads free or allocate target chunks, do not assume main-thread reuse or poisoning until allocator ownership is proved.
- The first worker-thread startup can perturb heap layout. If thread creation is lazy, warm it up before trusting a leak or remainder geometry.
- A freed heap object with a callable field can be the endgame. Before planning hook writes or poisoning, check whether tcache reuse can overwrite a stale struct's callback, vtable, or function pointer and whether the binary already has a stable call target.
- For largebin or fake-free plans, write the invariant table before coding. If two metadata roles overlap, treat it as a blocker.
- After a modern largebin attack, do not assume the attacked largebin chunk is immediately safe to reclaim. If `bk_nextsize` still points into the write target, first reclaim the smaller same-bin helper chunk and repair the survivor back to a self-loop.
- If live attach is flaky because of alarms, short-lived children, or PTYs, switch early to core-based validation.

## Rule Priority

1. `SKILL.md`
2. `rules/`
3. `workflows/`
4. `references/`
5. `scripts/`

## Project Boundaries

- This skill covers Linux glibc heap-pwn solving, not generic web, crypto, kernel, or non-heap exploit work.
- It still applies when a heap-labeled glibc challenge collapses into `FILE` / libio object corruption instead of classic allocator grooming, as long as the exploit surface and finish are still libc-heap-oriented.
- Use `ctf-reverse` first if the main blocker is understanding what the binary does rather than allocator behavior.
- Treat `how2heap` as a versioned behavior atlas, not as exploit stock to paste blindly.
- Prefer the smallest provable primitive and the most stable finish over aesthetically pleasing but assumption-heavy chains.
