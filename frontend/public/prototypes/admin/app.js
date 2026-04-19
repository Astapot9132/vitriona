const state = {
  view: "users",
  usersQuery: "",
  domainsQuery: "",
  users: [
    { id: "u1", name: "Анна Петрова", email: "anna.petrov@example.com", showcasesCount: 3, status: "Активен" },
    { id: "u2", name: "Иван Сидоров", email: "ivan.sidorov@example.com", showcasesCount: 12, status: "Активен" },
    { id: "u3", name: "Мария Смирнова", email: "m.smirnova@example.com", showcasesCount: 1, status: "Активен" },
    { id: "u4", name: "Алексей Кузнецов", email: "alex.kuznetsov@example.com", showcasesCount: 7, status: "Активен" },
    { id: "u5", name: "Екатерина Орлова", email: "orlovak@example.com", showcasesCount: 0, status: "Активен" }
  ],
  domainRequests: [
    {
      id: "d1",
      userName: "Анна Петрова",
      userEmail: "anna.petrov@example.com",
      requestedAt: "18.03.2026",
      domain: "example-anna.ru",
      status: "На рассмотрении"
    },
    {
      id: "d2",
      userName: "Иван Сидоров",
      userEmail: "ivan.sidorov@example.com",
      requestedAt: "17.03.2026",
      domain: "sidorov-click.site",
      status: "Одобрено"
    },
    {
      id: "d3",
      userName: "Мария Смирнова",
      userEmail: "m.smirnova@example.com",
      requestedAt: "16.03.2026",
      domain: "msmirnova.com",
      status: "На рассмотрении"
    },
    {
      id: "d4",
      userName: "Алексей Кузнецов",
      userEmail: "alex.kuznetsov@example.com",
      requestedAt: "15.03.2026",
      domain: "kuznetsov-park.ru",
      status: "Отказано"
    },
    {
      id: "d5",
      userName: "Екатерина Орлова",
      userEmail: "orlovak@example.com",
      requestedAt: "14.03.2026",
      domain: "orlovak.link",
      status: "На рассмотрении"
    }
  ]
};

function $(id) {
  return document.getElementById(id);
}

function showTopToast(text) {
  const el = $("toast-top");
  if (!el) return;
  el.textContent = text;
  el.classList.remove("hidden");
  window.clearTimeout(showTopToast._t);
  showTopToast._t = window.setTimeout(() => el.classList.add("hidden"), 2200);
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

function normalize(s) {
  return String(s || "").trim().toLowerCase();
}

function renderUsers() {
  const tbody = $("users-body");
  if (!tbody) return;
  tbody.innerHTML = "";
  const q = normalize(state.usersQuery);
  const list = state.users.filter(u => {
    if (!q) return true;
    return normalize(u.name).includes(q) || normalize(u.email).includes(q);
  });

  if (!list.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 6;
    td.className = "empty-row";
    td.style.padding = "14px 14px";
    td.textContent = "Нет результатов.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  list.forEach(u => {
    const tr = document.createElement("tr");
    const tdName = document.createElement("td");
    tdName.textContent = u.name;
    const tdEmail = document.createElement("td");
    tdEmail.textContent = u.email;
    const tdCount = document.createElement("td");
    tdCount.textContent = String(u.showcasesCount);

    const tdStatus = document.createElement("td");
    tdStatus.textContent = u.status === "Бан" ? "Бан" : "Активен";

    const tdBan = document.createElement("td");
    const banBtn = document.createElement("button");
    banBtn.type = "button";
    const isBanned = u.status === "Бан";
    banBtn.className = isBanned ? "btn-cell muted" : "btn-cell danger";
    banBtn.textContent = isBanned ? "Снять бан" : "Забанить";
    banBtn.addEventListener("click", () => {
      u.status = isBanned ? "Активен" : "Бан";
      renderUsers();
      showTopToast(isBanned ? "Бан снят (прототип)" : "Пользователь забанен (прототип)");
    });
    tdBan.appendChild(banBtn);

    const tdLogin = document.createElement("td");
    const loginBtn = document.createElement("button");
    loginBtn.type = "button";
    loginBtn.className = "btn-cell";
    loginBtn.textContent = "Войти в кабинет";
    loginBtn.addEventListener("click", () => {
      showTopToast("Вход в кабинет (прототип)");
    });
    tdLogin.appendChild(loginBtn);

    tr.append(tdName, tdEmail, tdCount, tdStatus, tdBan, tdLogin);
    tbody.appendChild(tr);
  });
}

function renderDomains() {
  const tbody = $("domains-body");
  if (!tbody) return;
  tbody.innerHTML = "";
  const q = normalize(state.domainsQuery);
  const list = state.domainRequests.filter(r => {
    if (!q) return true;
    return normalize(r.userName).includes(q) || normalize(r.userEmail).includes(q);
  });

  if (!list.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 7;
    td.className = "empty-row";
    td.style.padding = "14px 14px";
    td.textContent = "Нет результатов.";
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  list.forEach(r => {
    const tr = document.createElement("tr");
    const tdName = document.createElement("td");
    tdName.textContent = r.userName;
    const tdEmail = document.createElement("td");
    tdEmail.textContent = r.userEmail;
    const tdDate = document.createElement("td");
    tdDate.textContent = r.requestedAt;
    const tdDomain = document.createElement("td");
    tdDomain.textContent = r.domain;
    const tdStatus = document.createElement("td");
    tdStatus.textContent = r.status;

    const tdApprove = document.createElement("td");
    const tdReject = document.createElement("td");
    if (r.status === "На рассмотрении") {
      const okBtn = document.createElement("button");
      okBtn.type = "button";
      okBtn.className = "btn-cell success";
      okBtn.textContent = "Одобрить";
      okBtn.addEventListener("click", () => {
        r.status = "Одобрено";
        renderDomains();
        showTopToast("Заявка одобрена (прототип)");
      });
      tdApprove.appendChild(okBtn);

      const noBtn = document.createElement("button");
      noBtn.type = "button";
      noBtn.className = "btn-cell danger";
      noBtn.textContent = "Отказать";
      noBtn.addEventListener("click", () => {
        r.status = "Отказано";
        renderDomains();
        showTopToast("Заявка отклонена (прототип)");
      });
      tdReject.appendChild(noBtn);
    }

    tr.append(tdName, tdEmail, tdDate, tdDomain, tdStatus, tdApprove, tdReject);
    tbody.appendChild(tr);
  });
}

function setView(nextView) {
  state.view = nextView;
  const views = ["users", "domain-parking"];
  views.forEach(key => {
    const el = $(`view-${key}`);
    if (!el) return;
    el.classList.toggle("hidden", key !== nextView);
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
      const v = btn.getAttribute("data-view") || "users";
      setView(v);
    });
  });

  const usersSearch = $("users-search");
  if (usersSearch) {
    usersSearch.addEventListener("input", () => {
      state.usersQuery = usersSearch.value;
      renderUsers();
    });
  }

  const domainsSearch = $("domains-search");
  if (domainsSearch) {
    domainsSearch.addEventListener("input", () => {
      state.domainsQuery = domainsSearch.value;
      renderDomains();
    });
  }

  renderUsers();
  renderDomains();
  setView(state.view);
});

