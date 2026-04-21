# empirical-prompt-tuning trial result

## Target

- Target: `desktop-dnd-path-resolution`
- Canonical file: `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: browser fallback

- Request summary: browser で path が取れないときに既存 valid path を壊さず、次行動を案内する扱いを整理する
- Success: ○
- Failed `[critical]` items: なし
- Precision: 5 / 5 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] browser mode では D&D を supplemental として扱う: ○
- 解決失敗でも既存の valid path を保持する: ○
- 次の行動として browse dialog などの fallback を案内する: ○
- hard error と warning を分ける: ○
- 同じ warning の連続表示を避ける: ○

Observed ambiguity:

- 変更候補ファイルの参照は brief の記述をそのまま拾っており、実在確認まではしていない

Discretion completion by executor:

- browser では `Invalid input` のような曖昧エラーで止めず、保持中の valid value と次行動案内をセットにした

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Scenario B: desktop shell primary

- Request summary: desktop shell で D&D を主入力にし、image file drop を親フォルダへ寄せつつ不要 picker を避ける
- Success: ○
- Failed `[critical]` items: なし
- Precision: 5 / 5 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] desktop shell では D&D を primary input として扱う: ○
- native path / preload bridge を resolution order に含める: ○
- image file drop を親フォルダへ寄せる判断に触れる: ○
- valid path 解決後に不要 picker を開かない: ○
- unsupported path でも既存 valid value を保持する: ○

Observed ambiguity:

- 画像ファイルを親フォルダへ寄せる条件は「folder workflow のとき」という解釈で自然に補完されており、skill の意図と整合している

Discretion completion by executor:

- backend validation と frontend extraction を分け、最初に信頼できる path が取れたら止める方針を明確化した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Overall result

- 両 scenario とも成功
- browser / desktop shell の分岐、既存 valid path 保持、parent-folder 解決、不要 picker 回避の主要論点は安定して出た
- `Important` 群の最後の trial として通過してよい
