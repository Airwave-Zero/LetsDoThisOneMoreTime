

chrome.runtime.onInstalled.addListener(({reason}) => {
    if (reason === 'install') {
      chrome.tabs.create({
        url: "index.html"
      });
    }
  });

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "EXTRACTED_LINKS") {
        console.log("Extracted links from", sender.tab?.url, message.links);

        // Optionally store links in Chrome storage
        chrome.storage.local.set({ [sender.tab?.url || 'unknown']: message.links });
    }
});
