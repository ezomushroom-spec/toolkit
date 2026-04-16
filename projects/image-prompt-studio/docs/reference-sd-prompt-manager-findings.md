# 正本 SD Prompt Manager 調査メモ

## 1. 現状確認

- 正本: `E:\自作アプリ集\新しいフォルダー (2)`
- 形式: Python + customtkinter のローカル GUI アプリ。
- 起動口: `main.py`、`起動.bat`
- 主要構成:
  - `src/models/database.py`: SQLite の tags / prompts 管理。
  - `src/models/wildcard_manager.py`: wildcard ファイルの読み書き、リネーム、インポート、エクスポート。
  - `src/ui/tabs/prompt_tab.py`: プロンプト保存、カテゴリ、お気に入り、コピー。
  - `src/ui/tabs/wildcard_tab.py`: wildcard 編集、候補数表示、ランダムプレビュー、構文コピー。
  - `src/ui/tabs/builder_tab.py`: タグ検索、prompt / negative prompt への追加、wildcard 挿入。
  - `src/ui/components/suggest_textbox.py`: 入力中タグサジェスト。

## 2. データ確認

- `data/prompts.db` は SQLite。
- `tags` テーブルは約 140,782 件。
- `prompts` テーブルは 0 件。
- `tags` は Danbooru 系カテゴリ番号を持つ。
  - 0: general
  - 1: artist
  - 3: copyright
  - 4: character
  - 5: meta
- `prompts` は `prompt`、`negative_prompt`、`category`、`tags`、`favorite`、`created_at` を持つ。
- `data/wildcards` には txt / yaml 系 wildcard ファイルがある。
- `data/wildcard_config.json` は外部 SD WebUI extension 側の wildcard ディレクトリを指している。

## 3. 採用判断

- この Python app を現行挙動とデータ構造の正本として扱う。
- そのまま移植するのではなく、React 版が正本の機能とデータ構造へ追従する。
- 現在の React app は再構築先なので、正本に存在する DB やファイル I/O を入れる場合も段階的に扱う。
- 次段階で有力なのは次の 3 点。
  - prompt / negative prompt を別フィールドとして扱う。
  - wildcard を「参照」から「読み込み・編集・候補コピー」へ広げる。
  - タグ検索とサジェストを builder 機能として分離する。

## 4. 取り込むとよい構造

- プロンプト管理:
  - situation と prompt variant に `negativePrompt`、`favorite`、`tags` を追加できる。
  - category / attribute はタブ、tags は検索・絞り込みに分ける。
- ワイルドカード管理:
  - `__name__` 構文を表示・コピーできるようにする。
  - 1 行 1 候補の txt 形式を扱えるようにする。
  - 説明行は `# comment` として扱える。
  - ランダムプレビューは後続機能として有用。
- ビルダー:
  - タグ検索結果をクリックで prompt / negative prompt へ追加する構造が有用。
  - 入力中サジェストは便利だが、実装負荷が高いため後続に回す。

## 5. 今回すぐには取り込まないもの

- SQLite を直接読む機能。
- 外部 SD WebUI の wildcard ディレクトリを直接参照・上書きする機能。
- wildcard の削除、リネーム、エクスポート。
- Danbooru タグ DB の全件取り込み。
- 入力中サジェスト。

## 6. 未決事項

- 保存先を `localStorage` にするか、SQLite / JSON ファイル連携にするか。
- 外部 wildcard フォルダを読み取り専用で扱うか、編集保存まで許可するか。
- 成人向け・用途限定の wildcard ファイルをアプリ内でどう分類・非表示化するか。
- YAML wildcard を初回対応に含めるか、txt のみから始めるか。

## 7. 推奨する次の実装順

1. 既存 React app の型に `negativePrompt` と `favorite` を追加する。
2. wildcard を `token` / `options` だけでなく、`sourceName` と `description` を持つ形式へ拡張する。
3. `data/wildcards` 由来の txt 形式を手動インポートできる JSON 変換手順を用意する。
4. 保存機能を入れる場合は、まず `localStorage` で app 内編集の保全から始める。
5. 外部フォルダ連携や SQLite 読み込みは、データ破損リスクを整理してから別ステップにする。

## 7-1. 2026-04-07 React 側へ反映済み

- `negativePrompt` は React 側の variant に追加済み。
- `localStorage` による選択中 variant 保存を追加済み。
- `data/wildcards` 由来の txt importer を追加済み。
- importer は `school komono.txt`、`tipo_location.txt`、`view.txt` の 3 件だけを許可リストで取り込み、正本側へは書き込まない。
- UI では `__name__` 構文、source file、候補数、候補プレビュー、除外 summary、構文コピーを表示済み。

## 8. 再構築判断

- 2026-04-07 時点では、正本をそのまま移植するより、画像生成プロンプト管理ツールとして React 側へ再構築する方が妥当。
- 詳細な方針は `docs/remake-direction-from-sd-prompt-manager.md` に分離した。
