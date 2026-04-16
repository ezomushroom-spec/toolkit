# Post Manager 実装計画
## Pixivタグ支援 Phase 1

最終更新日: 2026-03-29  
基準仕様:
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-spec_revised_20260329.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\current-specification_20260328.md`

## 1. Goal

Pixivタグ支援機能の Phase 1 として、既存の `tags` を Pixiv 用タグとして扱いながら、同梱辞書と既存 `posts.csv` から候補を生成し、タスク編集モーダルの Pixiv セクションで安全に候補提示できる状態を作る。

この段階では、学習 DB、SQLite、共起学習、自動順位最適化の高度化は行わない。

## 2. Target files

### backend

- `app/src/app_schema.py`  
  `tags` の扱いを Pixiv 用タグとして説明しやすい共通語彙の基盤になる。

- `app/src/manager.py`  
  既存 `tags` の永続互換を守る中心。CSV round-trip の確認対象。

- `app/src/api_server.py`  
  Pixiv タグ候補取得 API を追加する想定。既存 UI と Electron UI の共通入口になる。

- `app/src/utils.py`  
  必要なら文字列正規化や簡易トークン分解の共通関数候補。

- `app/src/pixiv_tag_support.py`  
  新規追加候補。seed 読込、既存 tags 抽出、候補生成を集約する専用モジュール。

### frontend

- `app/web/index.html`  
  `タグ` 表記の見直し、Pixiv セクション配下の候補 UI 追加対象。

- `app/web/script.js`  
  候補取得 API 呼び出し、候補チップ描画、クリック追加、重複防止を実装する中心。

- `app/web/style.css`  
  候補タグチップや Pixivタグ補助 UI の見た目を追加する。

### data

- `app/data/pixiv_seed_tags.json`  
  同梱の汎用 Pixivタグ辞書。

- `app/data/pixiv_seed_works.json`  
  軽量な作品辞書。

## 3. Ordered implementation steps

### Step 1. 語彙と保存互換を固定する

- Purpose  
  `tags` を Pixiv 用タグとして扱う前提を UI と内部説明で揃える。

- Affected files  
  `app/src/app_schema.py`  
  `app/web/index.html`  
  `app/web/script.js`

- Why this step comes now  
  候補機能を足す前に、`tags` の意味がぶれていると UI 文言も API 名称も不安定になるため。

### Step 2. Pixivタグ支援の backend モジュールを分離追加する

- Purpose  
  seed 読込、既存 `posts.csv` からの tags 抽出、候補統合を `pixiv_tag_support.py` に閉じ込める。

- Affected files  
  `app/src/pixiv_tag_support.py`  
  `app/data/pixiv_seed_tags.json`  
  `app/data/pixiv_seed_works.json`

- Why this step comes now  
  候補ロジックを `api_server.py` や `manager.py` に直接混ぜると責務が散るため。先に backend の専用面を切り出すほうが安全。

### Step 3. 最小 suggest API を追加する

- Purpose  
  UI が候補取得できる共通入口を用意する。

- Affected files  
  `app/src/api_server.py`

- Why this step comes now  
  backend ロジックと UI 実装を疎結合に保つため。Web UI と Electron UI の差を作らないため。

### Step 4. タスク編集モーダルの Pixivタグ UI を追加する

- Purpose  
  Pixiv セクションに候補表示とクリック追加を導入する。

- Affected files  
  `app/web/index.html`  
  `app/web/script.js`  
  `app/web/style.css`

- Why this step comes now  
  API 契約が固まったあとで UI を乗せるほうが、ダミー実装や二度手間を避けやすい。

### Step 5. 重複防止と入力維持を入れる

- Purpose  
  候補クリックで同一タグを二重追加しないこと、候補取得失敗時でも手入力継続できることを保証する。

- Affected files  
  `app/web/script.js`

- Why this step comes now  
  候補 UI を出しただけでは誤追加や入力破壊のリスクが残るため。安全性の仕上げとして後段で入れる。

### Step 6. 表示文言とログを整える

- Purpose  
  `Pixivタグ` 表記、候補取得失敗時のフォールバック案内、Pixiv 以外へ影響しない説明を揃える。

- Affected files  
  `app/web/index.html`  
  `app/web/script.js`

- Why this step comes now  
  機能が揃ったあとに最終文言を合わせるほうが、案内が実装とずれにくい。

### Step 7. 検証と手動確認を行う

- Purpose  
  既存タスク編集、Pixivタグ保存、Pixiv 以外への無影響を確認する。

- Affected files  
  実装差分全体

- Why this step comes now  
  今回は `tags` の意味付け変更を伴うため、保存互換と UI 無害性の確認が必須。

## 4. Risks

- `tags` の意味変更により、既存ユーザーの認知と UI 位置が食い違う可能性がある。
- 候補生成をやりすぎると、Phase 1 なのに高度な自然言語解析へ膨らみやすい。
- `posts.csv` 抽出処理が保存ロジックへ混ざると、CSV round-trip を壊す恐れがある。
- 候補 UI を Pixiv セクションへ追加する際、既存モーダルのレイアウト圧迫が起こり得る。
- 作品辞書の一致規則を複雑化すると、誤候補が増えやすい。

## 5. Unknowns requiring final judgment

- `Pixivタグ` 入力欄を基本情報欄から即時移設するか、文言変更のみ先行するか。
- Phase 1 の作品辞書一致をどこまで許容するか。  
  例: 完全一致のみか、別名一致まで含むか。
- suggest API に `caption_pixiv` まで含めるか、初期は `title + target_folder + current_tags` に絞るか。
- seed データの初期件数をどこまで持つか。

## 6. Suggested implementation scope

最小安全スコープは以下。

- `tags` を UI 上 `Pixivタグ` と表記する
- `pixiv_tag_support.py` を追加する
- `pixiv_seed_tags.json` と `pixiv_seed_works.json` を最小件数で追加する
- `GET /api/pixiv-tags/suggest` を追加する
- Pixiv セクションに候補タグチップ群を表示する
- 候補クリック時は既存入力へ追記し、重複追加を防ぐ
- 失敗時は無害に手入力へ戻る

これを超える以下は Phase 1 範囲外とする。

- SQLite
- 学習 DB
- `learn` API
- 共起学習
- タイトル語学習
- フォルダ名学習
- 自動タグ確定

## 7. Data impact

- 既存 CSV 列は追加しない
- 既存 `tags` 列をそのまま使う
- 新規追加は読み取り系 seed JSON のみ
- Phase 1 では新しい永続 DB を導入しない

## 8. Rollback

戻し方は以下。

1. `app/src/pixiv_tag_support.py` を削除
2. `app/data/pixiv_seed_tags.json` と `app/data/pixiv_seed_works.json` を削除
3. `app/src/api_server.py` の Pixivタグ API 追加分を戻す
4. `app/web/index.html`, `app/web/script.js`, `app/web/style.css` の Pixivタグ支援 UI を戻す

この Phase では CSV スキーマ変更と DB 追加を行わないため、rollback はコード差分の巻き戻しだけで済む。

## 9. Confirmation checklist

- 既存の `tags` 保存が壊れていない
- `Pixivタグ` 表記が UI 上で一貫している
- 候補取得失敗時でも手入力保存できる
- Patreon / Discord UI に変化がない
- タスク保存、削除、実行系 UI が壊れていない
- Electron でも同じ API で候補取得できる
