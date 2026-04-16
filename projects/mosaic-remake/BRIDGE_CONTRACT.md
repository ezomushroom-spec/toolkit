# Mosaic Remake Bridge Contract

WinUI から Python core を呼ぶための暫定 CLI 契約です。

## 目的

- WinUI 側から内部モジュールへ直接依存しない
- 先に `process` ベースで接続し、後からローカル API へ移しても崩れにくくする

## コマンド

### health

```powershell
python bridge_cli.py health
```

返却:

- `model_path`
- `model_loaded`
- `class_names`
- `class_settings`

### preview

```powershell
python bridge_cli.py preview --image-path <path> --output-preview-path <path>
```

返却:

- `preview_path`
- `candidate_count`
- `candidates`

備考:

- 画像本体は JSON 返却せず、指定パスへ保存する
- WinUI 側は保存されたプレビュー画像を読む

### batch

```powershell
python bridge_cli.py batch --input-dir <path> --output-dir <path>
```

返却:

- `summary`
- `finished`
- `progress_count`

## request JSON

`--request` には JSON ファイルパスを渡せます。

例:

```json
{
  "model_path": "E:/.../ntd11_anime_nsfw_segm_v5-variant1.pt",
  "params": {
    "mask_type": "pixel",
    "shape_type": "mask",
    "imgsz": 960,
    "strength": 15.0,
    "margin": 18.0,
    "show_boxes": false
  },
  "class_settings": {
    "pussy": { "enabled": true, "conf": 0.6 }
  }
}
```

## 今後

- WinUI 側ではまず `health` と `preview` から接続する
- `batch` は次段で進捗ストリーム対応を検討する
- 将来的にローカル API 化しても、この入出力形状を大きく変えない
