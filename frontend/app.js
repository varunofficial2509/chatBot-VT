(() => {
  const messagesEl = document.getElementById("messages");
  const emptyState = document.getElementById("empty-state");
  const composer = document.getElementById("composer");
  const input = document.getElementById("question-input");
  const sendButton = document.getElementById("send-button");

  let sessionId = null;

  function addMessage(role, text) {
    if (emptyState) emptyState.remove();
    const wrapper = document.createElement("div");
    wrapper.className = `message ${role}`;

    const label = document.createElement("div");
    label.className = "label";
    label.textContent = role === "user" ? "Recruiter" : "AI";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    wrapper.appendChild(label);
    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return bubble;
  }

  function addThinking() {
    const wrapper = document.createElement("div");
    wrapper.className = "message assistant";
    wrapper.id = "thinking-indicator";
    const bubble = document.createElement("div");
    bubble.className = "bubble thinking";
    bubble.textContent = "Thinking...";
    wrapper.appendChild(bubble);
    messagesEl.appendChild(wrapper);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function removeThinking() {
    const el = document.getElementById("thinking-indicator");
    if (el) el.remove();
  }

  async function sendMessage(message) {
    addMessage("user", message);
    addThinking();
    sendButton.disabled = true;

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      sessionId = data.session_id;
      removeThinking();
      addMessage("assistant", data.answer);
    } catch (err) {
      removeThinking();
      addMessage(
        "assistant",
        "Sorry, something went wrong reaching the server. Please try again."
      );
    } finally {
      sendButton.disabled = false;
    }
  }

  composer.addEventListener("submit", (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    input.value = "";
    sendMessage(message);
  });
})();
