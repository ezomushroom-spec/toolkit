# Post Manager 実装前判断メモ

更新日: 2026-03-27

## 目的

- 実装開始前に固定すべき判断を 1 枚にまとめる。
- 実装担当が「どこを正本として、何を keep/fix として扱うか」を迷わない状態にする。

## 採用案

### 1. 正本実装先

- 正本実装先は `E:\自作アプリ集\workspace\projects\post-manager-remake\app` を採用する。
- 理由:
  - `src/`、`web/`、`docs/` が同じ場所にまとまっている
  - 最近の判断資料更新がこのパス側に入っている
  - `api_server.py` の実行中保護など、backup 側より新しい差分がある
- `E:\自作アプリ集\post_manager-fix-browser-close-issue_backup_20260323_025001` は参照用バックアップとして扱う。
- 読む先、実装先、文書更新先はすべてこの正本実装先に揃える。

### 2. Web の `全ステップ実行`

- 初回リメイクでは `Clean -> MEGA -> Discord` の前処理まとめ実行として keep する。
- 理由:
  - 現UIですでに前処理まとめ実行として説明されている
  - CLI の `--all` をそのまま Web に持ち込むと、Pixiv / Patreon の人手確認前提を壊しやすい
  - Web ではブラウザ系処理がサブプロセス + 手動確認前提であり、前処理系とは性質が違う
- 実装時の扱い:
  - Web 側は「前処理まとめ実行」の文脈を維持する
  - CLI の `--all` とは別仕様として明示する

### 3. Discord の `zip_url`

- 初回リメイクで fix 対象に含める。
- 採用案:
  - Discord 通知関数へ `zip_url` を渡す
  - README とテンプレート期待値をコード実装に揃える
- 理由:
  - 現行 README はダウンロードリンク利用前提
  - 現コードは `zip_url=None` を渡しており、仕様と実装がずれている

### 4. 設定保護の範囲

- 初回リメイクの最低保証は「既知キーの値維持」とする。
- 対象:
  - `mega.email`
  - `mega.password`
  - `discord.webhook_url`
  - `pixiv`
  - `patreon`
  - `discord`
- 補足:
  - 未知キー、コメント、YAML の並び順まで保持するかは第2段階の改善候補とする
  - ただし初回でも、未知キーが実運用で使われていると分かった場合は keep 方針を再判定する
- 実装時の扱い:
  - 少なくとも空パスワード維持ルールは崩さない
  - 設定保存まわりを変更するときは、既知キーの round-trip を検証する

### 5. `count / image_count`

- 初回リメイクでは派生値扱いを採用する。
- 採用案:
  - CSV に列が来ても壊さない
  - ただし正式な永続必須項目にはしない
  - UI 表示や実行中メモとして扱う
- 理由:
  - `posts.csv.sample` には列がある
  - 実コードでは主にメモリ上の補助値として扱っている
  - 初回で永続仕様に格上げすると、CSV 仕様固定の範囲が広がる

## keep / fix 整理

### keep

- 正本実装先を `projects/post-manager-remake/app` に固定
- Web の `全ステップ実行` は前処理まとめ実行として維持
- CSV 列名と列順
- Pixiv / Patreon の手動最終確認
- `browser_profile/` の保護
- `mega_password` 空欄維持

### fix

- Discord 通知に `zip_url` を渡す
- Web 経路から `Clean / MEGA` の `input()` 依存を切り離す
- README の `user_data/` や Enter 待ち説明など、古い文書を更新する

### 第2段階以降へ送るもの

- 未知キーや YAML 構造まで含めた設定保持
- Task の安定 ID 化
- WebSocket ログの本格接続
- `count / image_count` の永続仕様化の是非

## 実装前に守る運用ルール

- `data/posts.csv`、`config/*`、`browser_profile/` は保護対象として扱う
- 実装変更対象はまず `src/`、`web/`、`README.md`、`docs/` に限定する
- backup 側パスを並行正本として扱わない
- UI 変更は `構造 -> 見た目 -> 安全性` の順を守る

## 次の一手

1. この判断メモを正本 docs から参照できるようにする
2. 正本実装先固定を案件側 docs / AGENTS / app/docs の共通前提として扱う
3. 実装に入る前に、Discord `zip_url` と Web 非対話経路分離を最初の fix 対象として切る
