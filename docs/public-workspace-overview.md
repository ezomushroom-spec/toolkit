# Public Workspace Overview

この workspace は、AI エージェントを使った実装・診断・計画・レビューの運用ルールを整理し、再現しやすい形で改善していくための作業環境です。

特に、`empirical-prompt-tuning` を使って skill や guidance section を評価・改訂する流れを、実運用ベースで整備しています。

## この公開版に含まれるもの

- workspace 共通ルール
- agent skill 群
- skill の使い分け導線
- `empirical-prompt-tuning` の導入記録と rollout 記録
- workspace 改善のための trial / result / operating rule

## この公開版に含めていないもの

- 個別作品として扱う private project
- 公開判断が済んでいない project
- 作品固有の素材、設定、制作途中データ

公開対象の詳細は [../projects/workspace-operations/docs/public-release-scope_20260422.md](/E:/codex/workspace/projects/workspace-operations/docs/public-release-scope_20260422.md:1) を正本とします。

## この workspace の主な目的

1. 曖昧な依頼を、そのまま実装せずに整理・診断・計画へ落とせるようにする
2. 高頻度または高リスクの skill を、感覚ではなく evidence ベースで改善する
3. workspace ルール自体の誤読や裁量差を減らす
4. 変更を branch / commit / push / PR の形で外部反映しやすくする

## 主要な入口

- ルール全体を見る: [../AGENTS.md](/E:/codex/workspace/AGENTS.md)
- docs の入口を見る: [README.md](/E:/codex/workspace/docs/README.md)
- skill の棚卸しを見る: [skill-inventory.md](/E:/codex/workspace/docs/skill-inventory.md)
- skill の使い分けを見る: [subagent-prompts.md](/E:/codex/workspace/docs/subagent-prompts.md)
- `empirical-prompt-tuning` の運用記録を見る: [../projects/workspace-operations/START_HERE.md](/E:/codex/workspace/projects/workspace-operations/START_HERE.md)

## 補足

この公開版は「workspace の完成版」というより、`v1` の安定運用版に近い位置づけです。

基本ルールと主要 rollout は揃っていますが、将来の拡張候補として scored eval、`slash command` の canonical 化、追加 skill への横展開余地は残しています。
