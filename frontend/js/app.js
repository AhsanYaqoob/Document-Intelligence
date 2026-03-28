/* ─────────────────────────────────────────────────────
   AI Document Intelligence — Frontend JS
   Features: Upload, Q&A, Remove Doc, Clear Chat,
             Copy response, Toasts, localStorage,
             Markdown formatting, Char counter
───────────────────────────────────────────────────── */

const API_BASE = "/api/v1";
const API_KEY  = "my_super_secret_backend_key";
const LS_KEY   = "ai_doc_intel_docs";

// ─── State ───────────────────────────────────────────
let uploadedDocs    = loadDocs(); // [{ name, docId, time }]
let activeDocId     = null;
let activeDocName   = null;
let selectedFileObj = null;  // holds file from drag-drop OR browse
let msgCount      = 0;

// ─── DOM Refs ─────────────────────────────────────────
const dropZone        = document.getElementById("dropZone");
const fileInput       = document.getElementById("fileInput");
const selectedFile    = document.getElementById("selectedFile");
const fileNameEl      = document.getElementById("fileName");
const fileSizeEl      = document.getElementById("fileSize");
const clearFileBtn    = document.getElementById("clearFile");
const uploadBtn       = document.getElementById("uploadBtn");
const uploadBtnText   = document.getElementById("uploadBtnText");
const uploadSpinner   = document.getElementById("uploadSpinner");
const uploadStatus    = document.getElementById("uploadStatus");
const progressWrap    = document.getElementById("progressWrap");
const progressBar     = document.getElementById("progressBar");
const docsList        = document.getElementById("docsList");
const clearAllDocsBtn = document.getElementById("clearAllDocsBtn");
const chatWindow      = document.getElementById("chatWindow");
const questionInput   = document.getElementById("questionInput");
const charCounter     = document.getElementById("charCounter");
const sendBtn         = document.getElementById("sendBtn");
const sendBtnText     = document.getElementById("sendBtnText");
const sendSpinner     = document.getElementById("sendSpinner");
const activeDocBadge  = document.getElementById("activeDocBadge");
const activeDocNameEl = document.getElementById("activeDocName");
const clearChatBtn    = document.getElementById("clearChatBtn");
const msgCounterEl    = document.getElementById("msgCounter");
const modalBackdrop   = document.getElementById("modalBackdrop");
const modalTitle      = document.getElementById("modalTitle");
const modalMsg        = document.getElementById("modalMsg");
const modalConfirm    = document.getElementById("modalConfirm");
const modalCancel     = document.getElementById("modalCancel");
const headerStat      = document.getElementById("headerStat");
const headerDocCount  = document.getElementById("headerDocCount");
const headerDocPlural = document.getElementById("headerDocPlural");

// ─── Init ─────────────────────────────────────────────
renderDocsList();
updateHeaderStat();

// ─── Drop Zone ────────────────────────────────────────
dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover",  (e) => { e.preventDefault(); dropZone.classList.add("drag-over"); });
dropZone.addEventListener("dragleave", ()  => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = e.dataTransfer.files[0];
  if (file) handleFileSelect(file);
});
fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFileSelect(fileInput.files[0]);
});
clearFileBtn.addEventListener("click", () => {
  fileInput.value   = "";
  selectedFileObj   = null;
  selectedFile.style.display = "none";
  uploadBtn.disabled = true;
  setUploadStatus("");
  hideProgress();
});

function handleFileSelect(file) {
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    showToast("Only PDF files are supported.", "error");
    return;
  }
  selectedFileObj = file;          // ← store regardless of source
  fileNameEl.textContent = file.name;
  fileSizeEl.textContent = formatBytes(file.size);
  selectedFile.style.display = "flex";
  uploadBtn.disabled = false;
  setUploadStatus("");
}

// ─── Upload ───────────────────────────────────────────
uploadBtn.addEventListener("click", async () => {
  const file = selectedFileObj || fileInput.files[0];
  if (!file) return;

  setUploadLoading(true);
  setUploadStatus("Uploading and analyzing… this may take a moment.", "info");
  animateProgress();

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      headers: { "X-API-KEY": API_KEY },
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `Server error ${res.status}`);

    finishProgress();
    setUploadStatus(`✅ ${data.message}`, "success");
    addDocToList(data.filename, data.doc_id);
    showToast(`"${data.filename}" ready to query!`, "success");

    fileInput.value = "";
    selectedFileObj = null;
    selectedFile.style.display = "none";
    uploadBtn.disabled = true;
    setTimeout(() => { setUploadStatus(""); hideProgress(); }, 4000);

  } catch (err) {
    hideProgress();
    setUploadStatus(`❌ ${err.message}`, "error");
    showToast(err.message, "error");
  } finally {
    setUploadLoading(false);
  }
});

function setUploadLoading(loading) {
  uploadBtn.disabled = loading;
  uploadBtnText.textContent = loading ? "Analyzing…" : "Upload & Analyze";
  uploadSpinner.style.display = loading ? "inline-block" : "none";
}
function setUploadStatus(msg, type = "") {
  uploadStatus.textContent = msg;
  uploadStatus.className   = "upload-status" + (type ? ` ${type}` : "");
}

// Progress bar animation
let progressInterval = null;
function animateProgress() {
  progressWrap.style.display = "block";
  progressBar.style.width = "0%";
  let w = 0;
  progressInterval = setInterval(() => {
    w = Math.min(w + Math.random() * 4, 85);
    progressBar.style.width = w + "%";
  }, 300);
}
function finishProgress() {
  clearInterval(progressInterval);
  progressBar.style.width = "100%";
}
function hideProgress() {
  clearInterval(progressInterval);
  progressWrap.style.display = "none";
  progressBar.style.width = "0%";
}

// ─── Documents List ───────────────────────────────────
function addDocToList(filename, docId) {
  if (uploadedDocs.find((d) => d.docId === docId)) {
    selectDoc(docId, filename);
    return;
  }
  uploadedDocs.push({ name: filename, docId, time: Date.now() });
  saveDocs();
  renderDocsList();
  updateHeaderStat();
  selectDoc(docId, filename);
}

function renderDocsList() {
  clearAllDocsBtn.style.display = uploadedDocs.length ? "inline-block" : "none";

  if (uploadedDocs.length === 0) {
    docsList.innerHTML = '<p class="empty-msg">No documents uploaded yet.</p>';
    return;
  }
  docsList.innerHTML = uploadedDocs
    .slice()
    .reverse()
    .map((d) => `
      <div class="doc-item ${d.docId === activeDocId ? "active" : ""}"
           onclick="selectDoc('${escAttr(d.docId)}', '${escAttr(d.name)}')">
        <span class="doc-item-icon">📄</span>
        <div class="doc-item-info">
          <span class="doc-item-name" title="${escAttr(d.name)}">${escHtml(d.name)}</span>
          <span class="doc-item-time">${timeAgo(d.time)}</span>
        </div>
        <div class="doc-item-right">
          <span class="doc-item-badge">Ready</span>
          <button class="btn-remove-doc" title="Remove document"
            onclick="event.stopPropagation(); confirmRemoveDoc('${escAttr(d.docId)}', '${escAttr(d.name)}')">🗑</button>
        </div>
      </div>`)
    .join("");
}

function selectDoc(docId, docName) {
  if (activeDocId === docId) return;
  activeDocId   = docId;
  activeDocName = docName;

  activeDocBadge.style.display = "flex";
  activeDocNameEl.textContent  = docName;

  questionInput.disabled = false;
  sendBtn.disabled       = false;
  questionInput.placeholder = `Ask about "${docName}"…`;
  questionInput.focus();

  resetChat();
  renderDocsList();
}

// ─── Remove Document ──────────────────────────────────
let pendingRemoveId = null;

function confirmRemoveDoc(docId, docName) {
  pendingRemoveId = docId;
  modalTitle.textContent = "Remove Document?";
  modalMsg.textContent   = `"${docName}" will be removed from the list. This won't delete the file from the server.`;
  openModal();
}

modalConfirm.addEventListener("click", () => {
  if (pendingRemoveId) {
    removeDoc(pendingRemoveId);
    pendingRemoveId = null;
  }
  closeModal();
});
modalCancel.addEventListener("click",   closeModal);
modalBackdrop.addEventListener("click", (e) => { if (e.target === modalBackdrop) closeModal(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

function removeDoc(docId) {
  const doc = uploadedDocs.find((d) => d.docId === docId);
  uploadedDocs = uploadedDocs.filter((d) => d.docId !== docId);
  saveDocs();

  if (activeDocId === docId) {
    activeDocId   = null;
    activeDocName = null;
    activeDocBadge.style.display = "none";
    questionInput.disabled = true;
    sendBtn.disabled       = true;
    questionInput.placeholder = "Type your question and press Enter…";
    resetChat();
    clearChatBtn.style.display = "none";
    msgCounterEl.style.display = "none";
  }

  renderDocsList();
  updateHeaderStat();
  if (doc) showToast(`"${doc.name}" removed.`, "info");
}

// Clear All
clearAllDocsBtn.addEventListener("click", () => {
  pendingRemoveId = "__ALL__";
  modalTitle.textContent = "Remove All Documents?";
  modalMsg.textContent   = "All documents will be removed from the list.";
  openModal();
});
// Override confirm for all
modalConfirm.addEventListener("click", () => {}, false); // already attached above

// Re-attach with all-check:
modalConfirm.onclick = () => {
  if (pendingRemoveId === "__ALL__") {
    uploadedDocs = [];
    saveDocs();
    activeDocId = null; activeDocName = null;
    activeDocBadge.style.display = "none";
    questionInput.disabled = true; sendBtn.disabled = true;
    questionInput.placeholder = "Type your question and press Enter…";
    resetChat();
    clearChatBtn.style.display = "none";
    msgCounterEl.style.display = "none";
    renderDocsList();
    updateHeaderStat();
    showToast("All documents removed.", "info");
  } else if (pendingRemoveId) {
    removeDoc(pendingRemoveId);
  }
  pendingRemoveId = null;
  closeModal();
};

function openModal()  { modalBackdrop.classList.add("open"); }
function closeModal() { modalBackdrop.classList.remove("open"); pendingRemoveId = null; }

// ─── Clear Conversation ───────────────────────────────
clearChatBtn.addEventListener("click", () => {
  pendingRemoveId = "__CHAT__";
  modalTitle.textContent = "Clear Conversation?";
  modalMsg.textContent   = "All messages in this conversation will be cleared.";
  openModal();
});

// ─── Q&A ──────────────────────────────────────────────
sendBtn.addEventListener("click", sendQuestion);
questionInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) sendQuestion();
});

// Character counter
questionInput.addEventListener("input", () => {
  const len = questionInput.value.length;
  const max = 500;
  if (len === 0) { charCounter.textContent = ""; charCounter.className = "char-counter"; return; }
  charCounter.textContent = `${len}/${max}`;
  charCounter.className   = "char-counter" + (len > max ? " over" : len > 400 ? " warn" : "");
});

async function sendQuestion() {
  const q = questionInput.value.trim();
  if (!q || !activeDocId) return;

  questionInput.value = "";
  charCounter.textContent = "";
  hidePlaceholder();
  appendMessage("user", q);

  const typingId = appendTyping();
  setSendLoading(true);

  try {
    const res = await fetch(`${API_BASE}/ask/${encodeURIComponent(activeDocId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-KEY": API_KEY },
      body: JSON.stringify({ question: q }),
    });
    const data = await res.json();
    removeTyping(typingId);
    if (!res.ok) throw new Error(data.detail || `Server error ${res.status}`);
    await streamMessage(data.answer, data.sources);

  } catch (err) {
    removeTyping(typingId);
    appendMessage("ai", `⚠️ ${err.message}`);
  } finally {
    setSendLoading(false);
  }
}

function setSendLoading(loading) {
  sendBtn.disabled       = loading;
  questionInput.disabled = loading;
  sendBtnText.textContent = loading ? "…" : "Send";
  sendSpinner.style.display = loading ? "inline-block" : "none";
}

// ─── Chat Rendering ───────────────────────────────────
function hidePlaceholder() {
  const ph = document.getElementById("chatPlaceholder");
  if (ph) ph.remove();
}

function resetChat() {
  msgCount = 0;
  chatWindow.innerHTML = `
    <div class="chat-placeholder" id="chatPlaceholder">
      <div class="placeholder-icon">🤖</div>
      <p>Ask anything about <strong>${escHtml(activeDocName || "the document")}</strong>.</p>
      <div class="shortcut-hints">
        <span class="hint-chip">Enter ↵ to send</span>
        <span class="hint-chip">Click doc to switch</span>
      </div>
    </div>`;
  updateMsgCounter();
}

function appendMessage(role, text, sources = []) {
  hidePlaceholder();
  msgCount++;
  const div = document.createElement("div");
  div.className = `chat-message ${role}`;

  const time   = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const label  = role === "user" ? "You" : "AI";
  const copyId = "msg-" + Date.now();

  const sourcesHtml = (role === "ai" && sources.length)
    ? `<div class="sources-tag">📎 ${sources.map(escHtml).join(", ")}</div>`
    : "";

  const copyBtn = (role === "ai")
    ? `<button class="btn-copy" id="${copyId}" onclick="copyMsg('${copyId}', this)" title="Copy response">Copy</button>`
    : "";

  div.innerHTML = `
    <div class="bubble">${formatText(text)}</div>
    ${sourcesHtml}
    <div class="msg-meta-row">
      <span class="msg-meta">${label} · ${time}</span>
      ${copyBtn}
    </div>`;

  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  updateMsgCounter();
}

function appendTyping() {
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.className = "chat-message ai";
  div.id = id;
  div.innerHTML = `
    <div class="bubble bubble--typing">
      <div class="typing-bubble"><span></span><span></span><span></span></div>
    </div>`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return id;
}
function removeTyping(id) { const el = document.getElementById(id); if (el) el.remove(); }

// ─── Streaming renderer ───────────────────────────────
// Splits text into tokens (words + whitespace/newlines) the same way
// a real LLM streams — word by word, with natural pauses at punctuation.
async function streamMessage(text, sources = []) {
  hidePlaceholder();
  msgCount++;

  const time   = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const copyId = "msg-" + Date.now();

  const div = document.createElement("div");
  div.className = "chat-message ai";
  div.innerHTML = `
    <div class="bubble" id="sb-${copyId}"></div>
    <div class="msg-meta-row" id="mr-${copyId}" style="display:none;">
      <span class="msg-meta">AI · ${time}</span>
      <button class="btn-copy" id="${copyId}" onclick="copyMsg('${copyId}', this)" title="Copy response">Copy</button>
    </div>`;

  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  const bubbleEl = document.getElementById(`sb-${copyId}`);
  const metaRow  = document.getElementById(`mr-${copyId}`);

  // Tokenise: keep words AND whitespace as separate tokens so spacing is preserved
  const tokens = text.match(/[^\s]+|\n+|[ \t]+/g) || [];
  let shown = "";

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    shown += token;

    // Render plain text + blinking cursor (innerHTML escapes are handled by escHtml)
    bubbleEl.innerHTML = escHtml(shown) + '<span class="cursor"></span>';

    // Keep scroll pinned every few tokens
    if (i % 4 === 0) chatWindow.scrollTop = chatWindow.scrollHeight;

    // ── Natural delay logic ──────────────────────────────
    const trimmed = token.trim();
    const last    = trimmed[trimmed.length - 1] || "";
    let   delay   = 28 + Math.random() * 35;       // base 28–63 ms per word

    if (trimmed === "")              delay = 5;     // pure whitespace — nearly instant
    else if (/\n/.test(token))       delay += 160;  // newline pause (paragraph break)
    else if (/[.!?]$/.test(last))    delay += 220;  // sentence end — noticeable pause
    else if (/[,;:]$/.test(last))    delay += 90;   // clause pause
    else if (trimmed.length <= 2)    delay -= 10;   // tiny words (a, I, is) — quicker
    else if (trimmed.startsWith("**") || trimmed.startsWith("-")) delay += 30; // heading/list item

    await sleep(delay);
  }

  // ── Streaming complete: render formatted markdown HTML ──
  bubbleEl.innerHTML = formatText(text);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  if (sources.length) {
    const srcEl = document.createElement("div");
    srcEl.className = "sources-tag";
    srcEl.innerHTML = `📎 ${sources.map(escHtml).join(", ")}`;
    div.insertBefore(srcEl, metaRow);
  }

  metaRow.style.display = "flex";
  chatWindow.scrollTop = chatWindow.scrollHeight;
  updateMsgCounter();
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function updateMsgCounter() {
  if (msgCount === 0) {
    msgCounterEl.style.display = "none";
    clearChatBtn.style.display = "none";
  } else {
    msgCounterEl.style.display = "inline-block";
    msgCounterEl.textContent   = `${msgCount} message${msgCount !== 1 ? "s" : ""}`;
    clearChatBtn.style.display = "inline-block";
  }
}

// Copy to clipboard
function copyMsg(id, btn) {
  const bubble = btn.closest(".chat-message").querySelector(".bubble");
  const text   = bubble ? bubble.innerText : "";
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "Copied!";
    btn.classList.add("copied");
    setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("copied"); }, 2000);
  }).catch(() => showToast("Could not copy text.", "error"));
}

// ─── Text Formatting (mini markdown) ─────────────────
function formatText(raw) {
  let s = escHtml(raw);
  s = s.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/\*(.*?)\*/g,     "<em>$1</em>");
  s = s.replace(/`([^`]+)`/g,     "<code>$1</code>");
  s = s.replace(/^[-•]\s+(.+)$/gm, "<li>$1</li>");
  s = s.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
  s = s.replace(/^(\d+)\.\s+(.+)$/gm, "<li>$2</li>");
  s = s.replace(/\n/g, "<br>");
  return s;
}

// ─── Toast Notifications ─────────────────────────────
function showToast(msg, type = "info") {
  const icons  = { success: "✅", error: "❌", info: "ℹ️" };
  const container = document.getElementById("toastContainer");
  const toast  = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || "ℹ️"}</span>
    <span class="toast-text">${escHtml(msg)}</span>
    <button class="toast-close" onclick="dismissToast(this)">✕</button>`;
  container.appendChild(toast);
  setTimeout(() => dismissToast(toast.querySelector(".toast-close")), 4500);
}
function dismissToast(btn) {
  const toast = btn.closest(".toast");
  if (!toast) return;
  toast.classList.add("hiding");
  toast.addEventListener("animationend", () => toast.remove(), { once: true });
}

// ─── Header Stat ──────────────────────────────────────
function updateHeaderStat() {
  const n = uploadedDocs.length;
  if (n === 0) { headerStat.style.display = "none"; return; }
  headerStat.style.display = "inline-block";
  headerDocCount.textContent  = n;
  headerDocPlural.textContent = n === 1 ? "" : "s";
}

// ─── localStorage ─────────────────────────────────────
function saveDocs() {
  try { localStorage.setItem(LS_KEY, JSON.stringify(uploadedDocs)); } catch {}
}
function loadDocs() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || "[]"); } catch { return []; }
}

// ─── Utilities ────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function escAttr(str) {
  return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
function formatBytes(bytes) {
  if (bytes < 1024)       return bytes + " B";
  if (bytes < 1024*1024)  return (bytes/1024).toFixed(1) + " KB";
  return (bytes/(1024*1024)).toFixed(1) + " MB";
}
function timeAgo(ts) {
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  const h = Math.floor(diff / 3600000);
  const d = Math.floor(diff / 86400000);
  if (d > 0)  return `${d}d ago`;
  if (h > 0)  return `${h}h ago`;
  if (m > 0)  return `${m}m ago`;
  return "just now";
}
