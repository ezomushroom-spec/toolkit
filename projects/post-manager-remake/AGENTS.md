# Project Rules

- 正本実装先は `E:\codex\workspace\projects\post-manager-remake\app` として扱う。
- workspace 外の旧バックアップ候補と `archive/projects-backups/backup_app_before_electron_*` は参照専用の比較資料として扱う。
- 読む先、実装先、文書更新先は同じ project 内で境界を明示して揃える。
- このフォルダ自体は実装計画と判断記録の保管場所であり、project 直下の説明文書は `app/` 正本前提で保つ。
- `desktop-electron/` は workspace 内の主運用ターゲット候補だが、業務ロジックの正本は `app/` に置いたまま維持する。
- `archive/projects-backups/backup_app_before_electron_*` は active 実装先ではない退避コピーであり、参照専用で扱う。
- 実装前に計画が固まったら、要点を `docs/` に同期する。
- keep/fix の判断、運用資産の扱い、戻し方は本体側 docs と矛盾させない。
- 正本ロジックは `app/` に置いたまま維持し、Electron は主運用ターゲットとして扱う。
- 通常ブラウザ互換は保つが、UI / D&D / 導線判断は Electron 優先でよい。
- `browser_profile/`、`data/posts.csv`、`config/*` を壊す変更は、計画上でも危険操作として明示する。
- UI改善は「構造 -> 見た目 -> 安全性」の順を守る。
- Pixiv / Patreon は入力補助まで、最終投稿は人手確認前提を崩さない。

## 実装前フロー

エージェントは実装に入る前に、次の順で進める。

```mermaid
flowchart TD
    A["依頼・資料・現状コードを確認"] --> B["request-translate で論点分解"]
    B --> C{"曖昧さや複数論点が残るか"}
    C -- "はい" --> B
    C -- "いいえ" --> D["正本パスを一本化"]
    D --> E{"正本パスが固定できたか"}
    E -- "いいえ" --> Z1["実装しない<br/>判断待ちを docs に残す"]
    E -- "はい" --> F["実装前監査<br/>keep / fix / 要判断 / doc fix を整理"]
    F --> G["運用資産・データ影響・戻し方を整理"]
    G --> H["implementation-planner で実装順を整理"]
    H --> I{"主要未決事項が残るか"}
    I -- "はい" --> J["判断メモを作成して採用案を固定"]
    J --> K{"実装開始条件を満たしたか"}
    I -- "いいえ" --> K
    K -- "いいえ" --> Z2["実装しない<br/>不足条件を補完する"]
    K -- "はい" --> L{"UI変更を含むか"}
    L -- "はい" --> M["構造 -> 見た目 -> 安全性 の順で UI 方針を固定"]
    L -- "いいえ" --> N["実装へ進む"]
    M --> N
```

## 実装開始条件

- 正本パスが `app/` で固定されている
- backup 群を実装先に混ぜないことが明示されている
- keep / fix / 要判断 / doc fix が整理されている
- `data/posts.csv`、`config/*`、`browser_profile/` の保護方針がある
- 戻し方がある
- 初回実装スコープ外が明示されている
- UI変更がある場合は、構造方針が先に決まっている

## 長期化防止ルール

- 実装前監査は「実装のための判断固定」が目的であり、網羅調査そのものを目的化しない。
- 正本パス、主要未決事項、運用資産保護、戻し方が揃ったら、追加調査より先に判断メモを作る。
- 主要未決事項が 3 個以下になったら、無期限に探索を続けず、採用案を文書化して前進する。
- 「未確認」が残っていても、初回実装の安全性に直結しないものは第2段階候補へ送る。
- 実装停止条件は「正本パス未固定」「運用資産破壊リスク未整理」「戻し方不在」のいずれかが残る場合に限定する。
- それ以外は、最小安全スコープを切って実装準備完了へ進める。

## 実装前文書

- 実装前の採用案は `docs/pre-implementation-decision-memo_20260327.md` を参照する。
- backup 境界の判断は `docs/backup-boundary-decision_20260402.md` を参照する。
- 実装前の handoff は `docs/rebuild-thread-handoff.md` を参照する。

## 変更時の必須セット作業

- 更新する docs: `docs/implementation-plan.md`、必要なら `docs/phase3-current-state_20260402.md`、入口変更時は `START_HERE.md` と `PROJECT_SUMMARY.md`
- 最低限の確認コマンド: `python app/src/api_server.py` の起動確認、必要なら `node --check app/web/script.js`
- 最低限の手動確認: タスク一覧表示、runtime status、停止導線、設定保存や task 編集のロック状態
- 失敗時に先に見るログやファイル: `app/src/api_server.py`、`app/web/script.js`、Electron 併設時は `desktop-electron/runtime/backend.log`
