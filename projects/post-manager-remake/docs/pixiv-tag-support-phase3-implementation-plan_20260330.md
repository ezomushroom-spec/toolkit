# Post Manager 実装計画
## Pixivタグ支援 Phase 3

最終更新日: 2026-03-30  
基準仕様:
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-spec_revised_20260329.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-phase2-learning-spec_20260330.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\current-specification_20260328.md`

## 1. Goal

Pixivタグ支援の Phase 3 として、作品辞書連携と弱い文脈補正を追加し、作品名・別名・フォルダ名・タイトルから関連タグをより自然に上位提示できる状態を作る。

この段階でも、自由生成型の推論や外部巨大タグDB依存には進まない。

## 2. Target files

### backend

- `app/src/pixiv_tag_support.py`  
  作品一致、弱い文脈補正、将来の共起拡張ポイントをまとめる中心。

- `app/src/pixiv_tag_learning.py`  
  学習結果を作品補正とどう並べるかの接続点になる。

- `app/src/api_server.py`  
  既存 suggest API 契約を維持したまま順位補正結果を返す入口。

### data

- `app/data/pixiv_seed_works.json`  
  別名、作品タグ、主要キャラ、補助タグを少し厚くする主対象。

- `app/data/pixiv_seed_tags.json`  
  必要に応じて作品横断の補助タグを足す。

### frontend

- `app/web/script.js`  
  既存候補 UI を維持しつつ、source 表示や並びの違いを無理なく受ける。

## 3. Ordered implementation steps

### Step 1. 作品辞書の役割を固定する

- Purpose  
  `name / aliases / characters / related_tags` の使い分けを明確にし、Phase 3 で増やしてよい項目を固定する。

- Affected files  
  `app/data/pixiv_seed_works.json`  
  `docs/pixiv-tag-support-spec_revised_20260329.md`

- Why this step comes now  
  データ定義が曖昧なままロジックだけ強くすると、後で seed 更新が破綻しやすいため。

### Step 2. 作品一致を Phase 2 より一段だけ強くする

- Purpose  
  `title / caption_pixiv / target_folder` から、作品名完全一致だけでなく別名一致も安全に拾えるようにする。

- Affected files  
  `app/src/pixiv_tag_support.py`

- Why this step comes now  
  最も効果が出やすく、しかも外部依存なしで強化できるため。

### Step 3. 弱い文脈補正を追加する

- Purpose  
  フォルダ名やタイトル内の単語を、seed 作品辞書と seed タグ辞書に対する軽いヒントとして使う。

- Affected files  
  `app/src/pixiv_tag_support.py`

- Why this step comes now  
  作品一致だけでは拾えないケースを補えるが、自由解析へ行かずに済むため。

### Step 4. source と score の整理を行う

- Purpose  
  `learning / history / works / seed` の優先順を保ったまま、作品一致と弱い補正のスコア差を調整する。

- Affected files  
  `app/src/pixiv_tag_support.py`

- Why this step comes now  
  作品辞書を強くしすぎて学習結果を押しのけないようにするため。

### Step 5. seed works を増補する

- Purpose  
  メジャー作品について、別名と主要キャラを最低限増やして実用性を上げる。

- Affected files  
  `app/data/pixiv_seed_works.json`

- Why this step comes now  
  ロジックを変えた後でデータを増やすほうが、どの項目が効くかを見やすい。

### Step 6. UI の表示差分を最小で確認する

- Purpose  
  候補 source の違いが増えても、UI を複雑にせず自然に使えることを確認する。

- Affected files  
  `app/web/script.js`

- Why this step comes now  
  Phase 3 は backend 主体で進めるべきで、UI 変更は最小に留めるため。

### Step 7. 検証を行う

- Purpose  
  作品名、別名、キャラ名、フォルダ名ケースで候補順が改善するかを確認する。

- Affected files  
  実装差分全体

- Why this step comes now  
  Phase 3 は「より賢く見えるが誤候補も増えうる」段階なので、例ベース確認が重要なため。

## 4. Risks

- 作品辞書を強くしすぎると、個人学習より作品タグが前に出すぎる。
- 略称衝突で誤作品が上がる可能性がある。
- タイトルやフォルダ名の弱い分解規則を広げすぎると誤検出が増える。
- seed works の更新量が多すぎると保守が重くなる。

## 5. Unknowns requiring final judgment

- `aliases` をどこまで許容するか。  
  例: 完全一致のみ / 部分一致まで含むか。

- `characters` を作品一致なしでも候補に出すか。

- `caption_pixiv` の影響をどこまで強くするか。

- 共起学習を Phase 3 で実装するか、準備だけに留めるか。

## 6. Suggested implementation scope

最小安全スコープは以下。

- `pixiv_tag_support.py` の作品一致を別名対応まで強化
- フォルダ名とタイトルの弱いヒント補正を追加
- `learning > history > works > seed` の優先順を維持
- `pixiv_seed_works.json` を小さく増補
- UI は source ラベル調整程度に留める

これを超える以下は初回 Phase 3 範囲外とする。

- 外部辞書自動収集
- 自由生成型タグ推論
- 大規模作品DB化
- 学習管理 UI
- 共起学習の本実装

## 7. Data impact

- `posts.csv` のスキーマは変更しない
- `pixiv_tag_learning.json` の最小形式は維持する
- 追加の主対象は `pixiv_seed_works.json` と `pixiv_seed_tags.json`

## 8. Rollback

戻し方は以下。

1. `app/src/pixiv_tag_support.py` の Phase 3 補正ロジックを戻す
2. `app/data/pixiv_seed_works.json` と `app/data/pixiv_seed_tags.json` の増補分を戻す
3. UI 表示差分があれば戻す

この Phase は CSV と学習JSONの形式を変えないため、rollback はコード差分と seed データ差分の巻き戻しで済む。

## 9. Confirmation checklist

- 既存の保存時学習が壊れていない
- `learning` が依然として最上位に残る
- 作品名完全一致で関連タグが上がる
- 別名一致でも関連タグが上がる
- フォルダ名ヒントで極端な誤検出が出ない
- Electron と Web で suggest 結果が一致する
