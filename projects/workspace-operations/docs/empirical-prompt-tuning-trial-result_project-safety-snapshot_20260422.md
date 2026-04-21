# empirical-prompt-tuning trial result

## Target

- Target: `project-safety-snapshot`
- Canonical file: `E:\codex\workspace\.agents\skills\project-safety-snapshot\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: 高リスク変更前の snapshot

- Request summary: high-risk change 前に軽量 snapshot を作る
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\project-safety-snapshot-fixture`
- Created zip: `E:\codex\workspace\archive\snapshots\project-safety-snapshot-fixture\20260422_030548.zip`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] `archive/snapshots/<project_name>/` に zip ができる: ○
- snapshot 対象が project 単位になっている: ○
- 除外対象が過剰に含まれない: ○
- 保存先が短く報告される: ○

Observed ambiguity:

- zip の存在確認だけでは不十分なので、entries を確認した
- 実際の zip entry は `README.md` と `src/app.py` のみで、`build` と `dist` は除外されていた

Discretion completion by executor:

- skill の除外対象をそのまま採用し、project 単位で snapshot を実行した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Scenario B: docs-only 更新

- Request summary: docs-only 更新で snapshot が必要かを判断する
- Success: ○
- Failed `[critical]` items: なし
- Precision: 2 / 2 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 軽微変更では常時運用しない方針を保つ: ○
- docs-only 更新に snapshot を強制しない: ○

Observed ambiguity:

- なし

Discretion completion by executor:

- docs-only 更新を高リスク変更から除外する判断を、skill 本文どおりに行った

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Overall result

- 両 scenario とも成功
- この skill は trial でも `必要時だけ使う` 制約と `軽量 zip を作る` 目的を両立できていた
- 次の改訂は必須ではない
