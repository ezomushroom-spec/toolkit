# Archive Move Log

## 現状確認

- `active-backup-archive-mapping_20260331.md` で backup 判定した 5 件を対象にする
- root `projects/` 直下の backup 2 件と、`projects/post-manager-remake/` 直下の backup 3 件はいずれも active project と混同しやすい

## 採用判断

- root `projects/` 直下の backup 2 件は最低限の `START_HERE.md` を追加してから `archive/projects-backups/` へ移動する
- `projects/post-manager-remake/` 直下の backup 3 件は、active 側文書の参照更新と対応表更新を先に行ってから `archive/projects-backups/` へ移動する
- active 側 project は移動しない

## 移動対象

| 旧パス | 新パス | 理由 | 戻し方 |
| --- | --- | --- | --- |
| `projects/mosaic-remake_backup_before_winui_20260329_222652` | `archive/projects-backups/mosaic-remake_backup_before_winui_20260329_222652` | active と混同しやすい backup のため | 対応表を確認して `projects/` 側へ戻す |
| `projects/post-manager-remake_backup_before_pixiv_tag_spec_review_20260329_220258` | `archive/projects-backups/post-manager-remake_backup_before_pixiv_tag_spec_review_20260329_220258` | active と混同しやすい backup のため | 対応表を確認して `projects/` 側へ戻す |
| `projects/post-manager-remake/backup_app_before_electron_20260328_020023` | `archive/projects-backups/backup_app_before_electron_20260328_020023` | active project 直下の backup で混同しやすいため | 対応表を確認して `projects/post-manager-remake/` 側へ戻す |
| `projects/post-manager-remake/backup_app_before_electron_20260328_023322` | `archive/projects-backups/backup_app_before_electron_20260328_023322` | active project 直下の backup で混同しやすいため | 対応表を確認して `projects/post-manager-remake/` 側へ戻す |
| `projects/post-manager-remake/backup_app_before_electron_20260330_012354` | `archive/projects-backups/backup_app_before_electron_20260330_012354` | active project 直下の backup で混同しやすいため | 対応表を確認して `projects/post-manager-remake/` 側へ戻す |

## 未決事項

- 今後の backup は作成時点で `archive/projects-backups/` に置くか
- `archive/projects-retired/` をいつ作るか
