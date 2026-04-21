# empirical-prompt-tuning trial result

## Target

- Target: `ui-design-direction`
- Canonical file: `E:\codex\workspace\.agents\skills\ui-design-direction\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: 方向性を決める

- Request summary: 内部向け一覧画面の screen purpose、構成方針、hierarchy を出す
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 画面目的と主操作が明示される: ○
- hierarchy と layout direction が出る: ○
- generic dashboard 化しない: ○
- desktop / mobile か、少なくとも responsive の考慮に触れる: ○

Observed ambiguity:

- internal tool としての密度重視、一覧中心、行アクション整理が明確で、generic dashboard への逃避がない

Discretion completion by executor:

- 主目的を「対象行の判定」と「次の処理開始」に絞り、上部の細い操作バー + 中央一覧という構成を提示した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Scenario B: 既存文脈を保つ

- Request summary: 既存業務画面の運用感を崩さず方向性だけ整える
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 既存文脈を保つ前提を外さない: ○
- 過剰に派手な redesign に寄らない: ○
- product-fit / trust level を意識する: ○

Observed ambiguity:

- trust / familiarity / quiet tone を崩さず、既存業務システムらしい方向に寄せている

Discretion completion by executor:

- 上部に状態集約、中央に閲覧中心、編集対象だけ強めるという保守的な構図を提案した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Overall result

- 両 scenario とも成功
- この skill は `purpose と hierarchy を出す` と `既存文脈を保つ` の両方を安定して満たした
- 次の UI 系対象へ進んでよい
