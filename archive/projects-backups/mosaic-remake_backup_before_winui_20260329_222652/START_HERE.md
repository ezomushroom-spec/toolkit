# START HERE

## この project は何か

- `mosaic-remake` を WinUI 移行前の時点で退避した backup コピーです。
- active project ではなく、比較や復旧のために残している参照用コピーです。

## 最初に読む順番

1. 親案件の `projects/mosaic-remake/START_HERE.md`
2. この backup の `再構築準備メモ.md`
3. 必要な場合だけ `main.py` と `ui/`

## 正本

- この folder 自体は正本ではありません
- active 側の参照先: `projects/mosaic-remake`
- この backup の役割: 比較、復旧、差分参照

## 主要入口

- 通常起動: `通常起動.bat`
- 代替入口: `main.py`
- 主な確認方法: active 側との差分参照

## 触る前に注意するもの

- 壊してはいけない既存挙動: backup としての比較可能性
- 明示依頼なしで触らないもの: `settings.json`, `*.onnx`, `*.pt`, コード全体
- backup / profile / generated: この folder 全体が backup 扱い

## 最初の一手

- まず active 側の `projects/mosaic-remake/START_HERE.md` を読んで、こちらが正本でないことを確認する。
- そのうえで、必要な比較箇所だけを限定して読む。
