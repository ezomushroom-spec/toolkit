# Active / Backup / Archive 境界ルール

この文書は、`projects` と `archive` の境界を曖昧にしないための workspace 共通ルールをまとめる。
目的は「いま触る案件」と「退避コピー」と「保管対象」を混同しないこと。

## 1. 用語

### active project

現在の作業対象、または今後も継続して参照・更新する project。
原則として `projects/` に置く。

### backup

復旧や比較のために残す退避コピー。
正本ではない。
active project と同じ扱いをしない。

### archive

今は active ではないが、記録や参照のために残す対象。
旧 project、完了済み案件、退避コピー、判断メモの一部を含む。

## 2. `projects` に置いてよいもの

- active な案件本体
- active 案件に対する `AGENTS.md`
- active 案件に対する `START_HERE.md`
- active 案件の判断メモ、計画、レビュー文書
- active 案件の正本コード、正本設定、正本文書

## 3. `projects` に長く置かない方がよいもの

- 参照専用になった旧 project
- 復旧目的だけの backup コピー
- active project と誤認しやすい退避フォルダ
- 生成物や配布物の保管場所

例:
- `*_backup_*`
- `src_backup_*`
- 使い終わった移行前コピー

## 4. `archive` に移してよいもの

- active ではなくなった旧案件
- active project の退避コピー
- 完了済みで、今は参照中心の調査文書群
- 今後の再利用可能性は低いが、念のため残すもの

## 5. すぐ archive へ移動しない方がよいもの

- 現在の比較対象として頻繁に参照している backup
- 正本候補がまだ一本化できていない案件
- 入口文書や対応表が未整備のままの project
- 移動すると README や手順文書の参照が切れるもの

## 6. 移動前の必須条件

物理移動の前に、少なくとも次を残す。

- 旧パス
- 新パス
- 移動理由
- active / backup / archive の判定理由
- 戻し方
- 参照更新が必要な文書

対応表なしで path を変えない。

## 7. backup 命名フォルダの扱い

`*_backup_*` のような名前は、原則として active 扱いしない。

ただし、次の条件を満たす場合は一時的に `projects/` に残してよい。

- active project と比較しながら使っている
- まだ archive へ移す判断が固まっていない
- `START_HERE.md` や判断メモで「backup であること」が明示されている

上記を満たさない場合は、`archive/` 側へ寄せることを検討する。

## 8. 推奨ディレクトリ方針

現段階の推奨は次の通り。

- `projects/`: active project と active 文書
- `archive/projects-backups/`: backup project
- `archive/projects-retired/`: 停止済みまたは参照専用 project
- `archive/docs/`: 参照専用になった文書

この構造は推奨であり、実際の移動は対応表を作ってから行う。

## 9. 実務判断の優先順

1. active か
2. 正本か
3. 比較用 backup か
4. 参照専用 archive か

迷う場合は、先に文書で判定理由を残し、物理移動は保留する。

## 10. 現在の補足

- `archive/projects-backups/` は運用中
- `archive/projects-retired/` と `archive/docs/` は受け皿を先に作り、今後の段階整理に備える
- 受け皿を作っただけでは即移動しない。対応表と戻し方を残してから移す
