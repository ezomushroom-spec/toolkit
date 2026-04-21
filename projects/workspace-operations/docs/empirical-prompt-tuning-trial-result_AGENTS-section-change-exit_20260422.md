# empirical-prompt-tuning trial result

## Target

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 8. 変更の出口`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: standard flow

- Request summary: 通常の修正完了で、口頭完了だけで閉じず標準フローへ進める
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-exit-standard-flow`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 標準処理として `branch -> commit -> push -> PR` を維持する: ○
- 口頭完了だけで閉じない: ○
- 完了扱いの条件として外部反映フローに触れる: ○

Observed ambiguity:

- `branch` を新規作成と読むか、既存作業ブランチの継続と読むかは多少揺れるが、標準フローの骨格は崩れていない

Discretion completion by executor:

- 完了扱いの条件を「外部反映まで進める標準処理」として読んだ

Revision taken:

- 必須改訂なし

## Scenario B: exception case

- Request summary: push / PR をまだしたくない事情があるが、例外理由と戻し方が未記録
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-exit-exception-case`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 例外なら project 側文書に理由と戻し方が必要だと触れる: ○
- 標準処理を消さず、例外として扱う: ○
- `push しない = そのまま完了` にしない: ○

Observed ambiguity:

- 例外理由の最低粒度は project 文書の運用に委ねられるので、今後同じ迷いが続くなら project 側 template で補強余地がある

Discretion completion by executor:

- 例外を「標準ルールの不採用」ではなく「文書化された例外」として扱った

Revision taken:

- 必須改訂なし

## Overall result

- 標準ケースでも例外ケースでも、節の出口ルールは安定して読まれていた
- guidance section として十分機能しており、今回は本文追記なしでよい
