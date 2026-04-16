# START HERE

## この project は何か

- workspace の AGENTS、skills、運用文書の棚卸しや再編判断を記録する調査案件フォルダです。
- 実装コードではなく、現状確認、採用判断、未決事項の文書を残す用途です。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `agents-md-inventory_20260329.md`
4. `workspace-reorg-principles_20260331.md`
5. 必要なら `workspace-reorg-current-state_20260331.md`
6. 必要なら `workspace-reorg-next-actions_20260331.md`

## 正本

- この folder の役割: 監査メモと再編判断の保管場所
- 正本文書: このフォルダ内の監査メモと方針文書
- 参照対象: workspace root の `AGENTS.md`, `.codex/`, `.agents/skills`, `docs/`, `projects/`

## 主要入口

- 通常起動: なし
- 主な確認方法: 実ファイル構成と文書の突き合わせ

## 触る前に注意するもの

- 壊してはいけない既存挙動: root ルールと project ルールの責務分離
- 明示依頼なしで触らないもの: 実装コード、ビルド設定、依存関係
- backup / profile / generated: 該当なし

## 最初の一手

- まず `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで、この project が監査用であることと参照境界を確認する。
- 次に `agents-md-inventory_20260329.md` と `workspace-reorg-principles_20260331.md` を読んで、現行の棚卸し基準と再編原則を把握する。
- 次に workspace 実ファイルを見て、文書と実態の差だけを追加で記録する。
