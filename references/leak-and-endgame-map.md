# Leak and Endgame Map

Use this file after identifying a plausible allocator primitive. The remaining hard part is often leak recovery, trigger routing, or the final control-flow pivot.

## Leak routing

- Heap leak before `2.34`: read freed tcache metadata when possible; the stored key may reveal heap structure directly.
- Heap leak on `2.32+`: decode safe-linked pointers, recover same-page relations, or pivot through metadata control instead of expecting raw `fd`.
- Libc leak with normal `free`: unsorted or large-bin pointers remain the cleanest first choice.
- Libc leak with one useful read: value single-chunk large-bin or unsorted leaks, or partial stdout corruption.
- No easy libc leak: route through `house_of_water` or related tcache-perthread corruption to land a libc pointer in controlled metadata, then pivot into stdout.
- If a writable slot table or stale pointer array can be retargeted, try routing it into `stdout`, `stderr`, `environ`, or another pointer-bearing object before assuming a full FSOP setup is required.
- Do not count `/proc`, debugger bases, or helper-library metadata as leak routing. Use them only to validate a local hypothesis while you keep an in-band address-recovery plan alive.

## Leakless or low-leak modern routes

- `house_of_water`: use when UAF, overlap, or metadata reach exists but direct leak setup is awkward.
- `house_of_rust`: use when a TSU-style path can place libc data into tcache metadata and partial overwrites are acceptable.
- Partial-pointer brute force: reserve for cases where only low bits are missing and the retry budget is realistic.
- A guessed-PIE oracle is not a finish by itself. Measure the real retry throughput before committing to brute force; if missing entropy is still roughly 24 bits, treat it as a blocker, not a plan.

## No-`free` routing

- `house_of_tangerine`: use when the program can keep allocating but never frees.
- `sysmalloc_int_free`: use when top-chunk manipulation can still route allocator state into a reusable free path.
- Old `house_of_force`: keep only for pre-`2.29` targets that actually match the old wilderness assumptions.

## Trigger routing

- If the stale heap object itself contains a callback, vtable, or function pointer that a later menu action calls, treat that application-level call site as the first endgame candidate. A non-PIE PLT target plus a stable string or controlled argument can remove the need for libc leaks, hooks, or FSOP.
- If the binary will call `free` again and libc is old enough, hook-style finishes may still be the shortest route.
- If the binary exits cleanly, treat exit-linked targets such as `_IO_list_all`, `tls_dtor_list`, or `link_map` as first-class candidates.
- If the binary keeps printing or flushing, value stdout or FILE-based pivots.
- If the binary uses `scanf` or stdio input after corruption, consider stdin or FILE-based arbitrary-write pivots.
- If `environ` or another stack pointer becomes readable and a clean return site remains, treat stack-return ROP as a first-class endgame candidate.
- If `__malloc_assert -> fflush(stderr)` still exists on the shipped libc, treat `house of kiwi` as a trigger surface into later IO exploitation.

## Modern endgame defaults

- Prefer `house of apple2` as the default modern FSOP route when you can corrupt `_IO_list_all` or a FILE pointer.
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
