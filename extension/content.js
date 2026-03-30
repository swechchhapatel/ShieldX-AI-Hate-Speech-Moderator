function scanTextNodes() {
  const elements = document.body.getElementsByTagName("*");
  for (let el of elements) {
    for (let node of el.childNodes) {
      if (node.nodeType === Node.TEXT_NODE && node.textContent.trim().length > 10) {
        chrome.runtime.sendMessage(
          { type: "PREDICT_TEXT", text: node.textContent },
          response => {
            if (response && response.prediction !== undefined) {
              if (response.prediction === 0) { // hate speech
                blurNode(node, "hate");
              } else if (response.prediction === 1) { // offensive
                blurNode(node, "offensive");
              }
            }
          }
        );
      }
    }
  }
}

// function highlight(node, color) {
//   const span = document.createElement("span");
//   span.textContent = node.textContent;
//   span.style.backgroundColor = color;
//   span.style.borderRadius = "4px";
//   span.style.padding = "2px";
//   node.parentNode.replaceChild(span, node);
// }

function blurNode(node, type) {
  const span = document.createElement("span");
  span.textContent = node.textContent;

  // Highlight color based on type
  let bgColor = "";
  if (type === "hate") {
    bgColor = "rgba(255, 0, 0, 0.3)";
  } else if (type === "offensive") {
    bgColor = "rgba(255, 165, 0, 0.3)";
  }

  // Apply styles
  span.style.backgroundColor = bgColor;
  span.style.borderRadius = "4px";
  span.style.padding = "2px";
  span.style.filter = "blur(5px)"; // 👈 blur effect
  span.style.cursor = "pointer";

  // Optional: reveal text on hover
  span.addEventListener("mouseover", () => {
    span.style.filter = "blur(0)";
  });

  span.addEventListener("mouseout", () => {
    span.style.filter = "blur(5px)";
  });

  node.parentNode.replaceChild(span, node);
}

scanTextNodes();
// const observer = new MutationObserver(() => {
//   scanTextNodes();
// });

// observer.observe(document.body, {
//   childList: true,
//   subtree: true
// });