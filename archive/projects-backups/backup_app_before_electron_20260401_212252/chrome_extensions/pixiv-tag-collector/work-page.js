(function () {
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
        if (!text) {
          continue;
        }
        if (text.length > 80) {
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

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (!message || message.type !== "PIXIV_EXTRACT_WORK_TAGS") {
      return;
    }

    const tags = collectTagTexts();
    sendResponse({
      ok: tags.length > 0,
      pageUrl: location.href,
      title: collectTitle(),
      tags: tags,
      note: tags.length > 0 ? "" : "No tags found on artwork page."
    });
  });
})();
