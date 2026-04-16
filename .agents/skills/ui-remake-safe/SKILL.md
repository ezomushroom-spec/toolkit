---
name: ui-remake-safe
description: Improve an existing UI without breaking current functionality. Use when implementation should preserve behavior while improving structure, visual clarity, state handling, and misoperation resistance.
triggers: UI改善, UI remake, 安全にUI改善, 壊さずUI改善, 既存UI改善, UI整理改善, 使いやすく改善
---

# Purpose

This skill guides safe UI improvement.
It is for implementation-oriented UI work, but it should still preserve existing behavior unless a change is explicitly justified.

Use this skill when:
- the UI needs improvement but should not be rebuilt from scratch
- the screen works but feels confusing or unsafe
- the main agent is ready to implement changes after audit and planning
- the task is to improve usability without removing features

# Core rule

You may modify existing code when needed for the UI improvement.
Do not break existing functionality without explicit justification.
Do not expand into unrelated cleanup while refining the UI.

Improve the UI in this order:
1. Structure
2. Visual clarity
3. Safety and state handling

# This skill does

This skill:
- improves layout and grouping
- clarifies the main action
- improves labels and hierarchy
- strengthens loading, disabled, success, and error states
- reduces accidental actions
- encourages consistency and reuse
- prevents overlap, clipping, crushed controls, and scroll-area interference when compact UI areas are edited

# This skill does not do

This skill must not:
- remove features without explicit justification
- start with cosmetic changes only
- ignore loading and error states
- rewrite unrelated modules
- trade usability for decoration
- treat "do not change existing code" as a blanket rule

# Implementation order

## 1. Structure
- Group related controls
- Separate primary and secondary actions
- Reduce visual clutter
- Make screen purpose obvious
- Add a clear empty-state next action when the screen can start with no user data

## 2. Visual clarity
- Improve labels
- Improve hierarchy
- Improve spacing and consistency
- Make the main action clearer
- If a workflow has a safe execution order, show that order near the action area

## 3. Safety and state handling
- Prevent double execution
- Add or strengthen confirmations where needed
- Make loading visible
- Make errors actionable
- Make success states visible but not disruptive
- Disable execution controls when required prerequisites are missing
- Do not report partial or aborted batch flows as success
- Avoid repeated identical offline or polling warnings that bury useful logs

## 4. Overlap and operability guard
- Identify which region owns scrolling and which region must stay fixed
- Keep headers, tabs, chips, and lists from sharing cramped vertical space
- Ensure labels, first items, and primary controls are never clipped or half hidden
- Reserve visual space for scrollbars when they may appear and disappear
- Re-check narrower widths before finishing

# Output format

## 1. Planned UI changes
State the intended changes in plain language.

## 2. Behavior preservation notes
Explain what must remain unchanged.

When execution buttons are involved, explicitly note:
- what counts as a prerequisite
- what remains manual user confirmation
- which actions are still available while processing

When the UI is dense or scroll-heavy, explicitly note:
- which section scrolls
- which controls stay fixed
- where overlap or clipping regressions are most likely

## 3. Implementation notes
List the main implementation concerns.

## 4. Impact areas
State which files or modules are likely affected.

## 5. Risks
List likely regression risks.

# Style requirements

- Preserve behavior first
- Prefer incremental change
- Be explicit about state handling
- Prefer consistent reusable patterns
- Change existing code carefully when needed, not reflexively and not by avoidance
- For dangerous actions, show the target, explain the consequence, and require confirmation when interruption can lose work
- Treat overlap, clipping, and scrollbar interference as usability regressions, not cosmetic issues
