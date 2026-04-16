---
name: implementation-planner
description: Turn audit findings or requirements into a safe implementation plan without writing code. Use when you need an ordered change plan, file-level scope, risk notes, and a minimal sequence of steps before implementation.
triggers: 実装計画, implementation plan, 実装プラン, 変更計画, 実装手順, 影響範囲整理, 戻し方整理
---

# Purpose

This skill creates an implementation plan and a final implementation brief.
It is for planning and handoff preparation, not coding.
It does not block later code changes by the main agent.
It only keeps this phase focused on planning.

Use this skill when:
- audit findings already exist
- the task is large enough to benefit from sequencing
- you want to reduce accidental breakage
- multiple files may be affected
- the main agent needs a compact plan before implementation

# This skill does

This skill:
- organizes work into steps
- identifies target files and likely impact areas
- points out dependencies and risks
- separates confirmed work from unknowns
- prioritizes small, safe, reversible changes
- produces a final brief with purpose, scope, non-break requirements, completion criteria, and verification items

# This skill does not do

This skill must not:
- write code
- redesign the product without evidence
- silently expand scope
- remove features
- merge planning and implementation into one step

# Planning rules

Plan in this order:

1. Clarify the goal
2. Identify affected files or modules
3. Separate structural changes from visual changes
4. Separate safety/state work from cosmetic work
5. Note risks and unknowns
6. Produce an ordered implementation sequence

# Output format

## 1. Goal
State the intended improvement in plain language.

## 2. Target files
List likely files or modules and why they matter.

## 3. Ordered implementation steps
For each step, include:
- Step number
- Purpose
- Affected files
- Why this step comes now

## 4. Risks
List realistic breakage risks.

## 5. Unknowns requiring final judgment
List what the main agent must decide.

## 6. Suggested implementation scope
State the minimum safe scope for the first pass.

## 7. Final implementation brief
At the end, always output one Markdown code block that includes:
- 目的
- 対象範囲
- 壊してはいけないもの
- 完了条件
- 確認項目

The brief must not invent new requirements.
If something is still unknown, leave it as unknown.

# Style requirements

- Be conservative
- Prefer smaller changes first
- Keep the plan testable and reversible
- Avoid vague sequencing
