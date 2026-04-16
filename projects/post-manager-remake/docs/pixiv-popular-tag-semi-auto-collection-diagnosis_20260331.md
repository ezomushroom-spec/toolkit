# Pixiv人気タグの半自動収集方式 実装前診断 2026-03-31

## 1. 要求の整理

- 依頼の本質  
  `post-manager-remake` の既存 Pixivタグ支援とは別系統で、R18文脈の語彙棚を厚くするための「人気タグの半自動収集方式」を比較し、次スレッドで着手できる採用案まで整理する。

- 技術的に重要な論点  
  欲しいのは人気タグの自動辞書化ではなく、`seed候補 / learning寄り / 除外` に人手で仕分けるための原料づくりである。したがって、収集精度だけでなく、低負荷、規約面の無理の少なさ、既存 seed や learning を汚さない分離設計が重要になる。

- 既存資産の扱い  
  正本ロジックは [app](/E:/codex/workspace/projects/post-manager-remake/app) 側にある。現行の候補生成は [pixiv_tag_support.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_support.py) が `learning / history / works / seed` を軽量合成する方式で、保存時学習は [pixiv_tag_learning.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_learning.py) が単純カウント JSON を維持している。seed 正本は [pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json) と [pixiv_seed_works.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_works.json)。

- 既存処理やデータへの影響  
  既存の suggest 本体へ直接つなぐと、`外部辞書自動吸収は非目標` という現行方針と衝突しやすい。したがって初回は、ランタイム用の `seed` や `learning` を直接更新せず、人手棚卸し用の別出力を作る位置づけが安全である。

- 実運用上の前提  
  今回ほしいのは大規模自動収集ではなく、小規模・低負荷・人手確認前提で回せる方式である。最終採用は必ず人手確認にし、seed を辞書ブラウザ化しない。

## 2. 現状確認

- 現行の Pixivタグ支援は [pixiv_tag_support.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_support.py) で最大 18 件の候補を返す軽量設計であり、巨大タグ辞書を前提にしていない。
- [pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json) は少数の基礎語彙だけを持ち、[pixiv_seed_works.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_works.json) は作品・キャラ入口を担う。
- [pixiv_tag_learning.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_learning.py) は保存成功したタグだけを JSON に累積し、外部収集や自動採用は行わない。
- 既存文書でも、外部タグ自動吸収や大規模辞書化は段階的に避ける前提が続いている。
- そのため新件は、既存候補ロジックの延長ではなく「棚卸し原料を作る補助系」として分ける方が整合しやすい。

## 3. 候補アプローチ

### 候補A: 保存HTML取込方式

- 概要  
  人が Pixiv 上で少数の seed 検索語やタグ検索結果を開き、保存した HTML からローカルでタグを抽出して raw 化する。取得単位は `1検索語 or 1タグページ = 1保存HTML` とする。

- 強み  
  外向きアクセスを増やさずにローカル処理へ寄せられるため、運用上の無理が比較的少ない。取得件数を人が制御できるため低負荷で、R18語彙の棚卸し原料にも使いやすい。最終判断を人手に残しやすく、seed の即時辞書化にもつながりにくい。

- 弱み  
  保存手順が 1 段増える。作品単位の深い文脈や、タグ同士の共起までは拾いにくい。観測時点の表層的な人気タグに寄るため、作品固有の補助語彙は薄くなりやすい。

- 今回の適合度  
  高い。初回の本命候補として扱いやすい。

### 候補B: 代表作品観測方式

- 概要  
  人が代表的な人気作品を少数だけ開き、その作品に付いているタグ群を棚卸し原料として抜く。取得単位は `1作品 = 1タグ集合` とする。

- 強み  
  R18文脈の実用語彙を拾いやすく、検索結果だけでは見えにくい `行為 / シチュ / 属性` を補える。作品のまとまりで観測するため、実務タグの感触に近い。

- 弱み  
  作品固有タグ、キャラ名、イベント名などのノイズが混ざりやすい。収集者の作品選定バイアスも乗りやすく、低負荷を守るには件数制限が必須。

- 今回の適合度  
  中程度。候補Aの補助線として有効。

### 候補C: 超小規模クロール方式

- 概要  
  seed 語を少数に固定し、検索結果またはタグページを 1 語につき 1 ページ程度だけ取得して raw 化する。十分な待機時間、低件数、明示実行を前提にする。

- 強み  
  手作業を減らしながら、保存HTMLより一段だけ省力化できる。取得単位を小さく切れば、棚卸し原料づくりとしては必要十分なことが多い。

- 弱み  
  pixiv 側は検索や作品詳細取得にレートリミットやログ監視、reCAPTCHA などの対策を入れているため、広げるほど相性が悪い。ページ構造追従や保守の責務も増える。初回から本流にすると設計が重くなりやすい。

- 今回の適合度  
  低め。厳しい上限を付けた補助方式なら比較対象に残せる。

## 4. 推奨案

- 推奨する構成  
  `候補A: 保存HTML取込方式` を主方式とし、語彙の深さ補完として `候補B: 代表作品観測方式` を少量併用する。`候補C: 超小規模クロール方式` は、初回から必須にせず、A の保存作業を減らしたくなった段階で比較する。

- 推奨理由  
  今回の優先順位は「運用上の無理を抑える」「低負荷で続けられる」「最終採用を必ず人手確認にする」の3点であり、その条件に最も素直に合うのが候補Aである。pixiv は検索や作品詳細取得についてレートリミット、ログ監視、reCAPTCHA などの対策を入れているため、最初からクロールへ寄せすぎるのは得策ではない。保存HTML取込なら母集団を小さく保ちやすく、`seed候補 / learning寄り / 除外` への仕分けにもつなげやすい。作品観測は補助的に混ぜることで、検索結果だけでは不足しがちな R18 実務語彙を補完できる。

- 見送った候補とその理由  
  候補B単独は、作品バイアスやノイズ混入が大きく、棚卸し原料の安定運用としては少しぶれやすい。候補C単独は、最初から自動取得を中心に据えると、ページ構造追従や保守コストに加えて、pixiv 側対策との相性問題が先に立ちやすく、今回ほしい「小規模・低負荷・人手確認前提」の要件から外れやすい。

- 主なリスク  
  検索結果系だけだと、表層人気タグに寄りやすい。作品観測を入れすぎると、今度は作品固有ノイズが増える。raw を直接 seed や learning に流す設計にすると、現行の軽量方針が崩れる。

- 条件次第で有力になる次点案  
  保存HTMLの扱いが煩雑で継続しにくい場合は、候補Cを `seed語 5〜20件 / 1語1ページ / 明示実行のみ / 十分な待機あり` のような厳しい上限つき補助方式として採用する価値が上がる。ただし、その場合でも raw 出力までに留め、ランタイム反映は人手判定後に分離する。

## 5. 取得対象・取得単位・出力形式・採用フロー

### 取得対象

- 主対象  
  検索結果ページ、タグ検索ページの保存HTML

- 補助対象  
  代表作品ページ、必要時のみ超小規模な 1 ページ取得

- 初回で扱わないもの  
  大量ページ巡回、連続自動取得、ランキング全量追跡、無停止定期クロールのような高負荷導線

### 取得単位

- 検索結果系  
  `1 seed語 × 1保存HTML`

- 作品観測系  
  `1作品 × 1タグ集合`

- 超小規模クロールを入れる場合  
  `1 seed語 × 1ページ取得`

### 出力形式

- `raw`  
  `app/data/pixiv_popular_tag_collection_raw.jsonl` を使う。1 行 1 観測で、観測時点のタグ一覧、観測元種別、観測キー、観測日時を持つ。

- `review`  
  `app/data/pixiv_popular_tag_collection_review.csv` を使う。raw を正規化して重複寄せしたうえで、`seed候補 / learning寄り / 除外 / 判断保留` を人手で付けるレビュー用ファイルとする。

- 初回の原則  
  ランタイムで読む [pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json) や学習用 JSON を直接更新しない

### 採用フロー

1. 少数の seed 語を人が決める
2. 検索結果または作品ページを保存し、ローカルで抽出して raw を作る
3. raw を正規化して review 用一覧へまとめる
4. 人手で `seed候補 / learning寄り / 除外 / 判断保留` を付ける
5. seed に入れるものだけを限定反映する
6. learning 側へ寄せたいものは将来仕様と整合を取って別途検討する

## 5.1 公式方針を踏まえた自動化上限

- 2026-03-31 時点で、pixiv は検索や作品詳細取得の導線に対し、レートリミット、ログ保存・解析、reCAPTCHA などの対策を説明している。  
  参考: [pixiv inside 2023-05-09](https://inside.pixiv.blog/2023/05/09/183635)  
  参考: [pixiv inside 2023-05-17](https://inside.pixiv.blog/2023/05/17/102629)  
  参考: [reCAPTCHAとはなんですか？](https://www.pixiv.help/hc/ja/articles/38860105153561-reCAPTCHA%E3%81%A8%E3%81%AF%E3%81%AA%E3%82%93%E3%81%A7%E3%81%99%E3%81%8B)

- そのため、初回で許容する自動化は次までに留める。  
  `seed語 5〜20件程度`  
  `1語につき 1 ページ程度`  
  `明示実行のみ`  
  `十分な待機時間を入れる`  
  `raw 作成までで止める`

- これを超える広い自動巡回は、今回の棚卸し原料づくりの目的に対して過剰であり、運用上の無理も増えやすい。

## 6. workspace に入れる場合の最小構成

- 追加位置  
  正本コードは [app](/E:/codex/workspace/projects/post-manager-remake/app) 側を維持する。導入するとしても、既存 suggest 本体とは別に `収集補助用の単独スクリプト` と `収集結果データ` を分ける。

- 最小ファイル構成案  
  `app/src/pixiv_popular_tag_collection.py`  
  `app/data/pixiv_popular_tag_collection_raw.jsonl`  
  `app/data/pixiv_popular_tag_collection_review.csv`  
  `projects/post-manager-remake/docs/` 配下に採用判断メモ

- 既存運用を壊さない導入位置  
  [pixiv_tag_support.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_support.py) の suggest ロジックへは直接つながない。  
  [pixiv_tag_learning.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_learning.py) の保存時学習にも直接混ぜない。  
  既存の seed データ更新は、人手レビュー後の限定採用にする。

- 変えないこと  
  `posts.csv`、既存 seed / works の保存形式、保存時学習の JSON 形式、既存 UI の候補表示契約は初回では変えない。

## 7. 想定する戻し方

- 初回段階では raw / review 用の補助データと補助スクリプトだけを追加対象にする
- 収集補助が不要と判断した場合は、その補助スクリプトと補助データを退避すれば戻せる
- 既存 seed や learning へ自動接続しない前提にしておけば、既存運用への rollback は容易である

## 8. 実装前に確定すべきこと

- 先に決めるべき事項  
  初回は `保存HTML主 / 作品観測補助` で行くか  
  `learning寄り` を初回は単なるラベルに留めるか、将来の learning 反映候補として別棚にするか

- 後回しにしてよい事項  
  半自動補助スクリプトの有無  
  UI を付けるかどうか  
  learning 側に意味カテゴリを持たせるかどうか

- 想定する戻し方  
  既存ランタイムへつながない構成にしておけば、追加文書と補助ファイルの除去だけで戻せる

- 実装前に確認を入れるべきか  
  大きな分岐は少ないため、次スレッドではこの推奨案を初期案として進めてよい。出力形式は `raw = JSONL`、`review = CSV` を採用し、以後はこの前提で実装を進める。

## 9. 次スレッド開始時の最小到達目標

- 方式比較は `検索結果主 / 作品観測補助 / 半自動補助は保留` で固定する
- 方式比較は `保存HTML主 / 作品観測補助 / 超小規模クロールは保留` で固定する
- raw の取得単位と review の仕分け項目を固定する
- workspace へ入れる最小構成を、既存 suggest 本体と切り離した形で決める
- 実装に入るとしても、初回は補助スクリプトと raw / review 出力までに留める
