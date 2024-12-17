/* This file is the JS code that handles
1) Closing all current user tabs
2) Opens a new LC webpage for the user to finish

TODO 1: any url changes should automatically redirect user to a LC link
TODO 2: decide on a LC of the day (?)
TODO 3: instead of immediately taking user to LC, open a custom webpage/HTML that
shows users what they need to do to unlock browser

*/

chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeText({ text: 'OFF' });
});

chrome.action.onClicked.addListener(async (tab) => {
  if (chrome) {
    const prevState = await chrome.action.getBadgeText({ tabId: tab.id });
    const nextState = prevState === 'ON' ? 'OFF' : 'ON';

    // Update the badge text to the new state
    await chrome.action.setBadgeText({ tabId: tab.id, text: nextState });

    if (nextState === 'ON') {
      // Open a new tab
      // TODO 2
      const newTab = await chrome.tabs.create({ url: 'https://www.youtube.com' });

      // Get all tabs in the current window
      const allTabs = await chrome.tabs.query({ currentWindow: true });

      // Close all tabs except the newly opened one
      for (const t of allTabs) {
        if (t.id !== newTab.id) {
          await chrome.tabs.remove(t.id);
        }
      }

      /* Apply CSS to the newly opened tab
      // TODO 3
      await chrome.scripting.insertCSS({
        files: ['style.css'],
        target: { tabId: newTab.id }
      });*/
    } 
    else if (nextState === 'OFF') {
      // The extension should turn off once the user has completed a certain list of criteria
    }
  }
});