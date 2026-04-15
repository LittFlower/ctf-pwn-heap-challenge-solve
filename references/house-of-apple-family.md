# House Of Apple Family

Use this file when a modern FILE / libio finish is plausible, but the real question is which `house of apple` branch still fits the writable fields and heap-fengshui budget.

This file is for branch selection and constraint routing. Keep exact fake-FILE field work in `house-of-apple2.md` and exact libc-object reasoning in `libio-object-corruption.md`.

## Why this split exists

The `house of apple` family is not one route.

The practical split is based on which FILE-adjacent member you can really control:

- `_IO_list_all` or another FILE pointer can be retargeted to a heap carrier
- `_wide_data` can be pointed at controlled heap state
- `_codecvt` can be pointed at controlled heap state
- only one allocator write exists, so pointer retarget and carrier placement must be co-designed

## Branch map

### `house_of_apple1`

Treat as the bridge route when:
- a primitive equivalent to one `largebin attack` exists
- the first stable effect is only "arbitrary address write a heap address"
- later FILE / FSOP work still needs another idea

This is not yet direct execution. It is the pointer-delivery stage.

### `house_of_apple2`

Use when:
- you can control FILE `vtable`
- you can also control `_wide_data`
- the target still reaches a suitable wide FILE path such as `_IO_wfile_overflow`, `_IO_wfile_underflow_mmap`, or `_IO_wdefault_xsgetn`

What makes it valuable:
- it turns `_wide_data` control into direct code execution
- `_wide_vtable` is not protected by the normal FILE vtable validation path
- it fits well with a single `largebin attack` if the written heap address is already the fake FILE carrier

Constraint notes:
- requires known `heap` and `glibc` addresses
- requires a real IO trigger such as `exit`, flush, or `__malloc_assert`
- if the route can only overwrite one pointer, `_IO_list_all` retarget and fake FILE carrier placement must be solved together

### `house_of_apple3`

Use when:
- full `_wide_data` control is awkward or unstable
- you can control FILE `vtable`
- you can control `_codecvt`
- the target can still reach one of the `_codecvt`-consuming wide FILE paths

What makes it valuable:
- it shifts the post-FILE control point from `_wide_data->_wide_vtable` to `_codecvt`
- it can preserve default `_wide_data` state, which helps when touching `_wide_data` would break branch predicates
- it is useful in harsher conditions where only partial FILE-member control survives

Constraint notes:
- still needs known `heap` and `glibc` addresses
- still needs a real IO trigger
- if only partial FILE forgery is possible, keeping default `_wide_data` is often preferable to over-forging it

## Decision rules

- If the only thing you have is a one-shot heap-address write, stay in `apple1` language until you prove the carrier object.
- If `_wide_data` is controllable and the wide path is easy to satisfy, bias toward `apple2`.
- If `_wide_data` control is fragile but `_codecvt` is writable, bias toward `apple3`.
- If overwriting `_wide_data` would disturb the path predicate, keep `_wide_data` default and try an `apple3`-style `_codecvt` route first.
- If the route needs only one allocator write, reject any plan that spends it on `_IO_list_all` without already staging the carrier object.

## Heap-fengshui implications

- FILE target selection and carrier placement are part of the same design problem.
- For one-write routes, the inserted chunk from `largebin attack` should usually be the fake FILE carrier or point into it directly.
- The more constrained the FILE-member budget is, the more valuable it becomes to preserve default libc state and only replace the one member family that gives the final call edge.
- `apple2` is usually the better fit when you can afford to stage `_wide_data`, `_wide_vtable`, and supporting heap objects together.
- `apple3` is usually the better fit when `_codecvt` is the clean writable seam and `_wide_data` should remain default.

## Reporting language

When you report the route, say which branch was actually proved:

- Apple1-style heap-address delivery
- Apple2 `_wide_data` execution route
- Apple3 `_codecvt` execution route

That phrasing is more reusable than saying only "house of apple."
