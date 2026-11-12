# Очередь проекта «ИИ-щит»

Дата: 12 ноября 2026. Планы и архитектура подготовлены, программная реализация не начата; proposed означает запланированную, ещё не начатую задачу.

Владелец — уровень агента: L3 высший, L2 средний, L1 мелкий. Разбиение, волны и условия старта — в docs/ARCHITECTURE.md, разделы 8–9. Развёрнутые условия — в карточках планов. Агентов запускает пользователь.

| ID | Приоритет | Задача и границы | Статус | Владелец | Файлы |
|---|---|---|---|---|---|
| P00 | P0 | Спецификация, основной план, сложные и мелкие карточки | done | Координатор | docs/MVP_SCOPE.md; docs/superpowers/plans/*.md |
| P01 | P0 | Архитектура с локальными моделями, план M, согласование прежних планов | done | Координатор | docs/ARCHITECTURE.md; docs/superpowers/plans/2026-11-12-local-models.md |
| C01 | P0 | Каркас и единые API/UI-контракты | proposed | L3 | backend/app/{main,config,schemas}.py; frontend/src/{api/types,components/contracts}.ts; конфигурация; docs/{api,ui-contracts}.md |
| C02 | P0 | Перевод, резерв, правила, идемпотентность | proposed | L3 | backend/app/{db,models,auth}.py; transfers/; risk/; demo/seed.py; api/routes_transfers.py |
| C03 | P0 | Текстовый ИИ: локальный LLM, цепочка отказов, словарь, версии сигналов | proposed | L3 | backend/app/speech/*.py; api/routes_dialogues.py; transfers/service.py; risk/ |
| C04 | P0 | Доверенный, оператор, роли, события | proposed | L3 | backend/app/{approvals,alerts,api,demo}/; events.py; auth.py; transfers/service.py; frontend/src/api/ |
| C05 | P0 | Сборка полного текстового MVP | proposed | L3; страницы доверенного и оператора — L2 | frontend/src/{pages,api}/; App.tsx; main.tsx; i18n/index.ts |
| C06 | P1 | Голос через локальный Whisper | proposed | L3 + L2 | backend/app/speech/stt_client.py; api/routes_stt.py; frontend/src/stt/; contracts.ts; ClientPage.tsx |
| C07 | P0 | Инструкция и конфигурация поставки | proposed | L2 | Makefile; Dockerfile; docker-compose.yml; README.md; docs/runbook.md |
| F01 | P0 | Базовые стили, только CSS | proposed | L1 | frontend/src/styles/{tokens,base}.css |
| F02 | P0 | Форматирование денег и времени | proposed | L1 | frontend/src/lib/format.ts |
| F03 | P0 | Управляемая форма перевода | proposed | L1 | frontend/src/components/TransferForm.tsx |
| F04 | P0 | Представление риска и причин | proposed | L1 | frontend/src/components/RiskNotice.tsx |
| F05 | P0 | Карточка доверенного | proposed | L1 | frontend/src/components/ApprovalCard.tsx |
| F06 | P0 | Карточка оператора | proposed | L1 | frontend/src/components/AlertCard.tsx |
| F07 | P0 | Русские тексты по фиксированным ключам | proposed | L1 | frontend/src/i18n/ru.json |
| F08 | P0 | Казахские тексты, черновик для вычитки | proposed | L2 | frontend/src/i18n/kk.json |
| F09 | P0 | Русские примеры признаков и отрицаний | proposed | L1 | backend/app/speech/phrases/ru.json |
| F10 | P0 | Казахские примеры признаков и отрицаний | proposed | L2 | backend/app/speech/phrases/kk.json |
| F11 | P0 | Шесть синтетических демо-диалогов | proposed | L2 | data/demo/dialogues/*.json |
| F12 | P1 | Интерфейс микрофона и согласия | proposed | L1 | frontend/src/components/SpeechControls.tsx |
| F13 | P0 | Сценарий для спикеров | proposed | L2 | docs/demo-script.md |
| M01 | P0 | Инструкция установки и запуска моделей на ПК | proposed | L2 | ml/README.md; ml/requirements.txt |
| M02 | P0 | Подсказка и схема классификатора | proposed | L3 | backend/app/speech/{classifier_prompt.txt,llm_schema.json} |
| M04 | P0 | 24 пакета обучающих диалогов по 50 | proposed | L1 (ru); L2 (kk, mixed) | data/training/raw/*.jsonl |
| M05 | P0 | Инструкция разметки; тест из 120 диалогов пишут люди | proposed | L1 + сокомандники | docs/labeling-guide.md; data/evaluation/test.jsonl |
| M06 | P0 | Сборка обучающего набора | proposed | L2 | ml/data_gen/build_dataset.py |
| M07 | P0 | Скрипт замера качества | proposed | L2 | ml/eval/run_eval.py |
| M08 | P0 | Скрипт дообучения QLoRA и выгрузки GGUF | proposed | L3 | ml/train/{train_qlora.py,README.md} |
| M09 | P1 | Сервер распознавания речи | proposed | L2 | ml/serve/stt_server.py |
| M10 | P0 | Запуски на ПК: проверка, замеры, обучение, серверы | proposed | Пользователь | ml/eval/reports/; ml/out/ |
| E01 | P2 | Экспериментальный SOS после MVP | proposed | L3 | будущий отдельный модуль, пути определяются при открытии задачи |
| E03 | P2 | CatBoost при доказуемом дополнительном вкладе | proposed | L3 | будущий ml/ |
| E04 | P2 | Отдельный детектор дипфейков | proposed | L3 | будущий deepfake/ |
| E05 | P2 | Нативные сигналы Android | proposed | L3 | будущий android/ |
| E06 | P2 | Банковский пилот и настоящая интеграция | proposed | L3 / банк | отдельный план после появления требований |

E02 (измерение качества) перенесено в M04–M07 и M10; E07 (локальное распознавание) — в C06 и M09.
