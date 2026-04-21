# empirical-prompt-tuning 2nd iteration 準備

## 1. 対象

- Target: `windows-batch-launcher`
- Canonical file: `E:\codex\workspace\.agents\skills\windows-batch-launcher\SKILL.md`
- Iteration theme: first-run install 境界と broken `.venv` fallback

## 2. この iteration で見たいこと

- `node_modules` が無いときに install を自動実行するか、明示的に止めるかの判断境界
- `.venv` が存在するが壊れているとき、どこまで fallback を広げるか
- debug log に interpreter path と exit code をどこまで残すか

## 3. 固定 scenario

### Scenario A: install boundary

- Case type: `edge`
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-install-boundary`
- User-like request:

```text
この app を利用者が double-click で起動します。`node_modules` が無い初回状態もありえますが、勝手に install を走らせるべきか迷っています。安全な `start.bat` と `debug-start.bat` を整えてください。
```

Checklist:

- [critical] install を自動実行するかどうかの判断を明示する
- silent failure を避ける visible failure path がある
- ASCII-safe な batch を保つ
- debug launcher で原因追跡ができる

### Scenario B: broken venv fallback

- Case type: `edge`
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-broken-venv`
- User-like request:

```text
`.venv` があるのに壊れていて、`py -3` も信用できません。この app 用の `start.bat` と `debug-start.bat` を安全に整えてください。どの interpreter を試したかは必ず見えるようにしたいです。
```

Checklist:

- [critical] broad selector を盲信しない
- broken `.venv` を検知して次候補へ進む判断がある
- log に実 interpreter path と exit code が残る
- fallback を広げすぎず、失敗理由が見える

## 4. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `windows-batch-launcher` at `E:\codex\workspace\.agents\skills\windows-batch-launcher\SKILL.md`.

Work only inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-install-boundary`.
Create or repair `start.bat` and `debug-start.bat`.
Do not edit unrelated files.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `windows-batch-launcher` at `E:\codex\workspace\.agents\skills\windows-batch-launcher\SKILL.md`.

Work only inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-broken-venv`.
Create or repair `start.bat` and `debug-start.bat`.
Do not edit unrelated files.
```
