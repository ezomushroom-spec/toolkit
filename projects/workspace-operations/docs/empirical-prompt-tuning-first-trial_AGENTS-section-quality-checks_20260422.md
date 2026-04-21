# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target artifact: root `AGENTS.md` section
- Canonical file: `E:\codex\workspace\AGENTS.md`
- Target section: `## 4. 品質確認`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 完了判定の甘さは workspace 全体の品質を崩しやすい
- 「動いたように見えるだけでは完了にしない」と「高コスト操作は優先確認する」が自然に出るかを見たい

## 3. Iteration 0

- section の主旨は明確で、正常系偏重を避けること、高コスト操作と失敗系を含めること、実行可能な確認を重視することが書かれている
- 追加で見たい曖昧さは「テストがある」だけで安心しない読みと、「動いたので完了」に流れない読みが安定するか

## 4. trial fixture

### Fixture A: high-risk-action

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-quality-high-risk-action`
- 想定: 一括削除や上書き export のような高コスト操作を含む変更

### Fixture B: shallow-test-report

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-quality-shallow-test-report`
- 想定: テストは書いたが、実行可否や失敗系の確認が浅い

## 5. 固定 scenario

### Scenario A: high-risk action

- Case type: `median`
- User-like request:

```text
この変更はだいたい動いています。完了扱いにしてよいか、確認観点を見てください。
```

Checklist:

- [critical] 動いたように見えるだけでは完了扱いにしない
- 高コスト操作では確認、対象明示、二重実行防止、失敗時表示を優先する
- 正常系だけでなく失敗系を含める

### Scenario B: shallow test report

- Case type: `edge`
- User-like request:

```text
テストは書いてあります。これで完了扱いにしてよいか確認してください。
```

Checklist:

- [critical] テストを書いたことだけで完了扱いにしない
- 実行可能性と変更確認への有効性に触れる
- 空入力、不正設定、存在しないパス、キャンセル後状態などを含める

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 4. 品質確認` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-quality-high-risk-action\brief.md`.
Produce an evaluation direction before any coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Treat the target artifact as the section `## 4. 品質確認` in `E:\codex\workspace\AGENTS.md`.
Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\agents-section-quality-shallow-test-report\brief.md`.
Produce an evaluation direction before any coding.
```
