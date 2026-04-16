# Post Manager 再構築引き継ぎ

更新日: 2026-03-27

## 目的

この文書は、別スレッドで `Post Manager` を「既存機能を保持したまま再構築」するための引き継ぎ資料です。  
既存コードの延命ではなく、仕様と運用前提を保ったうえで、構造を整理した新実装へ組み替えることを前提にしています。

## 対象アプリ

- 現行本体: `E:\自作アプリ集\workspace\projects\post-manager-remake\app`
- 計画管理フォルダ: `E:\自作アプリ集\workspace\projects\post-manager-remake`

## 最初に固定すべきこと

- 実装対象の正本パスを最初に確定する
  - この handoff は `E:\自作アプリ集\workspace\projects\post-manager-remake\app` を現行本体として扱う
  - ただし `projects/post-manager-remake/AGENTS.md` と `docs/implementation-plan.md` には `E:\自作アプリ集\post_manager-fix-browser-close-issue_backup_20260323_025001` が正本として残っている
  - 別スレッドでは、どちらに対して読む / 実装する / 文書更新するかを着手前に 1 回で固定すること
- Web の `全ステップ実行` をどう定義するか最初に確定する
  - 現UIは `Clean -> MEGA -> Discord` の前処理まとめ実行として説明されている
  - CLI の `--all` は Pixiv / Patreon を含む
  - 人手確認フローを壊さないことを優先し、UI 文言を維持するか、実行対象を広げるかを最初に判断する
- Discord 通知に `zip_url` を含めるかを最初に確定する
  - README はリンク利用前提
  - 現行実装は `zip_url` を通知関数へ渡していない
- 設定保護の意味を最初に確定する
  - 最低限 keep すべきなのは既知項目の値
  - 未知キーや YAML の構造まで保持対象にするかは先に決める

## 再構築の前提

- 目的は「機能削減」ではなく「機能保持した再構築」
- Pixiv / Patreon は入力補助までに留め、最終投稿は人が行う
- `data/posts.csv`、`config/secrets.yaml`、`config/templates.yaml`、`browser_profile/` は運用資産として保護する
- UI 改善は `構造 -> 見た目 -> 安全性` の順で進める
- 既存 CLI 入口と Web 入口は、少なくとも初期段階では維持する

## なぜ再構築寄りにするか

- 現行は CLI と Web の二入口があり、業務フローと UI 状態管理が密結合
- CSV、設定、実行状態、ブラウザ profile、外部副作用が分散している
- 標準ブラウザ上の D&D など、Web 技術だけでは制約が強い箇所がある
- 既存コードを部分修正し続けるより、仕様固定後に再配置したほうが安全

## 保持すべき主要機能

### タスク管理

- `posts.csv` の読み書き
- タスク追加 / 編集 / 削除
- 既存列の保持
  - `target_folder`
  - `title`
  - `caption_pixiv`
  - `caption_patreon`
  - `caption_discord`
  - `tags`
  - `schedule`
  - `zip_password`
  - `patreon_tier`
  - `discord_channel`
  - `zip_url`

### 設定管理

- `secrets.yaml`
  - `mega.email`
  - `mega.password`
  - `discord.webhook_url`
- `templates.yaml`
  - `pixiv`
  - `patreon`
  - `discord`
- パスワード空欄保存時は既存値を維持

### 実行機能

- `Clean & Zip`
  - Pixiv 画像の clean
  - Patreon 配布 zip の生成
- `MEGA Upload`
  - zip のアップロード
  - `zip_url` の CSV 反映
- `Pixiv`
  - 投稿画面の自動入力
  - タグ、R-18、AI、予約などの既存補助
- `Patreon`
  - 作成画面の準備
  - サムネ / タイトル / 本文の入力補助
- `Discord`
  - Webhook 通知

### 実行状態と安全性

- 二重実行防止
- 実行中表示
- ブラウザ確認待ちの案内
- ブラウザ系プロセスの停止導線
- エラー時に次の行動が分かる表示

## 絶対に壊してはいけない運用前提

- Pixiv / Patreon の最終投稿ボタンを自動押下しない
- `browser_profile/` を初期化しない
- CSV スキーマを初手で壊さない
- `Clean` の上書き副作用を無断で変えない
- 実行中にタスクや設定を破壊的変更できないようにする

## 既知の問題と扱い

### 既知のズレ

- Web の「全ステップ実行」は現状 `clean -> mega -> discord`
- ただし現UIでは「前処理まとめ実行」として説明されており、単なる未実装とは限らない
- CLI の `--all` は全媒体を含む
- README には `user_data/` など古い説明が残る
- Discord 通知では現行実装が `zip_url` を渡していない

### 既知の制約

- 標準ブラウザでは D&D から絶対パスを取得できない場合がある
- そのため Web UI でのフォルダ指定は、参照 UI を主導線にしたほうが安全

## 推奨アーキテクチャ

### 1. 共通定義

- Task 定義
- Settings 定義
- 実行状態定義
- step 語彙定義

### 2. 実行層

- CLI 用対話経路
- Web 用非対話経路
- ブラウザ subprocess 管理

### 3. UI 層

- タスク一覧
- 実行パネル
- 設定
- ログ / 実行状態表示

## 推奨実装順

1. 正本パス、Web `all`、Discord `zip_url`、設定保護範囲を確定する
2. Task / Settings / 実行状態の単一定義を決める
3. CLI 対話経路と Web 非対話経路を完全に分ける
4. API / 実行状態 / プロセス管理を固める
5. UI を `構造 -> 見た目 -> 安全性` で再構築する
6. 文書と切り戻し手順を更新する

## 既存資料

### 本体側 docs

- `E:\自作アプリ集\workspace\projects\post-manager-remake\app\docs\リメイク前提整理_20260327.md`
- `E:\自作アプリ集\workspace\projects\post-manager-remake\app\docs\リメイク実装前設計_20260327.md`
- `E:\自作アプリ集\workspace\projects\post-manager-remake\app\docs\リメイク改訂実装計画_20260327.md`

### 案件側 docs

- `E:\自作アプリ集\workspace\projects\post-manager-remake\docs\implementation-plan.md`
- `E:\自作アプリ集\workspace\projects\post-manager-remake\docs\pre-implementation-decision-memo_20260327.md`

## 次スレッドに渡す依頼文のたたき台

```md
対象アプリ:
E:\自作アプリ集\workspace\projects\post-manager-remake\app

目的:
このアプリを、既存機能と運用前提を保持したまま再構築してください。
既存コードの延命ではなく、仕様を守った構造整理済みの実装へ置き換える方針で進めてください。

必須条件:
- Pixiv / Patreon は入力補助まで。最終投稿は人手確認
- data/posts.csv, config/secrets.yaml, config/templates.yaml, browser_profile/ を保護
- UI改善は 構造 -> 見た目 -> 安全性 の順
- CLI と Web の入口は初期段階では維持
- 二重実行防止、実行中表示、エラー時の次アクション表示を入れる

着手前に最初に固定すること:
1. 正本パスを確定する
   - この依頼文は `projects/post-manager-remake/app` を対象としている
   - ただし `projects/post-manager-remake/AGENTS.md` と `docs/implementation-plan.md` には別パスが残っているため、読む先 / 実装先 / 文書更新先を最初に一本化すること
2. Web の `全ステップ実行` の正を決める
   - 現UIは `Clean -> MEGA -> Discord` の前処理まとめ実行として説明されている
   - CLI の `--all` は Pixiv / Patreon を含む
3. Discord 通知で `zip_url` を本文へ含めるか決める
4. 設定保護の範囲を決める
   - 既知キーの値維持だけでよいか
   - 未知キーや YAML 構造も保持対象にするか

まず読む資料:
- app/docs/リメイク前提整理_20260327.md
- app/docs/リメイク実装前設計_20260327.md
- app/docs/リメイク改訂実装計画_20260327.md
- projects/post-manager-remake/docs/implementation-plan.md
- projects/post-manager-remake/docs/rebuild-thread-handoff.md

最初にやること:
1. 正本パスと未決事項を固定する
2. keep/fix を確認する
3. 再構築のファイル配置案を作る
4. 実装フェーズを切る
5. その後に実装へ入る
```

## 補足

- すでに一部改善は入っているが、別スレッドでは「改善済みコードを前提にせず、資料を正本として再判断」してよい
- ただし運用資産と人手確認フローだけは後退させない
