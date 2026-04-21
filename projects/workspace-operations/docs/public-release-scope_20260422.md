# public release scope

## 1. 目的

この workspace を公開するときに、どこまでを公開対象にし、どこを private 扱いで除外するかを固定する。

## 2. 現時点の基本方針

公開対象は、workspace 共通運用と `empirical-prompt-tuning` 導入に直接必要な範囲に限定する。

初回の公開では、`projects/` 配下は原則 whitelist 方式で扱う。

## 3. 公開対象

### workspace 共通

- `AGENTS.md`
- `.agents/skills/`
- `docs/skill-inventory.md`
- `docs/subagent-prompts.md`

### project 配下で公開するもの

- `projects/workspace-operations/`

`workspace-operations` は、workspace 自体の運用改善、trial 記録、導入判断、公開判断の記録置き場として扱う。

## 4. 初回公開で除外するもの

次の `projects/` は、現時点では private project 候補または公開判断未了として除外する。

- `projects/adult-ai-monetization-loop/`
- `projects/agents-governance-audit/`
- `projects/app-sample/`
- `projects/attendance-manager/`
- `projects/civitai-downloader-fix/`
- `projects/generated-image-finishing-tool/`
- `projects/image-prompt-desktop/`
- `projects/image-prompt-studio/`
- `projects/intent-label-sheet/`
- `projects/launcher-v2-remake/`
- `projects/mosaic-remake/`
- `projects/mosaic-remake-tk/`
- `projects/mosaic-remake-winui/`
- `projects/narrative-thumbnail-studio/`
- `projects/post-manager-remake/`
- `projects/postflow/`
- `projects/sd-prompt-helper/`
- `projects/skill-prompt-clipboard/`

## 5. この方針を採る理由

### A. private 作品群の混入を避けやすい

blacklist 方式ではなく whitelist 方式にすることで、公開判断が済んでいない project を誤って含めにくい。

### B. 今回の PR と整合する

現在の `empirical-prompt-tuning` PR は、`projects/` 配下では実質的に `workspace-operations` だけを対象にしている。

### C. 後から広げやすい

将来公開してよい project が出た場合は、この文書に追記しながら段階的に広げられる。

## 6. 今の判断

「完成版として公開する」対象は、現時点では次の意味に限定する。

- workspace 共通運用
- `empirical-prompt-tuning` の skill / guidance / rollout record
- それを支える `workspace-operations`

個別作品 project の公開は、この文書で明示的に追加許可したものだけにする。
