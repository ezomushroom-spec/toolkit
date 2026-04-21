---
name: desktop-dnd-path-resolution
description: Resolve drag-and-drop file or folder paths safely across browser and Electron-like desktop shells. Use when a web UI needs local folder D&D, native fallback, Windows absolute paths, or parent-folder resolution for dropped images.
triggers: D&D path, drag and drop path, Electron D&D, フォルダD&D, パス解決, ドロップパス, ネイティブD&D
---

# Purpose

Make folder drag-and-drop practical and safe in local desktop-oriented apps.
Handle the reality that normal browsers and Electron do not expose paths the same way.

# Use this skill when

- a local app accepts folders or local files by drag-and-drop
- the app runs in both browser mode and Electron-like desktop mode
- dropped items may be folders, images, or mixed file entries
- Windows absolute paths matter to backend processing

# Core rule

Treat browser D&D and desktop-shell D&D as different environments.
Do not promise the same reliability in both.

# Environment rules

## Browser mode

- D&D is supplemental unless path extraction is proven reliable
- prefer browse dialogs or explicit folder pickers as the primary fallback
- do not overwrite a valid existing input when D&D path extraction fails
- explain the next action when the browser cannot expose an OS path

## Electron or native shell mode

- D&D can be a primary input path
- prefer native path resolution such as preload bridges or web utils
- keep a native folder picker as the fallback, not the primary recovery for every drop
- if a valid dropped path is resolved, do not open an unnecessary selection dialog

# Resolution order

Use a deterministic order and stop at the first trusted result.

1. URI-like drag payloads that resolve to absolute local paths
2. plain text absolute paths
3. native file path access exposed by the desktop shell
4. file objects resolved through preload or bridge helpers
5. fallback picker or browse dialog

# Folder expectations

If the workflow expects a folder:

- accept a dropped folder directly
- if a dropped item is an image file, decide whether to map it to the parent folder
- reject unsupported paths without clearing the current valid value
- validate that the final resolved path is a directory before accepting it

# UI rules

- show whether D&D is primary or supplemental in the current environment
- on success, update the field immediately and validate it
- on failure, say why and what to do next
- if the folder exists but has zero images, show a warning rather than a hard error
- avoid repeating the same warning on every retry if nothing changed

# Safety rules

- preserve the previous valid path on D&D failure
- never silently coerce relative paths into unclear bases
- use absolute Windows paths when the backend expects filesystem access
- keep backend validation separate from frontend extraction

# Expected output

When using this skill, produce:

1. environment split: browser vs desktop shell
2. chosen path resolution order
3. fallback behavior
4. validation and warning behavior
5. implementation files likely to change

# Good companion skills

- use `ui-remake-safe` when the drop zone also needs UX improvement
- use `pre-implementation-diagnosis` when desktop shell adoption and responsibility split are still undecided
