# empirical-prompt-tuning 未決事項

## 1. 今回未決のこと

- fresh executor を使う empirical evaluation を、どのタイミングで常用に入れるか
- `slash command` 実体が今後追加された場合に、どの置き場を canonical にするか
- home 側 skill や plugin skill まで同じ優先度分類へ広げるか

## 2. 実装前に詰めること

- empirical evaluation を実施する回では、ユーザーの明示的な委任許可を取ること
- scenario ごとの duration や tool count をどこまで厳密に記録するか
- `static review only` を専用 result に分けるか、trial prep 側へ定型化するか

## 3. 後段でもよいこと

- `Opportunistic` 群への横展開
- root `AGENTS.md` 未 trial section の scenario 化
- home 側 skill の再分類
- snapshot zip の定期整理
- 初回成功 skill の 2nd iteration 実施タイミング

## 4. 再評価トリガー

- 新しい workspace skill を追加したとき
- 同じ skill で期待外れや誤用が 2 回以上出たとき
- 入口文書から辿った skill が実際の本文と噛み合わなくなったとき
- 初回 trial では触れていない edge case が実案件で表面化したとき
