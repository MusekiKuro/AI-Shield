# ИИ-щит

Синтетическое банковское демо: признаки социальной инженерии → объяснение → удержание перевода → независимое подтверждение или решение оператора. Настоящие переводы и банковские интеграции отсутствуют. Речь и текст обрабатываются на сервере команды, без передачи сторонним сервисам; сторонние звонки не перехватываются.

## Текущий этап

Написаны C01.1–C01.5: каркас FastAPI/React, схемы HTTP/данных, TypeScript-типы, props, реестр ключей локализации и конфигурация. Написаны файлы M02: общая подсказка и JSON Schema классификатора.

Сейчас зарегистрирован только `GET /api/health`. Экранные адреса `/client`, `/trusted`, `/operator`, `/demo` показывают оболочку; операции, SQLite, права, события и адаптеры будут реализованы C02–C06. Health имеет форму из архитектуры, но до фоновых проверок C03 возвращает `llm.available=false`, `llm.model=null`, `stt.available=false`; заданный URL не выдаётся за доступную модель.

Код написан, запуск не выполнялся. Тесты, линтеры, тайпчекеры, форматтеры и проверочные сборки не запускались; тестовой инфраструктуры нет. Качество локальных моделей и казахских текстов не измерено. Стартовые баллы правил нельзя представлять вероятностью мошенничества.

## Документы и исполнители

- [Границы MVP](docs/MVP_SCOPE.md) и [актуальная архитектура](docs/ARCHITECTURE.md).
- [API, схемы PhraseEntry/DemoDialogue и решения C01](docs/api.md).
- [Точные props, labels, ключи и CSS-контракт для F](docs/ui-contracts.md).
- [Карточки C](docs/superpowers/plans/2026-11-11-complex-tasks.md), [F](docs/superpowers/plans/2026-11-11-flash-tasks.md), [M](docs/superpowers/plans/2026-11-12-local-models.md).
- [Очередь](TASKS.md) и [состояние](PROJECT_STATE.md).

Следующие исполнители не меняют общие контракты. F01/F02/F03/F04/F07–F11 могут писать свои файлы; F05/F06 ждут helper F02. Контракт F12 объявлен заранее, изолированный компонент можно написать уже сейчас, подключение голоса остаётся C06. F13 ждёт фактического C05. Новые ключи, поля, зависимости, API-клиент и интеграцию экранов делает L3.

## Ручной запуск каркаса

Требуются Python 3.12 и Node.js 22 (от 22.12) или 24, npm от 10. Команды ниже — инструкция для отдельного ручного запуска, а не отчёт о выполненных командах. Рабочий каталог для backend — корень проекта.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ./backend
cp .env.example .env
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Во втором терминале:

```bash
cd frontend
npm ci
npm run dev
```

Открыть [клиент](http://127.0.0.1:5173/client), [доверенного](http://127.0.0.1:5173/trusted), [оператора](http://127.0.0.1:5173/operator), [демо](http://127.0.0.1:5173/demo). Vite проксирует `/api` и `/ws` на 127.0.0.1:8000, секретов в frontend нет. Документация текущего FastAPI — [Swagger](http://127.0.0.1:8000/docs), только для уже зарегистрированных маршрутов.

Windows: активация окружения `.venv\Scripts\Activate.ps1`, вместо cp — `Copy-Item .env.example .env`, Python 3.12 можно выбрать через `py -3.12`. Процесс один: будущая шина событий и полный текст сессий находятся в памяти приложения. Запуск нескольких workers не поддерживается контрактом. Раздача собранного React сервером и контейнер относятся к C07; команды сборки здесь не выполнялись.

## Конфигурация

`backend/app/config.py` читает корневой `.env` и окружение процесса, окружение имеет приоритет. Значения/defaults точно соответствуют ARCHITECTURE §6:

| Переменная | Default |
|---|---|
| DEMO_MODE | true |
| DATABASE_URL | sqlite:///./data/app.db |
| DECISION_TIMEOUT_MS | 3000 |
| APPROVAL_TTL_SECONDS | 120 |
| LLM_BASE_URL | пусто |
| LLM_MODEL | gemma-4-12b-shield |
| LLM_API_KEY | пусто |
| LLM_TIMEOUT_MS | 2500 |
| LLM_FALLBACK_BASE_URL / LLM_FALLBACK_MODEL | пусто / пусто |
| STT_BASE_URL / STT_API_KEY | пусто / пусто |
| STT_TIMEOUT_MS | 8000 |

LLM_BASE_URL и LLM_FALLBACK_BASE_URL — корень OpenAI API **с `/v1`**; STT_BASE_URL — адрес сервера **без `/v1`**. Адреса могут быть http/https в закрытой сети, без userinfo/query/fragment. Запасной LLM использует LLM_API_KEY, поскольку отдельного ключа нет в архитектуре; Ollama может игнорировать этот заголовок. Если запасной сервер требует иной ключ, L3 сначала расширяет конфигурацию. При пустом LLM URL C03 пропускает ступень; при пустом STT URL C06 скрывает микрофон. Включение URL сейчас ещё не подключает адаптер.

DEMO_MODE не назначает роль и не отменяет серверную авторизацию. Демо-токены, сид и PIN реализуют C02/C04; конфигурацию их выдачи нельзя считать уже реализованной. Старые облачные переменные не используются. Серверные ключи не выносятся в `VITE_*`, браузер, Git или логи. `.gitignore` исключает SQLite, звук, веса, адаптеры и `data/training/`.

## Зависимости

Прямые версии закреплены без диапазонов в pyproject.toml/package.json; доступность релизов и отсутствие prerelease-версий установлены по метаданным официальных реестров 12 ноября 2026. Это выбор версий, а не результат запуска приложения или проверки совместимости. Транзитивные Python-зависимости пока разрешаются установщиком, отдельный Python lock не создан. Написан frontend/package-lock.json: npm-дерево разрешено командой `npm install --package-lock-only --ignore-scripts --no-audit --no-fund`, без установки node_modules и запуска package scripts.

| Backend, Python 3.12 | Версия |
|---|---|
| FastAPI | 0.162.5 |
| Starlette | 1.10.0 |
| Uvicorn | 0.54.0 |
| websockets | 17.4 |
| SQLAlchemy | 2.1.8 |
| Pydantic / pydantic-settings | 2.14.3 / 2.16.2 |
| httpx / python-multipart | 0.28.1 / 0.0.33 |
| argon2-cffi / Hatchling | 25.1.0 / 1.33.0 |

| Frontend | Версия |
|---|---|
| React / react-dom | 19.3.1 / 19.3.1 |
| Vite / @vitejs/plugin-react | 8.3.8 / 6.3.0 |
| TypeScript | 7.0.2 |
| @types/react / @types/react-dom | 19.3.0 / 19.3.0 |
| @types/node | 22.20.5 |

Источники: [FastAPI/PyPI](https://pypi.org/pypi/fastapi/json), [Uvicorn](https://pypi.org/pypi/uvicorn/json), [SQLAlchemy](https://pypi.org/pypi/sqlalchemy/json), [Pydantic](https://pypi.org/pypi/pydantic/json), [pydantic-settings](https://pypi.org/pypi/pydantic-settings/json), [httpx](https://pypi.org/pypi/httpx/json), [python-multipart](https://pypi.org/pypi/python-multipart/json), [argon2-cffi](https://pypi.org/pypi/argon2-cffi/json), [Hatchling](https://pypi.org/pypi/hatchling/json), [React/npm](https://registry.npmjs.org/react/19.3.1), [react-dom](https://registry.npmjs.org/react-dom/19.3.1), [Vite](https://registry.npmjs.org/vite/8.3.8), [React plugin](https://registry.npmjs.org/@vitejs/plugin-react/6.3.0), [TypeScript](https://registry.npmjs.org/typescript/7.0.2), [React types](https://registry.npmjs.org/@types/react/19.3.0), [React DOM types](https://registry.npmjs.org/@types/react-dom/19.3.0), [Node types](https://registry.npmjs.org/@types/node/22.20.5).

Также: [Starlette/PyPI](https://pypi.org/pypi/starlette/json), [websockets/PyPI](https://pypi.org/pypi/websockets/json). Starlette закреплена явно, поскольку main.py использует её HTTPException; websockets обеспечивает будущий WS-транспорт Uvicorn без extras с незафиксированными дополнительными пакетами.

## Локальные модели

`backend/app/speech/classifier_prompt.txt` и `llm_schema.json` одинаково читают будущий адаптер C03 и скрипты M06–M08. Подсказка не меняется перед отправкой. Schema — голый объект JSON Schema; упаковку response_format, окно и проверку evidence описывает [API](docs/api.md). В ответе модели ровно шесть полей; status/source/model/session_id/segment_seq/received_at/uncertain добавляет сервер. Ни prompt, ни схема не принимают финансовых решений.

`ml/` — отдельное окружение для ПК с видеокартой, приложение его не импортирует. Скрипты замеров и обучения запускает пользователь. Имена моделей в исходных планах — кандидаты до проверки доступности M01/M10; написанная подсказка не доказывает качество или существование весов.

## Созданные файлы C01 и M02

26 новых файлов; TASKS.md и PROJECT_STATE.md обновлены отдельно, существующие планы и архитектура не переписаны.

```text
.env.example
.gitignore
README.md
backend/pyproject.toml
backend/app/__init__.py
backend/app/main.py
backend/app/config.py
backend/app/schemas.py
backend/app/api/__init__.py
backend/app/api/routes_health.py
backend/app/speech/classifier_prompt.txt
backend/app/speech/llm_schema.json
frontend/package.json
frontend/package-lock.json
frontend/tsconfig.json
frontend/vite.config.ts
frontend/index.html
frontend/src/main.tsx
frontend/src/App.tsx
frontend/src/shell.css
frontend/src/api/types.ts
frontend/src/components/contracts.ts
frontend/src/i18n/keys.ts
frontend/src/i18n/index.ts
docs/api.md
docs/ui-contracts.md
```
