# empirical-prompt-tuning trial result

## Target

- Target: `project-scaffolder`
- Canonical file: `E:\codex\workspace\.agents\skills\project-scaffolder\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: 中央値ケース

- Request summary: 画像整理ツール試作用の新規 project を標準構成で作る
- Created path: `E:\codex\workspace\projects\image-organization-tool-prototype`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 5 / 5 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] `projects/<slug>/` と標準 3 文書が作られる: ○
- `docs/current-state-check.md` `docs/implementation-plan.md` `docs/pre-implementation-decision.md` が揃う: ○
- summary は目的を外しすぎない: ○
- 不明項目を勝手に詳細化しすぎない: ○
- 既存 project と名前衝突した場合は止まる方針を保つ: ○

Observed ambiguity:

- user-like request では project 名を明示していないため、subagent が `image-organization-tool-prototype` を自力で決めた
- 今回の命名は妥当だが、命名規則は skill 本文で明示されていない

Discretion completion by executor:

- purpose から英語 slug を補完して project 名を決定した

Next revision theme:

- name 未指定時の project 名決定ルールを skill 本文へ明示する

## Scenario B: 日本語名ケース

- Request summary: `画像仕上げメモ整理` という intended name で新規 project を標準構成で作る
- Created path: `E:\codex\workspace\projects\画像仕上げメモ整理`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] Windows で危険な文字を避けた folder 名になる: ○
- 本来の project 名の意味が不自然に失われない: ○
- 標準構成の文書が揃う: ○
- 未確定事項を勝手に作り込みすぎない: ○

Observed ambiguity:

- 日本語名をそのまま folder に使ってよいかは skill 本文から推定できるが、slugify の具体規則は script 依存

Discretion completion by executor:

- safe character 判定を本文と実ファイル名から解釈して、そのまま日本語名を採用した

Next revision theme:

- 日本語名がそのまま通る条件と、slugify が変換する条件の説明を 1 行追加する

## Overall result

- 両 scenario とも成功
- 初回 empirical trial としては false negative は見えなかった
- 一方で、`name 未指定時の project 名決定` は executor の裁量補完に依存している
- 次の最小改訂は `project-scaffolder` に命名ルールの補足を入れること
