# empirical-prompt-tuning 導入前の現状確認

## 1. 現状確認

- 更新日: 2026-04-22
- 対象 project: `workspace-operations`
- 対象範囲: workspace 固有 skill 群、関連する入口文書、疑似 slash command 運用文言
- 正本実装先: `E:\codex\workspace\.agents\skills`
- 関連する入口: `E:\codex\workspace\docs\subagent-prompts.md`, `E:\codex\workspace\docs\skill-inventory.md`, `E:\codex\workspace\docs\workflow.md`, `E:\codex\workspace\AGENTS.md`

### 実コード / 実文書で確認できたこと

- 導入前棚卸し時点の workspace 固有 skill は 15 件で、診断 / UI / 環境依存 / 不具合調査で役割分担は概ね成立していた
- `docs/subagent-prompts.md` が入口の正本として機能している
- `docs/workflow.md` には `/opsx:new` `/opsx:ff` `/opsx:apply` という疑似 slash command 的な運用名があるが、独立した command 定義ファイルは見当たらない
- `CLAUDE.md` は workspace 内に見当たらず、共通指示は root `AGENTS.md` と `docs/*` に分散している

## 2. 静的レビューで見えたズレ

- `project-scaffolder` が削除済みの `implementation-brief-builder` を参照している
- `desktop-dnd-path-resolution` が削除済みの `python-web-electron-shell-migrator` を companion skill として参照している
- 既存の棚卸し文書は `基幹 / 補助 / 特化 / 環境依存` 分類が中心で、`Critical / Important / Opportunistic / Exempt` という評価優先度では整理されていない
- empirical な評価手順、scenario、checklist、記録項目の共通フォーマットがまだない

## 3. 初回分類方針

初回導入では、workspace 固有 skill と関連入口文書を次の観点で優先度付けする。

- 使用頻度
- 失敗時影響
- workspace / 破壊的変更 / 起動 / 高リスク判断との近さ
- 実行者の裁量補完が起きやすいか

## 4. 初回分類表

| Target | Type | Priority | 理由 |
|---|---|---|---|
| `project-scaffolder` | skill | Critical | project 構造と初期文書を直接生成し、誤ると後続案件の正本がぶれる |
| `project-safety-snapshot` | skill | Critical | 高リスク変更の直前に使う安全退避で、失敗時影響が大きい |
| `windows-batch-launcher` | skill | Critical | 起動不能や誤判定に直結しやすく、実害が出やすい |
| `subagent-debug-review` | skill | Critical | 調査委任と結論統合の境界を誤るとノイズや競合を増やしやすい |
| `request-translate` | skill | Important | 入口での論点分解品質が後段全体に効く |
| `pre-implementation-diagnosis` | skill | Important | 実装前判断の精度に影響する |
| `implementation-planner` | skill | Important | 実装順と戻し方の質に直結する |
| `code-review` | skill | Important | よく使うが破壊的変更そのものはしない |
| `ui-audit` | skill | Important | UI 改善の前提診断として重要 |
| `ui-design-direction` | skill | Important | 方向性の誤差が出やすい |
| `ui-remake-safe` | skill | Important | 実装寄りだが対象は比較的限定しやすい |
| `desktop-dnd-path-resolution` | skill | Important | OS / shell 差異で破綻しやすい |
| `ui-overlap-guard` | skill | Opportunistic | 編集時に狙って使う補助 skill |
| `image-finishing-tool-design` | skill | Opportunistic | 特定 domain で価値が高いが常用ではない |
| `plan-review` | skill | Opportunistic | 計画レビュー時に限定して使う |
| `/opsx:new`, `/opsx:ff`, `/opsx:apply` 記述 | workflow section | Opportunistic | 入口文言としては重要だが command 実体がない |
| root `AGENTS.md` の委任節 / 品質節 | guidance section | Important | 実装全体の運用に効くが skill 単位ではない |

## 5. 今回時点の結論

- `empirical-prompt-tuning` は既存 skill を置き換えるのではなく、評価と改訂の共通プロトコルとして導入するのが妥当
- 初回の empirical 評価対象は `Critical` から始める
- ただし現在は明示的な委任許可がないため、subagent を使った empirical evaluation は未実施で、今回は静的レビューと trial 計画までを正本とする
