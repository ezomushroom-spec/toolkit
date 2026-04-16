# Post Manager 実装計画
## Pixiv人気タグの半自動収集 初回導入

最終更新日: 2026-03-31  
基準文書:
- [pixiv-popular-tag-semi-auto-collection-diagnosis_20260331.md](/E:/codex/workspace/projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-diagnosis_20260331.md)
- [pixiv-tag-support-phase2-learning-spec_20260330.md](/E:/codex/workspace/projects/post-manager-remake/docs/pixiv-tag-support-phase2-learning-spec_20260330.md)
- [pixiv-tag-vocabulary-inventory-plan_20260331.md](/E:/codex/workspace/projects/post-manager-remake/docs/pixiv-tag-vocabulary-inventory-plan_20260331.md)

## 1. Goal

Pixiv人気タグの半自動収集を、既存の Pixivタグ支援ランタイムとは切り離した補助系として導入し、`seed候補 / learning寄り / 除外 / 判断保留` に人手で仕分けるための raw / review 原料を小規模に作れる状態を整える。初回は保存HTML取込を主導線とし、必要時のみ超小規模クロールを補助案として扱う。

この初回では、人気タグの自動採用、既存 suggest への自動接続、大規模巡回、自動辞書化は行わない。

## 2. Target files

### docs

- `projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-diagnosis_20260331.md`  
  方式比較と採用判断の正本。実装時もここから逸脱しないように参照する。

- `projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-implementation-plan_20260331.md`  
  この初回導入計画の正本。

### backend helper

- [pixiv_popular_tag_collection.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_popular_tag_collection.py)  
  検索結果スナップショットや作品観測結果を raw へ整形保存し、review CSV を組み立てる最小入口。既存の `pixiv_tag_support.py` や `pixiv_tag_learning.py` に責務を混ぜない。

### data

- `app/data/pixiv_popular_tag_collection_raw.jsonl`  
  観測タグ、観測元、観測キー、観測日時を 1 行 1 観測で保持する。

- `app/data/pixiv_popular_tag_collection_review.csv`  
  正規化後のタグ一覧と `seed候補 / learning寄り / 除外 / 判断保留` の人手判定を保持する。

### non-target for first pass

- [pixiv_tag_support.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_support.py)  
  初回では接続しない。

- [pixiv_tag_learning.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_learning.py)  
  初回では接続しない。

- [pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json)  
  初回では直接更新しない。

## 3. Ordered implementation steps

### Step 1. raw と review の役割を固定する

- Purpose  
  収集原料と人手判定結果を分け、既存 seed や learning を直接汚さない前提を固める。

- Affected files  
  `projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-diagnosis_20260331.md`  
  `projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-implementation-plan_20260331.md`

- Why this step comes now  
  ここが曖昧なまま実装すると、raw がそのまま辞書扱いされやすく、今回の目的から外れやすいため。

### Step 2. raw の最小レコード形式を決める

- Purpose  
  `保存HTML主 / 作品観測補助` の両方を無理なく保存できる raw 形式を固定する。

- Affected files  
  `app/data/pixiv_popular_tag_collection_raw.jsonl`  
  [pixiv_popular_tag_collection.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_popular_tag_collection.py)

- Why this step comes now  
  保存形式がぶれると、あとで review への集約と重複寄せが不安定になるため。

### Step 3. review の最小仕分け列を決める

- Purpose  
  人手で `seed候補 / learning寄り / 除外 / 判断保留` を付けるための review 形式を固定する。

- Affected files  
  `app/data/pixiv_popular_tag_collection_review.csv`  
  [pixiv_popular_tag_collection.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_popular_tag_collection.py)

- Why this step comes now  
  raw だけ先に作ると、結局どう使うのかが曖昧になり、棚卸し原料として止まりやすいため。

### Step 4. 補助スクリプトを最小機能で追加する

- Purpose  
  人が用意した観測結果を受け取り、raw へ追記できる最小の入口を作る。

- Affected files  
  [pixiv_popular_tag_collection.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_popular_tag_collection.py)  
  `app/data/pixiv_popular_tag_collection_raw.jsonl`

- Why this step comes now  
  先に形式が決まっていれば、スクリプトは単なる保存補助に限定でき、責務が膨らみにくいため。

### Step 5. raw から review への集約処理を追加する

- Purpose  
  観測タグの重複寄せと、人手レビュー開始に必要な一覧生成を最小限で実現する。

- Affected files  
  [pixiv_popular_tag_collection.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_popular_tag_collection.py)  
  `app/data/pixiv_popular_tag_collection_review.csv`

- Why this step comes now  
  raw を作るだけでは運用に入れず、人手判定の入口が必要だから。

### Step 6. 運用手順を docs に固定する

- Purpose  
  どの単位で観測し、どの順で raw を作り、どの時点で review を更新するかを誰でも再開できる形で残す。

- Affected files  
  `projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-diagnosis_20260331.md`  
  `projects/post-manager-remake/docs/pixiv-popular-tag-semi-auto-collection-implementation-plan_20260331.md`

- Why this step comes now  
  今回は UI より運用フローの再現性が重要であり、文書化が不足すると継続利用しにくいため。

### Step 7. 既存運用と分離できているか確認する

- Purpose  
  suggest 本体、seed、learning、既存保存フローへ副作用が入っていないことを確認する。

- Affected files  
  実装差分全体

- Why this step comes now  
  今回の最重要条件は「既存運用を壊さないこと」だから。

## 4. Risks

- raw と review の責務が曖昧だと、review 前の raw が実質辞書扱いされる恐れがある。
- 作品観測を増やしすぎると、作品固有タグや一時的なノイズが強く混ざる。
- 補助スクリプトにページ依存ロジックや取得処理を入れすぎると、半自動補助が本体化して保守コストが上がる。
- review 形式を複雑にしすぎると、人手確認フローが重くなり継続運用しづらい。
- 既存 suggest や learning へ早期接続すると、外部収集タグの混入経路が増えて rollback しづらくなる。
- 超小規模クロールを広げると、pixiv 側のレート制限や監視対策と相性が悪くなる。

## 5. Unknowns requiring final judgment

- raw を JSON にするか CSV にするか。  
- raw は JSONL、review は CSV で固定した。  
  今後の判断は列追加やメモ欄拡張の範囲に留める。

- 補助スクリプトを 1 本にするか、`raw 追記` と `review 集約` を分けるか。  
  初回は 1 本でもよいが、責務分離を優先するなら 2 本構成もあり得る。

- 作品観測の件数上限をどこまで許容するか。  
  低負荷を守るため、初回は少数に固定した方が安全。

- 超小規模クロールを本当に入れるか。  
  入れる場合も `seed語 5〜20件 / 1語1ページ / 明示実行 / 十分な待機あり` を超えない前提に固定した方が安全。

## 6. Suggested implementation scope

最小安全スコープは以下。

- `保存HTML主 / 作品観測補助` の方針を docs で固定する
- raw の最小保存形式を決める
- review の最小仕分け形式を決める
- 観測結果を raw に追記する最小補助スクリプトを追加する
- raw から review を作る最小集約処理を追加する
- 既存 suggest / learning / seed へは接続しない

この初回では以下を範囲外とする。

- Pixiv ページからの自動巡回取得
- 広い自動クロールや定期クロール
- 人気タグの自動採用
- 既存候補 UI への表示
- learning 側への自動反映
- seed JSON の自動更新
- 専用 UI の追加

## 7. Data impact

- `posts.csv` のスキーマは変更しない
- `pixiv_seed_tags.json` と `pixiv_seed_works.json` は初回では変更しない
- `pixiv_tag_learning.json` の形式は変更しない
- 新規追加は raw / review 用の補助データだけに留める

## 8. Rollback

戻し方は以下。

1. `app/src/` に追加した補助スクリプトを退避または削除する
2. `app/data/` に追加した raw / review 用ファイルを退避または削除する
3. `projects/post-manager-remake/docs/` のこの計画文書と診断メモだけを参照履歴として残す

既存の suggest、seed、learning、CSV 保存へ直接接続しない前提なので、rollback は補助資産の除去だけで済む。

## 9. Confirmation checklist

- raw 保存が既存 seed や learning を直接更新していない
- review 生成が raw だけを入力にしている
- 既存の `GET /api/pixiv-tags/suggest` に変更がない
- タスク保存時の learning 更新に変更がない
- `posts.csv` の読み書きに変更がない
- 観測単位と仕分け項目が docs と実装で一致している
- raw / review を削除しても既存機能へ影響がない
