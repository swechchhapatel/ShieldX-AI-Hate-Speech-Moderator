// ================================
// AI Moderator - Auto Page Scanner
// ================================

console.log(" AI Moderator: Active and scanning...");

// Flask API endpoint
const API_URL = "http://127.0.0.1:5000/moderate";
const CONFIDENCE_THRESHOLD = 0.6;
let moderationEnabled = true;
let processedItems = new Set();

// ================================
// CSS for Blur and Warning Overlay
// ================================
const style = document.createElement("style");
style.textContent = `
.ai-blurred {
  filter: blur(8px);
  opacity: 0.6;
  transition: all 0.3s ease;
  position: relative;
  user-select: none;
  cursor: pointer;
}

.ai-warning {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(220, 38, 38, 0.9);
  color: white;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  pointer-events: none;
  z-index: 999;
}

.ai-container {
  position: relative;
  display: inline-block;
}

.ai-revealed {
  filter: none !important;
  opacity: 1 !important;
  user-select: text !important;
}
`;
document.head.appendChild(style);

// ================================
// Helper Functions
// ================================

// Safe base64 encoding for all languages
function safeEncode(str) {
  return btoa(unescape(encodeURIComponent(str.substring(0, 50)))).replace(/[^a-zA-Z0-9]/g, "");
}

// Collect text-containing elements
function collectTextBlocks() {
  const selectors = [
    "p",
    "span",
    "div",
    "article",
    "li",
    "[role='article']",
    "[data-testid*='comment']",
    "[data-testid*='post']"
  ];
  const elements = [];

  selectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      const text = el.innerText?.trim();
      if (text && text.length > 15 && text.length < 2000) {
        const id = safeEncode(text);
        if (!processedItems.has(id)) {
          elements.push({ id, element: el, text });
        }
      }
    });
  });

  console.log(`🧩 Found ${elements.length} text blocks to check`);
  return elements;
}

// ================================
// Apply blur to hateful text
// ================================
function blurElement(el, confidence) {
  if (!el || el.classList.contains("ai-blurred")) return;

  // Create container
  const container = document.createElement("span");
  container.className = "ai-container";
  el.parentNode.insertBefore(container, el);
  container.appendChild(el);

  el.classList.add("ai-blurred");

  // Add warning overlay
  const warn = document.createElement("div");
  warn.className = "ai-warning";
  warn.textContent = `⚠ Hate Speech (${Math.round(confidence * 100)}%)`;
  container.appendChild(warn);

  // Reveal on click
  el.addEventListener("click", () => {
    el.classList.add("ai-revealed");
    warn.remove();
  });

  console.log("🧱 Blurred:", el.innerText.slice(0, 60));
}

// ================================
// Call Flask API to moderate
// ================================
async function moderateTextBlocks(blocks) {
  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comments: blocks.map(b => ({ id: b.id, text: b.text })) }),
    });

    if (!res.ok) throw new Error(`API Error: ${res.status}`);

    const data = await res.json();
    if (data.results) {
      data.results.forEach(r => {
        if (r.is_hate && r.confidence >= CONFIDENCE_THRESHOLD) {
          const blk = blocks.find(b => b.id === r.id);
          if (blk && blk.element) blurElement(blk.element, r.confidence);
          processedItems.add(r.id);
        }
      });
      console.log("✅ Moderation finished");
    }
  } catch (err) {
    console.error("❌ Failed to moderate:", err);
  }
}

// ================================
// Main Scan Loop
// ================================
function scanPage() {
  if (!moderationEnabled) return;
  const blocks = collectTextBlocks();
  if (blocks.length > 0) moderateTextBlocks(blocks);
}

// Initial scan + periodic re-scan
setTimeout(scanPage, 2000);
setInterval(scanPage, 10000);

// Watch for dynamically loaded content
const observer = new MutationObserver(() => {
  if (moderationEnabled) setTimeout(scanPage, 1000);
});
observer.observe(document.body, { childList: true, subtree: true });
