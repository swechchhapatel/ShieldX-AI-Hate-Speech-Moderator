chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PREDICT_TEXT") {
    fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: message.text })
    })
      .then(response => response.json())
      .then(data => sendResponse(data))
      .catch(err => sendResponse({ error: err.toString() }));
    return true; // keep the message channel open
  }
});
