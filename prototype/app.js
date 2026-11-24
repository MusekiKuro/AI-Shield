"use strict";

const messages = {
  ru: {
    brand: "ИИ-щит", brandCaption: "Защита переводов", roles: "Роли", language: "Язык",
    client: "Клиент", trusted: "Доверенный", operator: "Оператор", demo: "Пульт демо",
    sandbox: "Синтетические данные", prototype: "Макет MVP",
    clientTitle: "Проверка перевода",
    clientDescription: "Выберите сценарий и посмотрите, что произойдёт до списания.",
    trustedTitle: "Подтверждения",
    trustedDescription: "Проверьте сумму и получателя конкретного перевода.",
    operatorTitle: "Проверка оператором",
    operatorDescription: "Рассмотрите причины удержания и зафиксируйте решение.",
    demoTitle: "Пульт демо",
    demoDescription: "История действий в этом сеансе.",
    available: "Доступно на демо-счёте", reserved: "В резерве",
    newTransfer: "Новый перевод", scenario: "Сценарий демо", recipient: "Получатель", amount: "Сумма",
    checkTransfer: "Проверить перевод", resultTitle: "Результат проверки",
    normal: "Обычный перевод", text: "Подозрительная просьба", call: "Звонок отрицается",
    normalContext: "Текст разговора отсутствует. Проверка по данным перевода.",
    textContext: "Пример текста для анализа",
    sampleDialogue: "Срочно переведите деньги на безопасный счёт. Никому об этом не говорите.",
    callContext: "Клиент ответил: «Мне никто не звонил». Доверенного лица нет.",
    simulatedSignal: "Сигнал об активном звонке имитируется пультом демо.",
    newRecipient: "новый получатель", invalidAmount: "Укажите сумму в целых тенге.",
    insufficient: "На демо-счёте недостаточно доступных средств.",
    idleTitle: "Перевод ещё не проверен", idleDescription: "Здесь появятся решение и причины проверки.",
    completed: "Выполнен", paused: "На паузе", held: "Удержан", rejected: "Отклонён", cancelled: "Отменён",
    completedDescription: "Сумма списана с демо-счёта.",
    pausedDescription: "Перепроверьте получателя и сумму. Деньги пока в резерве.",
    heldDescription: "Деньги в резерве до независимого решения.",
    rejectedDescription: "Списание не выполнено. Резерв освобождён.",
    cancelledDescription: "Клиент отменил перевод. Резерв освобождён.",
    noneSource: "Источник · Данные операции", textSource: "Источник · Смоделированный анализ текста",
    callSource: "Источник · Данные операции и имитация сигнала",
    textReason: "Просьба срочно перевести деньги на «безопасный счёт» и сохранить это в тайне.",
    callReason: "В демо сымитирован активный звонок в момент подтверждения.",
    amountReason: "Сумма выше обычной для демо-клиента.",
    recipientReason: "Клиент впервые переводит этому получателю.",
    trustedAction: "Открыть доверенного", operatorAction: "Открыть оператора",
    cancel: "Отменить перевод", continueTransfer: "Получатель и сумма верны",
    resetDraft: "Другой перевод", history: "История переводов", emptyHistory: "В этом сеансе ещё нет переводов.",
    emptyTrusted: "Запросов на подтверждение пока нет.",
    emptyOperator: "Операций на ручной проверке пока нет.",
    approve: "Подтвердить", release: "Разрешить перевод", reject: "Отклонить",
    note: "Причина решения", notePlaceholder: "Например, получатель не подтверждён",
    noteRequired: "Укажите причину решения.",
    demoData: "Данные макета", demoDataDescription: "Сброс очищает историю текущего сеанса и восстанавливает демо-баланс.",
    reset: "Сбросить демо", journal: "Журнал решений", emptyJournal: "Пока решений нет.",
    demoNotice: "Учебный макет на вымышленных данных. Решения имитируются в браузере.",
    recipientAida: "Аида С.", recipientDaniyar: "Данияр К.", recipientAliya: "Алия Н.",
  },
  kk: {
    brand: "ЖИ-қалқан", brandCaption: "Аударымдарды қорғау", roles: "Рөлдер", language: "Тіл",
    client: "Клиент", trusted: "Сенімді тұлға", operator: "Оператор", demo: "Демо басқару",
    sandbox: "Жасанды деректер", prototype: "MVP макеті",
    clientTitle: "Аударымды тексеру",
    clientDescription: "Сценарийді таңдап, ақша есептен шығарылғанға дейін не болатынын көріңіз.",
    trustedTitle: "Растауға сұраулар",
    trustedDescription: "Нақты аударымның сомасы мен алушысын тексеріңіз.",
    operatorTitle: "Оператордың тексеруі",
    operatorDescription: "Аударымның кідіртілу себебін қарап, шешімді тіркеңіз.",
    demoTitle: "Демо басқару",
    demoDescription: "Осы сеанстағы әрекеттер тарихы.",
    available: "Демо шоттағы қолжетімді сома", reserved: "Резервте",
    newTransfer: "Жаңа аударым", scenario: "Демо сценарийі", recipient: "Алушы", amount: "Сома",
    checkTransfer: "Аударымды тексеру", resultTitle: "Тексеру нәтижесі",
    normal: "Әдеттегі аударым", text: "Күмәнді өтініш", call: "Клиент қоңырауды жоққа шығарды",
    normalContext: "Әңгіме мәтіні жоқ. Аударым деректері бойынша тексеріледі.",
    textContext: "Талдауға арналған мәтін үлгісі",
    sampleDialogue: "Ақшаңызды дереу қауіпсіз шотқа аударыңыз. Бұл туралы ешкімге айтпаңыз.",
    callContext: "Клиент «Маған ешкім қоңырау шалған жоқ» деп жауап берді. Сенімді тұлға жоқ.",
    simulatedSignal: "Белсенді қоңырау сигналы демо панелінде имитацияланады.",
    newRecipient: "жаңа алушы", invalidAmount: "Соманы бүтін теңгемен енгізіңіз.",
    insufficient: "Демо шотта қолжетімді қаражат жеткіліксіз.",
    idleTitle: "Аударым әлі тексерілген жоқ", idleDescription: "Мұнда тексеру нәтижесі мен себептері көрсетіледі.",
    completed: "Орындалды", paused: "Кідіртілді", held: "Резервке алынды", rejected: "Қабылданбады", cancelled: "Бас тартылды",
    completedDescription: "Сома демо шоттан есептен шығарылды.",
    pausedDescription: "Алушы мен соманы қайта тексеріңіз. Қаражат әзірге резервте.",
    heldDescription: "Қаражат тәуелсіз шешім қабылданғанға дейін резервте.",
    rejectedDescription: "Сома есептен шығарылмады. Резерв босатылды.",
    cancelledDescription: "Клиент аударымнан бас тартты. Резерв босатылды.",
    noneSource: "Дереккөз · Аударым деректері", textSource: "Дереккөз · Мәтін талдауының имитациясы",
    callSource: "Дереккөз · Аударым деректері және сигнал имитациясы",
    textReason: "Ақшаны шұғыл түрде «қауіпсіз шотқа» аударуды және бұл туралы ешкімге айтпауды сұрады.",
    callReason: "Растау кезінде белсенді қоңырау демода имитацияланды.",
    amountReason: "Сома демо клиенттің әдеттегі аударымынан жоғары.",
    recipientReason: "Клиент бұл алушыға алғаш рет ақша аударып жатыр.",
    trustedAction: "Сенімді тұлғаға өту", operatorAction: "Операторға өту",
    cancel: "Аударымнан бас тарту", continueTransfer: "Алушы мен сома дұрыс",
    resetDraft: "Басқа аударым", history: "Аударымдар тарихы", emptyHistory: "Бұл сеанста аударым әлі жоқ.",
    emptyTrusted: "Растауға жіберілген сұраулар әзірге жоқ.",
    emptyOperator: "Қолмен тексерілетін операциялар әзірге жоқ.",
    approve: "Растау", release: "Аударымға рұқсат беру", reject: "Қабылдамау",
    note: "Шешімнің себебі", notePlaceholder: "Мысалы, алушы расталмады",
    noteRequired: "Шешімнің себебін көрсетіңіз.",
    demoData: "Макет деректері", demoDataDescription: "Қалпына келтіру сеанс тарихын өшіріп, бастапқы демо балансты қайтарады.",
    reset: "Демоны қалпына келтіру", journal: "Шешімдер журналы", emptyJournal: "Әзірге шешім жоқ.",
    demoNotice: "Бұл — жасанды деректерге негізделген оқу макеті. Шешімдер браузерде имитацияланады.",
    recipientAida: "Айда С.", recipientDaniyar: "Данияр К.", recipientAliya: "Әлия Н.",
  },
};

const recipients = {
  aida: { label: "recipientAida", known: true },
  daniyar: { label: "recipientDaniyar", known: false },
  aliya: { label: "recipientAliya", known: false },
};

const scenarios = {
  normal: { recipient: "aida", amount: 12000, source: "noneSource" },
  text: { recipient: "daniyar", amount: 83000, source: "textSource" },
  call: { recipient: "aliya", amount: 135000, source: "callSource" },
};

const openingBalance = 480000;
const unusualAmount = 100000;
const views = ["client", "trusted", "operator", "demo"];
const transfers = [];
const journal = [];

const byId = (id) => document.getElementById(id);
const form = byId("transfer-form");
const scenarioSelect = byId("scenario");
const recipientSelect = byId("recipient");
const amountInput = byId("amount");

let language = "ru";
let activeView = "client";
let activeTransfer = null;
let submittedDraft = null;

const t = (key) => messages[language][key];
const recipientName = (id) => t(recipients[id].label);

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function button(label, variant, onClick) {
  const node = element("button", "button " + variant, t(label));
  node.type = "button";
  node.addEventListener("click", onClick);
  return node;
}

function money(amount) {
  return new Intl.NumberFormat(language === "kk" ? "kk-KZ" : "ru-KZ", {
    maximumFractionDigits: 0,
  }).format(amount) + " ₸";
}

function balance() {
  const reserved = transfers
    .filter((transfer) => transfer.status === "held" || transfer.status === "paused")
    .reduce((total, transfer) => total + transfer.amount, 0);
  const spent = transfers
    .filter((transfer) => transfer.status === "completed")
    .reduce((total, transfer) => total + transfer.amount, 0);
  return { available: openingBalance - spent - reserved, reserved };
}

function isNew(recipient) {
  return !recipients[recipient].known && !transfers.some(
    (transfer) => transfer.recipient === recipient && transfer.status === "completed",
  );
}

function fillSelect(select, entries, selected) {
  select.replaceChildren(...entries.map(([value, label]) => new Option(label, value)));
  select.value = selected;
}

function showError(key) {
  const error = byId("form-error");
  error.hidden = !key;
  error.textContent = key ? t(key) : "";
}

function renderContext() {
  const context = byId("scenario-context");
  if (scenarioSelect.value === "text") {
    const field = element("div", "field");
    const label = element("label", "", t("textContext"));
    label.htmlFor = "example-dialogue";
    const dialogue = element("textarea");
    dialogue.id = "example-dialogue";
    dialogue.readOnly = true;
    dialogue.value = t("sampleDialogue");
    field.append(label, dialogue);
    context.replaceChildren(field);
  } else if (scenarioSelect.value === "call") {
    context.replaceChildren(
      element("p", "", t("callContext")),
      element("p", "", t("simulatedSignal")),
    );
  } else {
    context.replaceChildren(element("p", "", t("normalContext")));
  }
}

function loadDraft(scenario) {
  scenarioSelect.value = scenario;
  recipientSelect.value = scenarios[scenario].recipient;
  amountInput.value = scenarios[scenario].amount;
  activeTransfer = null;
  submittedDraft = null;
  showError(null);
  renderContext();
  renderState();
}

function renderCopy() {
  document.documentElement.lang = language;
  document.title = t("brand") + " · " + t("prototype");
  for (const node of document.querySelectorAll("[data-copy]")) {
    node.textContent = t(node.dataset.copy);
  }
  for (const node of document.querySelectorAll("[data-aria]")) {
    node.setAttribute("aria-label", t(node.dataset.aria));
  }
  for (const node of document.querySelectorAll("[data-language]")) {
    node.setAttribute("aria-pressed", String(node.dataset.language === language));
  }
  fillSelect(
    scenarioSelect,
    Object.keys(scenarios).map((key) => [key, t(key)]),
    scenarioSelect.value || "normal",
  );
  showError(null);
  renderContext();
  showView(activeView);
}

function showView(view) {
  activeView = view;
  for (const name of views) {
    byId(name + "-view").hidden = name !== view;
    const nav = document.querySelector('[data-view="' + name + '"]');
    if (name === view) nav.setAttribute("aria-current", "page");
    else nav.removeAttribute("aria-current");
  }
  byId("page-title").textContent = t(view + "Title");
  byId("page-description").textContent = t(view + "Description");
  renderState();
}

function statusTag(status) {
  const tag = element("span", "tag", t(status));
  tag.dataset.status = status;
  return tag;
}

function reasonList(reasons) {
  const list = element("ul", "reason-list");
  for (const reason of reasons) list.append(element("li", "", t(reason)));
  return list;
}

function renderResult() {
  const target = byId("transfer-result");
  const box = element("div", "status-panel");
  if (!activeTransfer) {
    box.append(element("h3", "", t("idleTitle")), element("p", "", t("idleDescription")));
    target.replaceChildren(box);
    return;
  }

  const transfer = activeTransfer;
  box.dataset.status = transfer.status;
  box.append(element("h3", "", t(transfer.status)), element("p", "", t(transfer.status + "Description")));

  const detail = element("p", "result-details", recipientName(transfer.recipient) + " · " + money(transfer.amount));
  const source = element("p", "result-details", t(scenarios[transfer.scenario].source));
  const actions = element("div", "actions");
  const label = transfer.reviewer === "trusted" ? "trustedAction" : "operatorAction";

  if (transfer.status === "held") {
    actions.append(button(label, "primary", () => showView(transfer.reviewer)));
  }
  if (transfer.status === "paused") {
    actions.append(button("continueTransfer", "primary", () => changeStatus(transfer, "completed", "client")));
  }
  if (transfer.status === "paused" || transfer.status === "held") {
    actions.append(button("cancel", "danger", () => changeStatus(transfer, "cancelled", "client")));
  }
  actions.append(button("resetDraft", "secondary", () => {
    loadDraft(scenarioSelect.value);
    scenarioSelect.focus();
  }));

  target.replaceChildren(box, detail, source);
  if (transfer.reasons.length) target.append(reasonList(transfer.reasons));
  target.append(actions);
}

function renderHistory() {
  const target = byId("transfer-history");
  if (!transfers.length) {
    target.replaceChildren(element("p", "empty", t("emptyHistory")));
    return;
  }
  target.replaceChildren(...transfers.slice().reverse().map((transfer) => {
    const row = element("div", "row");
    const summary = element("div");
    const viewTransfer = element("button", "history-link", recipientName(transfer.recipient));
    viewTransfer.type = "button";
    viewTransfer.addEventListener("click", () => {
      activeTransfer = transfer;
      renderResult();
    });
    summary.append(viewTransfer, element("span", "row-detail", t(transfer.scenario)));
    row.append(summary, element("strong", "row-amount", money(transfer.amount)), statusTag(transfer.status));
    return row;
  }));
}

function renderQueue(role) {
  const target = byId(role + "-queue");
  const pending = transfers.filter((transfer) => transfer.status === "held" && transfer.reviewer === role);
  if (!pending.length) {
    target.replaceChildren(element("p", "card empty", t(role === "trusted" ? "emptyTrusted" : "emptyOperator")));
    return;
  }

  target.replaceChildren(...pending.map((transfer) => {
    const card = element("article", "card queue-item");
    const header = element("header");
    const details = element("div");
    details.append(
      element("h3", "", recipientName(transfer.recipient) + " · " + money(transfer.amount)),
      element("p", "queue-meta", t(transfer.scenario)),
    );
    header.append(details, statusTag(transfer.status));
    card.append(header);
    if (role === "operator") card.append(reasonList(transfer.reasons));

    let note;
    let error;
    if (role === "operator") {
      const field = element("div", "field");
      const label = element("label", "", t("note"));
      label.htmlFor = "note-" + transfer.id;
      note = element("textarea");
      note.id = label.htmlFor;
      note.placeholder = t("notePlaceholder");
      note.maxLength = 300;
      note.required = true;
      error = element("p", "form-error");
      error.setAttribute("role", "alert");
      error.hidden = true;
      field.append(label, note, error);
      card.append(field);
    }

    const resolve = (status) => {
      if (note && !note.value.trim()) {
        error.textContent = t("noteRequired");
        error.hidden = false;
        note.focus();
        return;
      }
      changeStatus(transfer, status, role, note ? note.value.trim() : "");
    };

    const actions = element("div", "actions");
    actions.append(
      button(role === "trusted" ? "approve" : "release", "primary", () => resolve("completed")),
      button("reject", "danger", () => resolve("rejected")),
    );
    card.append(actions);
    return card;
  }));
}

function renderJournal() {
  const target = byId("journal");
  if (!journal.length) {
    target.replaceChildren(element("p", "empty", t("emptyJournal")));
    return;
  }
  target.replaceChildren(...journal.slice().reverse().map((event) => {
    const row = element("div", "row");
    const summary = element("div");
    summary.append(element("strong", "row-title", t(event.role) + " · " + recipientName(event.transfer.recipient)));
    summary.append(element("span", "row-detail", event.note || t(event.transfer.scenario)));
    row.append(summary, element("strong", "row-amount", money(event.transfer.amount)), statusTag(event.status));
    return row;
  }));
}

function renderState() {
  const funds = balance();
  byId("available-balance").textContent = money(funds.available);
  byId("reserved-balance").textContent = money(funds.reserved);
  fillSelect(
    recipientSelect,
    Object.keys(recipients).map((id) => [
      id, recipientName(id) + (isNew(id) ? " · " + t("newRecipient") : ""),
    ]),
    recipientSelect.value || scenarios[scenarioSelect.value].recipient,
  );

  renderResult();
  renderHistory();
  if (activeView === "trusted" || activeView === "operator") renderQueue(activeView);
  if (activeView === "demo") renderJournal();
}

function assessFixture(scenario, amount, recipient) {
  const reasons = [];
  if (isNew(recipient)) reasons.push("recipientReason");
  if (amount >= unusualAmount) reasons.push("amountReason");

  if (scenario === "text") {
    return { status: "held", reviewer: "trusted", reasons: ["textReason", ...reasons] };
  }
  if (scenario === "call") reasons.push("callReason");
  if (scenario === "call" && reasons.length === 3) {
    return { status: "held", reviewer: "operator", reasons };
  }
  return { status: reasons.length >= 2 ? "paused" : "completed", reviewer: null, reasons };
}

function changeStatus(transfer, status, role, note = "") {
  if (transfer.status !== "paused" && transfer.status !== "held") return;
  transfer.status = status;
  journal.push({ transfer, status, role, note });
  renderState();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const amount = amountInput.valueAsNumber;
  const recipient = recipientSelect.value;
  const scenario = scenarioSelect.value;

  if (!Number.isSafeInteger(amount) || amount <= 0) {
    showError("invalidAmount");
    return;
  }

  const draft = [scenario, recipient, amount].join("|");
  if (submittedDraft && submittedDraft.key === draft) {
    activeTransfer = submittedDraft.transfer;
    renderResult();
    return;
  }
  if (amount > balance().available) {
    showError("insufficient");
    return;
  }

  showError(null);
  const transfer = {
    id: transfers.length + 1,
    amount,
    recipient,
    scenario,
    ...assessFixture(scenario, amount, recipient),
  };
  transfers.push(transfer);
  journal.push({ transfer, status: transfer.status, role: "client", note: "" });
  activeTransfer = transfer;
  submittedDraft = { key: draft, transfer };
  renderState();
});

scenarioSelect.addEventListener("change", () => loadDraft(scenarioSelect.value));
form.addEventListener("input", () => showError(null));

for (const nav of document.querySelectorAll("[data-view]")) {
  nav.addEventListener("click", () => showView(nav.dataset.view));
}
for (const toggle of document.querySelectorAll("[data-language]")) {
  toggle.addEventListener("click", () => {
    language = toggle.dataset.language;
    renderCopy();
  });
}

byId("reset-demo").addEventListener("click", () => {
  transfers.length = 0;
  journal.length = 0;
  loadDraft("normal");
  showView("client");
});

renderCopy();
loadDraft("normal");
