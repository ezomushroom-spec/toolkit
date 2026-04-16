---
name: ui-overlap-guard
description: Prevent layout overlap, crushed controls, and scroll-area interference in existing UIs. Use when Codex edits sidebars, tabs, chips, sticky headers, scroll containers, split panels, or compact control areas where visual overlap, hidden labels, scrollbar collisions, or reduced operability are likely.
triggers: レイアウト重なり, overlap guard, clipping, レイアウト崩れ, スクロール干渉, はみ出し防止, UI干渉
---

# Purpose

Prevent small layout regressions that make a UI hard to operate.
Focus on overlap, clipping, crushed controls, and scroll behavior before cosmetic tuning.

# Core rule

Treat control reachability and readable separation as structural requirements.
Do not rely on visual inspection alone when scroll containers, tabs, chips, or stacked panels are involved.

# Check in this order

## 1. Structure

- Identify which regions must remain independently operable.
- Separate fixed controls from scrollable content.
- Do not let headers, category rows, tabs, or chips share vertical space with content lists unless the separation is explicit.
- Give scrollbars their own visual space.

## 2. Visual clarity

- Ensure labels are never partially hidden by active controls.
- Avoid layouts where a horizontal scrollbar visually touches the next section's heading.
- Keep minimum control height for chips, tabs, and segmented buttons.
- Prevent wrapping that causes controls to intrude into the next block.

## 3. Safety and state handling

- Check focus styles for height growth or outline overlap.
- Check active states do not expand enough to crush neighboring controls.
- Confirm scrollable regions still work when content grows.
- Confirm the first actionable item in a list remains fully visible and clickable.

# High-risk patterns

- A sidebar with multiple stacked sections where more than one section scrolls.
- A horizontal tab or chip row placed directly above a vertical list.
- Scrollbars inside tight containers without reserved gutter space.
- Flex children with `min-height: 0` issues or missing fixed-height separation.
- Wrapping chips inside narrow containers.
- Borders, focus rings, or active styles that increase rendered size.

# Required prevention steps

When editing risky UI:

1. Decide which section is fixed and which section scrolls.
2. Reserve spacing between tab or chip rows and list content.
3. Use stable scrollbar space when a scrollbar may appear and disappear.
4. Ensure control rows have a minimum height that survives focus and active state.
5. Re-check at a narrow width before finishing.

# Implementation cues

- Prefer one scroll owner per vertical region.
- If a control row should always stay visible, keep it outside the scrolling list.
- If chips or tabs overflow, prefer one-line horizontal scrolling over unsafe wrapping when the next section is close below.
- Add bottom margin or padding where a scrollbar can visually collide with the next heading.
- Use `scrollbar-gutter: stable` when scrollbar appearance changes layout.
- Keep interactive rows at a predictable minimum height.

# Output format

## 1. Risk areas
List the regions likely to overlap or become hard to operate.

## 2. Prevention changes
State the structural protections to add before styling tweaks.

## 3. Behavior preservation notes
State what interaction patterns must remain unchanged.

## 4. Verification points
List what to re-check after implementation.

# Verification points

- No heading or first card is covered by controls.
- No chip, tab, or button is vertically crushed.
- Scrollbars do not cover labels or action targets.
- The focused control remains fully visible.
- The layout still works at narrower widths.
