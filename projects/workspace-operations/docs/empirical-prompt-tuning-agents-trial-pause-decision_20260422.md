# empirical-prompt-tuning AGENTS trial 一区切り判断

## 1. 目的

root `AGENTS.md` の section trial を、この時点でどこまで標準運用に含めるかを固定する。

## 2. 結論

`AGENTS.md` の section trial は、現時点ではここで一旦一区切りとする。

今後は `AGENTS.md` の全 section を順番に消化することを既定にせず、次の trigger が出たときだけ再開する。

## 3. 一区切りとする理由

### A. 主要な高影響 section はすでに見ている

少なくとも次の高影響 section は trial 済みである。

- `実装前の確認`
- `品質確認`
- `文書と配置`
- `ユーザー確認と委任`
- `変更の出口`

日常運用で誤読コストが大きい部分は、ひとまず一巡したとみなしてよい。

### B. ここから先は費用対効果が落ちやすい

残りの section を機械的に全部 scenario 化しても、今すぐの改善益より記録コストが先に増えやすい。

### C. 次に価値が高いのは guidance の網羅より実運用再評価

今後は未 trial section の消化より、実案件で edge case が出た既存 target の再評価や、新規 target の初回 trial のほうが価値が高い。

## 4. 再開トリガー

次のどれかが起きたら `AGENTS.md` section trial を再開してよい。

- `AGENTS.md` の特定 section を大きく改訂した
- 同じ guidance section で誤読や期待外れが 2 回以上出た
- project 文書との境界が曖昧で、workspace rule の読み分けが崩れた
- 新しい workspace-wide rule を root `AGENTS.md` に追加した

## 5. 現時点の運用

現時点では次を既定とする。

1. `AGENTS.md` section trial は一区切り済みと扱う
2. 未 trial section を backlog として保持する
3. 再開は trigger ベースで判断する
4. 新しい empirical 評価の主軸は skill / guidance の再評価と新規 target に置く
