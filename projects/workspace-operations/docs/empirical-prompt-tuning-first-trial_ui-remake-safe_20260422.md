# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `ui-remake-safe`
- Canonical file: `E:\codex\workspace\.agents\skills\ui-remake-safe\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 「壊さず改善する」という workspace ルールへの適合を見やすい
- UI 改善で scope を広げすぎないかを評価しやすい
- 構造 → 見た目 → 安全性の順序が守られるかを見たい

## 3. trial fixture

### Fixture A: improve-without-breakage

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-remake-safe-main`
- 想定: 既存画面は動くが、主操作が埋もれ、状態表示と危険操作の分離が弱い

### Fixture B: light-change

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-remake-safe-light`
- 想定: 軽い整理で済む画面

## 4. 固定 scenario

### Scenario A: 壊さず改善

- Case type: `median`
- User-like request:

```text
この画面を壊さず改善したいです。構造、状態表示、安全性の順で実装方針を出してください。
```

Checklist:

- [critical] 既存挙動を保つ前提が入る
- 構造 → 見た目 → 安全性の順で整理する
- 無関係な cleanup に広げない
- loading / error / dangerous action に触れる

### Scenario B: 軽微改善

- Case type: `edge`
- User-like request:

```text
この画面を少しだけ分かりやすくしたいです。大改造は不要です。
```

Checklist:

- [critical] 過剰な remake に広げない
- 小さく安全な改善にとどめる
- 主操作かラベルか grouping のような現実的な改善に落ちる

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `ui-remake-safe` at `E:\codex\workspace\.agents\skills\ui-remake-safe` for this task.

Work from the screen brief in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-remake-safe-main\screen.md`.
Produce a safe UI improvement direction before coding.
```

### Prompt B

```text
Use the skill `ui-remake-safe` at `E:\codex\workspace\.agents\skills\ui-remake-safe` for this task.

Work from the screen brief in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-remake-safe-light\screen.md`.
Produce a minimal safe UI improvement direction before coding.
```
