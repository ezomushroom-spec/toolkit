# バイブコーディング運用フレームワーク

## 目的

このワークスペースで、共通ルール、案件文脈、監査用 skill、背景説明を混ぜずに運用する。
既存資産を壊さず、追加や更新の判断先を明確にする。

## 配置原則

### `AGENTS.md`

- Workspace全体で常に守る短いルールだけを書く。
- 例: 機能削除禁止、段階移行、translation の前置、UI改善順、危険操作、二重実行防止、エラー表示、サブエージェントの権限。
- 長い説明、案件固有の事情、詳細な手順は書かない。

### `.agents/skills`

- translation、監査、計画、レビューなど、役割ごとの依頼単位を置く。
- UI の方向決めのように、subagent を必須にしない設計 skill を置いてもよい。
- 各 skill には目的、守ること、出力形式、禁止事項を書く。
- サブエージェントが実装主体にならないよう、コード編集禁止を明確にする。

### `.codex/agents`

- subagent の実行 role を置く。
- 各 role には model、description、developer_instructions を書く。
- `.agents/skills` の手順と対応づけるが、正本の役割を混ぜない。

### `docs`

- 背景説明、運用手順、使い分け、判断基準を置く。
- ルール本文の丸写しではなく、なぜその運用にするかを説明する。
- skill 本文の正本は持たず、使い分けだけを書く。

### `projects/<name>/AGENTS.md`

- 案件固有の文脈だけを書く。
- 例: 技術スタック、フォルダ責務、主操作、危険操作、データ境界、案件固有のテスト優先順位。
- Workspace共通ルールを繰り返しすぎない。

### `archive`

- 正本ではなくなった文書や、現運用から外した資料を隔離する。
- まだ参照する可能性があるものをすぐ削除せず、まずここへ移す。

## 判断の流れ

1. まず `AGENTS.md` で共通制約を確認する。
2. 依頼が曖昧なら `.agents/skills/request-translate/SKILL.md` と `.codex/agents/request-translator.toml` を使って translation を通す。
3. UI の方向性を決める必要があるなら `.agents/skills/ui-design-direction/SKILL.md` を使う。
4. 次に `projects/<name>/AGENTS.md` で案件文脈を確認する。
5. 実装時は `docs/coding-rules.md` を見る。
6. UI判断は `docs/ui-principles.md` を見る。
7. サブエージェントを使うときだけ `.agents/skills`、`.codex/agents`、`docs/subagent-prompts.md` を見る。

## この構成で避けたいこと

- AGENTS.md に詳細チェックリストを増やし続けること
- docs に skill の全文を複製すること
- translation を飛ばして曖昧な依頼をそのまま実装へ流すこと
- project 固有ルールを workspace 共通ルールとして固定すること
- サブエージェントに実装と最終判断を任せること
