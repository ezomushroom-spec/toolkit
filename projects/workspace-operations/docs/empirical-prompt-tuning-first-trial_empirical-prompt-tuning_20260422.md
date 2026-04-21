# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `empirical-prompt-tuning`
- Canonical file: `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`
- Priority: `Opportunistic`

## 2. この対象を選ぶ理由

- protocol skill 自身なので、artifact type 拡張と static-only 運用の線引きがぶれると全体記録に影響する
- 既存 skill 群の trial を一通り終えた今、次に広げる境界を点検しやすい

## 3. Iteration 0

- description と body の整合は取れている
- fresh executor 不可時に empirical validation 済み扱いへしない方針も明示されている
- 追加で見たい曖昧さは「guidance section のような非-skill artifact へ自然に広げられるか」と「static review only の記録が十分明確か」

## 4. trial fixture

### Fixture A: guidance-artifact

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\empirical-prompt-tuning-guidance-artifact`
- 想定: skill ではない workspace guidance section を protocol 対象に含めたい

### Fixture B: static-only

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\empirical-prompt-tuning-static-only`
- 想定: fresh executor を使えない回で、どこまで実施済み扱いにするかを整理したい

## 5. 固定 scenario

### Scenario A: guidance section expansion

- Case type: `median`
- User-like request:

```text
新しく root `AGENTS.md` の guidance section を empirical-prompt-tuning で評価対象に含めたいです。どう扱うべきか、trial の進め方を整理してください。
```

Checklist:

- [critical] artifact type の拡張を protocol の範囲内で扱う
- canonical file と scenario/checklist 固定の流れを保つ
- skill の全面テンプレ化へ流れない
- guidance section にも empirical review の適用条件を出せる

### Scenario B: static review only

- Case type: `edge`
- User-like request:

```text
この skill を empirical-prompt-tuning で見直したいです。ただ、今回は fresh executor を使えません。どこまでを実施済みとして扱うべきか、記録の仕方も含めて整理してください。
```

Checklist:

- [critical] self-rereading を empirical evaluation と呼ばない
- static review only で止める判断が出る
- pending / remaining risk を記録する方向が出る
- 「実施済み」と「未実施」を混同しない

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\empirical-prompt-tuning-guidance-artifact\brief.md`.
Produce an evaluation direction before any coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `empirical-prompt-tuning` at `E:\codex\workspace\.agents\skills\empirical-prompt-tuning\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\empirical-prompt-tuning-static-only\brief.md`.
Produce an evaluation direction before any coding.
```
