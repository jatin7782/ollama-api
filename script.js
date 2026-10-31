// Replace this with the public URL of your FastAPI server.
// Example:
// const API_URL = "https://xxxx-8000.app.github.dev";
const API_URL = "https://YOUR-CODESPACE-URL.app.github.dev";

const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const status = document.getElementById("status");

let conversation = [];

function addMessage(text, type) {
  const message = document.createElement("div");
  message.className = `message ${type}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = type === "user" ? "YOU" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  message.appendChild(avatar);
  message.appendChild(bubble);
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;

  return bubble;
}

async function checkServer() {
  if (API_URL.includes("YOUR-CODESPACE-URL")) {
    status.textContent = "Set API URL";
    status.className = "status error";
    return;
  }

  try {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) throw new Error("Server unavailable");

    const data = await response.json();

    if (data.ollama) {
      status.textContent = "AI Online";
      status.className = "status online";
    } else {
      status.textContent = "Ollama Offline";
      status.className = "status error";
    }
  } catch {
    status.textContent = "Server Offline";
    status.className = "status error";
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const text = input.value.trim();
  if (!text) return;

  const welcome = document.querySelector(".welcome");
  if (welcome) welcome.remove();

  addMessage(text, "user");

  conversation.push({
    role: "user",
    content: text
  });

  input.value = "";
  input.style.height = "auto";

  sendButton.disabled = true;
  sendButton.textContent = "Thinking...";

  const aiBubble = addMessage("Thinking...", "ai");

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: text,
        history: conversation.slice(0, -1)
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "AI request failed");
    }

    aiBubble.textContent = data.answer;

    conversation.push({
      role: "assistant",
      content: data.answer
    });
  } catch (error) {
    console.error(error);
    aiBubble.textContent = "Error: " + error.message;
  }

  sendButton.disabled = false;
  sendButton.textContent = "Send";
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 150)}px`;
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

checkServer();
