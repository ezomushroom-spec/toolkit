const { contextBridge, clipboard } = require("electron");

contextBridge.exposeInMainWorld("intentLabelDesktop", {
  writeClipboardText: async (text) => {
    clipboard.writeText(String(text ?? ""));
  },
});
