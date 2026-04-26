# Reroute Stuck Solve

Use this workflow when a heap solve has stalled because the current corridor is no longer coherent.

## Read First

- `rules/heap-solving-principles.md`
- `references/solver-fast-paths.md`
- `references/challenge-observation-checklist.md`
- `references/version-delta.md`
- `rules/output-contract.md`

## Triggers

Run this workflow immediately if any are true:

- you opened 3 or more corridor references without naming one proof target
- two proof attempts failed for reasons that contradict the current family
- the route still depends on `/proc`, debugger state, or copied local offsets
- the writable surface now looks like a live libc object instead of chunk metadata
- the solve keeps adding exploit code without a proved allocator claim

## Steps

1. Stop coding.
   - Do not add more exploit scaffolding while the corridor is unclear.
2. Write the current state in five lines.
   - current corridor
   - current proof target
   - last failed check
   - missing address classes
   - whether the draft is still remote-capable
3. Reduce the contradiction.
   - Name the exact fact that no longer fits: wrong ownership, no post-free write, no safe-linking bypass, wrong trigger surface, or no surviving stdio consumer.
4. Return to fast-path routing.
   - Re-answer the eight questions in `references/solver-fast-paths.md`.
   - Select exactly one new corridor.
   - Explicitly reject one tempting but wrong corridor.
5. Choose a smaller new proof target.
   - Prefer the smallest mechanical claim that tests the new corridor.
   - If the blocker is still address recovery, switch to a leak proof target before touching endgame code.
6. Resume only after the new route is stated cleanly.

## Completion Checklist

- [ ] Old corridor named explicitly
- [ ] Contradicting allocator fact written explicitly
- [ ] Exactly one new corridor selected
- [ ] One rejected corridor recorded with reason
- [ ] New proof target is smaller and mechanical

## Escape Conditions

- Stop and escalate to `workflows/debug-allocator-failure.md` if the blocker is an allocator abort you cannot classify.
- Stop and escalate to `workflows/choose-endgame.md` if the primitive is stable and only the final trigger is unclear.
