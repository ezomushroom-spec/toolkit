# Image Prompt Desktop

画像生成用プロンプト、ネガティブプロンプト、タグ、ワイルドカードを扱う Windows 向けデスクトップ再構築版です。

正本は `E:\自作アプリ集\新しいフォルダー (2)` の Python app です。この project は正本のデータ構造を参照しながら、PySide6 で使いやすい UI へ作り直すための新規実装先です。

## 現在の機能

- PySide6 の 3 ペイン UI
- 上位タブ `Prompt Studio` / `Wildcard Library`
- 正本 SQLite `data\prompts.db` の prompt 件数とカテゴリ読み取り
- 正本 `data\wildcards` の txt wildcard 読み取り
- prompt / negative prompt の編集欄
- prompt / negative prompt / wildcard token のクリップボードコピー
- wildcard 候補プレビュー
- wildcard 候補のリスト表示
- wildcard の desktop 版ローカル下書き編集
- wildcard ランダム候補プレビュー
- wildcard 候補行のダブルクリック挿入
- ランダム候補のコピー / Prompt 挿入
- 正本 tags の検索
- タグカテゴリ絞り込み
- 選択タグの prompt / negative prompt への挿入
- タグ検索結果のダブルクリック挿入
- desktop 版ローカル `data/session.json` への作業中 prompt 一時保存
- desktop 版ローカル `data/situations.json` への Situation Draft 保存
- Situation 名、登録タグ、使用 wildcard、メモの管理
- 保存済み Situation の読み込みと新規 Situation 化
- 読み取り失敗や空データの status 表示

## 初回スコープ外

- 正本 DB への prompt 保存
- wildcard の作成、削除、リネーム、外部フォルダへの書き込み
- 正本 wildcard の直接編集保存
- Situation Draft の正本 DB 連携
- PyInstaller packaging
- タグ DB の高度な全文検索、サジェスト、カテゴリ別フィルタ

## 起動

```powershell
python -m pip install -r requirements.txt
python main.py
```

または `start.bat` を使います。起動失敗を確認したい場合は `debug-start.bat` を使います。

## テスト

```powershell
python -m unittest discover -s tests
```

## 主な構成

- `main.py`: アプリ起動口
- `src/image_prompt_desktop/core.py`: 正本 DB / wildcard 読み取り
- `src/image_prompt_desktop/main_window.py`: PySide6 UI
- `src/image_prompt_desktop/style.py`: QSS テーマ
- `tests/test_core.py`: core の読み取り・解析テスト
- `docs/desktop-implementation-plan.md`: 実装計画
