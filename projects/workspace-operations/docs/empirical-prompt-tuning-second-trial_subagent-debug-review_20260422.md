# empirical-prompt-tuning 2nd iteration 準備

## 1. 対象

- Target: `subagent-debug-review`
- Canonical file: `E:\codex\workspace\.agents\skills\subagent-debug-review\SKILL.md`
- Iteration theme: borderline case での subagent 不使用判断と review / diagnosis の寄せ方

## 2. この iteration で見たいこと

- `分解可能案件` に見えても、単一ファイルへ収束するなら追加 subagent を使わない判断が出るか
- strict review と原因調査のどちらを主軸に始めるかを過不足なく選べるか
- 不明点を断定せず、主エージェントが最終統合責任を維持できるか

## 3. 固定 scenario

### Scenario A: borderline split

- Case type: `edge`
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-borderline-split`
- User-like request:

```text
保存時フリーズの原因を調べたいです。複数観点で見たほうがよさそうですが、調査の切り方と最小修正方針を整理してください。
```

Checklist:

- [critical] 追加 subagent を使うか使わないかの根拠を明示する
- 単一ファイルへ収束するなら主担当でまとめる判断が出る
- 最小修正方針へつながる整理になる

### Scenario B: review vs diagnosis

- Case type: `edge`
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-review-vs-diagnosis`
- User-like request:

```text
この最近の変更を厳しめに見て、危なそうなところと、必要なら原因調査の進め方を教えてください。
```

Checklist:

- [critical] strict review 主軸か diagnosis 主軸かを最初に整理する
- 再現未確定の段階で断定しすぎない
- review で出すべき危険箇所と、追加調査が必要な点を分ける

## 4. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `subagent-debug-review` at `E:\codex\workspace\.agents\skills\subagent-debug-review\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-borderline-split\brief.md`.
Produce a safe diagnosis and repair direction before coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `subagent-debug-review` at `E:\codex\workspace\.agents\skills\subagent-debug-review\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-review-vs-diagnosis\brief.md`.
Produce a strict but safe review and investigation direction before coding.
```
