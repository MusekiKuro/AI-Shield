# Состояние проекта

- Дата: 12 ноября 2026.
- Ветка: main; Git инициализирован.
- Текущая цель: C01.1–C01.5 и M02 написаны; общие API/UI-контракты готовы для карточек F, следующий этап — серверная цепочка перевода. Запуска и проверок не было, бизнес-маршруты ещё не реализованы; health каркаса false/null до проб C03.
- Изменённые файлы: 26 новых — backend/pyproject.toml, app/{__init__,main,config,schemas}.py, app/api/{__init__,routes_health}.py, app/speech/{classifier_prompt.txt,llm_schema.json}; frontend/{package.json,package-lock.json,tsconfig.json,vite.config.ts,index.html}, src/{main.tsx,App.tsx,shell.css,api/types.ts,components/contracts.ts,i18n/keys.ts,i18n/index.ts}; docs/{api,ui-contracts}.md; README.md; .env.example; .gitignore. Обновлены TASKS.md и PROJECT_STATE.md. Полный список — README.md. docs.zip не обновлялся.
- Блокеры: для F-контрактов нет; F05/F06 ждут только F02, F13 — C05. Последующие решения L3: выдача демо-токенов, политика неполных данных/сильных признаков, при необходимости отдельный ключ запасного LLM и отключение размышлений конкретного сервера. Качество/задержки моделей, доступность ПК на защите и формат сдачи не подтверждены; транзитивный Python lock отсутствует.
- Следующий шаг: по отдельному поручению выполнить C02 целиком по зафиксированному API.
