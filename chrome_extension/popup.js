// popup.js — Control panel for AI Moderator

const activateBtn = document.getElementById("activateBtn");
const deactivateBtn = document.getElementById("deactivateBtn");
const scanBtn = document.getElementById("scanBtn");
const statusText = document.getElementById("status");

function updateStatus(message) {
  statusText.innerHTML = `Status: <strong>${message}</strong>`;
}

// Ping current tab to check if contentScript is running
function pingContentScript(callback) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length === 0) return callback(false);
    chrome.tabs.sendMessage(tabs[0].id, { action: "ping" }, (response) => {
      if (chrome.runtime.lastError || !response) {
        callback(false);
      } else {
        callback(true);
      }
    });
  });
}

// Activate continuous moderation
activateBtn.addEventListener("click", () => {
  pingContentScript((isRunning) => {
    if (!isRunning) {
      updateStatus("Content script not running");
      alert("⚠️ Please refresh the page before activating.");
      return;
    }
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: "activateModeration" });
      updateStatus("Moderation Activated ✅");
    });
  });
});

// Deactivate continuous moderation
deactivateBtn.addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "deactivateModeration" });
    updateStatus("Moderation Deactivated ⛔");
  });
});

// Manual scan
scanBtn.addEventListener("click", () => {
  pingContentScript((isRunning) => {
    if (!isRunning) {
      updateStatus("Content script not running");
      alert("⚠️ Please refresh the page and try again.");
      return;
    }
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: "scanNow" });
      updateStatus("Scanning Page 🔍");
    });
  });
});

// Initial check
pingContentScript((isRunning) => {
  if (isRunning) updateStatus("Ready ✅");
  else updateStatus("Content script not running ❌");
});
