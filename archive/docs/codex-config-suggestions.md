# `.codex/config.toml` 追記候補

今回は既存運用を壊さないため、`E:\自作アプリ集\workspace\.codex\config.toml` は未変更。
必要になったときに検討できる候補だけをここへ残す。

## 候補 1: `tech-diagnostician` を role 登録する

目的:
- 実装前診断を role 名で呼びやすくする
- 新しく追加した `tech-diagnostician.toml` を config からも参照可能にする

候補差分:

```toml
[roles]
tech-diagnostician = ".codex/agents/tech-diagnostician.toml"
tech_diagnostician = ".codex/agents/tech-diagnostician.toml"

[agents.tech_diagnostician]
description = "Compare realistic implementation approaches before coding and recommend one in plain Japanese."
config_file = ".codex/agents/tech-diagnostician.toml"
```

入れる判断基準:
- 実装前診断をこの workspace で継続的に使う
- role 呼び出し名を既存 agent 群とそろえたい

## 候補 2: 品質レビュー専用 agent を後で追加する

目的:
- 実装後に「見た目が動く」以外の品質観点を点検する役割を分離する

現時点では未追加にした理由:
- まずは `AGENTS.md` と `docs/quality-gates.md` で main agent の完了条件を安定させる方が効果が大きい
- 役割を増やしすぎると運用が重くなる

必要になったら、次の責務で別 agent または skill に切り出す。

- 既存挙動保全の確認
- 失敗系チェックの抜け漏れ確認
- 完了報告の形式監査
- メモリ / GPU / 長時間処理の観点確認
