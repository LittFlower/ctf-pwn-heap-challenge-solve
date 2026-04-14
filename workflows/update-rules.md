# Rule Update Workflow

Use this workflow after a substantive solve, debugging loop, or skill maintenance pass.

## Classification Guide

- Stable heap-solving constraints or decision rules belong in `rules/`
- Ordered task procedures belong in `workflows/`
- Pitfalls, examples, and background notes belong in `references/`

## Sync Targets

| Change type | Files to update |
|---|---|
| New or renamed workflow or reference file | `SKILL.md` Common Tasks routing |
| New stable heap-solving rule | relevant `rules/*.md` |
| New allocator pitfall or recurring dead end | `references/gotchas.md` and, if costly, the relevant workflow checklist |
| Changed answer contract | `rules/output-contract.md` |
| Live solve revealed a faster recurring task split, routing shortcut, or first-pass question | `SKILL.md` Common Tasks routing and the relevant workflow or checklist |

Threshold: update the docs if the lesson would cause a future agent to choose the wrong heap model, technique family, or finish on a similar challenge.

## Solver-Efficiency Lens

Run this pass after every substantive solve or discarded exploit path:

- Did the skill route the agent to the right file set early enough?
- Did a missing first-pass question cause a long wrong turn?
- Did the skill assume real allocator activity existed before checking whether the writable surface was a live libc object such as `FILE` / libio state?
- Did a costly pitfall live only in `references/` when it should have blocked the mistake earlier in a workflow or `SKILL.md`?
- Did the solve expose a repeatable fast path that deserves its own Common Task entry?
- Would the proposed optimization preserve the same proof standard, or does it only look faster because it skips a validation step?

If any answer is yes, treat that as an efficiency regression even if the challenge was eventually solved.

## After-Action Review

Run this scan before considering the task complete:

- [ ] Did this task reveal a recurring allocator pitfall that was not documented?
- [ ] Did a missing or weak workflow step cause wasted time?
- [ ] Did the skill fail to surface the right route quickly enough for this task type?
- [ ] Did the task look heap-like at first but actually require libc-object / stream-path modeling instead of chunk geometry?
- [ ] Did a rule turn out to be outdated for newer libc behavior?
- [ ] Did a costly lesson land only in ad-hoc notes or scratch code?

If all answers are no, stop here.

## Recording Threshold

Record the lesson when at least two of the following are true:

1. It is likely to recur on another heap challenge.
2. Missing it would waste significant time or misroute the exploit.
3. The lesson is not obvious from reading the target code or the existing references.

## Activation Check

If the lesson is costly and task-relevant, do not leave it buried in `references/`.

- Update the relevant workflow checklist when the lesson should block a future wrong turn.
- Update `SKILL.md` Known Gotchas when the lesson should surface during task routing.
- Update `SKILL.md` Common Tasks when the lesson creates a repeatable task shape or a faster read path.
- Update `rules/*.md` only when the lesson is a long-lived constraint, not a one-off observation.
- Reject any "optimization" that improves speed only by weakening allocator modeling, primitive proof, or endgame validation.

## Completion Criteria

- [ ] New knowledge classified into the right file type
- [ ] `SKILL.md` routing updated if task paths changed
- [ ] Costly pitfalls surfaced in workflow or routing, not only in references
- [ ] No duplicated rule bodies introduced while recording the lesson
