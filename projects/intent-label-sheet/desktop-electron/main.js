const { app, BrowserWindow, dialog, screen, shell } = require("electron");
const fs = require("fs");
const path = require("path");

const PROJECT_ROOT = path.resolve(__dirname, "..");
const DIST_INDEX = path.join(PROJECT_ROOT, "dist", "index.html");
const WINDOW_WIDTH = 480;
const WINDOW_HEIGHT = 820;

let mainWindow = null;

if (!app.requestSingleInstanceLock()) {
  app.quit();
}

function resolveWindowPosition() {
  const { workArea } = screen.getPrimaryDisplay();
  return {
    x: Math.max(workArea.x + 16, workArea.x + workArea.width - WINDOW_WIDTH - 24),
    y: Math.max(workArea.y + 16, workArea.y + workArea.height - WINDOW_HEIGHT - 24),
  };
}

function createWindow() {
  const position = resolveWindowPosition();

  mainWindow = new BrowserWindow({
    width: WINDOW_WIDTH,
    height: WINDOW_HEIGHT,
    minWidth: 420,
    minHeight: 620,
    x: position.x,
    y: position.y,
    autoHideMenuBar: true,
    backgroundColor: "#0f1415",
    show: false,
    title: "Intent Label Sheet",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

async function boot() {
  if (!fs.existsSync(DIST_INDEX)) {
    dialog.showErrorBox(
      "Intent Label Sheet failed to start",
      "dist/index.html was not found.\nRun the web build first or use start.bat from the project root."
    );
    app.quit();
    return;
  }

  createWindow();
  await mainWindow.loadFile(DIST_INDEX);
}

app.whenReady().then(boot);

app.on("second-instance", () => {
  if (!mainWindow) {
    return;
  }

  if (mainWindow.isMinimized()) {
    mainWindow.restore();
  }

  mainWindow.focus();
});

app.on("window-all-closed", () => {
  app.quit();
});
