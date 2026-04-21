# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `ui-design-direction`
- Canonical file: `E:\codex\workspace\.agents\skills\ui-design-direction\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- UI の方向性を generic にせず決められるかを見たい
- screen purpose、主操作、hierarchy、product-fit tone が出るかを判定しやすい
- 既存文脈があるケースで無理に新奇性へ寄らないかも見たい

## 3. trial fixture

### Fixture A: internal-tool screen

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-design-direction-internal`
- 想定: 内部ツールの一覧画面を、密度を保ちながら整理したい

### Fixture B: existing-system screen

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-design-direction-existing`
- 想定: 既存の地味な業務画面があり、派手さより運用適合が必要

## 4. 固定 scenario

### Scenario A: 方向性を決める

- Case type: `median`
- User-like request:

```text
内部向け一覧画面を、作業効率を落とさずに整理したいです。画面構成と視覚階層の方向性を出してください。
```

Checklist:

- [critical] 画面目的と主操作が明示される
- hierarchy と layout direction が出る
- generic dashboard 化しない
- desktop / mobile か、少なくとも responsive の考慮に触れる

### Scenario B: 既存文脈を保つ

- Case type: `edge`
- User-like request:

```text
今の業務画面を少し良くしたいですが、見慣れた運用感は崩したくありません。方向性だけ整理してください。
```

Checklist:

- [critical] 既存文脈を保つ前提を外さない
- 過剰に派手な redesign に寄らない
- product-fit / trust level を意識する

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `ui-design-direction` at `E:\codex\workspace\.agents\skills\ui-design-direction` for this task.

Work from the screen brief in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-design-direction-internal\screen.md`.
Produce UI design direction before coding.
```

### Prompt B

```text
Use the skill `ui-design-direction` at `E:\codex\workspace\.agents\skills\ui-design-direction` for this task.

Work from the screen brief in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-design-direction-existing\screen.md`.
Produce UI design direction before coding.
```
