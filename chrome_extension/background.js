// ===============================
// AI Moderator Background Relay
// ===============================

const API_URL = "http://127.0.0.1:5000/moderate"; // Flask endpoint

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "moderateText") {
    fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comments: msg.data })
    })
      .then(res => res.json())
      .then(data => sendResponse({ ok: true, results: data.results }))
      .catch(err => {
        console.error("❌ Relay failed:", err);
        sendResponse({ ok: false, error: err.message });
      });
    return true; // Keep the message channel open for async response
  }
});
