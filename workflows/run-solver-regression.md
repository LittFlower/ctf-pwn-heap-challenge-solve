# Run Solver Regression

Use this workflow after changing routing, first-pass questions, or high-traffic references in this skill.

## Read First

- `rules/heap-solving-principles.md`
- `rules/output-contract.md`
- `references/solver-fast-paths.md`
- `references/solver-benchmark-suite.md`
- `workflows/update-rules.md`

## Steps

1. Choose the benchmark set.
   - Use at least 8 archetypes from `references/solver-benchmark-suite.md`.
   - Prefer one case per corridor instead of many near-duplicates from the same family.
2. Simulate first-pass routing only.
   - For each case, record the first corridor you would choose.
   - Record which files you would open before naming a proof target.
   - Do not skip directly to exploit scripting.
3. Name the first proof target.
   - Write one mechanical claim for each case: overlap, leak, chosen-pointer return, arbitrary write, or direct call trigger.
   - Write the missing runtime address classes explicitly.
4. Score the route.
   - Pass only if the route reaches one corridor and one proof target without hidden local-only assumptions.
   - Fail if the route opens too many corridors, hides a leak dependency, or jumps to an endgame family too early.
5. Aggregate the misses.
   - Group failures by cause: bad task routing, weak first-pass question, outdated version note, buried gotcha, or missing workflow step.
   - Fix the narrowest document that would have prevented the miss.
6. Feed the result back into the skill.
   - If a failure is route-level, update `SKILL.md` or `references/solver-fast-paths.md`.
   - If a failure is proof-level, update the relevant workflow or deep reference.
   - If a failure is only a one-off case, do not widen the default route.

## Completion Checklist

- [ ] At least 8 benchmark cases run
- [ ] Each case has a first corridor and first proof target recorded
- [ ] Hidden leak / base assumptions were counted as failures
- [ ] Route-level misses were mapped back to one document change
- [ ] `workflows/update-rules.md` was run after meaningful changes

## Escape Conditions

- Stop if the benchmark set is dominated by one corridor; rebalance the suite first.
- Stop if the evaluation itself starts depending on debugger-only facts rather than the skill's routing behavior.
