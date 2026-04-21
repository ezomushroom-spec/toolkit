# empirical-prompt-tuning trial result

## Target

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 4. 品質確認`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: high-risk action

- Request summary: 一括削除や上書き export のような高コスト操作を含む変更を、`動いた` だけで完了扱いにしない
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-quality-high-risk-action`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 動いたように見えるだけでは完了扱いにしない: ○
- 高コスト操作では確認、対象明示、二重実行防止、失敗時表示を優先する: ○
- 正常系だけでなく失敗系を含める: ○

Observed ambiguity:

- `確認ダイアログがある` と `実運用で対象が分かる` は別なので、UI 上の見え方まで実確認しないと浅い完了判定に流れうる

Discretion completion by executor:

- 完了判定を正常系から切り離し、高リスク操作の安全確認を独立したゲートとして扱った

Revision taken:

- 必須改訂なし

## Scenario B: shallow test report

- Request summary: `テストは書いた` だけで完了扱いへ流れそうな案件を引き戻す
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-quality-shallow-test-report`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] テストを書いたことだけで完了扱いにしない: ○
- 実行可能性と変更確認への有効性に触れる: ○
- 空入力、不正設定、存在しないパス、キャンセル後状態などを含める: ○

Observed ambiguity:

- `どの証跡を残せば十分か` の粒度は `docs/quality-gates.md` と合わせて運用する必要がある

Discretion completion by executor:

- `書いた` と `再現して判定できる` を分け、失敗系やキャンセル後状態まで確認対象へ戻した

Revision taken:

- 必須改訂なし

## Overall result

- 高リスク操作の完了判定と shallow test report の両方で、節の品質ゲートとしての読みは安定していた
- guidance section として十分機能しており、今回は本文追記なしでよい
