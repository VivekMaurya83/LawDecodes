document.addEventListener("DOMContentLoaded", async () => {
  // --- GLOBAL VARIABLES & CONFIG ---
  let sessions = [];
  let currentId = null;
  let saveTimeout;
  const token = localStorage.getItem("access_token");
  const API_BASE_URL = "http://127.0.0.1:8000";

  // --- CONSTANT for empty chat HTML for reuse ---
  const EMPTY_CHAT_HTML = `
    <div id="emptyChat" class="empty-chat-container">
        <div class="empty-chat-logo">LawDecodes</div>
        <h2>How can I help you today?</h2>
        <p>Upload a document to get started. You can ask for a summary, find legal terms, or ask specific questions about the content.</p>
    </div>`;

  // --- STATE VARIABLE for Q&A MODE ---
  let activeRagSessionPath = null;

  // --- DOM ELEMENT REFERENCES ---
  const dom = {
    chatWindow: document.getElementById("chatWindow"),
    chatNameEl: document.getElementById("chatName"),
    chatList: document.getElementById("chatList"),
    newChatBtn: document.getElementById("newChatBtn"),
    fileInput: document.getElementById("fileInput"),
    chatForm: document.getElementById("chatInputForm"),
    chatInput: document.getElementById("chatInput"),
    exitBtn: document.getElementById("exitBtn"),
    saveStatusEl: document.getElementById("saveStatus"),
    themeToggleBtn: document.getElementById("theme-toggle-btn"),
    usernameDisplay: document.getElementById("username-display"),
    comparisonModal: document.getElementById("comparisonModal"),
    closeModalBtn: document.getElementById("closeModalBtn"),
    originalTextContent: document.getElementById("originalTextContent"),
    summaryTextContent: document.getElementById("summaryTextContent"),
    exportDocxBtn: document.getElementById("exportDocxBtn"),
  };

  // --- API WRAPPER FOR AUTHENTICATION & ERROR HANDLING ---
  async function authorizedFetch(url, options = {}) {
    const defaultOptions = {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        ...options.headers,
      },
      keepalive: true,
    };
    if (options.body instanceof FormData) {
      delete defaultOptions.headers["Content-Type"];
    }
    const response = await fetch(url, { ...options, ...defaultOptions });
    if (response.status === 401) {
      localStorage.removeItem("access_token");
      alert("Your session has expired. Please log in again.");
      window.location.href = "./Login.html";
      throw new Error("Session expired");
    }
    return response;
  }

  // --- FILE UPLOAD LOGIC ---
  dom.fileInput.addEventListener("change", async (e) => {
    if (document.getElementById("emptyChat")) {
      dom.chatWindow.innerHTML = "";
    }
    dom.chatInput.placeholder = "Ask a question or type /clear...";
    const file = e.target.files[0];
    if (!file) return;
    const isPotentiallyNewChat =
      !dom.chatWindow.querySelector(".message-wrapper");
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await authorizedFetch(`${API_BASE_URL}/api/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("File upload failed.");
      const result = await response.json();
      addFileMessageToChat(result.filePath, result.originalFilename);
      if (isPotentiallyNewChat) {
        await saveCurrentChatToBackend();
      }
    } catch (error) {
      if (error.message !== "Session expired") {
        console.error("Error uploading file:", error);
        alert("Could not upload file.");
      }
    } finally {
      e.target.value = "";
    }
  });

  // --- UNIFIED CLICK LISTENER FOR ALL CHAT WINDOW BUTTONS ---
  dom.chatWindow.addEventListener("click", async (e) => {
    if (e.target.tagName === "BUTTON") {
      e.preventDefault();
      e.stopPropagation();
    }
    if (e.target.classList.contains("process-document-btn")) {
      const button = e.target;
      button.textContent = "Processing...";
      button.disabled = true;
      const filePath = button.dataset.filepath;
      try {
        const startResponse = await authorizedFetch(
          `${API_BASE_URL}/api/summarize`,
          { method: "POST", body: JSON.stringify({ filePath: filePath }) }
        );
        if (!startResponse.ok)
          throw new Error(
            (await startResponse.json()).detail || "Failed to start processing."
          );
        const startResult = await startResponse.json();
        pollForResult(
          startResult.report_filename,
          button,
          startResult.extractedFilePath,
          startResult.jargonFilename
        );
      } catch (error) {
        if (error.message !== "Session expired") {
          alert(`Error: ${error.message}`);
          button.textContent = "Process Document";
          button.disabled = false;
        }
      }
    }
    if (e.target.classList.contains("compare-btn")) {
      const button = e.target;
      button.textContent = "Loading...";
      button.disabled = true;
      const { extractedFilename, reportFilename } = button.dataset;
      const summaryText = button
        .closest(".message-content")
        .querySelector("div").innerHTML;
      try {
        const response = await authorizedFetch(
          `${API_BASE_URL}/api/get-extracted-text/${extractedFilename}`
        );
        if (!response.ok)
          throw new Error(
            (await response.json()).detail || "Could not fetch original text."
          );
        const data = await response.json();
        dom.originalTextContent.innerHTML = data.original_text;
        dom.summaryTextContent.innerHTML = summaryText;
        dom.exportDocxBtn.dataset.reportFilename = reportFilename;
        dom.exportDocxBtn.dataset.extractedFilename = extractedFilename;
        dom.comparisonModal.style.display = "flex";
      } catch (error) {
        alert(`Error loading comparison: ${error.message}`);
      } finally {
        button.textContent = "Compare Side-by-Side";
        button.disabled = false;
      }
    }
    if (e.target.classList.contains("view-jargon-btn")) {
      const button = e.target;
      button.textContent = "Loading Terms...";
      button.disabled = true;
      try {
        const response = await authorizedFetch(
          `${API_BASE_URL}/api/get-jargons/${button.dataset.jargonFilename}`
        );
        if (!response.ok) {
          throw new Error(
            (await response.json()).detail || "Could not fetch legal terms."
          );
        }
        const { terms } = await response.json();
        if (terms && terms.length > 0) {
          let formattedText =
            "### Legal Terms Found in Document\n\n" +
            terms
              .map(
                (item) => `**${item.term.trim()}**\n> ${item.definition.trim()}`
              )
              .join("\n\n---\n\n");
          addAssistantMessageToChat(formattedText);
        } else {
          addAssistantMessageToChat(
            "No specific legal jargon was identified in the document."
          );
        }
        button.style.display = "none";
      } catch (error) {
        addAssistantMessageToChat(
          `Sorry, I couldn't retrieve the legal terms: ${error.message}`
        );
        button.textContent = "View Legal Terms";
        button.disabled = false;
      }
    }
    if (e.target.classList.contains("copy-btn")) {
      const contentDiv = e.target
        .closest(".message-content")
        .querySelector("div");
      if (contentDiv) {
        navigator.clipboard
          .writeText(contentDiv.textContent)
          .then(() => {
            e.target.textContent = "Copied!";
            setTimeout(() => {
              e.target.textContent = "Copy";
            }, 2000);
          })
          .catch((err) => console.error("Failed to copy text: ", err));
      }
    }
  });

  // --- MODAL & EXPORT LOGIC ---
  dom.closeModalBtn.addEventListener("click", () => {
    dom.comparisonModal.style.display = "none";
  });
  dom.comparisonModal.addEventListener("click", (e) => {
    if (e.target === e.currentTarget) {
      dom.comparisonModal.style.display = "none";
    }
  });
  dom.exportDocxBtn.addEventListener("click", async () => {
    const button = dom.exportDocxBtn;
    const { reportFilename, extractedFilename } = button.dataset;
    if (!reportFilename || !extractedFilename) {
      alert("Error: Missing file info for export.");
      return;
    }
    button.textContent = "Generating...";
    button.disabled = true;
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/export-docx/${reportFilename}/${extractedFilename}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!response.ok) throw new Error("Server failed to generate DOCX file.");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `Analysis_Report_${reportFilename.replace(
        "_ANALYSIS_REPORT.txt",
        ""
      )}.docx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (error) {
      alert(`Export failed: ${error.message}`);
    } finally {
      button.textContent = "Export to DOCX";
      button.disabled = false;
    }
  });

  // --- POLLING LOGIC ---
  function pollForResult(
    reportFilename,
    buttonElement,
    extractedFilePath,
    jargonFilename
  ) {
    const maxRetries = 60;
    let retries = 0;
    const intervalId = setInterval(async () => {
      if (retries++ >= maxRetries) {
        clearInterval(intervalId);
        addAssistantMessageToChat(
          "The process is taking a long time. Q&A may be ready. Try asking a question."
        );
        activeRagSessionPath = extractedFilePath;
        buttonElement.style.display = "none";
        await saveCurrentChatToBackend(); // Save state on timeout
        return;
      }
      try {
        const reportResponse = await authorizedFetch(
          `${API_BASE_URL}/api/get-report/${reportFilename}`
        );
        if (reportResponse.ok) {
          clearInterval(intervalId);
          const result = await reportResponse.json();
          const summaryMessageContent = addAssistantMessageToChat(
            result.summary
          );
          buttonElement.style.display = "none";
          const extractedFilename = extractedFilePath.split("/").pop();
          const buttonContainer = document.createElement("div");
          buttonContainer.className = "attachment-buttons";
          buttonContainer.innerHTML = `<button type="button" class="action-btn compare-btn" data-extracted-filename="${extractedFilename}" data-report-filename="${reportFilename}">Compare Side-by-Side</button><button type="button" class="action-btn secondary view-jargon-btn" data-jargon-filename="${jargonFilename}">View Legal Terms</button>`;
          summaryMessageContent.appendChild(buttonContainer);
          activeRagSessionPath = extractedFilePath;
          dom.chatInput.placeholder = "Ask a question...";
          addAssistantMessageToChat(
            `✅ This document is now ready for Q&A. Ask your questions below.`
          );
          await saveCurrentChatToBackend();
        } else if (reportResponse.status !== 404) {
          clearInterval(intervalId);
          throw new Error(
            (await reportResponse.json()).detail || "Failed to fetch report."
          );
        }
      } catch (error) {
        if (error.message !== "Session expired") {
          clearInterval(intervalId);
          addAssistantMessageToChat(`An error occurred: ${error.message}`);
          buttonElement.style.display = "none";
        }
      }
    }, 5000);
  }

  // --- UI HELPER FUNCTIONS ---
  function createMessageHTML(content, time, isUser = false, isTyping = false) {
    const userAvatar = `<svg class="avatar" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/><path d="M12 15C14.2091 15 16 13.2091 16 11C16 8.79086 14.2091 7 12 7C9.79086 7 8 8.79086 8 11C8 13.2091 9.79086 15 12 15Z" stroke="currentColor" stroke-width="1.5"/><path d="M19.0002 19.5C19.0002 16.4624 15.8662 14 12.0002 14C8.13418 14 5.00024 16.4624 5.00024 19.5" stroke="currentColor" stroke-width="1.5"/></svg>`;
    const assistantAvatar = `<svg class="avatar" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 8V4m0 0a1.5 1.5 0 100 3 1.5 1.5 0 000-3z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 14a2.5 2.5 0 100 5 2.5 2.5 0 000-5z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M17 12a5 5 0 10-10 0 5 5 0 0010 0z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
    const wrapperClass = isUser
      ? "message-wrapper user"
      : "message-wrapper assistant";
    const messageClass = isTyping ? "message typing-message" : "message";
    return `<div class="${wrapperClass}"><div class="message-avatar">${
      isUser ? userAvatar : assistantAvatar
    }</div><div class="message-body"><div class="${messageClass}">${content}</div><div class="message-time">${time}</div></div></div>`;
  }
  function addFileMessageToChat(filePath, originalFilename) {
    const time = new Date().toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
    const content = `<div class="message-content"><a href="${API_BASE_URL}/${filePath.replace(
      "backend/",
      ""
    )}" target="_blank" class="attachment-link"><svg fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg><span class="attachment-name">${originalFilename}</span></a><div class="attachment-buttons"><button type="button" class="process-document-btn action-btn" data-filepath="${filePath}">Process Document</button></div></div>`;
    dom.chatWindow.insertAdjacentHTML(
      "beforeend",
      createMessageHTML(content, time, true)
    );
    dom.chatWindow.scrollTop = dom.chatWindow.scrollHeight;
  }
  function addAssistantMessageToChat(text, sources) {
    const time = new Date().toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
    let fullText = text || "";
    if (Array.isArray(sources) && sources.length > 0) {
      fullText += `\n\n**Sources:**\n${sources
        .filter((s) => s)
        .map((s) => `- ${s}`)
        .join("\n")}`;
    }
    const renderedHTML = marked.parse(fullText);
    const content = `<div class="message-content"><div>${renderedHTML}</div><button type="button" class="copy-btn">Copy</button></div>`;
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = createMessageHTML(content, time, false);
    const messageElement = tempDiv.firstElementChild;
    dom.chatWindow.appendChild(messageElement);
    dom.chatWindow.scrollTop = dom.chatWindow.scrollHeight;
    hljs.highlightAll();
    return messageElement.querySelector(".message-content");
  }
  function showTypingIndicator() {
    const time = new Date().toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
    const content = `<div class="typing-indicator"><span></span><span></span><span></span></div>`;
    dom.chatWindow.insertAdjacentHTML(
      "beforeend",
      createMessageHTML(content, time, false, true)
    );
    dom.chatWindow.scrollTop = dom.chatWindow.scrollHeight;
  }
  function removeTypingIndicator() {
    const indicator = dom.chatWindow.querySelector(".typing-indicator");
    if (indicator) {
      indicator.closest(".message-wrapper").remove();
    }
  }

  // --- CHAT FORM SUBMISSION (HANDLES Q&A MODE) ---
  dom.chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = dom.chatInput.value.trim();
    if (!query) return;
    const isPotentiallyNewChat =
      !dom.chatWindow.querySelector(".message-wrapper");
    if (document.getElementById("emptyChat")) {
      dom.chatWindow.innerHTML = "";
    }
    const time = new Date().toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    });
    const content = `<div class="message-content"><pre>${query}</pre></div>`;
    dom.chatWindow.insertAdjacentHTML(
      "beforeend",
      createMessageHTML(content, time, true)
    );
    dom.chatInput.value = "";
    dom.chatWindow.scrollTop = dom.chatWindow.scrollHeight;
    if (isPotentiallyNewChat) {
      await saveCurrentChatToBackend();
    }
    if (activeRagSessionPath) {
      showTypingIndicator();
      try {
        const response = await authorizedFetch(`${API_BASE_URL}/api/ask-rag`, {
          method: "POST",
          body: JSON.stringify({
            extractedFilePath: activeRagSessionPath,
            query: query,
          }),
        });
        if (!response.ok) {
          throw new Error(
            (await response.json()).detail || "Failed to get answer."
          );
        }
        const result = await response.json();
        removeTypingIndicator();
        addAssistantMessageToChat(result.response, result.sources);
      } catch (error) {
        if (error.message !== "Session expired") {
          removeTypingIndicator();
          addAssistantMessageToChat(
            `Sorry, I encountered an error: ${error.message}`
          );
        }
      }
    } else {
      addAssistantMessageToChat(
        "Please upload and process a document to start a Q&A session."
      );
    }
    await saveCurrentChatToBackend();
  });

  // --- CORE CHAT & PAGE MANAGEMENT FUNCTIONS ---
  async function saveCurrentChatToBackend() {
    if (!token || !currentId) return;
    const session = sessions.find((s) => s.id === currentId);
    if (!session || !dom.chatWindow.querySelector(".message-wrapper")) return;

    // --- MODIFICATION START: Logic to embed RAG state into the HTML ---
    let ragStateHolder = dom.chatWindow.querySelector("#rag-state-holder");
    if (activeRagSessionPath) {
      if (!ragStateHolder) {
        ragStateHolder = document.createElement("div");
        ragStateHolder.id = "rag-state-holder";
        ragStateHolder.style.display = "none";
        dom.chatWindow.prepend(ragStateHolder); // Add to the top of chat content
      }
      ragStateHolder.dataset.ragPath = activeRagSessionPath;
    } else if (ragStateHolder) {
      ragStateHolder.remove(); // Clean up if RAG is no longer active
    }
    // --- MODIFICATION END ---

    session.html = dom.chatWindow.innerHTML;

    if (session.isNew) {
      let newTitle = "Chat";
      const firstUserMessageText = dom.chatWindow.querySelector(
        ".message-wrapper.user .message-content pre"
      );
      const firstUserFile = dom.chatWindow.querySelector(
        ".message-wrapper.user .attachment-name"
      );
      if (firstUserMessageText) {
        newTitle = firstUserMessageText.textContent;
      } else if (firstUserFile) {
        newTitle = `File: ${firstUserFile.textContent}`;
      }
      session.name =
        newTitle.length > 35 ? `${newTitle.substring(0, 35)}...` : newTitle;
      dom.chatNameEl.textContent = session.name;
    }

    clearTimeout(saveTimeout);
    dom.saveStatusEl.textContent = "Saving...";
    dom.saveStatusEl.style.opacity = "1";
    try {
      await authorizedFetch(`${API_BASE_URL}/api/chats`, {
        method: "POST",
        body: JSON.stringify({
          chat_id: String(session.id),
          title: session.name,
          html_content: session.html,
        }),
      });
      if (session.isNew) {
        session.isNew = false;
        renderChatList();
      }
      dom.saveStatusEl.textContent = "All changes saved";
      saveTimeout = setTimeout(() => {
        dom.saveStatusEl.style.opacity = "0";
      }, 2000);
    } catch (error) {
      if (error.message !== "Session expired") {
        console.error("Error saving chat:", error);
        dom.saveStatusEl.textContent = "Error saving";
      }
    }
  }

  function renderChatList() {
    dom.chatList.innerHTML = "";
    sessions.forEach((session) => {
      const li = document.createElement("li");
      li.dataset.id = String(session.id);
      if (String(session.id) === String(currentId)) li.classList.add("active");
      li.innerHTML = `<span class="chat-title">${session.name}</span><button class="delete-chat-btn" title="Delete chat"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>`;
      dom.chatList.appendChild(li);
    });
  }

  function activateChat(chatId) {
    currentId = String(chatId);
    const session = sessions.find((s) => String(s.id) === String(chatId));
    if (session) {
      dom.chatNameEl.textContent = session.name;
      dom.chatWindow.innerHTML = session.html || EMPTY_CHAT_HTML;

      // --- MODIFICATION START: Logic to restore RAG state from the embedded div ---
      const ragStateHolder = dom.chatWindow.querySelector("#rag-state-holder");
      if (ragStateHolder && ragStateHolder.dataset.ragPath) {
        const savedRagPath = ragStateHolder.dataset.ragPath;
        activeRagSessionPath = savedRagPath;
        const fileName = savedRagPath.split("/").pop();
        dom.chatInput.placeholder = `Ask a question about ${fileName}...`;
      } else {
        activeRagSessionPath = null;
        dom.chatInput.placeholder = "Ask a question or type /clear...";
      }
      // --- MODIFICATION END ---

      renderChatList();
      dom.chatWindow.scrollTop = dom.chatWindow.scrollHeight;
    }
  }

  async function initializePage() {
    if (!token) {
      window.location.href = "./Login.html";
      return;
    }
    try {
      const [profileRes, chatsRes] = await Promise.all([
        authorizedFetch(`${API_BASE_URL}/api/profile`),
        authorizedFetch(`${API_BASE_URL}/api/chats`),
      ]);
      if (!profileRes.ok || !chatsRes.ok)
        throw new Error("Failed to load user data");
      const profileData = await profileRes.json();
      dom.usernameDisplay.textContent = profileData.name || "User";
      const savedChats = await chatsRes.json();
      sessions =
        savedChats.length > 0
          ? savedChats.map((c) => ({
              id: String(c.chat_id),
              name: c.title,
              html: c.html_content,
            }))
          : [
              {
                id: String(Date.now()),
                name: "New Chat",
                html: "",
                isNew: true,
              },
            ];
      const targetId =
        new URLSearchParams(window.location.search).get("chat_id") ||
        sessions[0]?.id;
      if (targetId) activateChat(targetId);
    } catch (error) {
      if (error.message !== "Session expired") {
        console.error(error);
      }
    }
  }

  dom.newChatBtn.addEventListener("click", async () => {
    await saveCurrentChatToBackend();
    activeRagSessionPath = null;
    dom.chatInput.placeholder = "Ask a question or type /clear...";
    const newId = String(Date.now());
    sessions.unshift({ id: newId, name: "New Chat", html: "", isNew: true });
    activateChat(newId);
  });

  dom.chatList.addEventListener("click", async (e) => {
    const li = e.target.closest("li");
    if (!li) return;
    const clickedChatId = li.dataset.id;
    if (e.target.closest(".delete-chat-btn")) {
      if (confirm("Are you sure you want to permanently delete this chat?")) {
        try {
          await authorizedFetch(`${API_BASE_URL}/api/chats/${clickedChatId}`, {
            method: "DELETE",
          });
          sessions = sessions.filter((s) => s.id !== clickedChatId);
          if (currentId === clickedChatId) {
            const newActiveId = sessions[0]?.id;
            if (newActiveId) {
              activateChat(newActiveId);
            } else {
              dom.newChatBtn.click();
            }
          } else {
            renderChatList();
          }
        } catch (error) {
          if (error.message !== "Session expired") {
            alert("Could not delete chat.");
          }
        }
      }
    } else if (clickedChatId !== currentId) {
      await saveCurrentChatToBackend();
      activateChat(clickedChatId);
    }
  });

  dom.exitBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    await saveCurrentChatToBackend();
    window.location.href = "./MainHomePage.html";
  });
  dom.themeToggleBtn.addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark-mode");
    localStorage.setItem("theme", isDark ? "dark" : "light");
  });
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden") {
      saveCurrentChatToBackend();
    }
  });
  function applyTheme() {
    if (localStorage.getItem("theme") === "dark") {
      document.body.classList.add("dark-mode");
    }
  }

  applyTheme();
  initializePage();
});
