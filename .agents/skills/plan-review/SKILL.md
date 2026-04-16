---
name: plan-review
description: Review a remake or refactor plan before implementation and find risks, weak points, and over-broad scope. Use when you want to ask things like リメイク計画をレビューして, この計画で問題ないか見て, 実装前にチェックしたい, or プランの穴を探して.
triggers: 計画レビュー, plan review, プランレビュー, プラン確認, 実装前レビュー, プランの穴確認, 計画妥当性確認
---

# Purpose

This skill reviews an implementation plan only.
It is for plan review, not coding.

Use this skill when:
- you want to review a remake plan before implementation
- you want to ask この計画で問題ないか見て
- you want to check a plan before implementation starts
- you want to ask プランの穴を探して
- you need to validate a refactor or UI improvement plan from multiple perspectives

# Accepted input

This skill can review a plan from:
- inline text
- a file
- a previous conversation summary

If the plan is unclear, incomplete, or too abstract, say what is missing before judging it.

# Review perspectives

Always review through these five perspectives:

1. behavior preservation and breakage risk
2. UI/UX improvement validity
3. maintainability and extensibility
4. implementation order and safety
5. scope control

# This skill does

This skill:
- finds holes in a plan before implementation starts
- checks whether existing behavior may break
- checks whether the UI/UX improvement is justified and coherent
- checks whether the implementation order is safe
- checks whether the scope should be split into phases
- points out missing conditions and decision points

# This skill does not do

This skill must not:
- write code
- turn the review into implementation
- silently expand the scope
- invent certainty when the input plan is vague
- judge a broad plan as safe without calling out phase split needs

# Severity rules

Use one severity for each problem:
- Critical
- High
- Medium
- Low

# Go / revise judgment rules

- any Critical -> revise first
- 3 or more High -> revise first
- scope too broad -> split into phases first
- otherwise -> ready to implement

# Language rule

- 日本語入力なら日本語で出力する

# Output format

## 1. review summary
State the overall review result briefly.

## 2. strengths
List what is already solid in the plan.

## 3. problems by perspective
For each perspective, include:
- Perspective
- Severity
- Problem
- Why it matters
- Safer direction

## 4. missing conditions
List missing assumptions, missing constraints, or missing decision points.

## 5. recommended revisions
List the most useful revisions before implementation.

## 6. go/revise judgment
State one of:
- revise first
- split into phases first
- ready to implement

Explain the reason in plain language.

# Style requirements

- Be concrete
- Prefer risk discovery over style commentary
- Be strict about scope and breakage risk
- Keep the review useful for the main agent
