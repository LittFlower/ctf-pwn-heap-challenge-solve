# Core Postmortem Validation

Use this when:
- live GDB attach is flaky because of `alarm`, short-lived inferiors, or PTY-driven launcher state
- the exploit already produces a crash or core after a likely successful heap or FSOP stage
- you need to prove post-execution facts such as `_IO_list_all` overwrite, fake FILE placement, or a finished ORW chain

If the route is really stdin/stdout field corruption, `_fileno` redirection, or another old stdio-field path, validate the live stream fields that should have changed before defaulting to fake-FILE or Apple-style postmortem checks.

The point is not just “open the core and look around”. The point is to answer a small set of yes/no
questions that close the proof loop after a partial-success crash.

## What core is good for

Core is especially strong at proving:
- the target write really landed
- the forged FILE or fake object is where the exploit expected
- the ROP / ORW buffer contains the expected chain
- the flag or other output buffer was already filled before the crash
- the final crash came after the intended side effect, not before it

Core is weaker at proving:
- transient allocator state before a write site
- exact largebin membership just before insertion
- race-sensitive live control flow

Use MI live debugging for transition proofs and core for postmortem closure.

## Minimal postmortem checklist

For a modern FSOP or heap-to-ROP chain, record:
- the expected target address after the allocator write
- the expected fake object base
- the expected ROP / ORW base
- the expected output buffer
- the expected post-success crash shape

For old stdio-field routes, record instead:
- the expected stream object (`stdin`, `stdout`, or another live `FILE *`)
- the expected redirected fd or staged read/write window
- the exact fields that should have changed, such as `_fileno`, `_IO_write_base`, `_IO_write_ptr`, `_IO_buf_base`, or `_IO_buf_end`
- the expected consuming stdio helper and intended read/write direction
- the expected side effect before the crash, such as redirected input, leaked output, or a completed write window

For historical `_IO_str_finish` / `_IO_str_overflow` claims, record in addition:
- the exact old-libc window being claimed
- whether the route depends on old `_s._allocate_buffer` / `_s._free_buffer` assumptions rather than modern `malloc/free`

Then check, in this order:

1. Target pointer overwrite
- Example: `_IO_list_all`, a FILE pointer, `tls_dtor_list`, or a vtable field
- Ask: does it now point at the controlled heap object?

2. Fake object fields
- Example for `apple2`:
  - `_lock`
  - `_wide_data`
  - vtable
  - the exact indirect-call slot reached by the shipped libc path
- Ask: do the critical offsets match the crafted payload?

3. Staged data
- Example:
  - `/flag` path string
  - stack pivot gadget
  - ORW buffer
  - final output buffer contents
- Ask: are these buffers populated exactly where the exploit expected?

4. Crash-after-success signature
- Example:
  - `syscall; ret` executed and the next return address is `0`
  - output buffer contains the flag even though RIP is now invalid
- Ask: did the intended side effect happen before the process died?

## Suggested command shape

Treat this as a compact checklist, not a mandatory exact script:

1. Load the program and core.
2. Read the target pointer that should have been overwritten.
3. Dump the fake object region.
4. Dump the staged ROP / ORW region.
5. Dump the expected output buffer.
6. Inspect registers and the top of stack near the crash.
7. Decide whether the crash is pre-effect or post-effect.

## Common conclusions

- target pointer changed, fake object valid, output buffer empty
  - execution reached the pivot setup but not the intended syscall path

- target pointer changed, fake object valid, output buffer contains the flag
  - the exploit already succeeded; the remaining bug is end-of-chain cleanup

- target pointer unchanged
  - the heap primitive did not land; return to allocator proof

- fake object partly valid but key field wrong
  - payload placement or base computation is wrong

- registers point into the staged chain and RIP is `0`
  - the chain advanced and then fell off the end; add a controlled final return only if cleanliness matters
