# Post Manager 追加仕様
## Pixivタグ支援 Phase 2 保存時学習仕様

最終更新日: 2026-03-30  
基準文書:
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-spec_revised_20260329.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\pixiv-tag-support-phase1-implementation-plan_20260329.md`
- `E:\codex\workspace\projects\post-manager-remake\docs\current-specification_20260328.md`

## 1. Goal

Pixivタグ支援の Phase 2 として、ユーザーが保存確定した Pixivタグだけを軽量に学習し、次回以降の候補順位へ反映できる状態を作る。

この段階では、共起学習、作品別学習、タイトル語学習、外部辞書自動吸収は行わない。

## 2. 基本方針

- 学習対象は `保存確定した Pixivタグ` のみとする
- 学習は候補順位調整のみに使う
- タグの自動追加、自動削除、自動置換は行わない
- `posts.csv` に学習データを混在させない
- 学習機能が壊れてもタスク保存は継続できる

## 3. 学習トリガー

### 3.1 採用トリガー

学習トリガーは `タスク編集モーダル保存成功時` とする。

対象条件:

- 新規タスク保存成功
- 既存タスク更新成功
- `tags` に 1 件以上の Pixivタグが入っている

### 3.2 非採用トリガー

以下では学習しない。

- モーダルを開いただけ
- 候補タグをクリックしただけ
- Pixiv 実行を開始しただけ
- Pixiv ブラウザ補助プロセスが完了しただけ
- タスク保存失敗時
- `tags` が空の保存

## 4. 保存先方針

### 4.1 正本の分離

`posts.csv` は投稿タスクの業務データ正本として維持し、学習データは別保存にする。

### 4.2 Phase 2 の保存先

Phase 2 の学習保存先は次を推奨する。

- `app/data/pixiv_tag_learning.json`

理由:

- Phase 2 は単純頻度だけなので JSON で十分
- 破損時の初期化と目視確認が容易
- SQLite 導入を Phase 3 以降へ送れる
- rollback が簡単

### 4.3 将来移行

Phase 3 以降で学習内容が増えた場合は、次への移行を許容する。

- `app/data/pixiv_tag_learning.sqlite3`

ただし Phase 2 実装では SQLite を前提にしない。

## 5. 保存データ仕様

### 5.1 最小形式

想定形式:

```json
{
  "version": 1,
  "updated_at": "2026-03-30T12:34:56+09:00",
  "tag_counts": {
    "オリジナル": 5,
    "女の子": 3,
    "ブルーアーカイブ": 2
  }
}
```

### 5.2 意味

- `version`  
  将来移行用のスキーマ版

- `updated_at`  
  最終更新日時

- `tag_counts`  
  保存確定された Pixivタグごとの累積採用回数

## 6. 学習内容

Phase 2 で学習するのは以下のみ。

- 個別タグの使用回数

Phase 2 では学習しないもの:

- タグ同士の共起
- 作品名とタグの対応
- タイトル語とタグの対応
- フォルダ名とタグの対応
- ネガティブ学習

## 7. 更新ルール

### 7.1 タグ分解

`tags` は現行仕様どおりスペース区切りで分解する。

更新前に以下を行う。

- 空文字除去
- 同一保存内の重複除去

### 7.2 加算

1 回の保存成功につき、出現した各タグを `+1` する。

例:

- 保存タグ: `オリジナル 女の子 オリジナル`
- 学習加算: `オリジナル +1`, `女の子 +1`

### 7.3 空保存

`tags` が空なら学習更新しない。

### 7.4 破損時

学習ファイルが壊れている場合:

1. タスク保存自体は成功させる
2. 学習更新は warning ログに落とす
3. 必要なら空の初期構造へ再生成する

## 8. 候補順位への反映

Phase 2 では、学習結果を `history` より上位の個人履歴として扱う。

推奨順位:

1. `learning`
2. `history`
3. `works`
4. `seed`

推奨スコア例:

- `learning`: `200 + count`
- `history`: `100 + count`
- `works`: `80`
- `seed`: `40 - 60`

## 9. API と backend への反映方針

### 9.1 学習更新

Phase 2 では専用 `learn` API を必須にしない。

推奨:

- タスク保存成功フロー内で backend が内部更新する

理由:

- 学習更新を UI から二重送信しにくい
- Web UI / Electron UI で挙動差分が出にくい
- 保存成功と学習成功の整合を backend 側で管理しやすい

### 9.2 候補取得

既存の `GET /api/pixiv-tags/suggest` を拡張し、学習結果を候補順位へ反映する。

## 10. 対象ファイル

### backend

- `app/src/pixiv_tag_support.py`
- `app/src/api_server.py`
- `app/src/manager.py`

### data

- `app/data/pixiv_tag_learning.json`

### frontend

- `app/web/script.js`

必要なら、学習状態の短い表示だけを追加する。
ただし Phase 2 では管理 UI は作らない。

## 11. UI 方針

Phase 2 で UI に足してよいもの:

- 候補順位の自然な改善
- 必要最小限の warning ログ

Phase 2 で UI に足さないもの:

- 学習 DB 管理画面
- リセットボタン
- 辞書エディタ
- 詳細スコア表示

## 12. リスク

- タスク保存成功と学習更新失敗が分離するため、学習だけ取りこぼす場合がある
- JSON 破損時に更新できなくなる可能性がある
- 運用初期は学習データが薄く、効果が見えにくい
- 保存のたびに即学習するため、仮タグを保存すると辞書が汚れやすい

## 13. リスク緩和

- 学習対象は保存成功時だけに限定する
- 同一保存内の重複タグは 1 回として扱う
- 学習失敗でタスク保存を失敗扱いにしない
- 学習ファイルには `version` を持たせる
- 破損時は空構造へ戻せるようにする

## 14. 非目標

Phase 2 の非目標は以下。

- SQLite 導入
- 共起学習
- 作品別学習
- タイトル語学習
- フォルダ名学習
- 外部辞書の自動収集
- 学習内容の可視化 UI

## 15. Rollback

戻し方は以下。

1. `app/src/pixiv_tag_support.py` の学習読込・更新処理を戻す
2. `app/src/api_server.py` または保存フローの学習呼び出しを戻す
3. `app/data/pixiv_tag_learning.json` を削除または退避する
4. UI に追加した学習関連の表示があれば戻す

この Phase は `posts.csv` スキーマを変更しないため、rollback はコード差分と学習ファイルの除去で済む。

## 16. Confirmation checklist

- タスク保存が従来どおり成功する
- `tags` が空の保存で学習更新しない
- 同一保存内の重複タグを二重加算しない
- 学習ファイル破損時でもタスク保存は継続する
- `GET /api/pixiv-tags/suggest` で学習タグが上位に出る
- Patreon / Discord 側に新しい影響が出ていない
