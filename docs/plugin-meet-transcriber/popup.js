/* ARVEX Meet Transcriber — popup.js
 * Conversa com o content script da aba do Meet via chrome.tabs.sendMessage. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let lastText = "";

  function withTab(cb) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (!tab || !/^https:\/\/meet\.google\.com\//.test(tab.url || "")) {
        $("status").innerHTML = "Abra uma aba do <b>Google Meet</b> para usar.";
        return;
      }
      cb(tab.id);
    });
  }

  function send(tabId, cmd, cb) {
    chrome.tabs.sendMessage(tabId, { cmd }, (resp) => {
      if (chrome.runtime.lastError) { $("status").textContent = "Recarregue a aba do Meet."; return; }
      cb && cb(resp);
    });
  }

  function refresh() {
    withTab((tabId) => {
      send(tabId, "status", (r) => {
        if (!r) return;
        lastText = r.text || "";
        $("status").innerHTML = (r.capturing ? "<b>● Gravando</b>" : "Parado") + " · <b>" + r.count + "</b> linhas";
        $("toggle").textContent = r.capturing ? "■ Parar transcrição" : "▶ Iniciar transcrição";
        $("toggle").dataset.on = r.capturing ? "1" : "0";
      });
    });
  }

  $("toggle").addEventListener("click", () => withTab((tabId) =>
    send(tabId, $("toggle").dataset.on === "1" ? "stop" : "start", () => setTimeout(refresh, 200))));
  $("copy").addEventListener("click", () => {
    if (!lastText) return;
    navigator.clipboard.writeText(lastText).then(() => { $("status").textContent = "Copiado!"; setTimeout(refresh, 800); });
  });
  $("download").addEventListener("click", () => {
    if (!lastText) { $("status").textContent = "Nada pra baixar ainda."; return; }
    const blob = new Blob([lastText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "transcricao-meet.txt"; a.click();
    URL.revokeObjectURL(url);
  });
  $("clear").addEventListener("click", () => withTab((tabId) => send(tabId, "clear", () => setTimeout(refresh, 200))));

  // ---- e-mail do closer (CRM) + seu nome — salvos em chrome.storage.local ----
  try {
    chrome.storage.local.get(["arvex_closer_email", "arvex_self_name"], (r) => {
      if (r && r.arvex_closer_email) $("email").value = r.arvex_closer_email;
      if (r && r.arvex_self_name) $("selfname").value = r.arvex_self_name;
    });
    $("email").addEventListener("input", () => {
      chrome.storage.local.set({ arvex_closer_email: $("email").value.trim() });
    });
    $("selfname").addEventListener("input", () => {
      chrome.storage.local.set({ arvex_self_name: $("selfname").value.trim() });
    });
  } catch (e) {}

  refresh();
})();
