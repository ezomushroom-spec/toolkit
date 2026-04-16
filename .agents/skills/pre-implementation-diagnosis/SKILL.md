---
name: pre-implementation-diagnosis
description: Use this skill when the request involves new UI structure, framework choice, architecture change, rebuild planning, or cross-layer design and the best implementation approach should be selected from the requirements before coding.
triggers: 実装前診断, architecture choice, framework choice, rebuild plan, implementation proposal, 技術選定, 構成選定, 実装方式比較
---

# Pre-Implementation Diagnosis Skill

## Purpose

This skill is for tasks where implementation should not begin until the implementation approach has been diagnosed.

Use this skill when:
- the user wants to build or rebuild an app
- the request implies framework choice or architecture choice
- the request affects UI structure, cross-layer responsibilities, or packaging direction
- the user is not specifying the technology stack
- UI quality, future extensibility, or operational ease matter in a way that may affect architecture or stack selection
- there are existing Python assets that may need to remain as the backend or core processing layer

Do not use this skill when:
- the user explicitly specified the full implementation stack and only wants coding
- the task is a small isolated patch with no architectural impact
- the request is only about fixing a narrow bug in an already decided stack
- the remaining choice is purely local implementation detail inside an established architecture

## Core rule

Do not start coding first.
Diagnose first, recommend second, implement third.

## Diagnosis workflow

### Step 1: Clarify the actual target

Infer and summarize:
- what the user is trying to achieve
- whether the core difficulty is UI, processing, data flow, packaging, or maintainability
- whether this is a new app, a rebuild, or an extension of an existing one
- which existing assets are actually present in the project and whether Python logic should be reused
- what existing flows, data, or entry points may be affected
- what a practical rollback path would look like at proposal level

### Step 2: Generate candidate approaches

Produce multiple realistic implementation approaches.

Examples of approach categories:
- single-stack local desktop app
- Python-centered architecture
- separated frontend/backend architecture
- Windows-native desktop architecture
- web-tech desktop architecture
- hybrid migration approach
- staged rewrite approach

Do not force a fixed number if only 2 strong candidates exist, but aim for 2-3 when realistic.
Do not invent weak options only to increase the count.

### Step 3: Evaluate each candidate

For each candidate, evaluate:

- Requirement fit
- Reliability of implementation
- Ease of building the required UI quality
- Reuse of existing Python logic
- Ease of future modification
- Operational simplicity for a non-expert user
- Packaging and distribution practicality
- Performance and resource cost
- Risk of over-complexity
- Impact on existing flows, data, and entry points

### Step 4: Select one recommendation

Choose one primary recommended approach.

Selection priority:
1. Ability to satisfy the request reliably
2. Maintainability
3. Reuse of valuable existing assets
4. UI quality and operational ease
5. Reasonable implementation complexity

Do not choose based on popularity or trendiness alone.
If another option becomes better only under a specific condition, state that condition briefly as a secondary note.

### Step 5: Explain trade-offs

State:
- why the recommended approach is the best fit
- why the other candidates were not selected
- what risks remain
- what decisions should be made before implementation starts
- whether user confirmation is needed before coding because of meaningful trade-offs

## Output format

Use the following structure in Japanese:

## 実装前診断
### 1. 要求の整理
- 依頼の本質
- 技術的に重要な論点
- 既存資産の扱い
- 既存処理やデータへの影響

### 2. 候補アプローチ
#### 候補A
- 概要
- 強み
- 弱み
- 今回の適合度

#### 候補B
- 概要
- 強み
- 弱み
- 今回の適合度

#### 候補C（必要な場合のみ）
- 概要
- 強み
- 弱み
- 今回の適合度

### 3. 推奨案
- 推奨する構成
- 推奨理由
- 見送った候補とその理由
- 主なリスク
- 条件次第で有力になる次点案

### 4. 実装前に確定すべきこと
- 先に決めるべき事項
- 後回しにしてよい事項
- 想定する戻し方
- 実装前に確認を入れるべきか

## Style rules

- Write in plain Japanese for a non-engineer.
- Minimize jargon.
- When a technical term is necessary, explain it briefly.
- Prefer practicality over brand-name enthusiasm.
- Do not present a framework name as the answer by itself; explain why the approach is suitable.

## Anti-patterns

Do not:
- jump into code immediately
- pick a framework only because it is modern
- preserve an old stack only because it is familiar
- recommend a complicated architecture without a clear payoff
- assume the user can judge frameworks by name alone
- recommend frontend/backend separation by default when the request does not justify the added complexity
