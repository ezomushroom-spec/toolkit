# skill validator 方針ギャップ整理

## 1. 何がずれているか

- workspace 固有 skill 16 件のうち 13 件が frontmatter に `triggers:` を持つ
- 一方、`C:\Users\ezomu\.codex\skills\.system\skill-creator\scripts\quick_validate.py` は frontmatter の許可キーを `name`, `description`, `license`, `allowed-tools`, `metadata` に限定している
- そのため、workspace で現用の skill 形式を strict validator に通すと、内容が妥当でも `triggers` だけで落ちる

## 2. 実確認

- `triggers:` を持つ workspace skill: 13
- `triggers:` を持たない workspace skill: 3
- validator の許可キー定義: `quick_validate.py` 40 行目付近

## 3. このズレの意味

- 現在の validator failure は、即「skill 品質が悪い」を意味しない
- むしろ、workspace 独自運用で trigger 語を frontmatter に持たせている設計と、skill-creator 側の strict schema が噛み合っていない
- empirical-prompt-tuning の trial で validator を補助指標に使う場合、この schema mismatch を未整理のまま品質 failure に混ぜるのは危険

## 4. 対応候補

### 候補 A: workspace skill から `triggers:` を除去する

- 長所:
  - strict validator と一致する
- 短所:
  - 既存 skill 群の trigger 語が frontmatter から消える
  - 現行入口文書や運用習慣との整合を崩しやすい
  - 大量改訂になりやすい

### 候補 B: validator を workspace 運用に合わせて拡張する

- 長所:
  - 既存 skill 形式を保ったまま validation できる
  - schema mismatch と skill 品質を分けて扱える
- 短所:
  - local tool 側の分岐運用が増える
  - upstream の strict schema とはずれる

### 候補 C: validation を 2 段に分ける

- 長所:
  - `strict upstream compatibility` と `workspace operational validity` を分離できる
  - empirical-prompt-tuning で「どの種類の失敗か」を記録しやすい
- 短所:
  - 運用説明を 1 枚追加する必要がある

## 5. 推奨

- 推奨案: 候補 C
- 理由:
  - 今の workspace では `triggers:` が広く使われており、一括除去はコストが高い
  - validator の strict failure と、empirical な instruction 品質 failure を分けて扱うほうが誤読が少ない
  - 将来 upstream 互換へ寄せる判断も後からできる

## 6. 実務ルール案

- `quick_validate.py` が `triggers:` で落ちた場合は、当面 `schema mismatch` として別記録にする
- `name` / `description` / YAML format の破損は通常の validation failure として扱う
- empirical-prompt-tuning の結果文書では、validator failure を次の 2 種に分ける
  - `schema mismatch`
  - `instruction quality issue`

## 7. 次の一手

1. `quick_validate.py` の結果を empirical result に書くとき、`schema mismatch` を別欄で記録する
2. 必要になった時点で、workspace 用 wrapper validator を用意する
3. `triggers:` を今すぐ一括除去する判断はしない
4. 実務ルールは `validator-recording-rule_20260422.md` を正本とする
