# Post Manager Phase 3 現状確認メモ

更新日: 2026-04-02

## 1. 現状確認

- 正本実装先は `E:\codex\workspace\projects\post-manager-remake\app`
- shell 側の主運用ターゲット候補は `E:\codex\workspace\projects\post-manager-remake\desktop-electron`
- 実装計画文書では「次の作業は Phase 3 の API / プロセス基盤固定」となっている
- ただし実コードを見ると、Phase 3 相当の基盤はかなり実装済み

### app/src/api_server.py で確認できたこと

- `/api/run/{step}` による step 実行 API がある
- `/api/process/{process_id}` の取得 / 停止 API がある
- `/api/runtime-status` と `/api/status` がある
- `current_execution` と `running_processes` による runtime 状態管理がある
- Pixiv / Patreon は `subprocess.Popen(...)` で別プロセス管理されている
- WebSocket ログ配信 `/ws/logs` もある

### app/web/script.js で確認できたこと

- `/api/run/{step}` を使う UI 導線がある
- `/api/runtime-status` のポーリングがある
- browser process の `process_id` を保持して停止する UI がある
- recent process / active process の表示更新がある

### desktop-electron/main.js で確認できたこと

- Python backend 起動と待機
- backend log 出力
- single instance lock
- native folder picker
- dropped path 正規化

## 2. 採用判断

- 採用判断: 文書上の「次は Phase 3」は古く、コード実態では Phase 3 の大半は実装済みとみなす
- したがって、次の主対象は「Phase 3 の新規着手」ではなく、Phase 3 完了判定の確認と Phase 4 着手のための不足洗い出しに置く

理由:

- API / runtime / process 管理 / Electron shell 側の主要骨格がすでに存在する
- UI 側も runtime status と process stop の導線を持っている
- ここで再び Phase 3 を主対象として扱うと、実装より文書の遅れに引っ張られる

## 3. 未決事項

- WebSocket ログが UI で主導線として使われているか、それとも poll が主導線か
- browser process の失敗時表示が十分か
- `/api/run/{step}` の sync step と browser step の UI 表現が一貫しているか
- `count / image_count` の責務整理はまだ Phase 3 ではなく fix 候補のまま
- Task の安定 ID 化も未着手の可能性が高い

## 4. 次の最小実装単位

### 対象

- `app/web/`
- 必要なら `app/src/api_server.py`
- 必要なら `desktop-electron/main.js`

### 目的

- Phase 3 を完了扱いできるかを確認し、UI 構造リメイク前に「実行状態の見え方」「停止導線」「失敗表示」の不足だけを埋める

### 実装順

1. UI で runtime status / active process / recent process がどこまで見えているか確認
2. browser process の失敗、停止、完了時の表示差分を確認
3. 不足があれば、表示と安全性だけを最小差分で補う
4. その後に Phase 4 の UI 構造見直しへ入る

### 確認点

- Pixiv / Patreon の browser process 開始中が分かるか
- 停止ボタンの対象と結果が明確か
- 失敗時に次の行動が分かるか
- sync step と browser step で実行中表示が破綻していないか
- Electron shell と通常 Web で folder 入力導線が崩れていないか

### 戻し方

- 今回は表示と runtime まわりの最小差分だけに限定する
- API 契約変更を避け、UI 表示差分は `app/web/` 単位で戻せるようにする

## 5. 今回時点の結論

- `post-manager-remake` は workspace 整理後の次着手候補として最有力
- 文書上の現在地は遅れており、実態は Phase 3 の大半実装済み
- 次の一手は「Phase 3 の残り確認と最小補修」または「Phase 4 UI 構造着手前の確認」に置くのが妥当
