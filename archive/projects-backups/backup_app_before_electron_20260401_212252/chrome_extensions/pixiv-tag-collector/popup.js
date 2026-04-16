const sourceKeyInput = document.getElementById("sourceKey");
const maxItemsSelect = document.getElementById("maxItems");
const delayMsSelect = document.getElementById("delayMs");
const collectButton = document.getElementById("collectButton");
const statusBox = document.getElementById("status");

function setStatus(text) {
  statusBox.textContent = text;
}

async function refreshRunState() {
  try {
    const response = await chrome.runtime.sendMessage({
      type: "PIXIV_GET_RUN_STATE"
    });
    const state = response?.state;
    if (!state) {
      return;
    }
    if (state.phase === "error" && state.lastError) {
      setStatus(`最後のエラー:\n${state.lastError}`);
      return;
    }
    if (state.phase === "completed") {
      setStatus(
        [
          "前回の実行は完了しています。",
          `成功: ${state.successCount ?? 0}`,
          `失敗: ${state.failedCount ?? 0}`
        ].join("\n")
      );
      return;
    }
    if (state.running) {
      setStatus(
        [
          "取得中...",
          `${state.completed ?? 0} / ${state.total ?? 0}`
        ].join("\n")
      );
    }
  } catch (_error) {
    // popup 初期表示では無視
  }
}

function defaultSourceKeyFromUrl(url) {
  try {
    const parsed = new URL(url);
    const keyword = parsed.searchParams.get("word") || parsed.searchParams.get("tag") || "";
    return keyword ? `pixiv-${keyword}` : "pixiv-list";
  } catch (_error) {
    return "pixiv-list";
  }
}

async function getActiveTab() {
  const tabs = await chrome.tabs.query({
    active: true,
    currentWindow: true
  });
  return tabs[0];
}

function collectArtworkUrlsInPage(maxItems) {
  function normalizeArtworkUrl(href) {
    try {
      const url = new URL(href, location.href);
      const match = url.pathname.match(/\/artworks\/(\d+)/);
      if (!match) {
        return "";
      }
      return `https://www.pixiv.net/artworks/${match[1]}`;
    } catch (_error) {
      return "";
    }
  }

  function isVisibleElement(element) {
    if (!element) {
      return false;
    }
    const rect = element.getBoundingClientRect();
    return rect.width > 24 && rect.height > 24;
  }

  const seen = new Set();
  const urls = [];
  const anchors = document.querySelectorAll('a[href*="/artworks/"]');

  for (const anchor of anchors) {
    const normalized = normalizeArtworkUrl(anchor.href);
    if (!normalized || seen.has(normalized)) {
      continue;
    }
    if (!isVisibleElement(anchor) && !anchor.querySelector("img")) {
      continue;
    }
    seen.add(normalized);
    urls.push(normalized);
    if (urls.length >= maxItems) {
      break;
    }
  }

  return {
    ok: true,
    pageUrl: location.href,
    count: urls.length,
    urls
  };
}

async function collectArtworkUrls(tabId, maxItems) {
  const injected = await chrome.scripting.executeScript({
    target: { tabId },
    func: collectArtworkUrlsInPage,
    args: [maxItems]
  });
  return injected?.[0]?.result;
}

async function startCollection() {
  collectButton.disabled = true;
  setStatus("一覧ページを確認しています...");

  try {
    const activeTab = await getActiveTab();
    if (!activeTab || !activeTab.id || !activeTab.url?.includes("pixiv.net")) {
      throw new Error("Pixiv の一覧ページを開いた状態で実行してください。");
    }

    const maxItems = Number(maxItemsSelect.value) || 10;
    const delayMs = Number(delayMsSelect.value) || 1800;
    setStatus("一覧ページから作品URLを取得しています...");
    const collected = await collectArtworkUrls(activeTab.id, maxItems);
    if (!collected?.ok) {
      throw new Error("一覧ページから作品 URL を取得できませんでした。");
    }
    if (!collected.urls || collected.urls.length === 0) {
      throw new Error("作品 URL が見つかりませんでした。Pixiv の一覧ページで再実行してください。");
    }

    const sourceKey = sourceKeyInput.value.trim() || defaultSourceKeyFromUrl(activeTab.url || "");
    sourceKeyInput.value = sourceKey;

    setStatus(`作品URLを ${collected.urls.length} 件見つけました。\n順に取得を開始します...`);

    const response = await chrome.runtime.sendMessage({
      type: "PIXIV_START_COLLECTION",
      payload: {
        sourceKey,
        listPageUrl: collected.pageUrl || activeTab.url || "",
        maxItems,
        delayMs,
        urls: collected.urls
      }
    });

    if (!response?.ok) {
      throw new Error(response?.error || "収集を開始できませんでした。");
    }

    const result = response.result;
    setStatus(
      [
        "完了しました。",
        `成功: ${result.success_count}`,
        `失敗: ${result.failed_count}`,
        "JSON ダウンロードを確認してください。"
      ].join("\n")
    );
  } catch (error) {
    setStatus(error instanceof Error ? error.message : String(error));
  } finally {
    collectButton.disabled = false;
  }
}

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type !== "PIXIV_TAG_COLLECTOR_STATUS") {
    return;
  }
  const payload = message.payload || {};
  if (payload.phase === "progress") {
    setStatus(
      [
        "取得中...",
        `${payload.completed} / ${payload.total}`,
        payload.currentUrl || "",
        payload.lastStatus ? `last: ${payload.lastStatus}` : ""
      ].filter(Boolean).join("\n")
    );
  }
});

collectButton.addEventListener("click", startCollection);
refreshRunState();
