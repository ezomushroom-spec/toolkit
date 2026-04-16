# START HERE

## この project は何か

- `post-manager-remake` を Pixiv tag spec review 前の時点で退避した backup コピーです。
- active project ではなく、比較や復旧のために残している参照用コピーです。

## 最初に読む順番

1. 親案件の `projects/post-manager-remake/START_HERE.md`
2. この backup の `AGENTS.md`
3. 必要な場合だけ `docs/` と `app/`

## 正本

- この folder 自体は正本ではありません
- active 側の参照先: `projects/post-manager-remake`
- この backup の役割: 比較、復旧、差分参照

## 主要入口

- 通常起動: `app/start_cli.bat`, `app/start_webui.bat`, `desktop-electron/start_electron.bat`
- 代替入口: `prepare_electron_migration.bat`, `create_app_backup.bat`
- 主な確認方法: active 側との差分参照

## 触る前に注意するもの

- 壊してはいけない既存挙動: backup としての比較可能性
- 明示依頼なしで触らないもの: `app/data/`, `app/config/`, browser profile 群, backup 群
- backup / profile / generated: この folder 全体が backup 扱い

## 最初の一手

- まず active 側の `projects/post-manager-remake/START_HERE.md` を読んで、こちらが正本でないことを確認する。
- そのうえで、必要な比較対象だけを限定して読む。
