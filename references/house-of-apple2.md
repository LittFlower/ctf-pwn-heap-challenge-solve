# House Of Apple2

Use this after `house-of-apple-family.md` already says the route is really `apple2` and the heap phase is already strong enough to:
- overwrite `_IO_list_all` or another FILE pointer
- place a controlled fake FILE on heap
- supply a later flush / exit / stdio trigger

This file is not a full history of FSOP. It is a compact operator checklist for modern glibc-style
`apple2` routes.
If the source material is really about `_fileno`, stdin/stdout arbitrary read/write, or historical `_IO_str_*` dispatch, leave this file and open `libio-stdio-primitives.md` first.

If `_wide_data` is not the clean controllable seam, go back and compare `apple3` in `house-of-apple-family.md` instead of forcing this layout.

## Scope

Prefer this route when:
- hooks are gone or unattractive
- the target libc is modern enough that FILE-based routing is more realistic than hook abuse
- a heap arbitrary write naturally lands on `_IO_list_all`
- the binary still reaches a stdio-linked trigger after corruption

Do not use this file as a substitute for exact version checks. Re-derive sensitive offsets from the
shipped libc.
Do not import historical fake-FILE base shifts or callback-slot folklore from old notes. Start from
the shipped libc's real `fflush` / wide-file consumer path and derive the final indirect call from
that path.

## Minimal prerequisites

Before choosing `apple2`, confirm all of:
- a controlled heap object can survive until the trigger
- `_IO_list_all` or a comparable FILE pointer can be redirected to that object
- the fake object can hold:
  - `_lock`
  - `_wide_data`
  - vtable
  - the chosen jump target or stack pivot staging area
- the trigger surface still exists after corruption

Typical trigger surfaces:
- clean program exit
- another stdio flush
- a later menu action that causes glibc to walk FILE structures

## Generic fake FILE checklist

At minimum, resolve these fields relative to the fake FILE base:

| Field | Why it matters |
| --- | --- |
| `_flags` | Keep it non-fatal for the intended path |
| `_IO_read_ptr` or equivalent gate field | Satisfy the path predicate that reaches the vtable call |
| `_IO_buf_base` / staged pointer field | Point to the ROP / ORW region when the path consumes it |
| `_lock` | Must be readable / writable enough for the chosen route |
| `_wide_data` | Often needed to keep the wide path coherent |
| vtable | Must point at the intended FILE jump table |
| verified indirect-call slot | Must match the actual slot the shipped libc dereferences on this path; often this lives under `_wide_data` rather than in the `FILE` object itself |

Do not trust old offsets blindly. Derive them from the shipped libc and verify them in memory.

## Common modern route shape

One practical pattern is:
1. use a heap primitive such as largebin attack to overwrite `_IO_list_all`
2. place fake FILE on heap
3. point its vtable to `_IO_wfile_jumps` or another version-appropriate table
4. re-derive the actual indirect call reached by the shipped path, often through `_wide_data->_wide_vtable`, and place the pivot or call target there
5. trigger exit or flush

Treat the exact jump target as version-sensitive. The important part is not the historical name of
the gadget, but that:
- the call site is reachable from the chosen FILE path
- the consumed registers or fields are satisfiable from your fake object
- the pivot lands inside your controlled staging region

## Single-write largebin carrier pattern

When the target gives only one allocator write such as one `largebin attack`, do not model the route as:

1. overwrite `_IO_list_all`
2. somehow place fake FILE later

Model it as:

1. design a carrier chunk `B` whose heap address is itself the value you want largebin to write
2. use the stale or overlapping write on largebin chunk `A` to both retarget `A->bk_nextsize` and finish the metadata or placement needed for `B`
3. trigger insertion of `B` so `_IO_list_all` becomes the carrier address in the same step

This pattern matters because the single largebin write gives you only a heap address, not a full fake-FILE payload write. The payload must already live at the written address.

Checklist:
- the route already has `heap` and `libc` bases
- `_IO_list_all` is the right target for the shipped trigger surface
- the carrier chunk survives until `exit` / flush
- the address written by largebin is exactly the fake FILE base, or a stable pointer the consumer will dereference into the fake FILE
- `_wide_data`, `_lock`, vtable, and staged chain fit in the carrier after any heap-metadata bytes you had to sacrifice for the largebin setup
- if the route relies on `_wide_data` to mutate another target before the final indirect call, prove that this second target does not require another arbitrary write

Common wrong model:
- "largebin attack writes `_IO_list_all`; fake FILE is a later step"

Stronger model:
- "`largebin attack` writes `_IO_list_all` to an already-prepared fake FILE carrier"

## ORW staging checklist

If the finish is ORW rather than `system`:
- store the path string at a stable controlled address
- store the pivot gadget and chain at a stable controlled address
- identify the final output buffer location
- keep the final `ret` behavior in mind; many successful chains still crash after the last syscall

For postmortem validation, record:
- fake FILE base
- staged path string address
- pivot gadget address
- syscall gadget address
- final output buffer address

## What to verify in debugger or core

Before the trigger:
- `_IO_list_all` still points to normal libc state
- fake FILE region matches the crafted payload

After the trigger or in core:
- `_IO_list_all` now points to the controlled heap object
- fake FILE key fields still match the planned values
- staged path string is present
- staged ORW / ROP region is present
- output buffer contains expected bytes if the chain executed

If the process printed the flag and then crashed, do not treat that as failure. Prove:
- the output buffer contains the flag
- registers and stack show the chain reached the final syscall path
- the crash is only an end-of-chain fall-through

## Failure mapping

- `_IO_list_all` unchanged
  - heap primitive failed, not FSOP

- `_IO_list_all` changed but fake FILE fields look wrong
  - payload placement or base computation is wrong

- fake FILE looks right but nothing reaches the staged chain
  - wrong jump target, wrong gate field, or wrong trigger surface

- staged chain executes and output buffer is filled, then RIP is invalid
  - success with missing cleanup; only repair if needed

## Practical preference

Prefer `apple2` over more fragile modern FILE routes when:
- the target write naturally reaches `_IO_list_all`
- the trigger is obvious
- the fake object can live on heap without further allocator reuse

Prefer the single-write largebin-carrier pattern when:
- only one arbitrary address write exists
- that write is a heap-address write such as `largebin_attack`
- the heap fengshui can make the inserted chunk itself the fake FILE carrier

Prefer a route that prints the flag and then crashes over a “clean” route that is still unproven.
