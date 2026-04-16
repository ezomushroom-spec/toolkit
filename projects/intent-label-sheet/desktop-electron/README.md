# desktop-electron

`intent-label-sheet` を独立小窓として開く Electron shell です。

## 役割

- project 直下の `dist/index.html` を読み込む
- 右下寄せの小窓として開く
- preload 経由で clipboard 書き込みを補助する

## 起動

project 直下の `start.bat` から起動するのを基本とする。

直接 shell を確認したい場合:

```powershell
cd desktop-electron
npm install
npm start
```
