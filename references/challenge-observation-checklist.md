# Challenge Observation Checklist

Use this file before naming any technique. Normalize the program surface first, then map it to allocator facts.

## Menu surface

- Record every operation and its real effect: `malloc`, `calloc`, `realloc`, `free`, show-only read, append, offset edit, or full rewrite.
- Record whether the writable target is normal chunk user data or a long-lived libc/application object such as `FILE`, `_IO_wide_data`, `_codecvt`, or a C++ stream wrapper.
- Record whether any menu action defers work to a worker thread, queue, signal handler, or background callback instead of acting entirely in the calling thread.
- Record whether the index table lives in `.bss`, heap, stack, or mixed storage.
- Record whether freed pointers stay reachable through stale indexes, copied aliases, or secondary containers.
- Record whether a stale slot table or pointer array can later be overwritten or repointed. A writable `.bss` slot table can become an address router rather than just bookkeeping.
- If a slot table may become a router, record which slot keeps a non-zero size or other writable-state bit after the retarget. A repointed pointer with a dead length field may still be unreadable or uneditable through the menu.
- Record whether allocation size, edit size, and shown length are independently controlled.
- Record whether a user-controlled knob such as `key` or difficulty changes all later allocation sizes.
- Record whether chunk reuse is immediate or gated by a state bit, reference count, or menu logic.

## I/O semantics

- Identify the actual input function: `read`, `fgets`, `gets`, `scanf("%s")`, `scanf("%c")`, `getline`, `memcpy`, `strcpy`, or custom parsing.
- Record whether newline, `NUL`, EOF, or spaces truncate or append bytes automatically.
- Record the allowed byte alphabet for the write primitive. `NUL` or newline rejection can turn an apparent arbitrary write into a constrained partial-overwrite problem.
- Record whether the command parser uses fixed-width short reads plus `atoi`-style parsing. If yes, verify whether `sendline` and fixed-width padded sends behave differently.
- Record whether fixed-width `read` returns after a short send or blocks until the whole width arrives. This determines whether a transport is full-clobber or low-clobber.
- Record whether partial writes, offset writes, or length confusion exist.
- Record whether output uses `puts`, `printf`, `write`, C++ streams, or buffered stdio.
- Record whether `show` is repeatable, single-shot, or format-string-like.

## Allocator surface

- Record every reachable size class, especially whether you can fill a tcache bin with 7 chunks.
- Record which thread performs each attacker-relevant `malloc` or `free`. Tcache reuse assumptions are invalid until allocator ownership is known.
- If a runtime knob changes sizes, write the exact real chunk sizes for the entire legal knob range, not just the first interesting candidate.
- Record whether `calloc` is reachable. `calloc` can skip normal tcache pops and make stash flows easier.
- Record whether `free` is reachable at all. If not, plan around top chunk or `sysmalloc`.
- If there is no user-reachable `malloc` or `free` path but a libc-managed object is writable, map the write window to exact object fields and stop treating the task as ordinary chunk grooming.
- Record whether you can create guard chunks to prevent consolidation.
- Record whether you can force large allocations that move unsorted chunks into large bins.

## Leak surface

- Record whether unsorted or large-bin pointers can be shown directly.
- Record whether freed tcache entries can be read back for heap leaks.
- Record whether stdout or stderr pointers are writable or re-pointable.
- Record whether a writable global pointer table can be repointed to `stdout`, `stderr`, `environ`, or another already-live pointer-bearing object.
- Record whether candidate leaks are in-band or only available through `/proc`, a debugger, `io.libs()`, or other same-host metadata. Do not confuse local validation visibility with a real challenge leak.
- Record whether stack, PIE, or libc pointers are already present in a printable structure.
- Record whether the program gives only one useful leak and whether it must recover both heap and libc.
- If the leak budget is tiny, prefer candidate size sets that make one read recover both heap and libc.

## Trigger surface

- Record whether the program exits cleanly through `exit`.
- Record whether normal exit, menu quit, or abort paths imply an `fflush` or other buffered-stdio walk even if the code never calls `fflush` directly.
- Record whether later code still calls `free`, `malloc`, `calloc`, `puts`, `fflush`, `scanf`, or C++ flush routines after corruption.
- Record whether later code calls `rewind`, `fseek`, `fclose`, wide-conversion helpers, or other stream operations that consume corrupted `FILE` / libio subfields.
- Record whether the first worker-thread startup is lazy and whether you can trigger it before measuring a precise heap layout.
- Record whether you can force one more `malloc` after corrupting top chunk metadata.
- Record whether a target address must satisfy side conditions such as `target+0x18` being writable.
- Record whether `alarm` or watchdog logic may make live attach or long debugger sessions unreliable.

## Version-sensitive notes

- Record whether the exact libc is known or only bracketed.
- Record whether hooks still exist.
- Record whether safe-linking applies.
- Record whether `tcache_key` is a heap pointer or randomized.
- Record whether a `kiwi`-style `__malloc_assert -> fflush(stderr)` trigger is even possible on this libc.

## Working notes format

Write the first pass in this structure:

1. Menu and input facts.
2. Allocator version and mitigations.
3. Primitive candidates.
4. Leak options.
5. Trigger options.
6. Hard preconditions and unknowns.
