# Pixivタグ語彙棚卸し方針 2026-03-31

## 現状確認

- 正本ロジックは [app/src/pixiv_tag_support.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_support.py) にあり、候補返却は `learning` / `history` / `works` / `seed` を統合して最大18件返す。
- 意味カテゴリは `rating / work / character / content` の4層で、表示側は [app/web/script.js](/E:/codex/workspace/projects/post-manager-remake/app/web/script.js) で `年齢区分 / 作品 / キャラ / 内容候補` に分けている。
- 初期表示件数は `rating:1, work:2, character:3, content:2` で、残りは `もっと見る` に退避している。
- [app/data/pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json) はまだ薄く、`オリジナル / 創作 / 女の子 / 男の子 / R-18 / 二次創作 / 制服 / 水着 / 巨乳 / メイド` の少数基礎タグしかない。
- [app/data/pixiv_seed_works.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_works.json) は作品・主要キャラの入口として機能している。
- learning は [app/src/pixiv_tag_learning.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_learning.py) の保存時学習で単純カウントされる。語彙の厚みは持てるが、意味の層分けまではまだ持っていない。

## 採用判断

### 1. 課題は「語彙量」と「語彙アクセス」を分けて扱う

- 語彙量不足は主に `pixiv_seed_tags.json` と learning 蓄積量の問題。
- 語彙アクセス不足は、候補の出し方と初期表示配分の問題。
- この2つを混ぜると、seed を増やしすぎて辞書ブラウザ化しやすい。

### 2. seed の役割は「少数の外せない基礎語彙」に限定する

- `作品 / キャラ / 少数の年齢区分` を主軸とする。
- R18文脈の語彙をまったく避けない。
- ただし `行為 / シチュ / 性癖` を seed の上位常連にしない。
- 誤爆コストの高い語彙は、同梱辞書より learning/history 側で届かせる。

### 3. R18語彙は内部棚で整理してから増やす

- 追加時は少なくとも次の内部棚で整理する。
- `年齢区分`
- `行為`
- `シチュ`
- `属性`
- `フェチ/嗜好`
- UI 表示は当面 `content` のままでよいが、辞書設計は内部棚を意識して増補する。
- これにより将来 `content` を `シチュ / 属性` へ分ける判断もしやすくなる。

### 4. 実装順は「Electron画面調整」より先に「語彙棚卸しの基準」を軽く固める

- 画面だけ触っても、母集団語彙が薄いと件数配分の評価がぶれやすい。
- 先に seed と R18語彙の追加方針を軽く定め、その後 Electron で実画面確認する。
- ただし大規模辞書化はしない。まずは少数の代表語彙で確認する。

## 棚卸しの進め方

### 対象

- [app/data/pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json)
- [app/src/pixiv_tag_support.py](/E:/codex/workspace/projects/post-manager-remake/app/src/pixiv_tag_support.py)
- [app/web/script.js](/E:/codex/workspace/projects/post-manager-remake/app/web/script.js)
- Electron 実画面

### 実装順

1. `pixiv_seed_tags.json` の既存語彙を `年齢区分 / 作品寄り / キャラ寄り / 内容寄り` に棚卸しする。
2. R18語彙の候補を `seed に入れる少数語彙` と `learning/history に任せる語彙` に分ける。
3. `seed に入れる少数語彙` だけを追加して、候補母集団を少し厚くする。
4. Electron 実画面で `R-18 東方 霊夢 メイド 巨乳` などの代表入力を触り、初期表示件数と `もっと見る` の頻度を観測する。
5. 必要なら `content` 内部を `シチュ / 属性` に分けるか判断する。

### 確認点

- `作品 / キャラ` が主役として先頭に来るか。
- `年齢区分` が少数でも安定して目に入るか。
- R18語彙を増やしても `content` が辞書棚化しないか。
- `もっと見る` を押さなくても最低限のタグ選定ができるか。
- `もっと見る` が頻出しすぎて操作ノイズにならないか。

### 戻し方

- 今回の棚卸しは seed データと表示件数の限定変更にとどめる。
- 巻き戻しは `pixiv_seed_tags.json` の追加分と、必要なら [app/web/script.js](/E:/codex/workspace/projects/post-manager-remake/app/web/script.js) の件数設定を戻せばよい。
- learning JSON と CSV 形式は変えない前提を維持する。

## 未決事項

- `content` を当面1グループで維持するか、`シチュ / 属性` に分けるか。
- `年齢区分` を常時表示のままにするか、R18文脈時だけ強く出すか。
- R18語彙のうち、どこまでを seed 同梱に含めるか。
- learning 側にも将来的に内部カテゴリを持たせるか。

## 追記: 全量取り込みの整理方針

- curated な少数タグは [app/data/pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json) に残す。
- 旧DB由来の全量語彙は [app/data/pixiv_bundled_vocabulary_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_bundled_vocabulary_tags.json) に分離する。
- suggestion では、`seed` は少数常備とフォールバック、`bundled vocabulary` は検索一致や文脈一致時の追加候補として使う。
- これにより「全部取り込む」と「候補棚を辞書ブラウザ化しない」を両立する。

## 次スレッドの開始点

- まず [app/data/pixiv_seed_tags.json](/E:/codex/workspace/projects/post-manager-remake/app/data/pixiv_seed_tags.json) の棚卸しから入り、`seedに残す少数R18語彙` と `learning/history寄り語彙` を仕分ける。
- その後に Electron 実画面で件数配分を触る。
