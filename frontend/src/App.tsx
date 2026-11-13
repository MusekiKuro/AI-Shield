import { Component, useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { Language } from "./api/types";
import { createTranslator, initialLanguage } from "./i18n";

const routes = ["client", "trusted", "operator", "demo"] as const;

class ScreenBoundary extends Component<
  { children: ReactNode; title: string; retry: string }, { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    if (this.state.failed) {
      return <section role="alert" className="shell-panel">
        <h1>{this.props.title}</h1>
        <button onClick={() => window.location.reload()}>{this.props.retry}</button>
      </section>;
    }
    return this.props.children;
  }
}

export default function App() {
  const [language, setLanguage] = useState<Language>(initialLanguage);
  const t = createTranslator(language);
  const path = window.location.pathname.replace(/\/$/, "") || "/client";
  const current = routes.find((route) => path === `/${route}`);

  useEffect(() => { document.documentElement.lang = language; }, [language]);

  return <div className="shell">
    <header className="shell-header">
      <a className="shell-brand" href="/client">{t("app.name")}</a>
      <label className="shell-language">
        {t("app.language")}
        <select value={language} onChange={(event) => setLanguage(event.target.value as Language)}>
          <option value="ru">Русский</option><option value="kk">Қазақша</option>
        </select>
      </label>
    </header>
    <p className="shell-demo">{t("app.syntheticDemo")}</p>
    <nav className="shell-nav" aria-label={t("app.name")}>
      {routes.map((route) => <a key={route} href={`/${route}`}
        aria-current={route === current ? "page" : undefined}>{t(`nav.${route}`)}</a>)}
    </nav>
    <main>
      <ScreenBoundary title={t("common.errorTitle")} retry={t("common.retry")}>
        <section className="shell-panel">
          <h1>{current ? t(`nav.${current}`) : t("app.notFound")}</h1>
          {current && <>
            <h2>{t("app.shellTitle")}</h2>
            <p>{t("app.shellDescription")}</p>
            <p>{t(`shell.${current}`)}</p>
          </>}
        </section>
      </ScreenBoundary>
    </main>
    <footer className="shell-footer">{t("app.processingNotice")}</footer>
  </div>;
}
