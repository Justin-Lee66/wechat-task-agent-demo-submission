const I18N = {
  en: {
    page_title: "WeChat Task Agent",
    subtitle: "Operations Dashboard",
    hero_subtitle: "Turn WeChat group updates into deduplicated project tasks and review-ready action lists.",
    workflow_cockpit: "Task operations desk",
    demo_state_label: "Demo state",
    current_snapshot_label: "Current stage",
    simulation_date_label: "Simulation date",
    nav_my_todo: "My Todo",
    nav_review: "Needs Review",
    nav_projects: "Project Board",
    nav_runs: "Run Log",
    auto_refresh_on: "Auto-refresh on",
    kpi_total: "Total tasks",
    kpi_due: "Due today",
    kpi_my_due: "My due today",
    kpi_me: "My tasks",
    kpi_open: "Open tasks",
    kpi_review: "Needs review",
    kpi_my_review: "My review",
    kpi_done: "Done",
    kpi_my_done: "My done",
    fixture_date_label: "Fixture date",
    current_user_label: "Current user",
    extractor_mode_label: "Extractor",
    auto_refresh_label: "Auto-refresh",
    on_label: "on",
    project_filter_label: "Project filter",
    filter_all: "All",
    filter_me: "@Me",
    my_todo_title: "My Todo",
    priority_todo_title: "Priority Todo",
    viewer_todo_subtitle: "Viewing as {viewer} · assigned tasks sorted by due date",
    manager_todo_subtitle: "Global view · open tasks sorted by due date",
    active_label: "active",
    related_label: "related",
    assigned_label: "assigned",
    only_viewer: "Only {viewer}",
    review_title: "Team Review Queue",
    fuzzy_label: "fuzzy",
    projects_title: "Project Boards",
    projects_count_label: "projects",
    runs_title: "Ingestion Run Log",
    latest_12: "latest 12",
    run_full_demo: "Run Full Demo",
    manual_controls: "Manual Controls",
    run_10am: "Run 10am",
    run_12pm: "Run 12pm",
    run_2pm: "Run 2pm",
    run_done: "Run status update",
    reset_db: "Reset database",
    due_label: "Due",
    empty_my_todo: "No assigned tasks for this viewer yet.",
    empty_priority_todo: "No open tasks yet.",
    review_help: "All fuzzy tasks across projects. This queue is not limited to the selected viewer.",
    review_badge: "Review",
    empty_review: "No fuzzy tasks yet.",
    task_col: "Task",
    assignee_col: "Assignee",
    due_col: "Due",
    status_col: "Status",
    source_col: "Source",
    confidence_col: "Confidence",
    me_badge: "@Me",
    needs_review_badge: "Needs review",
    demo_only_badge: "Demo-only update",
    unassigned_label: "Unassigned",
    none_label: "None",
    empty_projects: "Use the demo controls above to ingest the 10am, 12pm, and 2pm fixtures.",
    snapshot_col: "Stage",
    mode_col: "Mode",
    messages_col: "Messages",
    new_tasks_col: "New tasks",
    updated_col: "Updated",
    started_col: "Started",
    error_col: "Error",
    empty_runs: "No ingestion runs yet.",
    evidence_label: "Evidence",
    view_evidence: "View Evidence",
    source_messages_label: "Raw source messages",
    screenshot_label: "Source image",
    text_only_evidence: "Demo-only status update fixture. No source image is attached.",
    demo_only_fixture_label: "Demo-only status update fixture",
    canonical_key_label: "canonical_key",
    first_seen_label: "first_seen",
    last_seen_label: "last_seen",
    source_hashes_label: "source hashes",
    due_text_label: "due_text",
    due_at_label: "due_at",
    missing_due: "Missing due",
    missing_assignee: "Missing assignee",
    source_time_label: "source time",
    assignees_label: "assignees",
    mentions_label: "mentioned users",
    confidence_label: "confidence",
    running_generic: "Working...",
    reset_running: "Resetting database...",
    reset_complete: "Database reset.",
    ingest_running: "{snapshot} ingest running...",
    ingest_complete: "{snapshot} ingest complete: {messages} messages, {newTasks} new tasks, {updated} updated.",
    llm_key_missing: "LLM extraction requires OPENAI_API_KEY. Configure .env or choose text_fixture.",
    llm_fallback: "LLM failed; used text fixture fallback.",
    full_step_1: "Step 1/4: 10am update",
    full_step_2: "Step 2/4: 12pm update",
    full_step_3: "Step 3/4: 2pm update",
    full_step_4: "Step 4/4: status update",
    full_complete: "Full demo complete: {tasks} tasks, {duplicates} duplicates, {done} done.",
    error_prefix: "Error",
    title: "WeChat Task Agent Demo",
    snapshot_none: "none",
    snapshot_done_update: "status update",
  },
  zh: {
    page_title: "微信任务 Agent",
    subtitle: "AI 任务运营演示",
    hero_subtitle: "把微信群消息整理成去重后的项目任务和待复核清单。",
    workflow_cockpit: "任务运营台",
    demo_state_label: "演示状态",
    current_snapshot_label: "当前阶段",
    simulation_date_label: "模拟日期",
    nav_my_todo: "我的待办",
    nav_review: "待复核",
    nav_projects: "项目看板",
    nav_runs: "运行日志",
    auto_refresh_on: "自动刷新开启",
    kpi_total: "任务总数",
    kpi_due: "今日截止",
    kpi_my_due: "我的今日截止",
    kpi_me: "我的任务",
    kpi_open: "未完成任务",
    kpi_review: "待复核",
    kpi_my_review: "我的待复核",
    kpi_done: "已完成",
    kpi_my_done: "我的已完成",
    fixture_date_label: "模拟日期",
    current_user_label: "当前用户",
    extractor_mode_label: "抽取模式",
    auto_refresh_label: "自动刷新",
    on_label: "开启",
    project_filter_label: "项目筛选",
    filter_all: "全部",
    filter_me: "@我",
    my_todo_title: "我的待办",
    priority_todo_title: "重点待办",
    viewer_todo_subtitle: "当前视角：{viewer} · 负责的任务按截止时间排序",
    manager_todo_subtitle: "经理视角 · 未完成任务按截止时间排序",
    active_label: "进行中",
    related_label: "相关",
    assigned_label: "负责",
    only_viewer: "只看 {viewer}",
    review_title: "团队待复核队列",
    fuzzy_label: "需复核",
    projects_title: "项目看板",
    projects_count_label: "个项目",
    runs_title: "导入运行日志",
    latest_12: "最近 12 条",
    run_full_demo: "运行完整演示",
    manual_controls: "手动控制",
    run_10am: "导入 10am",
    run_12pm: "导入 12pm",
    run_2pm: "导入 2pm",
    run_done: "导入状态更新",
    reset_db: "重置数据库",
    due_label: "截止",
    empty_my_todo: "暂无当前视角负责的任务。",
    empty_priority_todo: "暂无未完成任务。",
    review_help: "展示所有项目中的模糊任务，不仅限于当前用户。",
    review_badge: "复核",
    empty_review: "暂无模糊任务。",
    task_col: "任务",
    assignee_col: "负责人",
    due_col: "截止时间",
    status_col: "状态",
    source_col: "来源时间",
    confidence_col: "置信度",
    me_badge: "@我",
    needs_review_badge: "待复核",
    demo_only_badge: "演示用更新",
    unassigned_label: "未指定负责人",
    none_label: "无",
    empty_projects: "使用上方演示按钮导入 10am、12pm 和 2pm 消息。",
    snapshot_col: "阶段",
    mode_col: "模式",
    messages_col: "消息",
    new_tasks_col: "新任务",
    updated_col: "更新",
    started_col: "开始时间",
    error_col: "错误",
    empty_runs: "暂无导入运行记录。",
    evidence_label: "原始消息",
    view_evidence: "查看来源",
    source_messages_label: "原始来源消息",
    screenshot_label: "来源图片",
    text_only_evidence: "演示用状态更新 fixture。该更新没有来源图片。",
    demo_only_fixture_label: "演示用状态更新 fixture",
    canonical_key_label: "canonical_key",
    first_seen_label: "首次出现",
    last_seen_label: "最后出现",
    source_hashes_label: "来源 hash 数",
    due_text_label: "原始截止文本",
    due_at_label: "解析截止时间",
    missing_due: "缺截止时间",
    missing_assignee: "缺负责人",
    source_time_label: "来源消息时间",
    assignees_label: "负责人",
    mentions_label: "提及用户",
    confidence_label: "置信度",
    running_generic: "处理中...",
    reset_running: "正在重置数据库...",
    reset_complete: "数据库已重置。",
    ingest_running: "正在导入 {snapshot}...",
    ingest_complete: "{snapshot} 导入完成：{messages} 条消息，{newTasks} 个新任务，{updated} 个更新。",
    llm_key_missing: "LLM 抽取需要配置 OPENAI_API_KEY。请配置 .env，或选择 text_fixture。",
    llm_fallback: "LLM 抽取失败，已回退到 text fixture。",
    full_step_1: "第 1/4 步：10am 消息",
    full_step_2: "第 2/4 步：12pm 消息",
    full_step_3: "第 3/4 步：2pm 消息",
    full_step_4: "第 4/4 步：状态更新",
    full_complete: "完整演示完成：{tasks} 个任务，{duplicates} 个重复，{done} 个已完成。",
    error_prefix: "错误",
    title: "微信任务 Agent 演示",
    snapshot_none: "无",
    snapshot_done_update: "状态更新",
  },
};

const STATUS_LABELS = {
  en: { todo: "todo", done: "done", success: "success", failed: "failed", running: "running" },
  zh: { todo: "待办", done: "已完成", success: "成功", failed: "失败", running: "运行中" },
};

const REASON_LABELS = {
  en: {
    missing_assignee: "Missing assignee",
    missing_due: "Missing due",
    unresolved_due: "Unresolved due",
    low_confidence: "Low confidence",
    ambiguous_timing: "Ambiguous timing",
    demo_only_status_update: "Demo-only status update",
  },
  zh: {
    missing_assignee: "缺负责人",
    missing_due: "缺截止时间",
    unresolved_due: "截止时间无法解析",
    low_confidence: "低置信度",
    ambiguous_timing: "时间表达模糊",
    demo_only_status_update: "演示用状态更新",
  },
};

let activeProjectFilter = "all";
let activeReviewFilter = "all";
let fullDemoRunning = false;
let activeProgressKey = null;
const VIEWER_KEY = "dashboardViewer";
const EXTRACTOR_KEY = "dashboardExtractorMode";
const VIEWERS = ["manager", "阿可", "Henry", "Iris", "Tara.L", "Chris"];
const EXTRACTOR_MODES = ["text_fixture", "llm_text", "llm_vision"];
const VIEWER_LABELS = {
  en: { manager: "Manager", "阿可": "阿可", Henry: "Henry", Iris: "Iris", "Tara.L": "Tara.L", Chris: "Chris" },
  zh: { manager: "经理", "阿可": "阿可", Henry: "Henry", Iris: "Iris", "Tara.L": "Tara.L", Chris: "Chris" },
};
let dashboardConfig = null;

function lang() {
  return localStorage.getItem("dashboardLanguage") || "en";
}

function selectedViewer() {
  const stored = localStorage.getItem(VIEWER_KEY) || "阿可";
  return VIEWERS.includes(stored) ? stored : "阿可";
}

function selectedExtractorMode() {
  const stored = localStorage.getItem(EXTRACTOR_KEY);
  return EXTRACTOR_MODES.includes(stored) ? stored : "text_fixture";
}

function setSelectedExtractorMode(mode) {
  localStorage.setItem(EXTRACTOR_KEY, EXTRACTOR_MODES.includes(mode) ? mode : "text_fixture");
  updateExtractorSelector();
}

function isManagerViewer(viewer = selectedViewer()) {
  return viewer === "manager";
}

function viewerLabel(viewer = selectedViewer()) {
  return VIEWER_LABELS[lang()][viewer] || viewer;
}

function t(key, values = {}) {
  let value = I18N[lang()][key] || I18N.en[key] || key;
  for (const [name, replacement] of Object.entries(values)) {
    value = value.replace(`{${name}}`, replacement);
  }
  return value;
}

let autoRefreshPausedUntil = 0;

function pauseAutoRefresh(ms = 12000) {
  autoRefreshPausedUntil = Math.max(autoRefreshPausedUntil, Date.now() + ms);
}

function shouldHoldAutoRefresh() {
  const active = document.activeElement;
  return Date.now() < autoRefreshPausedUntil || Boolean(active && active.closest?.("#viewer-select, #extractor-select, .manual-controls, .language-menu"));
}

function captureDashboardUiState() {
  const languageMenu = document.querySelector("#language-menu-options");
  return {
    windowX: window.scrollX,
    windowY: window.scrollY,
    manualOpen: Boolean(document.querySelector(".manual-controls")?.open),
    languageOpen: Boolean(languageMenu && !languageMenu.hidden),
    projectScrollTop: document.querySelector(".project-scroll")?.scrollTop || 0,
    reviewScrollTop: document.querySelector(".review-scroll")?.scrollTop || 0,
  };
}

function restoreDashboardUiState(state) {
  if (!state) return;
  const manual = document.querySelector(".manual-controls");
  if (manual) manual.open = state.manualOpen;

  const menu = document.querySelector("#language-menu-options");
  const languageButton = document.querySelector("#language-menu-button");
  if (menu) menu.hidden = !state.languageOpen;
  if (languageButton) languageButton.setAttribute("aria-expanded", state.languageOpen ? "true" : "false");

  const projectScroll = document.querySelector(".project-scroll");
  if (projectScroll) projectScroll.scrollTop = state.projectScrollTop;
  const reviewScroll = document.querySelector(".review-scroll");
  if (reviewScroll) reviewScroll.scrollTop = state.reviewScrollTop;
  window.scrollTo(state.windowX, state.windowY);
}

function applyLanguage() {
  const current = lang();
  document.documentElement.lang = current;
  document.documentElement.dataset.lang = current;
  document.title = t("title");

  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });

  document.querySelectorAll("[data-en][data-zh]").forEach((node) => {
    node.textContent = current === "zh" ? node.dataset.zh : node.dataset.en;
  });

  document.querySelectorAll("[data-status-label]").forEach((node) => {
    const status = node.dataset.statusLabel;
    node.textContent = STATUS_LABELS[current][status] || status;
  });

  document.querySelectorAll("[data-reason-label]").forEach((node) => {
    const reason = node.dataset.reasonLabel;
    node.textContent = REASON_LABELS[current][reason] || reason;
  });

  const languageButton = document.querySelector("#language-menu-button");
  if (languageButton) languageButton.textContent = current === "zh" ? "🌐 中文 ▾" : "🌐 EN ▾";

  document.querySelectorAll("[data-snapshot-label]").forEach((node) => {
    const snapshot = node.dataset.snapshotLabel;
    node.textContent = snapshot === "none" ? t("snapshot_none") : snapshot === "done_update" ? t("snapshot_done_update") : snapshot;
  });

  updateExtractorSelector();
  applyViewerMode();
  renderProgress();
}

async function getDashboardConfig() {
  if (dashboardConfig) return dashboardConfig;
  const response = await fetch("/api/config");
  if (!response.ok) throw new Error(response.statusText);
  dashboardConfig = await response.json();
  if (!localStorage.getItem(EXTRACTOR_KEY)) {
    const configuredDefault = dashboardConfig.default_extractor_mode;
    setSelectedExtractorMode(EXTRACTOR_MODES.includes(configuredDefault) ? configuredDefault : "text_fixture");
  }
  return dashboardConfig;
}

function updateExtractorSelector() {
  const selector = document.querySelector("#extractor-select");
  if (!selector) return;
  selector.value = selectedExtractorMode();
}

function extractorModeForSnapshot(snapshotId, requestedMode = selectedExtractorMode()) {
  return snapshotId === "done_update" ? "text_fixture" : requestedMode;
}

function ingestUrl(snapshotId, requestedMode = selectedExtractorMode()) {
  const mode = extractorModeForSnapshot(snapshotId, requestedMode);
  return `/api/ingest/${snapshotId}?extractor_mode=${encodeURIComponent(mode)}`;
}

async function canRunExtractorMode(snapshotId, requestedMode = selectedExtractorMode()) {
  const actualMode = extractorModeForSnapshot(snapshotId, requestedMode);
  if (!actualMode.startsWith("llm_")) return true;
  let config;
  try {
    config = await getDashboardConfig();
  } catch (error) {
    showToast(`${t("error_prefix")}: ${error.message}`, "error");
    return false;
  }
  if (config.openai_key_configured) return true;
  showToast(t("llm_key_missing"), "error");
  return false;
}

function maybeToastFallback(result) {
  if (result?.extractor_mode?.includes("fallback")) showToast(t("llm_fallback"), "warning");
}

async function refreshDashboard(options = {}) {
  const dashboard = document.querySelector("#dashboard");
  if (options.auto && shouldHoldAutoRefresh()) return;
  if (!dashboard) return;
  const uiState = captureDashboardUiState();
  const response = await fetch("/partials/dashboard", { headers: { "X-Requested-With": "fetch" } });
  if (response.ok) {
    dashboard.innerHTML = await response.text();
    applyLanguage();
    restoreDashboardUiState(uiState);
    const status = document.querySelector("#refresh-status");
    if (status) status.textContent = t("auto_refresh_on");
    if (fullDemoRunning) setActionsDisabled(true);
  } else {
    const status = document.querySelector("#refresh-status");
    if (status) status.textContent = t("error_prefix");
  }
}

function showToast(message, tone = "info") {
  const toast = document.querySelector("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.dataset.tone = tone;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 5200);
}

function setActionsDisabled(disabled) {
  document.querySelectorAll("[data-action-button], #run-full-demo").forEach((button) => {
    button.disabled = disabled;
  });
}

function setButtonLoading(button, isLoading) {
  if (!button) return;
  if (isLoading) {
    button.dataset.originalText = button.textContent;
    button.classList.add("loading");
    button.textContent = t("running_generic");
  } else {
    button.classList.remove("loading");
    delete button.dataset.originalText;
    applyLanguage();
  }
}

async function postJson(url) {
  const response = await fetch(url, { method: "POST" });
  const payload = await response.json().catch(async () => ({ error_message: await response.text() }));
  if (!response.ok) throw new Error(payload.error_message || payload.detail || response.statusText);
  return payload;
}

async function runSingleIngest(snapshotId, button) {
  const requestedMode = selectedExtractorMode();
  if (!(await canRunExtractorMode(snapshotId, requestedMode))) return;
  setActionsDisabled(true);
  setButtonLoading(button, true);
  showToast(t("ingest_running", { snapshot: snapshotId }));
  try {
    const result = await postJson(ingestUrl(snapshotId, requestedMode));
    await refreshDashboard();
    maybeToastFallback(result);
    showToast(
      t("ingest_complete", {
        snapshot: snapshotId,
        messages: result.new_messages_count,
        newTasks: result.new_tasks_count,
        updated: result.updated_tasks_count,
      }),
      "success",
    );
  } catch (error) {
    showToast(`${t("error_prefix")}: ${error.message}`, "error");
  } finally {
    setButtonLoading(button, false);
    setActionsDisabled(false);
  }
}

async function resetDatabase(button) {
  setActionsDisabled(true);
  setButtonLoading(button, true);
  showToast(t("reset_running"));
  try {
    await postJson("/api/reset");
    await refreshDashboard();
    showToast(t("reset_complete"), "success");
  } catch (error) {
    showToast(`${t("error_prefix")}: ${error.message}`, "error");
  } finally {
    setButtonLoading(button, false);
    setActionsDisabled(false);
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function runFullDemo(button) {
  if (fullDemoRunning) return;
  const requestedMode = selectedExtractorMode();
  if (!(await canRunExtractorMode("10am", requestedMode))) return;
  fullDemoRunning = true;
  setActionsDisabled(true);
  setButtonLoading(button, true);
  const steps = [
    ["10am", "full_step_1"],
    ["12pm", "full_step_2"],
    ["2pm", "full_step_3"],
    ["done_update", "full_step_4"],
  ];

  try {
    await postJson("/api/reset");
    await refreshDashboard();

    for (let index = 0; index < steps.length; index += 1) {
      const [snapshot, labelKey] = steps[index];
      activeProgressKey = labelKey;
      renderProgress();
      showToast(t("ingest_running", { snapshot }));
      const result = await postJson(ingestUrl(snapshot, requestedMode));
      await refreshDashboard();
      maybeToastFallback(result);
      if (index < steps.length - 1) await sleep(8000);
    }

    const summary = await fetch("/api/summary").then((response) => response.json());
    showToast(
      t("full_complete", {
        tasks: summary.total_tasks,
        duplicates: summary.duplicate_canonical_keys.length,
        done: summary.done_tasks,
      }),
      "success",
    );
  } catch (error) {
    showToast(`${t("error_prefix")}: ${error.message}`, "error");
  } finally {
    activeProgressKey = null;
    renderProgress();
    fullDemoRunning = false;
    setButtonLoading(button, false);
    setActionsDisabled(false);
  }
}

function renderProgress() {
  const progress = document.querySelector("#demo-progress");
  if (!progress) return;
  progress.hidden = !activeProgressKey;
  if (activeProgressKey) progress.textContent = t(activeProgressKey);
}

function viewerRoles(node) {
  return (node.dataset.viewerRoles || "").split("|").filter(Boolean);
}

function viewerActionRoles(node) {
  return (node.dataset.viewerActionRoles || "").split("|").filter(Boolean);
}

function isTaskRelatedToViewer(node, viewer = selectedViewer()) {
  if (isManagerViewer(viewer)) return false;
  return viewerRoles(node).includes(viewer);
}

function isTaskActionableForViewer(node, viewer = selectedViewer()) {
  if (isManagerViewer(viewer)) return false;
  return viewerActionRoles(node).includes(viewer);
}

function personMatchesViewer(person, viewer) {
  return person === viewer || (viewer === "Chris" && person.toLowerCase() === "mkt chris");
}

function updateViewerSelector() {
  const selector = document.querySelector("#viewer-select");
  if (!selector) return;
  selector.value = selectedViewer();
  selector.querySelectorAll("option").forEach((option) => {
    option.textContent = lang() === "zh" ? option.dataset.zh : option.dataset.en;
  });
}

function projectTaskRows() {
  return Array.from(document.querySelectorAll("#projects [data-task-row]"));
}

function updateViewerBadges() {
  const viewer = selectedViewer();
  const manager = isManagerViewer(viewer);
  document.querySelectorAll("[data-task-row]").forEach((node) => {
    const actionable = isTaskActionableForViewer(node, viewer);
    node.classList.toggle("self", !manager && actionable);
    const badge = node.querySelector("[data-viewer-badge]");
    if (badge) {
      badge.hidden = manager || !actionable;
      badge.textContent = t("me_badge");
    }
  });

  document.querySelectorAll(".person-chip[data-person]").forEach((chip) => {
    const person = chip.dataset.person;
    const selected = !manager && personMatchesViewer(person, viewer);
    chip.classList.toggle("self-person", selected);
    chip.textContent = selected ? `@${person}` : chip.dataset.personLabel;
  });
}

function updateViewerOnlyChips() {
  const viewer = selectedViewer();
  const manager = isManagerViewer(viewer);
  document.querySelectorAll("[data-viewer-only-chip]").forEach((chip) => {
    chip.hidden = manager;
    chip.textContent = t("only_viewer", { viewer: viewerLabel(viewer) });
  });
  if (manager && activeProjectFilter === "viewer") activeProjectFilter = "all";
  if (manager && activeReviewFilter === "viewer") activeReviewFilter = "all";
}

function updateMyTodo() {
  const viewer = selectedViewer();
  const manager = isManagerViewer(viewer);
  const rows = Array.from(document.querySelectorAll("#my-todo [data-task-row]"));
  let visible = 0;
  rows.forEach((node) => {
    const show = manager ? node.dataset.status !== "done" : isTaskActionableForViewer(node, viewer);
    node.hidden = !show;
    if (show) visible += 1;
  });

  const title = document.querySelector("[data-role-todo-title]");
  if (title) title.textContent = manager ? t("priority_todo_title") : t("my_todo_title");
  const subtitle = document.querySelector("[data-role-todo-subtitle]");
  if (subtitle) {
    subtitle.textContent = manager
      ? t("manager_todo_subtitle")
      : t("viewer_todo_subtitle", { viewer: viewerLabel(viewer) });
  }
  const count = document.querySelector("[data-my-todo-count]");
  if (count) count.textContent = visible;
  const countLabel = document.querySelector("[data-todo-count-label]");
  if (countLabel) countLabel.textContent = manager ? t("active_label") : t("assigned_label");
  const empty = document.querySelector("[data-my-todo-empty]");
  if (empty) {
    empty.hidden = visible > 0;
    empty.textContent = manager ? t("empty_priority_todo") : t("empty_my_todo");
  }
}

function updateKpis() {
  const viewer = selectedViewer();
  const manager = isManagerViewer(viewer);
  const rows = projectTaskRows();
  const scoped = manager ? rows : rows.filter((row) => isTaskActionableForViewer(row, viewer));
  const openRows = rows.filter((row) => row.dataset.status !== "done");
  const scopedOpen = scoped.filter((row) => row.dataset.status !== "done");
  const values = {
    total: rows.length,
    secondary: manager ? openRows.length : scoped.length,
    due: scopedOpen.filter((row) => row.dataset.dueToday === "true").length,
    review: scoped.filter((row) => row.dataset.needsReview === "true").length,
    done: scoped.filter((row) => row.dataset.status === "done").length,
  };
  Object.entries(values).forEach(([key, value]) => {
    const node = document.querySelector(`[data-kpi="${key}"]`);
    if (node) node.textContent = value;
  });
  const labelKeys = manager
    ? { secondary: "kpi_open", due: "kpi_due", review: "kpi_review", done: "kpi_done" }
    : { secondary: "kpi_me", due: "kpi_my_due", review: "kpi_my_review", done: "kpi_my_done" };
  const secondaryLabel = document.querySelector("[data-kpi-secondary-label]");
  if (secondaryLabel) secondaryLabel.textContent = t(labelKeys.secondary);
  ["due", "review", "done"].forEach((key) => {
    const label = document.querySelector(`[data-kpi-label="${key}"]`);
    if (label) label.textContent = t(labelKeys[key]);
  });
}

function applyViewerMode() {
  updateViewerSelector();
  updateViewerBadges();
  updateViewerOnlyChips();
  updateMyTodo();
  updateKpis();
  applyProjectFilter(activeProjectFilter);
  applyReviewFilter(activeReviewFilter);
}

function projectRowMatches(node, filter) {
  if (filter === "all") return true;
  if (filter === "viewer" || filter === "me") return isTaskRelatedToViewer(node);
  return node.dataset.projectFilter === filter;
}

function applyProjectFilter(filter) {
  activeProjectFilter = filter || "all";
  if (isManagerViewer() && activeProjectFilter === "viewer") activeProjectFilter = "all";
  document.querySelectorAll("[data-project-filter-button]").forEach((chip) => {
    chip.classList.toggle("active", chip.dataset.projectFilterButton === activeProjectFilter);
  });

  const projectPanel = document.querySelector("#projects");
  if (!projectPanel) return;

  projectPanel.querySelectorAll("[data-task-row]").forEach((node) => {
    node.hidden = !projectRowMatches(node, activeProjectFilter);
  });

  projectPanel.querySelectorAll("[data-project-section]").forEach((section) => {
    const visibleRows = section.querySelectorAll("[data-task-row]:not([hidden])").length;
    section.hidden = activeProjectFilter !== "all" && visibleRows === 0;
  });
}

function applyReviewFilter(filter) {
  activeReviewFilter = filter || "all";
  if (isManagerViewer() && activeReviewFilter === "viewer") activeReviewFilter = "all";
  document.querySelectorAll("[data-review-filter-button]").forEach((chip) => {
    chip.classList.toggle("active", chip.dataset.reviewFilterButton === activeReviewFilter);
  });

  const reviewPanel = document.querySelector("#review");
  if (!reviewPanel) return;

  reviewPanel.querySelectorAll("[data-task-row]").forEach((node) => {
    node.hidden = !projectRowMatches(node, activeReviewFilter);
  });
}

document.addEventListener("click", (event) => {
  const languageMenuButton = event.target.closest("#language-menu-button");
  if (languageMenuButton) {
    pauseAutoRefresh();
    const menu = document.querySelector("#language-menu-options");
    const expanded = languageMenuButton.getAttribute("aria-expanded") === "true";
    if (menu) menu.hidden = expanded;
    languageMenuButton.setAttribute("aria-expanded", expanded ? "false" : "true");
    return;
  }

  const languageChoice = event.target.closest("[data-language-choice]");
  if (languageChoice) {
    pauseAutoRefresh();
    localStorage.setItem("dashboardLanguage", languageChoice.dataset.languageChoice);
    const menu = document.querySelector("#language-menu-options");
    const button = document.querySelector("#language-menu-button");
    if (menu) menu.hidden = true;
    if (button) button.setAttribute("aria-expanded", "false");
    applyLanguage();
    return;
  }

  const fullDemo = event.target.closest("#run-full-demo");
  if (fullDemo) {
    runFullDemo(fullDemo);
    return;
  }

  const ingest = event.target.closest("[data-ingest]");
  if (ingest) {
    runSingleIngest(ingest.dataset.ingest, ingest);
    return;
  }

  const reset = event.target.closest("#reset-db");
  if (reset) {
    resetDatabase(reset);
    return;
  }

  const projectFilter = event.target.closest("[data-project-filter-button]");
  if (projectFilter) {
    pauseAutoRefresh();
    applyProjectFilter(projectFilter.dataset.projectFilterButton);
    return;
  }

  const reviewFilter = event.target.closest("[data-review-filter-button]");
  if (reviewFilter) {
    pauseAutoRefresh();
    applyReviewFilter(reviewFilter.dataset.reviewFilterButton);
    return;
  }

  const screenshot = event.target.closest("[data-lightbox-src]");
  if (screenshot) {
    const lightbox = document.querySelector("#lightbox");
    const image = document.querySelector("#lightbox-image");
    if (lightbox && image) {
      image.src = screenshot.dataset.lightboxSrc;
      lightbox.hidden = false;
    }
    return;
  }

  const evidence = event.target.closest("[data-evidence-payload]");
  if (evidence) {
    openEvidenceModal(evidence.dataset.evidencePayload);
    return;
  }

  if (event.target.closest("#evidence-close") || event.target.id === "evidence-modal") {
    closeEvidenceModal();
    return;
  }

  if (event.target.closest("#lightbox-close") || event.target.id === "lightbox") {
    const lightbox = document.querySelector("#lightbox");
    if (lightbox) lightbox.hidden = true;
  }
});

document.addEventListener("change", (event) => {
  const viewerSelect = event.target.closest("#viewer-select");
  if (viewerSelect) {
    pauseAutoRefresh();
    localStorage.setItem(VIEWER_KEY, viewerSelect.value);
    applyViewerMode();
    return;
  }

  const extractorSelect = event.target.closest("#extractor-select");
  if (extractorSelect) {
    pauseAutoRefresh();
    setSelectedExtractorMode(extractorSelect.value);
  }
});

document.addEventListener("toggle", (event) => {
  if (event.target.closest?.(".manual-controls")) pauseAutoRefresh();
}, true);

document.addEventListener("focusin", (event) => {
  if (event.target.closest?.("#viewer-select, #extractor-select, .manual-controls, .language-menu")) pauseAutoRefresh();
});

document.addEventListener("pointerdown", (event) => {
  if (event.target.closest?.("#viewer-select, #extractor-select, .manual-controls, .language-menu, .project-scroll, .review-scroll")) pauseAutoRefresh();
});

document.addEventListener("wheel", (event) => {
  if (event.target.closest?.(".project-scroll, .review-scroll, .manual-controls")) pauseAutoRefresh();
}, { passive: true });

document.addEventListener("scroll", (event) => {
  if (event.target?.matches?.(".project-scroll, .review-scroll")) pauseAutoRefresh();
}, true);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    const lightbox = document.querySelector("#lightbox");
    if (lightbox) lightbox.hidden = true;
    closeEvidenceModal();
  }
});

function openEvidenceModal(payloadJson) {
  const modal = document.querySelector("#evidence-modal");
  if (!payloadJson || !modal) return;
  const payload = JSON.parse(payloadJson);
  const current = lang();

  document.querySelector("#evidence-modal-title").textContent = current === "zh" ? payload.title_zh : payload.title_en;
  document.querySelector("#evidence-modal-subtitle").textContent = `${payload.project} · ${payload.canonical_key}`;

  const rawContainer = document.querySelector("#evidence-raw-messages");
  rawContainer.innerHTML = "";
  for (const message of payload.raw_messages || []) {
    const block = document.createElement("div");
    block.className = "raw-message";
    const meta = document.createElement("div");
    meta.className = "raw-meta";
    meta.textContent = `${message.snapshot_id} · ${message.source_time} · ${message.sender}`;
    const pre = document.createElement("pre");
    pre.textContent = message.raw_text;
    block.append(meta, pre);
    rawContainer.appendChild(block);
  }

  const screenshotButton = document.querySelector("#evidence-screenshot-button");
  const screenshotImage = document.querySelector("#evidence-screenshot");
  const textOnly = document.querySelector("#evidence-text-only");
  const demoOnly = document.querySelector("#evidence-demo-only");
  if (demoOnly) demoOnly.hidden = !payload.is_demo_only_update;
  if (payload.screenshot_url) {
    screenshotButton.hidden = false;
    screenshotButton.dataset.lightboxSrc = payload.screenshot_url;
    screenshotImage.src = payload.screenshot_url;
    textOnly.hidden = true;
  } else {
    screenshotButton.hidden = true;
    screenshotImage.removeAttribute("src");
    textOnly.hidden = false;
  }

  const fields = document.querySelector("#evidence-fields");
  fields.innerHTML = "";
  const labels = {
    canonical_key: "canonical_key_label",
    due_text: "due_text_label",
    due_at: "due_at_label",
    source_message_time: "source_time_label",
    first_seen_snapshot: "first_seen_label",
    last_seen_snapshot: "last_seen_label",
    source_hash_count: "source_hashes_label",
    assignees: "assignees_label",
    mentioned_users: "mentions_label",
    confidence: "confidence_label",
  };
  for (const [field, labelKey] of Object.entries(labels)) {
    const item = document.createElement("span");
    item.innerHTML = `<strong>${t(labelKey)}</strong>: ${payload.fields[field] ?? "—"}`;
    fields.appendChild(item);
  }

  modal.hidden = false;
  modal.setAttribute("aria-hidden", "false");
}

function closeEvidenceModal() {
  const modal = document.querySelector("#evidence-modal");
  if (modal) {
    modal.hidden = true;
    modal.setAttribute("aria-hidden", "true");
  }
}

document.addEventListener("click", (event) => {
  const menu = document.querySelector("#language-menu-options");
  const button = document.querySelector("#language-menu-button");
  if (!menu || !button) return;
  if (!event.target.closest(".language-menu")) {
    menu.hidden = true;
    button.setAttribute("aria-expanded", "false");
  }
});

applyLanguage();
getDashboardConfig().then(updateExtractorSelector).catch(() => {});
setInterval(() => refreshDashboard({ auto: true }), 3000);
