/**
 * PocketSage — Frontend Application
 * Gère l'UI, les appels API vers FastAPI, et l'état de l'app.
 */

const API_BASE = window.location.origin;
const USER_ID = "user_demo";

let currentLang = "en";
let currentView = "dashboard";

// ── NAVIGATION ──
document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    const view = btn.dataset.view;
    switchView(view);
  });
});

function switchView(view) {
  // Nav items
  document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
  document.querySelector(`[data-view="${view}"]`).classList.add("active");

  // Views
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.getElementById(`view-${view}`).classList.add("active");

  currentView = view;

  // Titres
  const titles = {
    dashboard: { title: "Dashboard", subtitle: "Vue d'ensemble de tes finances" },
    chat: { title: "Assistant", subtitle: "Parle à PocketSage" },
    transactions: { title: "Transactions", subtitle: "Historique complet" },
    alerts: { title: "Alertes", subtitle: "Situation et prévisions" },
  };

  const t = titles[view] || titles.dashboard;
  document.getElementById("page-title").textContent = t.title;
  document.getElementById("page-subtitle").textContent = t.subtitle;

  // Charger les données selon la vue
  if (view === "dashboard") loadDashboard();
  if (view === "transactions") loadTransactions();
  if (view === "alerts") loadAlerts();
  if (view === "chat") initChat();
}

// ── LANGUE ──
document.querySelectorAll(".lang-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentLang = btn.dataset.lang;
  });
});

// ── DASHBOARD ──
async function loadDashboard() {
  try {
    const res = await fetch(`${API_BASE}/summary/${USER_ID}`);
    const data = await res.json();

    document.getElementById("stat-revenus").textContent =
      formatCFA(data.revenus);
    document.getElementById("stat-depenses").textContent =
      formatCFA(data.depenses);
    document.getElementById("stat-solde").textContent =
      formatCFA(data.solde);
    document.getElementById("stat-transactions").textContent =
      data.nb_transactions;

    // Transactions récentes
    loadRecentTransactions();

    // Alertes
    checkAlertBanner();

  } catch (e) {
    console.error("Dashboard error:", e);
  }
}

async function loadRecentTransactions() {
  try {
    const res = await fetch(`${API_BASE}/transactions/${USER_ID}?limit=5`);
    const data = await res.json();
    const list = document.getElementById("recent-list");

    if (!data.transactions || data.transactions.length === 0) {
      list.innerHTML = `<p class="empty-state">Aucune transaction pour l'instant.<br/>Commence à parler à ton assistant !</p>`;
      return;
    }

    list.innerHTML = data.transactions.slice(-5).reverse().map(tx => `
      <div class="tx-item">
        <div class="tx-left">
          <div class="tx-icon ${tx.type}">
            <span class="material-symbols-outlined">${tx.type === "depense" ? "paid" : "savings"}</span>
          </div>
          <div>
            <p class="tx-desc">${tx.description || tx.categorie}</p>
            <p class="tx-cat">${tx.categorie} • ${tx.source || "cash"}</p>
          </div>
        </div>
        <span class="tx-amount ${tx.type}">
          ${tx.type === "depense" ? "-" : "+"}${formatCFA(tx.montant)}
        </span>
      </div>
    `).join("");

  } catch (e) {
    console.error("Transactions error:", e);
  }
}

async function checkAlertBanner() {
  try {
    const res = await fetch(`${API_BASE}/alerts/${USER_ID}?lang=${currentLang}`);
    const data = await res.json();

    if (data.level && data.level !== "green" && data.message) {
      const banner = document.getElementById("alert-banner");
      const icons = { yellow: "warning_amber", red: "error", green: "check_circle" };
      document.getElementById("alert-icon").innerHTML = `<span class="material-symbols-outlined">${icons[data.level] || "warning_amber"}</span>`;
      document.getElementById("alert-message").textContent = data.message;
      banner.style.display = "flex";
      document.getElementById("alert-badge").innerHTML = `<span class="material-symbols-outlined">notifications</span>`;
    }
  } catch (e) {
    console.error("Alert error:", e);
  }
}

// ── CHAT ──
let chatInitialized = false;

function initChat() {
  if (chatInitialized) return;
  chatInitialized = true;

  const messages = document.getElementById("chat-messages");
  const welcomes = {
    fr: "👋 Bonjour ! Je suis **PocketSage**. Dis-moi ce que tu as dépensé ou reçu aujourd'hui !",
    en: "👋 Hello! I'm **PocketSage**. Tell me what you spent or received today!",
    fon: "👋 Kudo! Un nyɔnu **PocketSage**. Ɖɔ nǔ e a sɔ́ dó alɔ mɛ é!",
    yo: "👋 Ẹ káàbọ̀! Mo jẹ **PocketSage**. Sọ fún mi ohun tí o nà tàbí gba lónìí!",
  };

  addAgentMessage(welcomes[currentLang] || welcomes.fr, "Orchestrator");

  // Enter key
  document.getElementById("chat-input").addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
  });
}

function addAgentMessage(text, agent = "PocketSage", extra = null) {
  const messages = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "message agent";

  let extraHTML = "";
  if (extra && extra.transaction_saved) {
    const tx = extra.transaction;
    extraHTML = `
      <div class="tx-saved-badge">
        ✅ ${tx.type === "depense" ? "Dépense" : "Revenu"} enregistré(e) :
        ${formatCFA(tx.montant)} • ${tx.categorie} • ${tx.source}
      </div>
    `;
  }

  div.innerHTML = `
    <div class="message-avatar"><span class="material-symbols-outlined">savings</span></div>
    <div>
      <div class="agent-badge">${agent}</div>
      <div class="message-bubble">${text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</div>
      ${extraHTML}
      <p class="message-meta">${new Date().toLocaleTimeString()}</p>
    </div>
  `;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function addUserMessage(text) {
  const messages = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "message user";
  div.innerHTML = `
    <div class="message-avatar"><span class="material-symbols-outlined">account_circle</span></div>
    <div>
      <div class="message-bubble">${text}</div>
      <p class="message-meta">${new Date().toLocaleTimeString()}</p>
    </div>
  `;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function addTypingIndicator() {
  const messages = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "message agent";
  div.id = "typing";
  div.innerHTML = `
    <div class="message-avatar"><span class="material-symbols-outlined">savings</span></div>
    <div class="message-bubble">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTypingIndicator() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}

async function sendMessage() {
  const input = document.getElementById("chat-input");
  const btn = document.getElementById("send-btn");
  const text = input.value.trim();
  if (!text) return;

  // Afficher message utilisateur
  addUserMessage(text);
  input.value = "";
  btn.disabled = true;

  // Cacher les suggestions
  document.getElementById("chat-suggestions").style.display = "none";

  // Typing indicator
  addTypingIndicator();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: USER_ID,
        message: text,
        lang: currentLang,
      }),
    });

    const data = await res.json();
    removeTypingIndicator();

    addAgentMessage(
      data.response,
      data.agent_used || "PocketSage",
      data.data
    );

    // Rafraîchir le dashboard si transaction sauvegardée
    if (data.data && data.data.transaction_saved) {
      setTimeout(loadDashboard, 500);
    }

  } catch (e) {
    removeTypingIndicator();
    addAgentMessage("❌ Erreur de connexion. Vérifie que le serveur tourne.", "Système");
  }

  btn.disabled = false;
  input.focus();
}

function sendSuggestion(btn) {
  document.getElementById("chat-input").value = btn.textContent;
  sendMessage();
}

// ── QUICK ACTIONS ──
function quickAction(type) {
  const messages = {
    depense: "J'ai fait une dépense",
    revenu: "J'ai reçu de l'argent",
    analyse: "Analyse mes dépenses ce mois",
    alerte: "Vais-je tenir jusqu'à la fin du mois ?",
  };
  switchView("chat");
  setTimeout(() => {
    document.getElementById("chat-input").value = messages[type] || "";
    document.getElementById("chat-input").focus();
  }, 100);
}

// ── TRANSACTIONS ──
async function loadTransactions() {
  const monthFilter = document.getElementById("month-filter").value;
  let url = `${API_BASE}/transactions/${USER_ID}`;
  if (monthFilter) url += `?month=${monthFilter}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById("transactions-tbody");

    if (!data.transactions || data.transactions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Aucune transaction</td></tr>`;
      return;
    }

    tbody.innerHTML = [...data.transactions].reverse().map(tx => `
      <tr>
        <td>${formatDate(tx.date)}</td>
        <td>${tx.description || "-"}</td>
        <td>${tx.categorie || "-"}</td>
        <td><span class="badge ${tx.source || 'cash'}">${tx.source || "cash"}</span></td>
        <td><span class="badge ${tx.type}">${tx.type}</span></td>
        <td class="tx-amount ${tx.type}">
          ${tx.type === "depense" ? "-" : "+"}${formatCFA(tx.montant)}
        </td>
      </tr>
    `).join("");

  } catch (e) {
    console.error("Load transactions error:", e);
  }
}

// ── ALERTS ──
async function loadAlerts() {
  try {
    const res = await fetch(`${API_BASE}/alerts/${USER_ID}?lang=${currentLang}`);
    const data = await res.json();
    const container = document.getElementById("alerts-container");

    const icons = { green: "check_circle", yellow: "warning_amber", red: "error" };
    const icon = icons[data.level] || "check_circle";

    let actionsHTML = "";
    if (data.actions && data.actions.length > 0) {
      actionsHTML = `
        <ul style="margin-top:12px; padding-left:20px; color: var(--text-muted); font-size:14px; line-height:2;">
          ${data.actions.map(a => `<li>${a}</li>`).join("")}
        </ul>
      `;
    }

    container.innerHTML = `
      <div class="alert-card ${data.level || 'green'}">
        <h3 style="font-size:16px; margin-bottom:8px;">
          <span class="material-symbols-outlined">${icon}</span> Situation financière du mois
        </h3>
        <p style="color: var(--text-muted); font-size:14px; line-height:1.7;">
          ${data.message || "Situation saine. Continue comme ça !"}
        </p>
        ${actionsHTML}
      </div>
    `;
  } catch (e) {
    document.getElementById("alerts-container").innerHTML =
      `<p class="empty-state">Impossible de charger les alertes.</p>`;
  }
}

// ── UTILS ──
function formatCFA(amount) {
  if (!amount && amount !== 0) return "0 FCFA";
  return new Intl.NumberFormat("fr-FR").format(Math.round(amount)) + " FCFA";
}

function formatDate(isoDate) {
  if (!isoDate) return "-";
  return new Date(isoDate).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

// ── INIT ──
window.addEventListener("load", () => {
  loadDashboard();

  // Définir le mois courant dans le filtre
  const today = new Date();
  const monthStr = today.toISOString().slice(0, 7);
  document.getElementById("month-filter").value = monthStr;
});