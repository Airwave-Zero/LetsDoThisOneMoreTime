(() => {
    const links = Array.from(document.querySelectorAll('a')).map(anchor => anchor.href);

    // Send the links to the background script
    chrome.runtime.sendMessage({ type: "EXTRACTED_LINKS", links });
})();