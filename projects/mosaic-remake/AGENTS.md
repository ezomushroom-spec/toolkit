# Project Rules

- このファイルは `mosaic-remake` 固有の前提だけを扱う。
- Workspace 共通ルールは上位の `AGENTS.md` を優先する。
- 正本コードは `main.py`、`ui/`、`core/`、`utils/` に置き、review 用一時フォルダや build 生成物を混ぜない。
- `settings.json`、`*.onnx`、`*.pt` は運用資産として扱い、変更前に影響対象と戻し方を整理する。
- UI 変更では、`ui/` と `core/` の責務境界を崩さず、構造 -> 見た目 -> 安全性の順で進める。
- 起動導線や build 手順を変えるときは、`通常起動.bat`、`main.py`、`build.bat` の整合を保つ。
- 一時 review フォルダや変換検証コードは、本体正本と混同しない。

## この案件で確認を優先するもの

- UI から core を呼ぶ導線の保全
- `settings.json` とモデル読み込みの互換
- 一時フォルダや build 生成物を正本として触っていないこと

## build / run / test

- 開発起動: `python main.py`
- 通常起動: `通常起動.bat`
- 補助確認: `test_onnx.py`, `build.bat`
- 実行前提: `settings.json`、`*.onnx`、`*.pt` の運用資産を壊さないこと

## 変更時の必須セット作業

- 更新する docs: 正本や確認手順が変わる場合は `PROJECT_SUMMARY.md`、入口変更時は `START_HERE.md`
- 最低限の確認コマンド: `python main.py`、必要なら `test_onnx.py`
- 最低限の手動確認: UI から core を呼ぶ主導線、設定読込、モデル読込
- 失敗時に先に見るログやファイル: `main.py`、`ui/main_window.py`、`settings.json` の参照箇所
