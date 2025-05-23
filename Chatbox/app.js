// Elementreferenzen
const chatInput = document.getElementById('chat-input');
const chatWindow = document.getElementById('chat-window');
const chatForm = document.getElementById('chat-form');
const authStatus = document.getElementById('auth-status');
const chatList = document.getElementById('chat-list');
const sendButton = document.getElementById('send-button');
const overlayMenu = document.getElementById('overlay-menu');

// Zustände
let isLoggedIn = false;
let username = "";
let isGenerating = false;
let generationTimeout;
let conversations = [];

// UI aktualisieren je nach Login-Status
function updateAuthUI() {
  authStatus.textContent = isLoggedIn ? username : "Anmelden";
}

// Login-Logik beim Klicken auf Auth-Status
authStatus.addEventListener('click', () => {
  if (!isLoggedIn) {
    const name = prompt("Vorname:");
    const surname = prompt("Nachname:");
    let email = prompt("E-Mail:");
    while (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      email = prompt("Ungültige E-Mail. Bitte gib eine gültige Adresse ein:");
    }

    // Passwortabfrage mit Overlay
    const wrapper = document.createElement('div');
    wrapper.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    wrapper.innerHTML = `
      <div class="bg-white p-6 rounded-lg shadow-md relative">
        <label class="block mb-2 text-sm font-medium">Passwort:</label>
        <div class="flex items-center border rounded px-2">
          <input id="password-field" type="password" class="flex-1 p-2 outline-none" />
          <button id="toggle-password" type="button" class="ml-2 text-gray-500">👁️</button>
        </div>
        <button id="submit-login" class="mt-4 bg-primary text-white px-4 py-2 rounded">Login</button>
      </div>
    `;
    document.body.appendChild(wrapper);

    // Passwort anzeigen/verbergen
    document.getElementById('toggle-password').addEventListener('click', () => {
      const input = document.getElementById('password-field');
      const btn = document.getElementById('toggle-password');
      input.type = input.type === 'password' ? 'text' : 'password';
      btn.textContent = input.type === 'password' ? '👁️' : '🙈';
    });

    // Login durchführen
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

// Overlay-Sidebar ein-/ausblenden
function toggleOverlay() {
  overlayMenu.classList.toggle('-translate-x-full');
}

// Neues Gespräch starten
function newChat() {
  const previousContent = chatWindow.innerHTML;
  if (previousContent.trim() !== '') {
    conversations.push(previousContent);
  }
  chatWindow.innerHTML = '';

  const index = conversations.length;
  const now = new Date().toLocaleTimeString();
  const item = document.createElement('div');
  item.textContent = `Gespräch von ${now}`;
  item.className = 'p-2 rounded hover:bg-gray-200 cursor-pointer';
  item.dataset.index = index;

  // Klick auf gespeichertes Gespräch
  item.addEventListener('click', () => {
    document.querySelectorAll('#chat-list > div').forEach(el => el.classList.remove('active-chat'));
    item.classList.add('active-chat');
    chatWindow.innerHTML = conversations[index] || '';
  });

  chatList.appendChild(item);
  document.querySelectorAll('#chat-list > div').forEach(el => el.classList.remove('active-chat'));
  item.classList.add('active-chat');
}

// Nachricht senden
function sendMessage(e) {
  e.preventDefault();
  if (isGenerating) {
    cancelGeneration();
    return;
  }

  const text = chatInput.value.trim();
  if (!text) return;

  // Nutzer-Blase anzeigen
  const userBubble = document.createElement('div');
  userBubble.className = 'flex justify-end';
  userBubble.innerHTML = `<div class="bg-blue-100 p-4 rounded-xl max-w-2xl shadow">${text}</div>`;
  chatWindow.appendChild(userBubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  chatInput.value = '';

  // Antwort generieren
  startGeneration();
}

// Botantwort mit Animation simulieren
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

    // Zeichenweise Textanzeige
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

// Beende die Generierung
function stopGeneration() {
  isGenerating = false;
  sendButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="white" viewBox="0 0 24 24" stroke="black">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7" />
  </svg>`;
}

// Generierung abbrechen
function cancelGeneration() {
  clearTimeout(generationTimeout);
  stopGeneration();
}

// Werbung für Gäste anzeigen
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

  // Schließen erst nach 30 Sekunden möglich
  setTimeout(() => closeBtn.classList.remove('hidden'), 30000);
}

// Enter + Shift Verhalten steuern
chatInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

// Initialisierung beim Laden
window.onload = () => {
  newChat();
  updateAuthUI();
};
