const DEFAULT_DELAY_MS = 1800;
const MAX_ITEMS = 20;
let runState = null;

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getTimestampSlug() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

function sanitizeFilename(value) {
  return String(value || "pixiv-tag-collection")
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, "-")
    .replace(/\s+/g, "-")
    .slice(0, 80);
}

function setBadge(text, color) {
  chrome.action.setBadgeText({ text: text || "" });
  if (color) {
    chrome.action.setBadgeBackgroundColor({ color });
  }
}

function setRunState(patch) {
  runState = {
    ...(runState || {}),
    ...patch
  };
}

function sendStatus(payload) {
  chrome.runtime.sendMessage({
    type: "PIXIV_TAG_COLLECTOR_STATUS",
    payload
  }).catch(() => {});
}

function waitForTabComplete(tabId) {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      chrome.tabs.onUpdated.removeListener(listener);
      reject(new Error("Timed out waiting for artwork page load."));
    }, 20000);

    function listener(updatedTabId, changeInfo) {
      if (updatedTabId !== tabId) {
        return;
      }
      if (changeInfo.status === "complete") {
        clearTimeout(timeoutId);
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
      }
    }

    chrome.tabs.onUpdated.addListener(listener);
  });
}

async function sendMessageToTab(tabId, message) {
  return chrome.tabs.sendMessage(tabId, message);
}

function extractArtworkDataInPage() {
  function cleanText(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function dedupe(values) {
    const result = [];
    const seen = new Set();
    for (const value of values) {
      if (!value || seen.has(value)) {
        continue;
      }
      seen.add(value);
      result.push(value);
    }
    return result;
  }

  function collectTagTexts() {
    const tags = [];
    const selectors = [
      'a[href*="/tags/"]',
      'a[href*="%E3%82%BF%E3%82%B0"]'
    ];

    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        const text = cleanText(element.textContent).replace(/^#/, "");
        if (!text || text.length > 80) {
          continue;
        }
        tags.push(text);
      }
    }

    return dedupe(tags);
  }

  function collectTitle() {
    const metaTitle = document.querySelector('meta[property="og:title"]')?.content;
    if (cleanText(metaTitle)) {
      return cleanText(metaTitle);
    }
    const heading = document.querySelector("h1");
    return cleanText(heading?.textContent || document.title);
  }

  const tags = collectTagTexts();
  return {
    ok: tags.length > 0,
    pageUrl: location.href,
    title: collectTitle(),
    tags,
    note: tags.length > 0 ? "" : "No tags found on artwork page."
  };
}

async function exportResults(result) {
  const json = JSON.stringify(result, null, 2);
  const url = `data:application/json;charset=utf-8,${encodeURIComponent(json)}`;
  const filename = `pixiv-tag-collection/${sanitizeFilename(result.source_key)}-${getTimestampSlug()}.json`;

  try {
    await chrome.downloads.download({
      url,
      filename,
      saveAs: false
    });
  } catch (error) {
    throw new Error(
      `Failed to start JSON download: ${error instanceof Error ? error.message : String(error)}`
    );
  }
}

async function processArtworkUrl(url, index, total) {
  const tab = await chrome.tabs.create({
    url,
    active: false
  });

  try {
    await waitForTabComplete(tab.id);
    await delay(600);
    const scriptResults = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: extractArtworkDataInPage
    });
    const response = scriptResults?.[0]?.result;

    return {
      index: index + 1,
      status: response?.ok ? "success" : "failed",
      page_url: url,
      work_title: response?.title || "",
      tags: Array.isArray(response?.tags) ? response.tags : [],
      note: response?.note || ""
    };
  } catch (error) {
    return {
      index: index + 1,
      status: "failed",
      page_url: url,
      work_title: "",
      tags: [],
      note: error instanceof Error ? error.message : String(error)
    };
  } finally {
    if (tab.id) {
      await chrome.tabs.remove(tab.id).catch(() => {});
    }
    setBadge(`${index + 1}/${total}`, "#4a6ee0");
  }
}

async function runCollection(request) {
  const urls = Array.isArray(request.urls) ? request.urls.slice(0, MAX_ITEMS) : [];
  const sourceKey = String(request.sourceKey || "pixiv-list").trim() || "pixiv-list";
  const listPageUrl = String(request.listPageUrl || "").trim();
  const maxItems = Math.max(1, Math.min(Number(request.maxItems) || 10, MAX_ITEMS));
  const delayMs = Math.max(1200, Number(request.delayMs) || DEFAULT_DELAY_MS);

  runState = {
    startedAt: new Date().toISOString(),
    total: Math.min(urls.length, maxItems),
    completed: 0,
    running: true,
    phase: "started",
    lastError: "",
    successCount: 0,
    failedCount: 0
  };

  setBadge("RUN", "#4a6ee0");
  sendStatus({
    phase: "started",
    total: runState.total,
    completed: 0
  });

  const items = [];
  const targetUrls = urls.slice(0, maxItems);

  for (let index = 0; index < targetUrls.length; index += 1) {
    const item = await processArtworkUrl(targetUrls[index], index, targetUrls.length);
    items.push(item);
    setRunState({
      completed: index + 1,
      phase: "progress"
    });
    sendStatus({
      phase: "progress",
      total: targetUrls.length,
      completed: runState.completed,
      currentUrl: targetUrls[index],
      lastStatus: item.status
    });
    if (index < targetUrls.length - 1) {
      await delay(delayMs);
    }
  }

  const successCount = items.filter((item) => item.status === "success").length;
  const failedCount = items.filter((item) => item.status !== "success").length;
  const result = {
    version: 1,
    exported_at: new Date().toISOString(),
    source_type: "work",
    source_key: sourceKey,
    list_page_url: listPageUrl,
    requested_count: targetUrls.length,
    success_count: successCount,
    failed_count: failedCount,
    items
  };

  await exportResults(result);

  setRunState({
    running: false,
    phase: "completed",
    successCount,
    failedCount,
    lastError: ""
  });
  setBadge(successCount ? "DONE" : "FAIL", successCount ? "#2f8f4e" : "#b23a48");
  sendStatus({
    phase: "completed",
    total: targetUrls.length,
    completed: targetUrls.length,
    successCount,
    failedCount
  });

  setTimeout(() => {
    if (!runState?.running) {
      setBadge("", "#4a6ee0");
    }
  }, 8000);

  return result;
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message) {
    return;
  }

  if (message.type === "PIXIV_START_COLLECTION") {
    runCollection(message.payload)
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error) => {
        const messageText = error instanceof Error ? error.message : String(error);
        setRunState({
          running: false,
          phase: "error",
          lastError: messageText
        });
        setBadge("ERR", "#b23a48");
        sendResponse({
          ok: false,
          error: messageText
        });
      });
    return true;
  }

  if (message.type === "PIXIV_GET_RUN_STATE") {
    sendResponse({
      ok: true,
      state: runState
    });
  }
});
