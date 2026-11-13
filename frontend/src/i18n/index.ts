import type { Language } from "../api/types";
import { messageSpec } from "./keys";
import type { MessageKey, Messages, Translate } from "./keys";

// F07/F08 create the dictionaries. An empty glob keeps the C01 shell independent.
const modules = import.meta.glob<Partial<Messages>>("./{ru,kk}.json", {
  eager: true, import: "default",
});

const shellRu: Partial<Messages> = {
  "app.name": "ИИ-щит",
  "app.syntheticDemo": "Синтетическое банковское демо. Настоящие деньги не переводятся.",
  "app.processingNotice": "Обработка на сервере команды без передачи сторонним сервисам.",
  "app.language": "Язык интерфейса",
  "app.shellTitle": "Основа приложения",
  "app.shellDescription": "Созданы каркас и контракты. Операции подключаются на следующих этапах.",
  "app.notFound": "Страница не найдена",
  "nav.client": "Клиент", "nav.trusted": "Доверенный",
  "nav.operator": "Оператор", "nav.demo": "Пульт демо",
  "shell.client": "Здесь будет форма перевода и объяснение решения сервера.",
  "shell.trusted": "Здесь будут запросы на подтверждение конкретной суммы и получателя.",
  "shell.operator": "Здесь будут удержанные операции и разрешённые решения.",
  "shell.demo": "Здесь будут синтетические диалоги и переключатели simulated.",
  "common.errorTitle": "Не удалось показать экран",
  "common.retry": "Повторить загрузку",
};
const shellKk: Partial<Messages> = {
  "app.name": "ИИ-щит",
  "app.syntheticDemo": "Жасанды деректерге негізделген банк демосы. Нақты ақша аударылмайды.",
  "app.processingNotice": "Деректер команда серверінде өңделеді, сыртқы сервистерге берілмейді.",
  "app.language": "Интерфейс тілі",
  "app.shellTitle": "Қолданбаның негізі",
  "app.shellDescription": "Қаңқасы мен келісімдері жазылды. Операциялар келесі кезеңдерде қосылады.",
  "app.notFound": "Бет табылмады",
  "nav.client": "Клиент", "nav.trusted": "Сенімді тұлға",
  "nav.operator": "Оператор", "nav.demo": "Демо басқару панелі",
  "shell.client": "Мұнда аударым нысаны мен сервер шешімінің түсіндірмесі болады.",
  "shell.trusted": "Мұнда нақты сома мен алушыны растау сұраулары болады.",
  "shell.operator": "Мұнда ұсталған операциялар мен рұқсат етілген шешімдер болады.",
  "shell.demo": "Мұнда жасанды диалогтар мен simulated ауыстырғыштары болады.",
  "common.errorTitle": "Экранды көрсету мүмкін болмады",
  "common.retry": "Қайта жүктеу",
};

export const dictionaries: Record<Language, Readonly<Partial<Messages>>> = {
  ru: { ...shellRu, ...modules["./ru.json"] },
  kk: { ...shellKk, ...modules["./kk.json"] },
};

/** No HTML interpretation. Absent future copy is visibly an untranslated key. */
export function createTranslator(language: Language): Translate {
  return ((key: MessageKey, params?: Record<string, string | number>) => {
    const template = dictionaries[language][key] ?? `[${key}]`;
    return template.replace(/\{([A-Za-z][A-Za-z0-9]*)\}/g, (match, name: string) => {
      if (!(messageSpec[key].params as readonly string[]).includes(name)) return match;
      return params && Object.hasOwn(params, name) ? String(params[name]) : match;
    });
  }) as Translate;
}

export function initialLanguage(): Language {
  return navigator.language.toLowerCase().startsWith("kk") ? "kk" : "ru";
}
