# empirical-prompt-tuning result log 保管方針

## 1. 目的

`empirical-prompt-tuning` の result log を、どこへ、どの粒度で、何を正本として残すかを固定する。

この文書は、trial ごとの根拠を失わず、後から横断しやすい記録方式を保つための正本である。

## 2. 結論

result log は当面、`projects/workspace-operations/docs/` に trial ごとの個別文書で残す。

月次集計や一覧表を追加する場合でも、それは補助集計とし、正本は個別 result log のまま維持する。

## 3. この方式を採る理由

### A. 判定根拠を落としにくい

trial ごとに scenario、checklist、failed critical items、ambiguity、最小改訂テーマが違うため、月次集計だけに寄せると「なぜその判定だったか」が抜けやすい。

### B. 2nd iteration と guidance section trial に相性がよい

同じ target の初回 trial、2nd iteration、`AGENTS.md` section trial は粒度が揃わない。個別文書を正本にすると、対象ごとの差分や補強理由を追いやすい。

### C. 今の運用規模に対して十分低コスト

現時点では対象数は増えたが、まだ daily logging を強制するほどの量ではない。先に月次集計を正本にすると、集計整備の負担が先に増える。

## 4. 正本と補助の役割分担

### 正本

- `empirical-prompt-tuning-trial-result_*.md`
- 必要に応じて `empirical-prompt-tuning-first-trial_*.md`
- 必要に応じて `empirical-prompt-tuning-second-trial_*.md`

### 補助

- `PROJECT_SUMMARY.md` の現在地
- `empirical-prompt-tuning-operating-rule_20260422.md`
- 将来追加する月次集計や index 文書

補助文書だけを読んでも大枠判断はできるようにしてよいが、pass/fail や改訂理由の最終根拠は個別 result log を参照する。

## 5. 最低限残す項目

個別 result log には最低限次を残す。

- target
- trial の種類
- scenario の要点
- success / failure
- ambiguity
- discretion 補完が出た箇所
- failed `[critical]` item の有無
- 今回の改訂テーマ

fresh executor を使えた回では、可能な範囲で次も残す。

- tool usage の要点
- duration の概算
- retry の有無

これらは厳密な計測系ではなく、比較判断に使える粒度でよい。

## 6. `static review only` の扱い

fresh executor 不可の回は、個別 result log を作らずに済ませない。

少なくとも次のどちらかを残す。

1. `first-trial` 文書に `static review only` と `empirical evaluation pending` を明記する
2. 専用の result log を作り、その回が未実施評価であることを明記する

自己再読だけの結果を、通常の empirical result と混在させない。

## 7. 月次集計を作る条件

次のどれかが発生したら、補助として月次集計か index を追加してよい。

- result log が 30 件前後を超えて一覧性が落ちた
- 同一 target の再評価が増え、個別文書だけでは追跡しづらくなった
- 月次レビューや定例報告へ転用したくなった

ただし、その場合でも個別 result log を捨てない。

## 8. いまの運用判断

現時点では次の形を既定とする。

1. 個別 result log を正本とする
2. `PROJECT_SUMMARY.md` と `operating rule` で現在地だけ短く示す
3. 月次集計は必要になるまで作らない
