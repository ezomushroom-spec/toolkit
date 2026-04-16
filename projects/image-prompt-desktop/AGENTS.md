# Project Rules

- この project は `image-prompt-desktop` の固有ルールだけを扱う。
- Workspace 共通ルールは `E:\codex\workspace\AGENTS.md` を優先する。
- 現行挙動とデータ構造の正本は `E:\自作アプリ集\新しいフォルダー (2)` の Python app とする。
- この project は PySide6 によるデスクトップ再構築先であり、正本 Python app を直接編集しない。
- 初回実装では正本 SQLite / wildcard は読み取り中心で扱い、保存、削除、リネーム、外部 wildcard 書き込みは入れない。
- `dist/`, `build/`, `.venv/`, `__pycache__/`, `*.log` は正本扱いしない。
- UI 改善は構造 -> 見た目 -> 安全性の順で行う。
- クリップボードコピー、空データ、存在しない path、読み取り失敗の表示を確認対象に含める。

## build / run / test

- 開発起動: `python main.py`
- launcher: `start.bat`, `debug-start.bat`
- テスト: `python -m unittest discover -s tests`
- 依存確認: `python -c "import PySide6; print('PySide6 ok')"`

## 確認を優先するもの

- `main.py` から起動できること
- launcher が `cd /d "%~dp0"` で作業ディレクトリを固定すること
- 正本 `data\prompts.db` と `data\wildcards` を書き換えないこと
- prompt / negative prompt を個別コピーできること
- wildcard token を `__name__` 形式でコピーできること
- wildcard ランダム確認は読み取りだけで行うこと
- wildcard 候補やタグ検索結果のダブルクリック挿入は UI 編集欄だけに反映すること
- wildcard 操作は `Wildcard Library` タブに分離し、Prompt 編集画面に混ぜないこと
- タグ検索は SQLite 読み取り専用で行い、選択タグの挿入だけを UI 側編集欄へ反映すること
- 作業中 prompt の保存は desktop 版ローカル `data/session.json` に限定し、正本 DB に書かないこと
- Situation Draft の保存は desktop 版ローカル `data/situations.json` に限定し、正本 DB に書かないこと
- Wildcard 下書き保存は desktop 版ローカル `data/wildcard_drafts.json` に限定し、正本 wildcard ファイルに書かないこと
