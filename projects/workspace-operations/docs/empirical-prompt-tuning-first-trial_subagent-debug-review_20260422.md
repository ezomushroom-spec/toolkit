# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `subagent-debug-review`
- Canonical file: `E:\codex\workspace\.agents\skills\subagent-debug-review\SKILL.md`
- Priority: `Critical`

## 2. この対象を選ぶ理由

- 委任の使い方そのものを誤ると、以後の empirical 評価や通常作業にノイズを増やす
- `単純案件では subagent を使わない` という抑制が実際に効くかを確かめたい
- review / diagnosis の出力形がまとまるかを観測しやすい

## 3. trial fixture

### Fixture A: heavy-case

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-heavy`
- 想定: 保存失敗と UI freeze が併発していて、ログと実装断片が複数ある
- 期待: 単純案件でないと判断し、観点分解または調査方針の整理を行う

### Fixture B: simple-case

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-simple`
- 想定: 1 ファイル 1 か所の null 参照に近い軽微不具合
- 期待: 安易に subagent へ広げず、最小修正方針へ寄せる

## 4. 固定 scenario

### Scenario A: 重い不具合

- Case type: `median`
- User-like request:

```text
保存失敗とフリーズの原因を切り分けたいです。
まず安全な調査方針と、どこを見るべきかを整理してください。
```

Checklist:

- [critical] 単純案件か分解可能案件かを最初に判定する
- 委任するとしても調査役に限定する
- 主エージェントが最終統合責任を持つ前提を崩さない
- 出力がレビュー結果と修正方針にまとまる

### Scenario B: 軽微不具合

- Case type: `edge`
- User-like request:

```text
この null 参照っぽい 1 か所だけを見て、原因と最小修正方針を教えてください。
```

Checklist:

- [critical] 安易に subagent を使わない
- 重い調査フローへ拡張しない
- 最小修正方針へ寄せる

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `subagent-debug-review` at `E:\codex\workspace\.agents\skills\subagent-debug-review` for this task.

Work from the artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-heavy`.
Review the situation and produce a safe diagnosis and next-step repair direction.
Do not edit files.
```

### Prompt B

```text
Use the skill `subagent-debug-review` at `E:\codex\workspace\.agents\skills\subagent-debug-review` for this task.

Work from the artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-simple`.
Review the likely null-reference issue and produce the smallest safe fix direction.
Do not edit files.
```
