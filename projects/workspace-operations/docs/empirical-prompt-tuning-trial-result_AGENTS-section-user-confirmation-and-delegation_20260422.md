# empirical-prompt-tuning trial result

## Target

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 6. ユーザー確認と委任`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: no permission

- Request summary: 分解利得はあるが、ユーザーは subagent 利用を明示的には許可していない
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-delegation-no-permission`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 明示許可なしでは subagent を使わない: ○
- それでも main agent で前進できる方針を出す: ○
- 無用な停止ではなく、許可が必要な境界を説明できる: ○

Observed ambiguity:

- `必要なら深く見て` のような文言を、main agent の深掘り許可と subagent 許可のどちらに読むかがやや揺れうる

Discretion completion by executor:

- 無許可では subagent を起動せず、main agent で一次切り分けを先に進める方針を保った

Revision taken:

- `必要なら深く見て` や `詳しく調べて` だけでは subagent 許可とみなさない一文を section へ追加した

## Scenario B: delegation permitted

- Request summary: ユーザーは subagent 利用を明示的に許可している
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-delegation-with-permission`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 許可ありでも境界が明確な探索へ絞る: ○
- 同じファイル群の無秩序な並列編集を避ける: ○
- 利用者や運用者視点を含める余地に触れる: ○
- main agent が最終判断を持つ前提を崩さない: ○

Observed ambiguity:

- `利用者や運用者視点を少なくとも 1 つ含める` の適用範囲は案件によって揺れうるが、節全体の趣旨は安定して解釈されていた

Discretion completion by executor:

- 許可ありでも探索・切り分けの境界を先に作り、丸投げへ流れなかった

Revision taken:

- 必須改訂なし

## Overall result

- 無許可ケースと許可ありケースの両方で、節の芯は安定して解釈された
- 追加した 1 行で、main agent の深掘り許可と subagent 許可の誤読リスクは下がった
- guidance section の初回実 trial として通過してよい
