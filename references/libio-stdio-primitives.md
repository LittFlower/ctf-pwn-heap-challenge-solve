# Libio Stdio Primitives

Use this file when the source material says `_fileno`, stdin or stdout arbitrary read/write, `_IO_str_finish`, `_IO_str_overflow`, or an old `FSOP` label that still points at classic stdio-field corruption instead of modern Apple-family routes.

This file is for operator routing, not for a full history of libio exploitation.

## The split that matters

Do not collapse these into one generic `FSOP` bucket:

- `_fileno` retarget of an already-live stream
- stdin-backed arbitrary write through underflow / refill logic
- stdout-backed arbitrary read or leak through flush / overflow logic
- historical `_IO_str_jumps` dispatch such as `_IO_str_finish` or `_IO_str_overflow`
- modern FILE routes such as `house_of_apple2`

The trigger surface, required fields, and libc window differ enough that the wrong bucket wastes time immediately.

## Family map

### `_fileno` retarget

Use when:
- a live `FILE *` such as `stdin`, `stdout`, or another already-open stream is writable
- the target file descriptor is already open in the process
- a later stdio helper really consumes that same stream object in the intended direction

The first proof target is not code execution. It is "the next stdio read or write uses the attacker-chosen fd instead of the default one."

### stdin arbitrary write

Use when:
- a live input stream is writable
- later input goes through stdio helpers, not raw `read(0, ...)`
- the route can force buffer refill / underflow

Typical consumers include `_IO_new_file_underflow` and the refill path that eventually feeds input helpers such as `_IO_file_xsgetn`.

Operator note:
- on current glibc source, `_IO_new_file_underflow` explicitly checks line-buffered or unbuffered input streams and may call `_IO_OVERFLOW (stdout, EOF)` first when line-buffered `stdout` is linked
- if the route depends on a later stdio read, inventory whether this implicit stdout flush helps or perturbs the intended leak / trigger order

Typical operator checklist:
- input buffer appears empty, often by making `_IO_read_ptr == _IO_read_end`
- the stream still allows reads, typically meaning `_IO_NO_READS` is not set
- `_fileno` still names the intended input source, often `0`
- `_IO_buf_base` and `_IO_buf_end` bound the target write window

Treat this as a directed write primitive first, not as a generic FILE endgame.

### stdout arbitrary read or leak

Use when:
- a live output stream is writable
- later program output reaches that stream through stdio helpers such as `puts`, `printf`, or `fwrite`, not only raw `write(1, ...)` or `send`
- the route can force flush / overflow or otherwise consume the staged write window

Typical consumers include `_IO_new_file_overflow` and `_IO_new_file_xsputn`, plus write helpers that flush the staged window on the next output path.

Operator note:
- raw `write(1, ...)` style output does not consume the live `stdout FILE` state directly, so a staged stdout leak window is only relevant if some later stdio output path still survives
- on current glibc source, `_IO_new_file_overflow` first switches into put mode with `_IO_write_end = _IO_buf_end`, but narrows `_IO_write_end` back to `_IO_write_ptr` for line-buffered or unbuffered streams, so do not model every stdout route as if `_IO_write_end` alone always carries the usable window
- if the live sink is really `stderr` or another non-stdout stream, do not blindly inherit stdout newline/full-buffer assumptions; record the actual stdio helper or assert/flush path that consumes that stream on the shipped target

Typical operator checklist:
- the stream still allows writes, typically meaning `_IO_NO_WRITES` is not set
- the stream is in a writing state, often through `_IO_CURRENTLY_PUTTING` or an equivalent path predicate
- `_fileno` names the intended output sink, often `1`
- `_IO_write_base` and `_IO_write_ptr` span the address range to leak
- check the buffering mode before choosing the controlling edge: full buffering often behaves like `_IO_buf_end`, while line-buffered or unbuffered paths often collapse the immediate write edge back to `_IO_write_ptr`
- some paths also require a read/write-state consistency gate such as `_IO_read_end == _IO_write_base` or an appending-style flag before the leak is actually emitted
- the next output path really forces flush / overflow, often because the buffer is full or the output includes a newline on a line-buffered stream

This is often the cheapest libc or stack leak route, not the final control-flow pivot.

### Historical `_IO_str_jumps` FSOP

Use when:
- the target is truly old
- the source material explicitly depends on `_IO_str_finish` or `_IO_str_overflow`
- the route is a real old-stdio chain, not a modern Apple-style FILE path with different dispatch

Treat the split carefully:
- pre-`2.24`: old fake-vtable style notes may still be historically relevant
- `2.24-2.27`: in-vtable `_IO_str_jumps` style routes may still matter on matching targets
- `2.28+`: do not default to the old `_IO_str_*` recipes; prefer re-deriving the shipped libc path and compare modern FILE or exit-linked routes first

Accuracy note:
- current glibc source keeps `_IO_str_overflow` and `_IO_str_finish`, but the modern implementation directly uses `malloc` and `free`
- therefore, inherited notes that depend on `_s._allocate_buffer` or `_s._free_buffer` should be treated as old-libc lineage hints, not as drop-in formulas for modern targets

If the note says `house_of_orange`, remember that Orange often carried the old `_IO_list_all` plus `_IO_str_*` lineage. On modern libc, keep Orange as a historical routing hint, not as a drop-in endgame.

## Decision rules

- If a later `scanf`, `fgets`, `getc`, or comparable stdio input path still runs, compare `_fileno` retarget and stdin arbitrary-write before building a heavier fake-FILE plan.
- If the program will still `puts`, `printf`, `fwrite`, `fflush`, or exit through stdio, compare stdout arbitrary-read before assuming the first useful step must already be code execution.
- If later output is only raw `write(1, ...)`, `send`, or another non-stdio path, do not spend time on stdout FILE leakage unless some separate stdio flush or buffered output still remains.
- If the source material only says `FSOP`, separate "old `_IO_str_*` dispatch", "live-stream field corruption", and "modern Apple-family FILE endgame" before choosing offsets.
- If the writable seam is `_codecvt`, wide data, or another modern subobject, leave this file and return to `libio-object-corruption.md`.
- If the route already has `_IO_list_all` control or a writable FILE pointer on modern libc, compare `house_of_apple2` before inheriting old `_IO_str_*` notes literally.

## Reporting language

When you report the route, say which of these was proved first:

- redirected stdio fd through `_fileno`, including the intended read or write direction and the later stdio helper that consumes it
- stdin-backed arbitrary write window
- stdout-backed leak window
- historical `_IO_str_jumps` dispatch, including the claimed old-libc window and whether old `_s._allocate_buffer` / `_s._free_buffer` assumptions are in play
- modern FILE endgame chosen instead

That phrasing is more reusable than saying only `FSOP`.
