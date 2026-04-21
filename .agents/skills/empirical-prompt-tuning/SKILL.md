---
name: empirical-prompt-tuning
description: Evaluate and iteratively improve agent-facing instructions such as skills, slash commands, task prompts, and workspace guidance sections without replacing their domain purpose. Use when a newly created or heavily revised instruction behaves inconsistently, when a frequently used instruction needs hardening, or when description/body alignment, trigger clarity, success criteria, or executor discretion need empirical review with fresh-agent execution when available.
---

# Purpose

Treat this skill as a quality-assurance and revision protocol for existing instructions.
Do not use it to flatten all skills into one writing style.

Keep the target instruction's purpose, domain specialization, and proven workflow.
Improve only what blocks reliable execution and reliable evaluation.

# Use this skill for

- a new skill or major revision that has not been hardened yet
- a frequently used instruction that behaves differently across runs
- a skill, slash command, or guidance section whose description promises more than the body supports
- prompts that require too much hidden judgment from the executor
- workflows that fail on edge cases or depend too much on reference hunting

# Do not use this skill for

- one-off prompts whose evaluation cost is higher than their value
- mechanical style unification across unrelated skills
- replacing domain-specific workflows with generic templates
- claiming empirical validation when fresh-executor testing is unavailable

# Core rule

Use this skill as an evaluation protocol, not as an upper policy that forces other instructions to conform.

Judge the target on:

1. trigger clarity
2. description/body alignment
3. success criteria that can be checked after execution
4. how much unspoken discretion the executor must invent
5. how safely the workflow behaves in edge cases

# Protocol

## 1. Scope the target

- identify the artifact type: skill, slash command, task prompt, or workspace guidance section
- identify the canonical file
- state why the artifact matters now: frequency, risk, or recent failure
- classify it as `Critical`, `Important`, `Opportunistic`, or `Exempt`

## 2. Run Iteration 0 before any empirical test

Check the target statically first.

- compare frontmatter or short description against the body
- remove stale references and obsolete neighboring-skill names
- tighten ambiguous trigger language
- state what counts as success and failure
- mark any part that still depends on executor guesswork

Do not start broad rewrites here.
Fix only the clearest alignment gaps first.

## 3. Create evaluation scenarios

Prepare 2 to 3 scenarios for each `Critical` or `Important` target.

- include 1 median case
- include 1 or 2 edge cases
- keep scenarios realistic and short
- freeze the judging checklist before running the test

Use the templates in [references/templates.md](references/templates.md) when helpful.

## 4. Create a fixed checklist

For each scenario, create 3 to 7 checks.

- include at least 1 `[critical]` item
- write checks so pass/fail can be judged after the run
- do not move the goalposts after the result is seen

## 5. Run empirical evaluation only with fresh-executor separation

If the environment allows a fresh agent or another independent executor, use that for empirical evaluation.

- use a fresh executor for each pass
- do not reuse the same thread as the test surface
- do not pass the expected answer or your diagnosis
- pass only the target instruction, the task artifact, and the user-like request

If fresh-executor separation is not available or not permitted, stop at static review and record that empirical evaluation is pending.
Do not call self-rereading an empirical evaluation.

## 6. Record execution evidence

For each run, record:

- success or failure
- checklist pass/fail
- precision notes
- tool usage count or notable tool choices
- duration if available
- retry count
- ambiguous points
- places where the executor invented missing judgment
- failed `[critical]` items

## 7. Revise one theme at a time

Use `1 iteration = 1 theme`.

Examples:

- clarify trigger conditions
- tighten output contract
- reduce hidden discretion
- harden one edge case

Do not mix unrelated cleanup into the same revision.

## 8. Stop when the signal flattens

Default stopping rule:

- 2 consecutive iterations with no new ambiguity and only small improvement

For `Critical` targets, prefer:

- 3 consecutive stable iterations before calling the target hardened

# Output contract

When using this skill, produce:

1. target and reason for evaluation
2. classification
3. Iteration 0 findings
4. fixed scenarios and checklists
5. empirical results or a clear statement that only static review was possible
6. minimal revision theme
7. remaining risks and next trigger for re-evaluation

# Guardrails

- do not rewrite all existing instructions at once
- do not optimize only for success rate or only for fewer tool calls
- do not delete necessary safety text just to make prompts shorter
- do not call the work done if empirical evaluation was skipped
- do not erase the target's domain-specific workflow without evidence
