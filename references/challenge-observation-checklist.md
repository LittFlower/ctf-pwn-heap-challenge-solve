# Challenge Observation Checklist

Use this file before naming any technique. Normalize the program surface first, then map it to allocator facts.

Use it to capture target-specific observations and unknowns, not to store reusable anti-patterns or solver lessons. Put recurring mistakes in `gotchas.md` instead.

## Menu surface

- Record every operation and its real effect: `malloc`, `calloc`, `realloc`, `free`, show-only read, append, offset edit, or full rewrite.
- Record whether the writable target is normal chunk user data or a long-lived libc/application object such as `FILE`, `_IO_wide_data`, `_codecvt`, or a C++ stream wrapper.
- Record whether any menu action defers work to a worker thread, queue, signal handler, or background callback instead of acting entirely in the calling thread.
- Record whether the index table lives in `.bss`, heap, stack, or mixed storage.
- Record whether freed pointers stay reachable through stale indexes, copied aliases, or secondary containers.
- Record whether a stale slot table or pointer array can later be overwritten or repointed. A writable `.bss` slot table can become an address router (`pointer router`) rather than just bookkeeping.
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
- If the hoped-for leak is through writable `stdout`, record whether later output still goes through stdio helpers like `puts`, `printf`, or `fwrite`, or only through raw `write`/`send`; raw fd writes do not consume `stdout FILE` state directly.
- If the hoped-for leak is through writable `stdout`, record the effective buffering mode as observed in the shipped target path: full buffering, line buffering, or unbuffered. This changes whether the practical edge is `_IO_buf_end` or an `_IO_write_ptr`-collapsed line-buffered path.
- If the hoped-for leak is through writable `stderr` or another already-live output stream, record the actual consuming helper or assert/flush path and do not assume stdout-style newline/full-buffer triggering without proving it on the shipped target.
- If the hoped-for write primitive is through writable `stdin`, record whether later input still goes through stdio helpers like `scanf`, `fgets`, or `getc`, or only through raw `read`; raw fd reads do not consume `stdin FILE` state directly.
- Record whether `show` is repeatable, single-shot, or format-string-like.
- If a live stream object such as `stdin`, `stdout`, or another already-open `FILE *` is writable, record whether later code still consumes that same stream through stdio helpers, and whether the source material is really pointing at `_fileno`, stdin/stdout arbitrary read/write, or old `_IO_str_*` notes rather than a generic modern FILE route.
- If `_fileno` redirection is in play, record whether the desired target fd is already open in the process and which later stdio helper still reads from or writes to that same live stream object.
- If stdout-style partial leakage is in play, record what actually forces the later flush or overflow: newline, line-buffering, full buffer, explicit `fflush`, clean `exit`, or another stdio walk.

## Allocator surface

- Record every reachable size class, especially whether you can fill a tcache bin with 7 chunks.
- Record which thread performs each attacker-relevant `malloc` or `free`. Tcache reuse assumptions are invalid until allocator ownership is known.
- If a runtime knob changes sizes, write the exact real chunk sizes for the entire legal knob range, not just the first interesting candidate.
- Record whether `calloc` is reachable. `calloc` can skip normal tcache pops and make stash flows easier.
- Record whether `free` is reachable at all. If not, plan around top chunk or `sysmalloc`.
- If there is no user-reachable `malloc` or `free` path but a libc-managed object is writable, map the write window to exact object fields and stop treating the task as ordinary chunk grooming.
- Record whether you can create guard chunks to prevent consolidation.
- Record whether you can force large allocations that move unsorted chunks into large bins.
- Record whether one stale or overlapping write window can simultaneously reach largebin metadata such as `bk_nextsize` and the body or header of a later carrier chunk. This decides whether one-write largebin-plus-FILE routes are even plausible.

## Leak surface

- Record whether unsorted or large-bin pointers can be shown directly.
- Record whether freed tcache entries can be read back for heap leaks.
- Record whether stdout or stderr pointers are writable or re-pointable.
- Record whether a writable global pointer table can be repointed to `stdout`, `stderr`, `environ`, or another already-live pointer-bearing object.
- Record whether candidate leaks are in-band or only available through `/proc`, a debugger, `io.libs()`, or other same-host metadata. Do not confuse local validation visibility with a real challenge leak.
- Record which runtime address classes the intended route actually needs: heap, libc, PIE, stack, pointer guard, or none. If a class is needed and not yet recoverable in-band, mark it as an open requirement instead of silently borrowing it from local metadata.
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
