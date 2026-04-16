---
name: ui-audit
description: Audit an existing UI and identify usability, clarity, hierarchy, consistency, and safety issues before implementation. Use when a screen feels confusing, cluttered, inconsistent, or risky, or when you need project-specific UI rules derived from a real app.
triggers: UI監査, UI audit, 画面監査, 現状UI確認, 改善前UI確認, UI診断, 使い勝手監査
---

# Purpose

This skill reviews an existing UI and produces a structured diagnosis.
It is for inspection only.
It does not block later code changes by the main agent.
It only keeps this phase focused on inspection.

Use this skill when:
- the interface feels hard to understand
- users may be making mistakes
- you want to improve a screen safely
- you need concrete UI findings before planning implementation
- you want to extract project-specific UI rules from an existing app

# This skill does

This skill:
- inspects the UI structure
- finds usability and safety problems
- identifies hierarchy and clarity issues
- checks state visibility such as loading and error handling
- proposes candidate rules for AGENTS.md, skills, and docs

# This skill does not do

This skill must not:
- write code
- redesign the whole product without evidence
- remove features
- focus only on visual polish while ignoring usability
- produce vague suggestions such as “make it cleaner”

# Audit order

Inspect the UI in this order:

1. Structure
2. Priority of actions and information
3. Misoperation prevention
4. State visibility
5. Consistency
6. Beginner usability

# Inspection checklist

## Main action clarity
- Is the main action obvious?
- Are too many actions emphasized at once?
- Can the user tell what to do next?

## Information hierarchy
- Is important information placed where the eye reaches first?
- Are related controls grouped together?
- Is secondary information too prominent?

## Terminology and labels
- Are labels understandable to non-experts?
- Are similar things named consistently?
- Are button labels action-oriented?

## Misoperation prevention
- Are dangerous actions protected?
- Can the user accidentally trigger delete, reset, overwrite, export, or batch actions?
- Are invalid states blocked before execution?

## State visibility
- Is loading visible?
- Is double execution prevented?
- Are success and failure clearly communicated?
- Does the user know what to do after an error?

## Visual consistency
- Are spacing and alignment reasonably consistent?
- Do equivalent controls look and behave the same?
- Is the screen too dense?

# Severity levels

Use one severity for each issue:
- High
- Medium
- Low

# Output format

## 1. Summary
A short plain-language summary of the current UI quality.

## 2. Problems
For each problem, include:
- Title
- Severity
- Where it appears
- What is wrong
- Why it matters
- Realistic improvement direction

## 3. Candidate rules
Split findings into:
- Rules for AGENTS.md
- Rules for skills
- Notes for docs

For each candidate, include:
- Suggested wording
- Why it belongs there
- Whether it should always apply

## 4. Priority order
List the recommended fix order.

## 5. Risks and unknowns
State what cannot be judged from the current material.

# Style requirements

- Be concrete
- Prefer evidence over taste
- Prioritize usability over appearance
- Write clearly for a non-expert reader
