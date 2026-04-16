const { contextBridge, ipcRenderer, webUtils } = require("electron");

contextBridge.exposeInMainWorld("postManagerDesktop", {
  platform: process.platform,
  pickFolder: () => ipcRenderer.invoke("dialog:pick-folder"),
  normalizeDroppedPath: (rawPath) => ipcRenderer.invoke("path:normalize-dropped", rawPath),
  getPathForFile: (file) => {
    try {
      return webUtils.getPathForFile(file) || "";
    } catch (error) {
      return "";
    }
  }
});
