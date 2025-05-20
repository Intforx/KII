const chatInput = document.getElementById('chat-input');
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const sidebar = document.getElementById('sidebar');
const authStatus = document.getElementById('auth-status');
const chatList = document.getElementById('chat-list');
const sendButton = document.getElementById('send-button');

let isLoggedIn = false;
let username = "";
let isGenerating = false;
let generationTimeout;
let conversations = [];

function updateAuthUI() {
  authStatus.textContent = isLoggedIn ? username : "Anmelden";
}

authStatus.addEventListener('click', () => {
  if (!isLoggedIn) {
    const name = prompt("Vorname:");
    const surname = prompt("Nachname:");
    let email = prompt("E-Mail:");
    while (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      email = prompt("Ungültige E-Mail. Bitte gib eine gültige Adresse ein:");
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';

    wrapper.innerHTML = `
      <div class="bg-white p-6 rounded-lg shadow-md relative">
        <label class="block mb-2 text-sm font-medium">Passwort:</label>
        <div class="flex items-center border rounded px-2">
          <input id="password-field" type="password" class="flex-1 p-2 outline-none" />
          <button id="toggle-password" type="button" class="ml-2 text-gray-500">
            👁️
          </button>
        </div>
        <button id="submit-login" class="mt-4 bg-primary text-white px-4 py-2 rounded">Login</button>
      </div>
    `;
    document.body.appendChild(wrapper);

    document.getElementById('toggle-password').addEventListener('click', () => {
      const input = document.getElementById('password-field');
      const btn = document.getElementById('toggle-password');
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
      } else {
        input.type = 'password';
        btn.textContent = '👁️';
      }
    });

    document.getElementById('submit-login').addEventListener('click', () => {
      const password = document.getElementById('password-field').value;
      if (!password) return alert("Bitte gib ein Passwort ein!");
      username = name + " " + surname;
      isLoggedIn = true;
      updateAuthUI();
      wrapper.remove();
    });
  }
});

function toggleSidebar() {
  if (sidebar.classList.contains('w-64')) {
    sidebar.classList.remove('w-64', 'p-4');
    sidebar.classList.add('w-0');
  } else {
    sidebar.classList.remove('w-0');
    sidebar.classList.add('w-64', 'p-4');
  }
}

function sendMessage(e) {
  e.preventDefault();
  if (isGenerating) {
    cancelGeneration();
    return;
  }

  const text = chatInput.value.trim();
  if (!text) return;

  const userBubble = document.createElement('div');
  userBubble.className = 'flex justify-end';
  userBubble.innerHTML = `<div class="bg-blue-100 p-4 rounded-xl max-w-2xl shadow">${text}</div>`;
  chatWindow.appendChild(userBubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  chatInput.value = '';

  startGeneration();
}

function startGeneration() {
  isGenerating = true;
  sendButton.innerHTML = '◼️';

  if (!isLoggedIn) showAdPopup();

  generationTimeout = setTimeout(() => {
    const botBubble = document.createElement('div');
    botBubble.className = 'flex';
    const botText = "Das ist eine Beispielantwort über Kunstgeschichte.";
    const botContent = document.createElement('div');
    botContent.className = "bg-gray-200 p-4 rounded-xl max-w-2xl shadow whitespace-pre-wrap";
    botBubble.appendChild(botContent);
    chatWindow.appendChild(botBubble);

    let index = 0;
    const interval = setInterval(() => {
      if (index < botText.length) {
        botContent.textContent += botText[index++];
        chatWindow.scrollTop = chatWindow.scrollHeight;
      } else {
        clearInterval(interval);
        stopGeneration();
      }
    }, 30);
  }, 500);
}

function stopGeneration() {
  isGenerating = false;
  sendButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="white" viewBox="0 0 24 24" stroke="black">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7" />
  </svg>`;
}

function cancelGeneration() {
  clearTimeout(generationTimeout);
  stopGeneration();
}

function newChat() {
  const previousContent = chatWindow.innerHTML;
  if (previousContent.trim() !== '') {
    conversations.push(previousContent);
  }
  chatWindow.innerHTML = '';

  const index = conversations.length;
  const item = document.createElement('div');
  const now = new Date().toLocaleTimeString();
  item.textContent = `Gespräch von ${now}`;
  item.className = 'p-2 rounded hover:bg-gray-200 cursor-pointer';
  item.dataset.index = index;

  item.addEventListener('click', () => {
    document.querySelectorAll('#chat-list > div').forEach(el => el.classList.remove('active-chat'));
    item.classList.add('active-chat');
    chatWindow.innerHTML = conversations[index] || '';
  });

  chatList.appendChild(item);
  document.querySelectorAll('#chat-list > div').forEach(el => el.classList.remove('active-chat'));
  item.classList.add('active-chat');
}

function showAdPopup() {
  const popup = document.createElement('div');
  popup.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
  const inner = document.createElement('div');
  inner.className = 'bg-white p-8 rounded-lg relative text-center max-w-md';
  inner.innerHTML = '<p class="mb-4">Registriere dich, um unbegrenzt zu chatten!</p>';
  const closeBtn = document.createElement('button');
  closeBtn.textContent = '✕';
  closeBtn.className = 'absolute top-2 right-2 text-gray-500 hidden';
  closeBtn.onclick = () => popup.remove();
  inner.appendChild(closeBtn);
  popup.appendChild(inner);
  document.body.appendChild(popup);
  setTimeout(() => closeBtn.classList.remove('hidden'), 30000);
}

chatInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

window.onload = () => {
  newChat();
  updateAuthUI();
};
