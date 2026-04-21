# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `desktop-dnd-path-resolution`
- Canonical file: `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- browser と desktop shell の分岐が曖昧だと誤実装になりやすい
- D&D failure 時に既存 valid path を守れるかが実務上重要
- image file drop を親フォルダへ寄せる条件と不要 picker 回避を評価したい

## 3. Iteration 0

- frontmatter description と body の整合は取れている
- browser mode は supplemental、desktop shell mode は primary という軸も明確
- stale companion reference は前回までに整理済み
- 追加で見たい曖昧さは「画像ファイルを親フォルダへ寄せる条件を executor がどう解釈するか」

## 4. trial fixture

### Fixture A: browser-fallback

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-browser-fallback`
- 想定: browser では絶対パスが取れず、既存 valid path を守りながら次行動を案内したい

### Fixture B: shell-primary

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-shell-primary`
- 想定: desktop shell では native path を優先し、image drop を親フォルダへ寄せつつ不要 picker を避けたい

## 5. 固定 scenario

### Scenario A: browser fallback

- Case type: `median`
- User-like request:

```text
通常ブラウザでも使える drop zone の扱いを整理したいです。パスが取れないときに既存の valid path を壊さない方針で、実装の考え方を出してください。
```

Checklist:

- [critical] browser mode では D&D を supplemental として扱う
- 解決失敗でも既存の valid path を保持する
- 次の行動として browse dialog などの fallback を案内する
- hard error と warning を分ける
- 同じ warning の連続表示を避ける

### Scenario B: desktop shell primary

- Case type: `edge`
- User-like request:

```text
Electron 風の desktop shell では drag and drop を主入力にしたいです。画像ファイルを落としたときは親フォルダで扱いたいので、path 解決順と fallback を整理してください。
```

Checklist:

- [critical] desktop shell では D&D を primary input として扱う
- native path / preload bridge を resolution order に含める
- image file drop を親フォルダへ寄せる判断に触れる
- valid path 解決後に不要 picker を開かない
- unsupported path でも既存 valid value を保持する

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `desktop-dnd-path-resolution` at `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution` for this task.

Work from the brief in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-browser-fallback\screen.md`.
Produce a practical drag-and-drop path handling direction before coding.
```

### Prompt B

```text
Use the skill `desktop-dnd-path-resolution` at `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution` for this task.

Work from the brief in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-shell-primary\screen.md`.
Produce a practical drag-and-drop path handling direction before coding.
```
