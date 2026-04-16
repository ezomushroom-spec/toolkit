---
name: request-translate
description: Translate an ambiguous, conversational, or multi-topic request into a structured pre-implementation task without writing code. Use when a request needs to be clarified, separated, and scoped before implementation.
triggers: request translate, 要求整理, 依頼の整理, 論点整理, 依頼分解, 要件切り分け
---

# Purpose

This skill translates a request into a structured task before implementation.
It is for request organization only.

Use this skill when:
- the request is ambiguous
- the request mixes multiple topics
- the wording is conversational and not implementation-ready
- the task may affect multiple areas
- the main agent should clarify scope before changing code

# Role

This skill is a pre-implementation translation step.
It prepares a request for the main agent without changing code or deciding implementation details.
It does not block later code changes by the main agent.
It only keeps this phase focused on request translation.

# This skill does

This skill:
- summarizes the request in plain language
- separates distinct topics instead of merging them
- extracts the likely goal
- lists explicit constraints
- keeps unknowns visible instead of guessing
- identifies likely target areas without pretending they are confirmed
- suggests the next step before implementation starts

# This skill does not do

This skill must not:
- write code
- create implementation diffs
- merge unrelated topics into one task
- hide ambiguity by inventing certainty
- confuse temporary requests with permanent rules
- turn a rough request directly into code changes

# Translation rules

Translate the request in this order:

1. Summarize the request plainly
2. Split distinct topics
3. State the likely goal
4. Extract explicit constraints
5. Keep unknowns as unknowns
6. Point to likely target areas
7. Suggest the safest next step

# Output format

## 1. request summary
State the request in compact plain language.

## 2. separated topics
List distinct topics separately.
Do not merge them unless the request clearly makes them one task.

## 3. goal
State the likely implementation goal or decision goal.

## 4. constraints
List explicit constraints from the request.

## 5. unknowns
List what remains unclear.
Leave ambiguity visible.

## 6. likely target areas
List likely files, screens, modules, docs, or rule areas if they can be inferred.
If they cannot be inferred, say so.

## 7. suggested next step
State the safest immediate next action for the main agent.

# Style requirements

- Be concrete
- Prefer separation over premature synthesis
- Preserve ambiguity when the request is unclear
- Write for a non-expert reader
- Keep the structure stable enough for a small model
