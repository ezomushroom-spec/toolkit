# empirical-prompt-tuning trial result

## Target

- Target: `subagent-debug-review`
- Canonical file: `E:\codex\workspace\.agents\skills\subagent-debug-review\SKILL.md`
- Evaluation date: 2026-04-22
- Iteration: `2nd`
- Executor separation: empirical
- Revision theme: borderline case での subagent 不使用判断と review / diagnosis の寄せ方の明確化

## Scenario A: borderline split

- Request summary: 複数観点に見えるが単一ファイルへ収束する保存時フリーズの調査方針を整理する
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-borderline-split`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 追加 subagent を使うか使わないかの根拠を明示する: ○
- 単一ファイルへ収束するなら主担当でまとめる判断が出る: ○
- 最小修正方針へつながる整理になる: ○

Observed ambiguity:

- `分解可能案件` と `単純案件寄り` の呼び方は揺れるが、利得が薄いなら主担当でまとめる判断は安定している

Discretion completion by executor:

- UI / I-O / logging に分けたくなる入口を見せつつ、最終集約点が `save_document()` と `src/save_manager.py` であることを根拠に subagent 不使用を選んだ

Revision taken:

- `境界案件` として、入口は複数でも収束先が同じなら主エージェントでまとめてよいことを本文へ補足した

## Scenario B: review vs diagnosis

- Request summary: 再現未確定の最近差分に対して strict review と原因調査の寄せ方を整理する
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-review-vs-diagnosis`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] strict review 主軸か diagnosis 主軸かを最初に整理する: ○
- 再現未確定の段階で断定しすぎない: ○
- review で出すべき危険箇所と、追加調査が必要な点を分ける: ○

Observed ambiguity:

- review と diagnosis の比重は brief の書き方で多少揺れるが、再現未確定なら review 先行という軸は安定していた

Discretion completion by executor:

- 例外握り潰し、error 表示、リソース解放、正常系破壊リスクを先に review で洗い、その後に必要最小限の再現調査へ切り分けた

Revision taken:

- execution flow に、再現未確定で `厳しめに見てほしい` 依頼なら strict review 主軸で始める補足を追加した

## Overall result

- borderline split と review vs diagnosis の両方で、過剰委任を抑えた安全な判断が出た
- 本文へ小さく基準を足したことで、`使わない理由` と `review 先行条件` は初回より明確になった
