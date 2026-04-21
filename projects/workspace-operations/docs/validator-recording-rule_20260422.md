# validator recording rule

## 1. 目的

empirical-prompt-tuning の result 文書で、validator failure を instruction quality issue と混同しないための記録ルールを固定する。

## 2. failure の分け方

### schema mismatch

- validator の strict schema と workspace 運用形式のズレ
- 例:
  - `triggers:` による failure
  - strict validator が許可しない frontmatter key

### instruction quality issue

- skill 本文や frontmatter 自体の品質問題
- 例:
  - `name` / `description` の破損
  - YAML format 不正
  - description と body の乖離
  - success criteria の弱さ

## 3. result 文書での書き方

trial result には、必要に応じて次を分けて書く。

- Validation:
  - strict validator result
  - schema mismatch の有無
  - instruction quality issue の有無

## 4. 今回の適用例

- `project-scaffolder` の `< >` は instruction quality issue 寄りで修正対象
- `triggers:` で strict validator が落ちる既存 skill 群は schema mismatch として扱う

## 5. 実務ルール

- schema mismatch だけで trial を failure 扱いにしない
- instruction quality issue は empirical result の改訂テーマに含める
- strict validator の結果を使うときは、どちらの failure かを明記する
