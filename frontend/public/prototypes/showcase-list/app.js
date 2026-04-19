const state = {
  view: "showcases",
  showcases: [
    {
      id: "13259",
      platform: {
        main: "1331923, 123",
        sub: "ID 1331923"
      },
      url: "example.sync.link"
    }
  ],
  domains: []
};

function $(id) {
  return document.getElementById(id);
}

function showToast(text) {
  showTopToast(text);
}

function showTopToast(text) {
  const el = $("toast-top");
  if (!el) return;
  el.textContent = text;
  el.classList.remove("hidden");
  window.clearTimeout(showTopToast._t);
  showTopToast._t = window.setTimeout(() => el.classList.add("hidden"), 2200);
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    showToast("Ссылка скопирована");
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
    showToast("Ссылка скопирована");
  }
}

function cloneShowcase(sc) {
  const nextId = String((Number(sc.id) || 0) + 1);
  return {
    ...sc,
    id: nextId,
    platform: {
      ...sc.platform,
      sub: sc.platform?.sub ? sc.platform.sub.replace(/\bID\s+\d+\b/, `ID ${nextId}`) : `ID ${nextId}`
    }
  };
}

function openModal(title, bodyHtml) {
  const modal = $("modal");
  const titleEl = $("modal-title");
  const bodyEl = $("modal-body");
  if (!modal || !titleEl || !bodyEl) return;
  titleEl.textContent = title;
  bodyEl.innerHTML = bodyHtml;
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
}

function closeModal() {
  const modal = $("modal");
  if (!modal) return;
  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
}

function render() {
  const tbody = $("showcases-body");
  const empty = $("empty-state");
  if (!tbody || !empty) return;

  tbody.innerHTML = "";

  if (!state.showcases.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  state.showcases.forEach(sc => {
    const tr = document.createElement("tr");

    const tdId = document.createElement("td");
    tdId.textContent = sc.id;

    const tdPlatform = document.createElement("td");
    const main = document.createElement("div");
    main.className = "platform-main";
    main.textContent = sc.platform.main;
    const sub = document.createElement("div");
    sub.className = "platform-sub";
    sub.textContent = sc.platform.sub;
    tdPlatform.append(main, sub);

    const tdUrl = document.createElement("td");
    const a = document.createElement("a");
    a.className = "url-link";
    a.href = `https://${sc.url}`;
    a.target = "_blank";
    a.rel = "noreferrer";
    a.textContent = sc.url;
    tdUrl.appendChild(a);

    const tdActions = document.createElement("td");
    tdActions.className = "col-actions";
    const actions = document.createElement("div");
    actions.className = "actions";

    const btnView = document.createElement("button");
    btnView.type = "button";
    btnView.className = "btn-secondary";
    btnView.textContent = "Посмотреть";
    btnView.addEventListener("click", () => {
      showToast("Открытие витрины (прототип)");
    });

    const btnCopy = document.createElement("button");
    btnCopy.type = "button";
    btnCopy.className = "icon-btn";
    btnCopy.title = "Скопировать витрину";
    btnCopy.innerHTML = '<span class="icon icon-copy" aria-hidden="true"></span>';
    btnCopy.addEventListener("click", () => {
      state.showcases.unshift(cloneShowcase(sc));
      render();
      showToast("Витрина скопирована");
    });

    const btnStats = document.createElement("button");
    btnStats.type = "button";
    btnStats.className = "icon-btn";
    btnStats.title = "Посмотреть статистику";
    btnStats.innerHTML = '<span class="icon icon-chart" aria-hidden="true"></span>';
    btnStats.addEventListener("click", () => {
      openModal(
        "Статистика витрины",
        `<div style="color:#6b7280;margin-bottom:10px;">Прототип: данные фиктивные</div>
         <div style="display:grid;gap:8px;">
           <div><strong>Переходы:</strong> 1 284</div>
           <div><strong>Клики по CTA:</strong> 392</div>
           <div><strong>CR:</strong> 30.5%</div>
         </div>`
      );
    });

    const btnEdit = document.createElement("button");
    btnEdit.type = "button";
    btnEdit.className = "icon-btn";
    btnEdit.title = "Редактировать";
    btnEdit.innerHTML = '<span class="icon icon-edit" aria-hidden="true"></span>';
    btnEdit.addEventListener("click", () => {
      showToast("Редактирование (прототип)");
    });

    const btnDelete = document.createElement("button");
    btnDelete.type = "button";
    btnDelete.className = "icon-btn danger";
    btnDelete.title = "Удалить";
    btnDelete.innerHTML = '<span class="icon icon-trash" aria-hidden="true"></span>';
    btnDelete.addEventListener("click", () => {
      const ok = window.confirm("Удалить витрину? (прототип)");
      if (!ok) return;
      state.showcases = state.showcases.filter(s => s !== sc);
      render();
      showToast("Витрина удалена");
    });

    actions.append(btnView, btnCopy, btnStats, btnEdit, btnDelete);
    tdActions.appendChild(actions);

    tr.append(tdId, tdPlatform, tdUrl, tdActions);
    tbody.appendChild(tr);
  });
}

function renderDomains() {
  const tbody = $("domains-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (!state.domains.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 7;
    td.style.padding = "14px 14px";
    td.style.color = "#6b7280";
    td.style.fontSize = "13px";
    td.textContent = "Нет результатов.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
}

function setView(nextView) {
  state.view = nextView;
  const views = [
    { id: "view-showcases", key: "showcases" },
    { id: "view-domain-parking", key: "domain-parking" }
  ];
  views.forEach(v => {
    const el = $(v.id);
    if (!el) return;
    el.classList.toggle("hidden", v.key !== nextView);
  });
  document.querySelectorAll(".sidebar-nav .nav-item[data-view]").forEach(btn => {
    const isActive = btn.getAttribute("data-view") === nextView;
    btn.classList.toggle("is-active", isActive);
    if (isActive) btn.setAttribute("aria-current", "page");
    else btn.removeAttribute("aria-current");
  });
}

document.addEventListener("click", e => {
  const t = e.target;
  if (!(t instanceof HTMLElement)) return;
  if (t.dataset.close === "true") closeModal();
  if (t.closest?.("[data-close='true']")) closeModal();
});

document.addEventListener("keydown", e => {
  if (e.key === "Escape") closeModal();
});

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".sidebar-nav .nav-item[data-view]").forEach(btn => {
    btn.addEventListener("click", () => {
      setView(btn.getAttribute("data-view") || "showcases");
    });
  });

  const saveBtn = $("domain-save");
  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      const systemSelect = $("system-domain-select");
      const webmaster = $("webmaster-domain-input");
      const confirm = $("domain-confirm");
      const sysOk = !!(systemSelect && systemSelect.value.trim());
      const webOk = !!(webmaster && webmaster.value.trim());
      const confOk = !!(confirm && confirm.checked);
      if (!sysOk || !webOk || !confOk) {
        showTopToast("Заполните обязательные поля и подтвердите владение доменом");
        return;
      }
      showToast("Домен сохранён (прототип)");
      setView("showcases");
    });
  }

  const createBtn = $("create-showcase");
  if (createBtn) {
    createBtn.addEventListener("click", () => {
      const id = String(Math.floor(10000 + Math.random() * 89999));
      state.showcases.unshift({
        id,
        platform: { main: "1331923, 123", sub: `ID ${id}` },
        url: "example.sync.link"
      });
      render();
      showToast("Витрина создана (прототип)");
    });
  }

  render();
  renderDomains();
  setView(state.view);
});

