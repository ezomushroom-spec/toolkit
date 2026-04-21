# empirical-prompt-tuning 運用ルール

## 1. 目的

workspace で `empirical-prompt-tuning` を回すときの最小運用ルールを 1 枚に固定する。

この文書は、どの対象をいつ評価するか、fresh executor が使えない回をどう記録するか、2nd iteration をいつ打つかを短く判断するための正本である。

## 2. 対象の種類

`empirical-prompt-tuning` の対象は次の 4 種とする。

1. workspace skill
2. slash command
3. task prompt
4. workspace guidance section

workspace guidance section を扱う場合の canonical file は原則として root [AGENTS.md](/E:/codex/workspace/AGENTS.md:1) とし、対象 section を明記する。

## 3. 優先順位

優先順位は次の 4 区分で付ける。

- `Critical`
- `Important`
- `Opportunistic`
- `Exempt`

判断基準は次の通り。

- `Critical`: 使用頻度が高い、失敗時影響が大きい、workspace ルールや安全性に直結する
- `Important`: 重要だが常時は使わない、または project 文脈が必要
- `Opportunistic`: 実案件や改訂タイミングでだけ評価すればよい
- `Exempt`: 一回限り、または評価コストが割に合わない

## 4. いつ回すか

次のいずれかで evaluation を開始する。

- 新しい workspace skill を追加したとき
- 既存 skill や guidance section を大きく改訂したとき
- 同じ対象で期待外れや誤用が 2 回以上出たとき
- 入口文書と本文が噛み合わなくなったとき
- 初回 trial で触れていない edge case が実案件で表面化したとき

## 5. 基本フロー

1. target, canonical file, classification を決める
2. Iteration 0 を行う
3. scenario を 2〜3 個固定する
4. checklist を 3〜7 項目で固定する
5. fresh executor を使える回なら empirical evaluation を行う
6. 1 iteration = 1 theme で最小改訂する
7. result log と current state を更新する

## 6. Iteration 0 の必須項目

- description と body の整合確認
- stale reference や obsolete name の除去
- trigger や適用条件の曖昧さ確認
- success / failure の見え方確認
- executor が補完している裁量の明示

## 7. Scenario と Checklist

標準形は次の通り。

- 1 median case
- 1 edge case
- 必要なら edge case をもう 1 件

Checklist は次を守る。

- 少なくとも 1 つは `[critical]`
- 実行後に pass/fail 判定できる文にする
- 後から判定基準を動かさない

## 8. fresh executor が使える回

empirical evaluation 済みと呼べるのは次を満たす回だけ。

- ユーザーの明示的な委任許可がある
- fresh executor を毎回分けられる
- expected answer や診断結果を渡していない
- result log に success / failure / ambiguity / failed critical items を残せる

## 9. fresh executor が使えない回

次までは実施済み扱いにしてよい。

- target と重要度の整理
- Iteration 0
- scenario と checklist の作成
- remaining risk の整理

次は実施済み扱いにしない。

- empirical evaluation
- success / failure の確定
- tool usage や duration の実測
- hardened / validated の宣言

記録上は次の文言を使う。

- `static review only`
- `empirical evaluation pending`

`self-rereading` を empirical evaluation と呼ばない。

## 10. 2nd iteration を打つ条件

初回成功でも次のどれかがあれば 2nd iteration 候補にする。

- 裁量差が残った
- edge case がまだ弱い
- 失敗時コストが高い
- rule の境界が実運用でぶれやすい

2nd iteration では 1 skill につき 1 theme だけを扱う。

## 11. Guidance section の扱い

root `AGENTS.md` の section を対象にするときは次を守る。

- target section を明記する
- workspace-wide rule と project-specific rule を混同しない
- section の主旨を変えず、誤読しやすい 1 点だけを補う
- guidance section でも scenario / checklist / result log の形は skill と揃える

## 12. 記録先

result log の正本は `projects/workspace-operations/docs/` に trial ごとの個別文書で残す。

保管方針の正本は `empirical-prompt-tuning-result-log-storage-policy_20260422.md` とする。

月次集計や一覧表を追加しても、それは補助集計とし、pass/fail や改訂理由の正本は個別 result log に置く。

最低限残す文書は次。

- current state
- adoption / rollout
- open questions
- first trial or second trial prep
- result log

## 13. 今の既定

- `Critical` と `Important` の初回横展開は完了
- `Opportunistic` の初回横展開は完了
- 2nd iteration 候補 3 件も完了
- `AGENTS.md` では少なくとも `ユーザー確認と委任`、`実装前の確認`、`品質確認`、`文書と配置`、`変更の出口` を trial 済み

## 14. 次の自然な対象

次に進めるときは次の順を基本にする。

1. 実運用で edge case が出た既存 target の 2nd iteration
2. 新規追加された workspace skill
3. `AGENTS.md` で trigger が立った section の再開
4. slash command や task prompt の canonicalization

`AGENTS.md` の section trial は、現時点では `empirical-prompt-tuning-agents-trial-pause-decision_20260422.md` に基づき一区切り済みとする。
