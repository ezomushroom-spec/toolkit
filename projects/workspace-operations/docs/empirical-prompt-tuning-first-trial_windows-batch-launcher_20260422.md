# empirical-prompt-tuning 初回 trial 準備

## 1. 初手対象

- Target: `windows-batch-launcher`
- Canonical file: `E:\codex\workspace\.agents\skills\windows-batch-launcher\SKILL.md`
- Priority: `Critical`

## 2. この対象を選ぶ理由

- 起動不能や silent failure に直結しやすい
- batch 文面、working directory、debug launcher、interpreter 方針という観測点が明確
- 実プロジェクトを触る前に fixture で判定しやすい

## 3. trial fixture

### Fixture A: dev server

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-dev`
- 想定: `npm run dev` でローカル dev server を起動する小さな web app
- 期待: `start.bat` と `debug-start.bat` を安全に整備する

### Fixture B: python launcher

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-python`
- 想定: `py -3` だと意図しない interpreter を拾う可能性がある Python app
- 期待: project-local interpreter 優先と debug ログを持つ launcher を整備する

## 4. 固定 scenario

### Scenario A: dev server 起動 batch

- Case type: `median`
- User-like request:

```text
このローカル app 用に `start.bat` と `debug-start.bat` を作ってください。
double-click 起動で失敗時に原因が見えるようにしたいです。
```

Checklist:

- [critical] working directory 固定と失敗時可視化が入る
- ASCII 安全な batch 文面になる
- command 存在確認または first-run dependency 方針がある
- debug launcher の役割が分かる

### Scenario B: Python interpreter の食い違い

- Case type: `edge`
- User-like request:

```text
`py -3` だと違う Python が選ばれて落ちます。
この app 用の `start.bat` と `debug-start.bat` を安全に直してください。
```

Checklist:

- [critical] broad selector を盲信しない
- project-local interpreter 優先が示される
- log で実際の interpreter を確認できる

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `windows-batch-launcher` at `E:\codex\workspace\.agents\skills\windows-batch-launcher` for this task.

Work only inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-dev`.
Create `start.bat` and `debug-start.bat` for this local app.
Make double-click startup failures visible.
Keep the batch files ASCII-safe.
Do not change unrelated files.
```

### Prompt B

```text
Use the skill `windows-batch-launcher` at `E:\codex\workspace\.agents\skills\windows-batch-launcher` for this task.

Work only inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-python`.
Repair or create `start.bat` and `debug-start.bat` for this Python app.
Assume `py -3` may select the wrong interpreter.
Prefer project-local interpreters when available and keep logging visible.
Do not change unrelated files.
```
