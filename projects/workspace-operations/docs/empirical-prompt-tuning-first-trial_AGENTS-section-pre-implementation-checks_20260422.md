# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 2. 実装前の確認`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 実装前診断、方式比較、正本確認、進行フローの線引きは workspace 全体の実装品質に直結する
- 小規模修正では重くしすぎず、architecture change では比較を省かない、という読み分けを見たい

## 3. Iteration 0

- section 自体の主旨は明確で、`小規模修正では必要最小限` と `新規 UI / architecture change では診断と比較を行う` の両方が明文化されている
- 追加で見たい曖昧さは「どこからが重い比較対象になるか」と「docs ではなく実コード・実データを優先する読みが自然に出るか」

## 4. trial fixture

### Fixture A: small-fix

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-precheck-small-fix`
- 想定: 小規模修正なので必要最小限の整理で十分

### Fixture B: architecture-choice

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-precheck-architecture`
- 想定: 新規 UI / architecture change を伴い、実装前診断と比較が必要

## 5. 固定 scenario

### Scenario A: small fix

- Case type: `median`
- User-like request:

```text
このボタン文言だけ直したいです。実装前に必要な整理があればやってください。
```

Checklist:

- [critical] 小規模修正では必要最小限の整理に留める
- 重い方式比較や大きな計画へ広げない
- それでも対象と影響は最低限整理する

### Scenario B: architecture choice

- Case type: `edge`
- User-like request:

```text
この案件をどう実装するか迷っています。実装前に、比較と進め方を整理してください。
```

Checklist:

- [critical] 実装前診断と比較が必要だと判断する
- 既存 Python core 維持案を比較対象に含める
- docs だけでなく実コード・実データ・現用設定を優先する
- 進行フローや戻し方に触れる

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 2. 実装前の確認` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-precheck-small-fix\brief.md`.
Produce an evaluation direction before any coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 2. 実装前の確認` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-precheck-architecture\brief.md`.
Produce an evaluation direction before any coding.
```
