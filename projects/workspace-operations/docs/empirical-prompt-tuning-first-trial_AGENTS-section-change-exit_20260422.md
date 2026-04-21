# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 8. 変更の出口`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 変更完了の出口が曖昧だと、workspace の標準運用がぶれやすい
- 標準処理と例外処理の両方をどう読むかを確認しやすい

## 3. Iteration 0

- section は `branch -> commit -> push -> PR` を標準とし、例外時は理由と戻し方を project 文書へ残すことを求めている
- 追加で見たい曖昧さは「口頭完了だけで閉じないか」と「例外を標準破棄ではなく例外として扱えるか」

## 4. trial fixture

### Fixture A: standard-flow

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-exit-standard-flow`
- 想定: 通常の修正完了なので標準処理を踏むべき

### Fixture B: exception-case

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-exit-exception-case`
- 想定: push/PR をまだしない事情はあるが、例外理由と戻し方が未記録

## 5. 固定 scenario

### Scenario A: standard flow

- Case type: `median`
- User-like request:

```text
修正は終わりました。これで完了扱いにしてよいですか。
```

Checklist:

- [critical] 標準処理として `branch -> commit -> push -> PR` を維持する
- 口頭完了だけで閉じない
- 完了扱いの条件として外部反映フローに触れる

### Scenario B: exception case

- Case type: `edge`
- User-like request:

```text
今回は push や PR をまだしたくありません。このまま完了扱いにしてよいか見てください。
```

Checklist:

- [critical] 例外なら project 側文書に理由と戻し方が必要だと触れる
- 標準処理を消さず、例外として扱う
- `push しない = そのまま完了` にしない

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 8. 変更の出口` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-exit-standard-flow\brief.md`.
Produce an evaluation direction before any coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 8. 変更の出口` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-exit-exception-case\brief.md`.
Produce an evaluation direction before any coding.
```
