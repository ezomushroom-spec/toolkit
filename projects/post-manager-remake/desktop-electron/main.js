const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const { spawn, execFileSync } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const PROJECT_ROOT = path.resolve(__dirname, "..");
const APP_ROOT = path.join(PROJECT_ROOT, "app");
const SERVER_URL = "http://127.0.0.1:8000/";
const SERVER_ENTRY = path.join(APP_ROOT, "src", "api_server_desktop.py");
const RUNTIME_DIR = path.join(__dirname, "runtime");
const BACKEND_LOG = path.join(RUNTIME_DIR, "backend.log");

let mainWindow = null;
let backendProcess = null;
let isQuitting = false;
const singleInstanceLock = app.requestSingleInstanceLock();
app.commandLine.appendSwitch("disable-http-cache");

if (!singleInstanceLock) {
  app.quit();
}

function ensureRuntimeDir() {
  fs.mkdirSync(RUNTIME_DIR, { recursive: true });
}

function appendBackendLog(chunk) {
  ensureRuntimeDir();
  fs.appendFileSync(BACKEND_LOG, chunk);
}

function candidatePythonCommands() {
  return [
    { command: path.join(APP_ROOT, ".venv", "Scripts", "python.exe"), args: [] },
    { command: path.join(APP_ROOT, "venv", "Scripts", "python.exe"), args: [] },
    { command: "python", args: [] },
    { command: "py", args: ["-3.10"] },
    { command: "py", args: ["-3"] }
  ];
}

function commandExists(candidate) {
  try {
    if (path.isAbsolute(candidate.command) && !fs.existsSync(candidate.command)) {
      return false;
    }
    execFileSync(candidate.command, [...candidate.args, "--version"], {
      stdio: "ignore",
      cwd: APP_ROOT
    });
    return true;
  } catch (error) {
    return false;
  }
}

function resolvePythonCommand() {
  const candidate = candidatePythonCommands().find(commandExists);
  if (!candidate) {
    throw new Error("Python interpreter was not found for Post Manager.");
  }
  return candidate;
}

function waitForServer(url, timeoutMs = 30000, intervalMs = 500) {
  const start = Date.now();

  return new Promise((resolve, reject) => {
    const tryConnect = () => {
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode < 500) {
          resolve();
          return;
        }
        retry(new Error(`Server responded with ${res.statusCode}`));
      });

      req.on("error", retry);
      req.setTimeout(2000, () => {
        req.destroy(new Error("Server connection timed out"));
      });
    };

    const retry = (error) => {
      if (Date.now() - start >= timeoutMs) {
        reject(error);
        return;
      }
      setTimeout(tryConnect, intervalMs);
    };

    tryConnect();
  });
}

async function ensureBackendServer() {
  try {
    await waitForServer(SERVER_URL, 2000, 300);
    return;
  } catch (error) {
    // Start a new backend below.
  }

  const python = resolvePythonCommand();
  ensureRuntimeDir();
  appendBackendLog(`\n=== backend start ${new Date().toISOString()} ===\n`);
  backendProcess = spawn(
    python.command,
    [...python.args, SERVER_ENTRY],
    {
      cwd: APP_ROOT,
      windowsHide: false,
      stdio: ["ignore", "pipe", "pipe"],
      env: {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
        PYTHONUTF8: "1"
      }
    }
  );

  if (backendProcess.stdout) {
    backendProcess.stdout.on("data", (chunk) => {
      appendBackendLog(chunk);
    });
  }

  if (backendProcess.stderr) {
    backendProcess.stderr.on("data", (chunk) => {
      appendBackendLog(chunk);
    });
  }

  backendProcess.on("exit", (code) => {
    backendProcess = null;
    if (!isQuitting && code !== 0 && mainWindow) {
      dialog.showErrorBox(
        "Post Manager backend stopped",
        `Python server exited unexpectedly with code ${code}.\n\nSee: ${BACKEND_LOG}`
      );
    }
  });

  await waitForServer(SERVER_URL, 30000, 500);
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1480,
    height: 980,
    minWidth: 1100,
    minHeight: 760,
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

ipcMain.handle("dialog:pick-folder", async () => {
  const targetWindow = mainWindow || BrowserWindow.getFocusedWindow();
  const result = await dialog.showOpenDialog(targetWindow, {
    title: "Post Manager: フォルダを選択",
    properties: ["openDirectory"]
  });

  if (result.canceled || !result.filePaths.length) {
    return "";
  }

  return result.filePaths[0];
});

ipcMain.handle("path:normalize-dropped", async (_event, rawPath) => {
  if (typeof rawPath !== "string" || !rawPath.trim()) {
    return "";
  }

  const normalized = path.normalize(rawPath.trim());
  if (!path.isAbsolute(normalized) || !fs.existsSync(normalized)) {
    return "";
  }

  try {
    const stats = fs.statSync(normalized);
    if (stats.isDirectory()) {
      return normalized;
    }
    if (stats.isFile()) {
      return path.dirname(normalized);
    }
  } catch (error) {
    return "";
  }

  return "";
});

async function boot() {
  createMainWindow();

  try {
    await ensureBackendServer();
    try {
      await mainWindow.webContents.session.clearCache();
    } catch (error) {
      // ignore cache clear failures and continue boot
    }
    await mainWindow.loadURL(SERVER_URL);
  } catch (error) {
    dialog.showErrorBox(
      "Post Manager failed to start",
      `${error.message}\n\nUse app/start_webui.bat to verify the Python backend.\nBackend log: ${BACKEND_LOG}`
    );
    app.quit();
  }
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
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  isQuitting = true;
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    boot();
  }
});
