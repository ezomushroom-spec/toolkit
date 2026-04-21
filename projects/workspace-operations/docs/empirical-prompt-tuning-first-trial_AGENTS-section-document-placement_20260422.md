# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 5. 文書と配置`
- Priority: `Important`

## 2. この対象を選ぶ理由

- project 文書の入口と archive 境界がぶれると、workspace 全体の正本判断が崩れやすい
- active project と参照中心 folder の置き分けを自然に読めるかを見たい

## 3. Iteration 0

- section には `projects` と `archive` の役割、入口文書、判断・計画文書、調査メモの配置、active と backup の混同回避が書かれている
- 追加で見たい曖昧さは「active だが入口未整備の案件をどう正すか」と「archive 移動前に何を残すか」

## 4. trial fixture

### Fixture A: active-project-placement

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-doc-placement-active-project`
- 想定: active project だが入口文書と文書配置が未整備

### Fixture B: archive-boundary

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-doc-placement-archive-boundary`
- 想定: 参照専用になった folder が `projects` 側に残っていて active と混同しやすい

## 5. 固定 scenario

### Scenario A: active project placement

- Case type: `median`
- User-like request:

```text
この project の文書配置をどう整理すべきか見てください。
```

Checklist:

- [critical] active project なら `projects` 側で入口文書を揃える
- 判断・計画文書を project 配下へ寄せる
- 直下散在メモをそのまま許さない
- index や入口導線更新の必要性に触れる

### Scenario B: archive boundary

- Case type: `edge`
- User-like request:

```text
この folder をそのまま `projects` に置いてよいか、配置の観点で見てください。
```

Checklist:

- [critical] active でないなら `archive` 側を検討する
- 旧→新対応表や戻し方を残す必要に触れる
- active project と混同しない名前・文書・置き場を求める

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 5. 文書と配置` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-doc-placement-active-project\brief.md`.
Produce an evaluation direction before any coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 5. 文書と配置` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-doc-placement-archive-boundary\brief.md`.
Produce an evaluation direction before any coding.
```
