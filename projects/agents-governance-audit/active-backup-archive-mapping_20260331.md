# Active / Backup / Archive Mapping

## 現状確認

`archive/projects-backups/` を作成し、backup 名フォルダ 2 件を `projects/` から移動した。
これにより、active project と backup project の一覧上の混在はひとまず解消した。

## 採用判断

今回は、判定固定だけで止めず、対応表に沿って最小限の物理移動まで適用した。
以後の backup も、原則として active project と同列に長く置かない方針で扱う。

## 旧構成 → 新構成

| 旧パス | 旧分類 | 現在の配置 | 現在の分類 | 理由 |
| --- | --- | --- | --- | --- |
| `projects/app-sample` | active project | `projects/app-sample` | active | 現行案件 |
| `projects/launcher-v2-remake` | active project | `projects/launcher-v2-remake` | active | 現行案件 |
| `projects/mosaic-remake` | active project | `projects/mosaic-remake` | active | 現行案件 |
| `projects/mosaic-remake-winui` | active project | `projects/mosaic-remake-winui` | active | 現行案件 |
| `projects/post-manager-remake` | active project | `projects/post-manager-remake` | active | 現行案件 |
| `projects/skill-prompt-clipboard` | active project | `projects/skill-prompt-clipboard` | active | 現行案件 |
| `projects/agents-governance-audit` | 調査案件 | `projects/agents-governance-audit` | active document project | workspace 運用監査の現行案件 |
| `projects/mosaic-remake_backup_before_winui_20260329_222652` | backup | `archive/projects-backups/mosaic-remake_backup_before_winui_20260329_222652` | backup | active と混同しやすかったため移動 |
| `projects/post-manager-remake_backup_before_pixiv_tag_spec_review_20260329_220258` | backup | `archive/projects-backups/post-manager-remake_backup_before_pixiv_tag_spec_review_20260329_220258` | backup | active と混同しやすかったため移動 |
| `projects/post-manager-remake/backup_app_before_electron_20260328_020023` | backup | `archive/projects-backups/backup_app_before_electron_20260328_020023` | backup | active project 直下で混同しやすかったため移動 |
| `projects/post-manager-remake/backup_app_before_electron_20260328_023322` | backup | `archive/projects-backups/backup_app_before_electron_20260328_023322` | backup | active project 直下で混同しやすかったため移動 |
| `projects/post-manager-remake/backup_app_before_electron_20260330_012354` | backup | `archive/projects-backups/backup_app_before_electron_20260330_012354` | backup | active project 直下で混同しやすかったため移動 |

## 適用時の確認点

- `archive/projects-backups/` を新設した
- `archive/projects-retired/` と `archive/docs/` の受け皿を追加した
- backup 2 件に `START_HERE.md` を追加してから移動した
- 旧→新パスの対応は `archive-move-log_20260331.md` に残した
- `projects/` 一覧から root 直下 backup 名フォルダが外れたことを確認した
- `projects/post-manager-remake/` 直下の `backup_app_before_electron_*` 3 件も archive 側へ寄せる
- archive 側の `backup_app_before_electron_*` 3 件にも参照専用の `START_HERE.md` を追加する

## 未決事項

- `archive/projects-retired/` と `archive/docs/` の受け皿をいつ実際の移動に使い始めるか
- `projects` 内の backup を一括移動するか、案件ごとに段階移動するか
- 今後の backup を作成時点で直接 `archive/projects-backups/` に置く運用へ寄せるか
