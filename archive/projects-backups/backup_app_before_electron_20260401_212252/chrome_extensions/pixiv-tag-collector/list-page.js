(function () {
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

  function collectArtworkUrls(maxItems) {
    const seen = new Set();
    const ordered = [];

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
      ordered.push(normalized);
      if (ordered.length >= maxItems) {
        break;
      }
    }

    return ordered;
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (!message || message.type !== "PIXIV_COLLECT_ARTWORK_URLS") {
      return;
    }

    const maxItems = Math.max(1, Math.min(Number(message.maxItems) || 10, 20));
    const urls = collectArtworkUrls(maxItems);
    sendResponse({
      ok: true,
      pageUrl: location.href,
      count: urls.length,
      urls: urls
    });
  });
})();
