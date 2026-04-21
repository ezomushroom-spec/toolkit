# empirical-prompt-tuning trial result

## Target

- Target: `subagent-debug-review`
- Canonical file: `E:\codex\workspace\.agents\skills\subagent-debug-review\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: 重い不具合

- Request summary: 保存失敗とフリーズが併発する不具合の安全な調査方針を出す
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-heavy`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 単純案件か分解可能案件かを最初に判定する: ○
- 委任するとしても調査役に限定する: ○
- 主エージェントが最終統合責任を持つ前提を崩さない: ○
- 出力がレビュー結果と修正方針にまとまる: ○

Observed ambiguity:

- `分解可能案件` と判定しつつ、実ファイルが 1 か所に収束している場合に追加 subagent を使うべきかは裁量の余地がある

Discretion completion by executor:

- `分解可能案件` だが並列調査の利点が薄いので追加 subagent は使わない、という抑制判断を行った

Next revision theme:

- `分解可能だが単一ファイルへ収束する場合は主担当でまとめてよい` という判断基準を本文へ補ってもよい

## Scenario B: 軽微不具合

- Request summary: null 参照に近い 1 か所の不具合原因と最小修正方針を出す
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\subagent-debug-review-simple`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 安易に subagent を使わない: ○
- 重い調査フローへ拡張しない: ○
- 最小修正方針へ寄せる: ○

Observed ambiguity:

- 早期 return を空文字にするか `None` にするかは呼び出し側契約に依存する

Discretion completion by executor:

- 値契約が未提示なので、戻り値方針は呼び出し側に合わせて選ぶべきと留保した

Next revision theme:

- `最小修正方針では、契約未確定部分を断定しない` という出力上の期待を本文へ足してもよい

## Overall result

- 両 scenario とも成功
- この skill は heavy case / simple case の切り分けで過剰委任を抑えられている
- 大きな改訂は不要
- 補うなら、`分解可能だが追加 subagent が不要な条件` を 1 段だけ明示するとさらに安定しそう
