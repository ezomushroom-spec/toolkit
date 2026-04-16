# Post Manager 実装計画
## Pixivタグ支援 Phase 4

最終更新日: 2026-03-31  
基準仕様:
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-spec_revised_20260329.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-phase2-learning-spec_20260330.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\current-specification_20260328.md`

## 1. Goal

Pixivタグ支援の Phase 4 として、`作品 / キャラ` だけでは足りない実務タグを扱いつつ、候補 UI を辞書ブラウザ化させずに、`主カテゴリ中心の少数表示 + 補助カテゴリの段階表示` へ整理する。

この段階でも、自由生成型の推論や巨大外部タグDB依存には進まない。

## 2. Target files

### backend

- `app/src/pixiv_tag_support.py`  
  候補の意味カテゴリ、初期表示配分、`もっと見る` 向けの返却整形を担う中心。

- `app/src/pixiv_tag_learning.py`  
  `行為名 / シチュ / 性癖` を learning 側へ寄せる時の接続点。

- `app/src/api_server.py`  
  既存 suggest API 契約を壊さず、必要ならカテゴリ情報を返す入口。

### data

- `app/data/pixiv_seed_tags.json`  
  少数の `年齢区分` と、誤爆しにくい基礎タグの整理対象。

- `app/data/pixiv_seed_works.json`  
  作品タグと主要キャラタグの強化対象。

### frontend

- `app/web/index.html`  
  候補領域の見出しや展開導線を追加する対象。

- `app/web/script.js`  
  意味カテゴリ別描画、初期表示件数、`もっと見る` 制御を実装する中心。

- `app/web/style.css`  
  候補群の段階表示と、モーダル圧迫を防ぐ見た目調整を行う。

## 3. Ordered implementation steps

### Step 1. タグ層を UI 用カテゴリへ落とす

- Purpose  
  `年齢区分 / 作品 / キャラ / 内容候補` のように、UI 上で見せる単位を固定する。

- Affected files  
  `docs/pixiv-tag-support-spec_revised_20260329.md`  
  `app/src/pixiv_tag_support.py`

- Why this step comes now  
  `出所` と `意味カテゴリ` を混ぜたまま UI へ出すと、件数制御より先に認知負荷が破綻するため。

### Step 2. seed と learning の担当を明確にする

- Purpose  
  `seed は作品 / キャラ / 少数の年齢区分`、`learning/history は行為 / シチュ / 性癖寄り` を実装上でも守れる形にする。

- Affected files  
  `app/data/pixiv_seed_tags.json`  
  `app/src/pixiv_tag_support.py`

- Why this step comes now  
  先に担当分けをしないと、初期表示件数をいじってもノイズ源が増えるだけになるため。

### Step 3. 初期表示件数を主カテゴリ中心に絞る

- Purpose  
  全件横並びではなく、最初に見るべき候補だけを少数表示にする。

- Affected files  
  `app/src/pixiv_tag_support.py`  
  `app/web/script.js`

- Why this step comes now  
  `10件固定` を外しても、そのまま全件表示に寄るとモーダルを侵食するため。

### Step 4. 補助カテゴリを段階表示にする

- Purpose  
  `行為名 / シチュ / 性癖` を必要時だけ見せる `もっと見る` または折りたたみ導線を追加する。

- Affected files  
  `app/web/index.html`  
  `app/web/script.js`  
  `app/web/style.css`

- Why this step comes now  
  内容タグは重要だが増殖しやすく、主入力欄の下に常時全件表示すると GUI を侵犯しやすいため。

### Step 5. 年齢区分を小さく安定表示する

- Purpose  
  `R-18` などの少数重要タグを、補助候補に埋もれない形で扱う。

- Affected files  
  `app/data/pixiv_seed_tags.json`  
  `app/src/pixiv_tag_support.py`  
  `app/web/script.js`

- Why this step comes now  
  年齢区分は内容タグより件数が少なく、しかも漏れコストが高いため、別格として整理する価値がある。

### Step 6. 実動例で件数と見え方を確認する

- Purpose  
  二次創作、成人向け、全年齢寄りで、候補が多すぎず少なすぎないかを見る。

- Affected files  
  実装差分全体

- Why this step comes now  
  この段階は「精度」だけでなく「画面を壊さないこと」が重要だから。

## 4. Risks

- `行為名 / シチュ / 性癖` を安易に seed 化すると誤爆が増える。
- 意味カテゴリを増やしすぎると、今度は UI が見出しだらけになる。
- `もっと見る` の中身が多すぎると、ただの隠れた全件表示になる。
- 年齢区分の扱いを広げすぎると、全年齢中心運用ではノイズに感じられる。

## 5. Unknowns requiring final judgment

- `年齢区分` を常時表示にするか、条件付き表示にするか。
- `行為名 / シチュ / 性癖` のカテゴリ境界をどこまで厳密に分けるか。
- `learning` で拾われた sensitive 寄りタグを弱表示にするかどうか。
- `もっと見る` を1段で済ませるか、カテゴリごとに個別展開するか。

## 6. Suggested implementation scope

最小安全スコープは以下。

- 意味カテゴリを `年齢区分 / 作品 / キャラ / 内容候補` の4層に整理
- 初期表示を主カテゴリ中心の少数表示へ変更
- `内容候補` だけ `もっと見る` で展開
- `seed` と `learning/history` の担当分けを明確化

この段階では、以下は範囲外とする。

- 性癖タグの大規模 seed 化
- カテゴリごとの複雑な設定 UI
- 学習管理画面
- 共起学習の本実装
- 外部辞書自動取得

## 7. Data impact

- `posts.csv` のスキーマは変更しない
- `pixiv_tag_learning.json` の最小形式は維持する
- 主な変更対象は `pixiv_seed_tags.json` と suggest 結果の構造

## 8. Rollback

戻し方は以下。

1. `app/src/pixiv_tag_support.py` のカテゴリ分けと段階表示向け整形を戻す
2. `app/web/index.html` `app/web/script.js` `app/web/style.css` のグルーピング UI を戻す
3. `pixiv_seed_tags.json` の増補分を戻す

この Phase でも CSV と learning JSON の形式を変えないため、rollback はコード差分と seed データ差分の巻き戻しで済む。

## 9. Confirmation checklist

- `作品 / キャラ` が初期表示で見つけやすい
- `年齢区分` が補助候補に埋もれない
- `行為 / シチュ / 性癖` が GUI を侵食しない
- `もっと見る` を開かなくても最低限のタグ選定ができる
- `learning` と `history` の価値が消えていない
- Electron と Web で suggest 結果の意味が一致する
