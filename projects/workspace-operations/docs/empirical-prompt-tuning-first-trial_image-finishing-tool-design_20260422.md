# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `image-finishing-tool-design`
- Canonical file: `E:\codex\workspace\.agents\skills\image-finishing-tool-design\SKILL.md`
- Priority: `Opportunistic`

## 2. この対象を選ぶ理由

- domain-specific skill として、汎用エディタ化へ流れないかを確認したい
- recipe reuse, preview/final consistency, batch 志向を本当に優先できるかを見たい
- 画像処理エンジンと GUI の責務分離を強く補正できるかを評価しやすい

## 3. Iteration 0

- description と body の整合は取れている
- avoid / prefer / design rules / GUI rules が比較的はっきりしている
- 追加で見たい曖昧さは「自由編集要求が混ざったときに専用ツール性を守れるか」

## 4. trial fixture

### Fixture A: good-fit

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\image-finishing-tool-design-good-fit`
- 想定: recipe / preview / final / batch に素直に寄る案件

### Fixture B: editor-drift

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\image-finishing-tool-design-editor-drift`
- 想定: 自由編集要求が混ざって、汎用エディタ化へ流れやすい案件

## 5. 固定 scenario

### Scenario A: recipe-centered finishing tool

- Case type: `median`
- User-like request:

```text
このアプリの設計方針を考えたいです。recipe / preset 中心で、preview と final apply が揃い、あとで batch apply にも広げやすい構成を提案してください。
```

Checklist:

- [critical] recipe / preset 中心の framing が出る
- preview と final が同じ定義を共有する前提に触れる
- batch apply への拡張に触れる
- 処理エンジンと UI の分離に触れる

### Scenario B: editor drift pressure

- Case type: `edge`
- User-like request:

```text
このアプリの設計方針を考えてください。自由編集もできるようにしたいですが、仕上げワークフローとしても使いたいです。
```

Checklist:

- [critical] 汎用エディタ方向への不用意な拡張を避ける
- 専用仕上げツールとしての軸を守る
- recipe / batch / preview consistency を崩さない
- 自由編集要求をそのまま中心要件にしない

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `image-finishing-tool-design` at `E:\codex\workspace\.agents\skills\image-finishing-tool-design\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\image-finishing-tool-design-good-fit\brief.md`.
Produce a product/design direction before coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `image-finishing-tool-design` at `E:\codex\workspace\.agents\skills\image-finishing-tool-design\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\image-finishing-tool-design-editor-drift\brief.md`.
Produce a product/design direction before coding.
```
