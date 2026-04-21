# empirical-prompt-tuning trial result

## Target

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 5. 文書と配置`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: active project placement

- Request summary: active project だが入口文書や判断・計画文書の配置が未整備
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-doc-placement-active-project`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] active project なら `projects` 側で入口文書を揃える: ○
- 判断・計画文書を project 配下へ寄せる: ○
- 直下散在メモをそのまま許さない: ○
- index や入口導線更新の必要性に触れる: ○

Observed ambiguity:

- `どこまでを入口文書として必須にするか` は project の成熟度で多少揺れるが、最低限 `AGENTS.md` / `START_HERE.md` / `PROJECT_SUMMARY.md` を揃える方向は安定していた

Discretion completion by executor:

- active project の入口文書と判断・計画文書を `projects/<name>/` 配下へ寄せる前提を崩さなかった

Revision taken:

- 必須改訂なし

## Scenario B: archive boundary

- Request summary: 参照専用になった旧 folder を `projects` に残すべきかを判断する
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-doc-placement-archive-boundary`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] active でないなら `archive` 側を検討する: ○
- 旧→新対応表や戻し方を残す必要に触れる: ○
- active project と混同しない名前・文書・置き場を求める: ○

Observed ambiguity:

- `参照される` ことと `active` であることの区別は運用依存で揺れうるが、archive 移動前に対応表と戻し方が必要という軸は安定していた

Discretion completion by executor:

- archive 送りを急がず、active / backup / archive の区別と移動前要件をまとめて要求した

Revision taken:

- 必須改訂なし

## Overall result

- active project の入口整備と archive 境界の両方で、節の配置原則は安定して読まれていた
- guidance section として十分機能しており、今回は本文追記なしでよい
