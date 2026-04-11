# House Of Apple2

Use this after the heap phase is already strong enough to:
- overwrite `_IO_list_all` or another FILE pointer
- place a controlled fake FILE on heap
- supply a later flush / exit / stdio trigger

This file is not a full history of FSOP. It is a compact operator checklist for modern glibc-style
`apple2` routes.

## Scope

Prefer this route when:
- hooks are gone or unattractive
- the target libc is modern enough that FILE-based routing is more realistic than hook abuse
- a heap arbitrary write naturally lands on `_IO_list_all`
- the binary still reaches a stdio-linked trigger after corruption

Do not use this file as a substitute for exact version checks. Re-derive sensitive offsets from the
shipped libc.

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
| secondary jump slot | May need to contain a gadget or function such as `svcudp_reply+26` |

Do not trust old offsets blindly. Derive them from the shipped libc and verify them in memory.

## Common modern route shape

One practical pattern is:
1. use a heap primitive such as largebin attack to overwrite `_IO_list_all`
2. place fake FILE on heap
3. point its vtable to `_IO_wfile_jumps` or another version-appropriate table
4. use a jump target that pivots into a staged ROP / ORW region
5. trigger exit or flush

Treat the exact jump target as version-sensitive. The important part is not the historical name of
the gadget, but that:
- the call site is reachable from the chosen FILE path
- the consumed registers or fields are satisfiable from your fake object
- the pivot lands inside your controlled staging region

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

Prefer a route that prints the flag and then crashes over a “clean” route that is still unproven.
