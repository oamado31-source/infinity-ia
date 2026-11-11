"use strict";

const token = window.PANEL_TOKEN;
const el = (id) => document.getElementById(id);
const select = (css) => document.querySelectorAll(css);
let snapshot = null;
let formInitialized = false;
let logKind = "job";
let logJob = "";
let lastLogText = null;
let toastHandle = null;
let updating = false;

function notify(message, error = false) {
  const box = el("toast");
  box.textContent = message;
  box.classList.toggle("error", error);
  box.hidden = false;
  if (toastHandle !== null) clearTimeout(toastHandle);
  toastHandle = setTimeout(() => { box.hidden = true; }, error ? 6500 : 3500);
}

async function api(url, data) {
  const options = {headers: {"X-Panel-Token": token}, cache: "no-store"};
  if (data !== undefined) {
    options.method = "POST";
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(data);
  }
  const response = await fetch(url, options);
  const json = await response.json();
  if (!response.ok || !json.ok) {
    throw new Error(json.error || "Operação não concluída.");
  }
  return json;
}

function text(id, value) {
  const target = el(id);
  if (target) target.textContent = value == null ? "—" : String(value);
}

function pill(id, label, className) {
  const target = el(id);
  target.className = "pill " + className;
  target.textContent = label;
}

function updateBranches(branches, current) {
  const box = el("branch-select");
  const oldValues = Array.from(box.options).map((o) => o.value).join("|");
  const newValues = branches.join("|");
  if (oldValues !== newValues) {
    const previous = box.value || current;
    box.replaceChildren();
    if (!branches.length) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "Execute Buscar atualizações";
      box.append(option);
    }
    branches.forEach((b) => {
      const option = document.createElement("option");
      option.value = b;
      option.textContent = b + (b === current ? " (atual)" : "");
      box.append(option);
    });
    box.value = branches.includes(previous) ? previous : (branches.includes(current) ? current : branches[0]);
  }
}

function fillConfig(cfg) {
  Object.entries({
    campaign: "campaign", manifest: "manifest", model: "model",
    ssh_host: "ssh-host", ssh_user: "ssh-user", ssh_key: "ssh-key"
  }).forEach(([name, id]) => { el(id).value = cfg[name] || ""; });
  formInitialized = true;
}

function formConfig() {
  return {
    campaign: el("campaign").value.trim(),
    manifest: el("manifest").value.trim(),
    ssh_host: el("ssh-host").value.trim(),
    ssh_user: el("ssh-user").value.trim(),
    ssh_key: el("ssh-key").value.trim(),
    model: el("model").value.trim()
  };
}

async function saveConfig() {
  const config = formConfig();
  const result = await api("/api/config", config);
  if (snapshot) snapshot.config = result.config;
  return result.config;
}

function renderStatus(data) {
  snapshot = data;
  if (!formInitialized) fillConfig(data.config);
  const g = data.git;
  const goodGit = !g.error;
  text("metric-branch", goodGit ? g.branch : "Erro Git");
  text("metric-clean", goodGit ? (g.dirty ? "Alterações locais detectadas" : "Cópia local sem alterações") : g.error);
  text("metric-commit", goodGit ? g.commit.split(" ")[0] : "—");
  text("git-detail", goodGit ? g.detail : g.error);
  pill("git-pill", goodGit ? (g.dirty ? "Modificações locais" : "Cópia limpa") : "Erro", goodGit ? (g.dirty ? "warn" : "good") : "bad");
  updateBranches(g.branches || [], g.branch);

  const busy = !!data.active;
  const last = data.jobs.length ? data.jobs[data.jobs.length - 1] : null;
  const running = data.service.running;
  const active = data.jobs.find((j) => j.id === data.active);
  text("metric-task", active ? "Executando" : (last ? (last.status === "ok" ? "Concluído" : last.status === "error" ? "Falha" : "Aguardando") : "Inativo"));
  text("metric-task-hint", active ? active.label : (last ? last.label : "Nenhuma tarefa em execução"));
  text("metric-lab", running ? "Em execução" : "Parado");
  text("metric-lab-hint", data.service.campaign || data.config.campaign);
  text("lab-state-text", running ? "Laboratório ativo" : "Serviço desligado");
  text("lab-state-detail", running ? "PID " + data.service.pid + " · " + data.service.campaign : "Pronto para iniciar com sua configuração");
  text("lab-pill", running ? "● Online" : "Serviço parado");
  pill("lab-pill", running ? "● Online" : "Serviço parado", running ? "good" : "neutral");
  el("lab-orb").classList.toggle("running", running);
  pill("python-pill", data.python + (data.venv ? " · .venv" : " · global"), data.venv ? "good" : "warn");
  pill("job-pill", active ? "● " + active.label : (last ? (last.status === "ok" ? "✓ Última tarefa OK" : "Última tarefa: " + last.status) : "Sem tarefas"), active ? "warn" : last && last.status === "ok" ? "good" : last && last.status === "error" ? "bad" : "neutral");

  select("[data-action]").forEach((b) => { b.disabled = busy || ((b.dataset.action === "sync" || b.dataset.action === "pull") && running); });
  el("switch-branch").disabled = busy || running || !g.branches || !g.branches.length;
  el("start-lab").disabled = busy || running;
  el("stop-lab").disabled = !running;
  el("pin-lab").disabled = busy;
  text("lab-path", "Banco: ~/.infinity-ai/campaigns/" + data.config.campaign + ".sqlite3");
  text("ssh-hint", data.config.ssh_host ? "SSH configurado no painel" : data.ssh_inherited ? "SSH herdado do Terminal" : "Configure o SSH antes de iniciar o laboratório.");
  text("log-location", "Arquivos locais de log: " + data.logs_dir);
  renderJobs(data.jobs);

  el("connection").textContent = "● Conectado";
  el("connection").style.color = "";
}

function renderJobs(jobs) {
  const box = el("job-select");
  const ids = jobs.map((job) => job.id);
  const listed = Array.from(box.options).map((option) => option.value);
  if (listed.join("|") !== ids.join("|")) {
    const selected = box.value || logJob;
    box.replaceChildren();
    jobs.forEach((job) => {
      const option = document.createElement("option");
      option.value = job.id;
      const time = job.started ? job.started.slice(11, 19) : "";
      option.textContent = time + " · " + job.label + " (" + job.status + ")";
      box.append(option);
    });
    if (!jobs.length) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "Nenhum log ainda";
      box.append(option);
    }
    box.value = ids.includes(selected) ? selected : (ids.length ? ids[ids.length - 1] : "");
  } else {
    jobs.forEach((job, index) => {
      const option = box.options[index];
      if (option) option.textContent = job.started.slice(11, 19) + " · " + job.label + " (" + job.status + ")";
    });
  }
  logJob = box.value;
  box.disabled = logKind !== "job" || !jobs.length;
}

async function loadLog() {
  let url;
  let status = "Monitorando";
  if (logKind === "service") {
    url = "/api/log?kind=service";
    if (snapshot) status = snapshot.service.running ? "● Serviço ativo" : "Serviço parado";
  } else {
    if (!logJob) {
      text("log-content", "Execute uma tarefa para consultar os logs.");
      text("log-state", "—");
      return;
    }
    url = "/api/log?kind=job&id=" + encodeURIComponent(logJob);
    if (snapshot) {
      const job = snapshot.jobs.find((j) => j.id === logJob);
      status = job ? job.status : "Arquivado";
    }
  }
  const result = await api(url);
  const output = el("log-content");
  if (result.text !== lastLogText) {
    const scroll = output;
    const nearBottom = scroll.scrollHeight - scroll.scrollTop - scroll.clientHeight < 95;
    output.textContent = result.text || (logKind === "service" ? "O serviço ainda não gerou logs." : "Aguardando saída do comando...");
    if (nearBottom || lastLogText === null) scroll.scrollTop = scroll.scrollHeight;
    lastLogText = result.text;
  }
  text("log-state", status);
}

async function refresh() {
  if (updating) return;
  updating = true;
  try {
    const data = await api("/api/status");
    renderStatus(data);
    await loadLog();
  } catch (error) {
    el("connection").textContent = "● Desconectado";
    el("connection").style.color = "#f19b9f";
    if (snapshot === null) notify(error.message, true);
  } finally {
    updating = false;
  }
}

function openJobLog(id) {
  logKind = "job";
  logJob = id;
  el("job-select").value = id;
  select("[data-log]").forEach((b) => b.classList.toggle("active", b.dataset.log === logKind));
  lastLogText = null;
  el("logs").scrollIntoView({behavior: "smooth", block: "start"});
  refresh();
}

async function runAction(action, branch) {
  try {
    const payload = {action: action};
    if (branch) payload.branch = branch;
    if (action === "pin") {
      if (!window.confirm("Registrar a revisão do pacote 1369 DR na campanha do laboratório? A operação altera somente o banco desta campanha.")) return;
      payload.confirmed = true;
    }
    const result = await api("/api/action", payload);
    notify("Iniciado: " + result.job.label);
    openJobLog(result.job.id);
  } catch (error) {
    notify(error.message, true);
  }
}

select("[data-action]").forEach((button) => {
  button.addEventListener("click", () => { runAction(button.dataset.action); });
});
el("switch-branch").addEventListener("click", async () => {
  const branch = el("branch-select").value;
  if (!branch) return;
  if (snapshot && snapshot.git.branch === branch) {
    notify("Você já está nesta branch.");
    return;
  }
  if (!window.confirm("Trocar a cópia local para " + branch + "? Alterações locais impedem a operação.")) return;
  await runAction("switch", branch);
});
el("refresh").addEventListener("click", refresh);
el("config-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await saveConfig();
    notify("Configurações salvas apenas neste computador.");
    await refresh();
  } catch (error) {
    notify(error.message, true);
  }
});
el("start-lab").addEventListener("click", async () => {
  try {
    await saveConfig();
    await api("/api/lab/start", {});
    notify("Serviço do BG2:EE iniciado. Acompanhe o console.");
    logKind = "service";
    select("[data-log]").forEach((b) => b.classList.toggle("active", b.dataset.log === logKind));
    lastLogText = null;
    await refresh();
  } catch (error) {
    notify(error.message, true);
  }
});
el("stop-lab").addEventListener("click", async () => {
  try {
    await api("/api/lab/stop", {});
    notify("Solicitado encerramento do serviço.");
    await refresh();
  } catch (error) {
    notify(error.message, true);
  }
});
el("pin-lab").addEventListener("click", async () => {
  try {
    await saveConfig();
    await runAction("pin");
  } catch (error) {
    notify(error.message, true);
  }
});
select("[data-log]").forEach((button) => {
  button.addEventListener("click", async () => {
    logKind = button.dataset.log;
    select("[data-log]").forEach((b) => b.classList.toggle("active", b === button));
    el("job-select").disabled = logKind !== "job";
    lastLogText = null;
    await refresh();
  });
});
el("job-select").addEventListener("change", async () => {
  logJob = el("job-select").value;
  lastLogText = null;
  await refresh();
});
el("copy-log").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(el("log-content").textContent);
    notify("Log copiado.");
  } catch (error) {
    notify("Não foi possível copiar o log.", true);
  }
});
el("scroll-log").addEventListener("click", () => {
  const terminal = el("log-content");
  terminal.scrollTop = terminal.scrollHeight;
});
select(".navlink").forEach((link) => {
  link.addEventListener("click", () => {
    select(".navlink").forEach((item) => item.classList.toggle("active", item === link));
  });
});

refresh();
setInterval(refresh, 1800);
