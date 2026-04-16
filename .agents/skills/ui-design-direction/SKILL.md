---
name: ui-design-direction
description: Guide UI design direction, frontend screen structure, layout refinement, visual hierarchy, and product-fit tone so outputs do not collapse into generic patterns. Use for UI design direction, frontend screen structure, layout refinement, visual hierarchy improvement, domain-fit checks, landing page design, dashboard or app screen design, and requests to improve an existing UI that feels generic. Do not use for backend design, database schema design, API-only work, logo-only requests, or purely visual art with no product or interface goal.
triggers: UI方向性, design direction, デザイン方針, レイアウト方針, 画面構成方針, visual hierarchy, 見た目の方向性, 業種に合うUI, domain fit UI
---

# Purpose

Use this skill to define or refine UI direction before writing frontend code.
Focus on purpose, constraints, composition, hierarchy, responsive behavior, and fit with the existing product context.

This skill is for interface direction and screen structure.
It is not a replacement for implementation, audit, or backend design.

# Core principles

- Identify the screen purpose before proposing layout.
- Fix constraints before arranging components.
- Treat the screen as one composition, not a pile of widgets.
- Prefer strong visual hierarchy over extra decorative parts.
- Use existing UI, existing design systems, reference images, and product context when they exist.
- Distinguish landing pages, dashboards, forms, and internal tools instead of forcing one generic pattern.
- Check whether the proposal fits the product category, user expectation, and trust level instead of following visual fashion.
- Always consider both desktop and mobile behavior.
- Validate clarity, consistency, and misoperation resistance after the direction is chosen.
- Avoid visual novelty that breaks the product context.

# Relationship to nearby skills

- Use `ui-audit` to diagnose problems in an existing UI.
- Use `ui-design-direction` to decide what the UI should become and how it should be structured.
- Use `ui-remake-safe` when implementation is requested and the UI must be improved without breaking behavior.
- Use `pre-implementation-diagnosis` when the main problem is architecture or stack choice rather than UI direction.

# Operating procedure

## 1. Identify the goal

- State the screen type.
- State the main user action.
- State what the user should understand in the first few seconds.

## 2. Lock constraints

- Note required content, interactions, existing components, design system limits, and device constraints.
- If there is an existing UI or screenshot, preserve its useful logic before proposing changes.
- If the request conflicts with product context, say so.

## 2.5 Check product-fit tone

- State the product category, primary user, and expected impression.
- Decide whether the UI should feel quiet, trustworthy, efficient, warm, premium, or fast-moving.
- Call out obvious anti-patterns for that product type before proposing stylistic variation.
- Prefer "fits this product" over "looks generally impressive".

## 3. Choose the composition

- Decide the dominant region, supporting regions, and the reading path.
- Decide what deserves the strongest emphasis.
- Remove weak filler regions before adding new parts.

## 4. Build hierarchy

- Prioritize with layout, spacing, density, scale, and grouping before relying on color.
- Make the main action unmistakable.
- Keep secondary actions visible but clearly subordinate.

## 5. Adapt to screen type

- Use different structure rules for landing pages, dashboards, forms, and internal tools.
- Explain why the chosen structure fits that type.

## 6. Resolve responsive behavior

- Describe what changes on mobile and what stays fixed.
- Do not treat mobile as a simple stacked copy of desktop.
- Call out dense areas, overflow risks, and touch-target concerns.

## 7. Prepare for validation

- Define what should be checked after implementation.
- Include clarity, consistency, responsiveness, and misoperation resistance.
- Include a short product-fit check such as trust, density, tone, and whether the proposal would feel out of place in that domain.

# Output rules

When proposing a UI direction, structure the answer in this order:

1. Screen purpose
2. Constraints and fixed assumptions
3. Proposed composition
4. Visual hierarchy and main action
5. Responsive behavior
6. Fit with product category and existing UI or design system
7. Anti-patterns to avoid
8. Validation points after implementation

Keep the proposal concrete.
If important information is missing, say what is missing instead of smoothing over it.

# Heuristics to avoid mediocre output

- Do not default to hero plus three cards plus CTA without a reason.
- Do not default to a dashboard that is only a grid of equal-weight cards.
- Do not default to a form that is only one long vertical stack without grouping.
- Do not solve weak hierarchy by adding more panels, badges, or helper text.
- Do not give every section equal visual weight.
- Do not center everything by habit.
- Do not use decorative variation to hide structural weakness.
- Prefer one clear dominant move over many medium-strength moves.
- Reduce regions before adding regions.
- Use spacing and grouping to create order before introducing extra components.
- If the existing product is quiet and utilitarian, keep the new direction compatible with that tone.
- Do not make a finance, medical, or operations screen feel playful or unstable without a strong reason.
- Do not make an internal tool decorative enough to hide the main workflow.

# Special guidance by screen type

## Landing page

- Lead with one clear promise and one primary action.
- Build a deliberate narrative flow rather than repeating interchangeable sections.
- Use stronger contrast between hero, proof, detail, and conversion areas.
- Avoid startup-template sameness.

## Dashboard / app screen

- Organize by user decisions, not by symmetrical card count.
- Surface the most important status or action first.
- Separate monitoring, action-taking, and drill-down areas clearly.
- Avoid making every widget compete equally.

## Form

- Group by decision and dependency, not by raw field order.
- Reduce cognitive switching.
- Keep inline help and errors near the decision point.
- Make primary submit, save, or continue actions obvious.

## Internal tool

- Optimize for speed, scanability, and low-error operation.
- Prefer dense but disciplined layouts over decorative spaciousness.
- Make filters, bulk actions, and destructive actions explicit.
- Preserve experienced-user efficiency while keeping first use understandable.

# Validation checklist

- Is the screen purpose obvious?
- Is the main action unmistakable?
- Is the reading path clear on desktop?
- Is the reading path still clear on mobile?
- Are secondary actions truly secondary?
- Does the proposal fit the existing product language?
- Are loading, error, empty, and success states considered?
- Are dangerous actions visually and behaviorally separated?
- Is there any region that exists only because the layout feels empty?
- Would a user understand what changed and why after implementation?
- Does the visual tone match the product category and user expectation?

# If implementation is requested

- First restate the chosen direction, constraints, and hierarchy.
- Use existing UI components and design system rules when available.
- Implement the smallest version that proves the direction.
- Verify desktop and mobile behavior explicitly.
- Check clarity, consistency, and misoperation resistance after implementation.
- If the requested design direction would break product context, explain the tradeoff before coding.

# What good use looks like

- "Improve this generic dashboard so the main workflow is clearer."
- "Propose a stronger layout direction for this internal tool screen."
- "Refine the visual hierarchy of this form before implementation."
- "Give this landing page a less template-like structure while staying consistent with the product."
- "Use the existing design system and make this app screen feel more deliberate."
- "Check whether this dashboard direction fits the product's domain and trust level."

# Non-trigger examples

- "Design the database schema."
- "Plan the API."
- "Create a backend architecture."
- "Make a logo."
- "Generate pure concept art."
- "Pick a color palette with no interface or product goal."
