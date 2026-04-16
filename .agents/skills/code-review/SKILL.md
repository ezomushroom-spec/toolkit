---
name: code-review
description: Review code for correctness, resource efficiency, maintainability, readability, and UI safety without editing it. Use before or after implementation when you need structured findings and practical fixes.
triggers: コードレビュー, code review, 実装レビュー, レビュー指摘, バグレビュー, リスクレビュー
---

# Purpose

This skill performs a structured code review.
It is for evaluation only.
It does not block later code changes by the main agent.
It only keeps this phase focused on review.

Use this skill when:
- code was newly generated
- a change feels risky
- you want a pre-merge review
- you want to find likely bugs before testing
- you want practical feedback, not style-only commentary

# Review lenses

Always review through these five lenses:

1. Bug and exception risk
2. Resource waste
3. Extensibility and maintainability
4. Readability and understandability
5. UI safety and misoperation resistance

# This skill does

This skill:
- finds likely failure points
- points out wasteful patterns
- checks whether the structure will be hard to extend
- checks clarity of naming and grouping
- checks whether the UI flow is safe for users

# This skill does not do

This skill must not:
- edit code
- rewrite large sections without justification
- give shallow “cleaner code” comments without specifics
- ignore user-facing risk in favor of style preferences

# Output format

## 1. Review summary
State the overall quality briefly.

## 2. Findings by lens
For each lens:
- Problem area
- Why it is a problem
- Realistic fix

## 3. Highest-priority fixes
List the most urgent fixes first.

## 4. Low-priority issues
List nice-to-have improvements separately.

## 5. Risks if unchanged
Explain what may go wrong if the code stays as-is.

# Style requirements

- Be concrete
- Prioritize correctness and safety
- Prefer practical fixes over idealized rewrites
- Assume the reader may not be an expert
