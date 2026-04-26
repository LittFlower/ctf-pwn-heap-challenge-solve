# Leak and Endgame Map

Use this file after identifying a plausible allocator primitive. The remaining hard part is often leak recovery, trigger routing, or the final control-flow pivot.

If the source material is still using old names such as `house_of_roman`, open `how2heap-legacy-writeup-labels.md` first, then return here to evaluate the actual leak and endgame demands.

If the notes use underscore forms such as `house_of_apple2`, `house_of_cat`, `house_of_emma`, `house_of_banana`, or `house_of_kiwi`, treat them as the same endgame routes described here and keep the decision focused on trigger surface and version fit rather than naming style.

If the notes say `无 leak` or `no leak`, keep the route in this file and decide whether the real branch is modern metadata-side low-leak control, a historical leakless chain such as `house_of_roman`, or simply a challenge that still needs a leak despite the wording.

## Leak routing

- Heap leak before `2.34`: read freed tcache metadata when possible; the stored key may reveal heap structure directly.
- Heap leak on `2.32+`: decode safe-linked pointers, recover same-page relations, or pivot through metadata control instead of expecting raw `fd`.
- Libc leak with normal `free`: unsorted or large-bin pointers remain the cleanest first choice.
- Libc leak with one useful read: value single-chunk large-bin or unsorted leaks, or partial stdout corruption.
- No easy libc leak: route through `house_of_water` or related tcache-perthread corruption to land a libc pointer in controlled metadata, then pivot into stdout.
- If `tcache_perthread_struct` itself was forged and freed into unsorted for the libc leak, assume the leak step also corrupted `counts[]`. Repair the per-thread metadata before treating `environ` or another tcache-poison target as live.
- If a writable slot table or stale pointer array can be retargeted, try routing it into `stdout`, `stderr`, `environ`, or another pointer-bearing object before assuming a full FSOP setup is required.
- Do not count `/proc`, debugger bases, or helper-library metadata as leak routing. Use them only to validate a local hypothesis while you keep an in-band address-recovery plan alive.

## Leakless or low-leak modern routes

- `house_of_water`: use when UAF, overlap, or metadata reach exists but direct leak setup is awkward.
- `house_of_rust`: use when a TSU-style path can place libc data into tcache metadata and partial overwrites are acceptable.
- Partial-pointer brute force: reserve for cases where only low bits are missing and the retry budget is realistic.
- A guessed-PIE oracle is not a finish by itself. Measure the real retry throughput before committing to brute force; if missing entropy is still roughly 24 bits, treat it as a blocker, not a plan.
- If the source material says `无 leak` or `no leak`, verify whether it really means metadata-side low-leak steering or only "no easy leak was found yet."

## Historical leakless route

- `house_of_roman`: keep only for old hook-era libc where fake fastbins, unsorted-bin writes, and relative overwrites can still drive a leakless brute-force finish. Treat it as a historical combined chain, not as a modern default.

## No-`free` routing

- `house_of_tangerine`: use when the program can keep allocating but never frees, and the old wilderness can be turned into a tcache-style chosen-pointer return.
- `sysmalloc_int_free`: use when top-chunk manipulation routes allocator state into a reusable free path, but the later tcache-poison bridge or chosen-pointer return is not proved yet.
- Old `house_of_force`: keep only for pre-`2.29` targets that actually match the old wilderness assumptions.

## Trigger routing

- If the stale heap object itself contains a callback, vtable, or function pointer that a later menu action calls, treat that application-level call site as the first endgame candidate. A non-PIE PLT target plus a stable string or controlled argument can remove the need for libc leaks, hooks, or FSOP.
- If the binary will call `free` again and libc is old enough, hook-style finishes may still be the shortest route.
- If the binary exits cleanly, treat exit-linked targets such as `_IO_list_all`, `tls_dtor_list`, or `link_map` as first-class candidates.
- If the binary keeps printing or flushing, value stdout or FILE-based pivots.
- If the binary uses `scanf` or stdio input after corruption, consider stdin or FILE-based arbitrary-write pivots.
- If later input is only raw `read` or another non-stdio path, do not treat that alone as a surviving stdin FILE pivot trigger.
- If the source material says `_fileno`, stdin/stdout arbitrary read/write, or old `FSOP`, open `libio-stdio-primitives.md` before ranking Apple-family routes against historical `_IO_str_*` dispatch.
- If redirected fd use through `_fileno` already solves the challenge goal, keep it as the primary route instead of automatically escalating into a heavier Apple-family or generic FILE endgame.
- If `environ` or another stack pointer becomes readable and a clean return site remains, treat stack-return ROP as a first-class endgame candidate.
- After a per-thread-struct unsorted leak, `environ` plus saved-return overwrite is often the cleanest follow-up, but only if the later poison uses chunks outside the forged large-chunk span and the corrupted tcache metadata has been repaired first.
- If `__malloc_assert -> fflush(stderr)` still exists on the shipped libc, treat `house of kiwi` as a trigger surface into later IO exploitation.
- If the real trigger is allocator abort into `malloc_printerr` on an old writable-GOT target, treat `strlen@GOT`-style retargets as narrow trigger helpers only. They can provide a call edge, but their argument control is usually much weaker than normal FSOP or stack-return routes.

## Modern endgame defaults

- Prefer `house of apple2` as the default modern FSOP route when you can corrupt `_IO_list_all` or a FILE pointer.
- If the only arbitrary write is a single `largebin attack`, prefer `apple2` layouts where the written heap address already points to the fake FILE carrier. Do not spend the only write on `_IO_list_all` unless the carrier is already staged at that heap address.
- If `_wide_data` is hard to control cleanly but `_codecvt` is writable, compare an Apple3-style route before abandoning FILE-based finishes.
- Prefer `house of cat` only when `apple2` is blocked and the version-specific conditions are acceptable.
- Treat `house of emma` as higher-cost: it usually needs point-guard control plus stderr routing.
- Treat `house of banana` as strong when a `link_map` or fini-array style surface is already reachable.
- Treat `tls_dtor_list` as an exit-linked option when pointer mangling can be satisfied cleanly.

## Practical preferences

- Prefer a direct stale-struct call hijack over allocator-heavy finishes when it needs no leak and has a deterministic trigger.
- Prefer a direct pointer-table rewrite into `environ` plus saved-RIP control over allocator-heavier FSOP when the primitive already reaches a stable global slot table and the stack trigger is clean.
- Prefer a stable leak plus a stable FSOP route over a fragile one-shot `system` write.
- Prefer `apple2` over `cat` when both are possible.
- Prefer a route with an obvious later trigger over a theoretically cleaner primitive with no execution surface.
- State the exact trigger you are saving for: `exit`, `malloc`, `free`, `puts`, `fflush`, `scanf`, or C++ stream flush.
