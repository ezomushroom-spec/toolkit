# START HERE

## この project は何か

- `generated-image-finishing-tool` は、生成画像に対する仕上げ工程を順序付きレシピとして保存し、単画像調整と複数画像への一括適用を行う専用ツールの新規案件です。
- 現段階では、実装前の要求整理、採用判断、未決事項整理をこの folder で進めます。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `docs/current-status.md`
4. `docs/adoption-decision.md`
5. `docs/open-questions.md`
6. workspace ルールが必要なら `E:\codex\workspace\AGENTS.md`

## 正本

- 正本コード: `app/`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/current-status.md`, `docs/adoption-decision.md`, `docs/open-questions.md`
- 正本設定 / データ候補: `requirements.txt`, `data/recipes/`, `data/settings/`
- `startup.log`, `data/logs/`, `app/**/__pycache__/` は生成物であり、正本ではない

## 主要論点

- 生成画像仕上げに特化した工程モデルをどう置くか
- 単画像プレビューと一括適用で同じレシピ定義をどう共有するか
- 専門性、機能的な GUI、安定動作をどう優先順に実装へ落とすか
- CPU 正本と将来の GPU 段階導入をどう両立するか

## 触る前に注意するもの

- `app/` を読まずに文書だけで挙動を判断しない
- `current-status.md` は現状確認、`adoption-decision.md` は採用判断、`open-questions.md` は未決事項として保つ
- GEGL 型工程モデルは保留論点であり、現時点では主設計に戻さない

## 最初の一手

- まず `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで正本境界を確認する
- 次に `docs/current-status.md` と `docs/adoption-decision.md` を読んで目的と採用方針を確認する
- 実装やレビューでは `app/main.py`、`app/core/`、`app/ui/` を見て実コードの状態を先に確かめる
- 最後に `docs/open-questions.md` を読んで、未固定論点だけを切り分ける
