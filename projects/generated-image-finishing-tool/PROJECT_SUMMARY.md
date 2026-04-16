# Project Summary

## 1. Purpose

- 生成画像に対して、仕上げ工程を順序付きレシピとして保存し、単画像調整と複数画像への一括適用を安定して行える専用ツールを構築する案件です。
- 汎用画像編集ソフトの代替ではなく、生成画像の仕上げ品質、再現性、安全性を重視します。

## 2. Source of Truth

- この folder の役割: 実装コード、入口文書、採用判断、未決事項を同じ project 内で管理する
- 正本コード: `app/`
- 正本文書: `AGENTS.md`, `START_HERE.md`, `docs/current-status.md`, `docs/adoption-decision.md`, `docs/open-questions.md`
- 正本設定 / データ候補: `requirements.txt`, `data/recipes/`, `data/settings/`
- 生成物: `startup.log`, `data/logs/`, `app/**/__pycache__/`

## 3. Primary Goals

- 専門性の高い仕上げ工程を扱えること
- 機能的で誤操作しにくい GUI を備えること
- 単画像調整と一括適用を同じレシピ定義で回せること
- 元画像を破壊せず、ローカル運用で安定動作すること

## 4. Initial Scope

- 単画像読込
- 5 工程の順序付き編集
- 補正前後比較
- レシピ保存 / 再読込
- 単画像書き出し
- 一括適用
- 進捗表示
- 失敗一覧表示
- 日本語パス対応

## 5. Out of Scope For Initial Release

- 自由描画
- 汎用レイヤー編集
- 部分適用マスク
- 複数レシピ比較
- 高度なアセット管理
- 全面 GPU 化

## 6. Adopted Direction

- 実行エンジン層: Python 正本
- 初期処理方針: CPU 正本
- GPU: 任意加速として段階導入
- UI 第一候補: PySide6 系デスクトップ GUI
- レシピ形式: JSON
- 設計原則: UI と処理本体を分離する

## 7. Planned Structure

- `app/core/recipe`
- `app/core/engine`
- `app/core/image_io`
- `app/core/batch`
- `app/core/state`
- `app/core/logging`
- `app/core/errors`
- `app/ui`

## 8. Current Open Questions

- project 名の正式名称
- UI 基盤の最終確定
- 工程順序変更を初期版から有効にするか
- 一括適用の入力単位をフォルダ優先で固定するか
- 出力命名規則の細則

## 9. Recommended First Step

- `AGENTS.md` と `START_HERE.md` を読んで正本境界と生成物境界を確認する
- `app/main.py`、`app/core/`、`app/ui/` を見て、実装状態と責務分離を確認する
- `docs/current-status.md`、`docs/adoption-decision.md`、`docs/open-questions.md` を読んで、文書上の意図と実装上の差分を確認する

## 10. Rollback Hint

- 文書変更だけなら `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`、`docs/` の差分で閉じて戻せる
- 実装開始後も、処理コアと UI を分離し、単画像適用と一括適用を同じ処理コア上に載せる構成を維持する
