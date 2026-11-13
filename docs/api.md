# API и данные «ИИ-щит»

Контракт C01, 12 ноября 2026. Источники: `ARCHITECTURE.md` (имеет приоритет), `MVP_SCOPE.md`, `backend/app/schemas.py`; ручное TypeScript-отражение — `frontend/src/api/types.ts`.

Сейчас написан маршрут `GET /api/health`. Остальные маршруты ниже — зафиксированный контракт для C02–C06, а не реализованные операции. Swagger текущего каркаса не заменяет этот документ: будущие маршруты туда пока не зарегистрированы. Код не запускался.

## Общие правила

- JSON UTF-8, поля `snake_case`. Дополнительные поля запрещены. `null` передаётся явно, кроме отмеченных необязательных входных полей. Строки текста не обрезаются и не нормализуются при приёме: иначе потеряются точные цитаты.
- `EntityId` — непрозрачная строка длиной 1–128; клиент не разбирает ID. Ревизии и `seq` — целые от 1 до `9007199254740991`, `last_seq`/`segment_seq` допускают 0, когда сегментов нет. Сервер отклоняет bool, дроби и числовые строки вместо целых.
- `Money` — положительное целое число тенге до `9007199254740991`. Балансы допускают 0. `balance_tenge` — средства до вычета резервов, `reserved_tenge` — резерв, `available_tenge` уже вычислен сервером. UI не вычисляет доступный остаток.
- Входные даты с часовым поясом; ответы — UTC ISO 8601 с `Z`. Отображение — Asia/Almaty, F02. `expected_revision` относится к объекту маршрута: переводу, запросу подтверждения или тревоге. Несовпадение → 409, затем новый snapshot. Победившее решение атомарно изменяет также связанный перевод.
- Язык текстов причин/вопросов — язык текущего снимка. `GET /api/snapshot?language=ru|kk` выбирает локализацию; не роль. По умолчанию `ru`. При смене языка snapshot запрашивается заново.
- Во всех ответах `X-Request-ID`, в ошибках также `request_id`. Клиент показывает локализованный текст по `code`; сырые исключения и произвольный `detail` не показываются.
- Только `/api/health` общедоступен. Остальные маршруты требуют `Authorization: Bearer <demo-role-token>`. Токен назначает роль и участника на сервере; путь экрана/поле JSON роль не назначают. Получение и хранение демо-токенов реализует C02/C04, не F-карточки. Токены не передавать в query URL. Веб-сокет использует первый кадр авторизации, см. ниже.
- Полные диалоги, PIN, ключи и аудио не журналировать. PIN не возвращать и не сохранять в открытом виде; текст и звук не класть в БД или файлы. После завершения сессии или 15 минут бездействия полный текст удаляется. Выбранные короткие доказательные фрагменты решения остаются до сброса демо; сильные признаки действуют ещё 5 минут после конца сессии.

## Перечисления

| Тип | Значения |
|---|---|
| Language | `ru`, `kk` |
| DialogueLanguage | `ru`, `kk`, `mixed` |
| Speaker | `caller`, `customer`, `unknown`; в файлах DemoDialogue только первые два |
| Role | `client`, `trusted`, `operator`, `demo` |
| TransferStatus | `ASSESSING`, `PAUSED`, `HELD`, `COMPLETED`, `REJECTED`, `CANCELLED` |
| RiskLevel | `low`, `medium`, `high` |
| SignalStatus / SignalSource | `ready`, `pending`, `unknown` / `llm`, `dictionary`, `none` |
| Scheme | `bank_security`, `relative_in_trouble`, `investment`, `marketplace`, `none` |
| ApprovalPolicy | `trusted_allowed`, `operator_required` |
| TransferAction | `answer`, `cancel` |
| ApprovalStatus | `PENDING`, `APPROVED`, `REJECTED`, `EXPIRED`, `CANCELLED` |
| AlertPriority / AlertKind | `medium`, `high` / `fraud_suspected`, `approval_expired`, `assessment_interrupted` |
| AlertStatus / AlertAction | `OPEN`, `RESOLVED` / `release`, `reject`, `mark_fraud` |
| QuestionId / AnswerValue | `recipient_known`, `request_context` / `yes`, `no`, `unsure` |
| SpeechState / AudioLanguage | `idle`, `recording`, `recognizing`, `error` / `ru`, `kk`, `auto` |
| PhraseFeature / PhraseContext | `urgency`, `secrecy`, `safe_account`, `impersonation` / `request`, `warning`, `quotation` |

`APPROVED` означает записанное «Да», а не гарантированное выполнение: при `operator_required` перевод остаётся HELD. `CANCELLED` у подтверждения означает, что запрос закрыт отменой/другим решением. EXPIRED не разрешает перевод. Для терминальных переводов `allowed_actions=[]`.

## Схемы результата

В таблицах поля обязательны, если явно не отмечено иное. `[]` — массив, `?` — допускается отсутствие поля; `| null` — допускается null.

| Схема | Точные поля |
|---|---|
| ClassifierResult | `scheme: Scheme`, `active_request: boolean`, `urgency: boolean`, `secrecy: boolean`, `safe_account_request: boolean`, `evidence: string[]` (0–3 фрагмента по 1–120 символов) |
| SpeechAssessment | Все поля ClassifierResult + `status: SignalStatus`, `source: SignalSource`, `model: string \| null`, `session_id: EntityId \| null`, `segment_seq: integer >=0`, `received_at: UTC`, `uncertain: boolean` |
| Reason | `code: ReasonCode`, `text: string` (1–500), `evidence?: string \| null` (1–120, если есть; по умолчанию null) |
| PauseQuestion | `id: QuestionId`, `text: string` (1–500) |
| RiskView | `level: RiskLevel`, `score: integer 0..100`, `policy: ApprovalPolicy`, `reasons: Reason[]`, `speech: SpeechAssessment`, `questions: PauseQuestion[]` |
| RecipientView | `id: EntityId`, `label: string` (1–200), `is_new: boolean` (из серверной истории COMPLETED) |
| CustomerView | `id: EntityId`, `label: string`, `balance_tenge: integer >=0`, `reserved_tenge: integer >=0`, `available_tenge: integer >=0` |
| TransferView | `id: EntityId`, `revision: Revision`, `amount_tenge: Money`, `recipient_id: EntityId`, `recipient_label: string`, `status: TransferStatus`, `risk: RiskView`, `allowed_actions: TransferAction[]`, `created_at: UTC`, `updated_at: UTC` |
| ApprovalView | `id: EntityId`, `revision: Revision`, `transfer_id: EntityId`, `transfer_revision: Revision`, `amount_tenge: Money`, `recipient_id: EntityId`, `recipient_label: string`, `status: ApprovalStatus`, `policy: ApprovalPolicy`, `expires_at: UTC`, `can_respond: boolean` |
| AlertView | `id: EntityId`, `revision: Revision`, `transfer_id: EntityId`, `transfer_revision: Revision`, `amount_tenge: Money`, `recipient_label: string`, `priority: AlertPriority`, `kind: AlertKind`, `reasons: Reason[]`, `status: AlertStatus`, `allowed_actions: AlertAction[]`, `created_at: UTC` |
| DialogueView | `id: EntityId`, `language: DialogueLanguage`, `status: active \| ended`, `last_seq: integer >=0`, `speech: SpeechAssessment` (полного текста здесь нет) |
| ErrorResponse | `code: ErrorCode`, `message: string` (безопасный общий текст), `request_id: string` |
| HealthResponse | `status: "ok"`, `llm: {available: boolean, model: string \| null}`, `stt: {available: boolean}` |

`uncertain` — добавленное метаполе словарного анализа: неоднозначный контекст. Это не седьмое поле вывода LLM. У валидного LLM `uncertain=false`; при неясном словарном контексте — true; при pending/unknown — true. `source=llm` требует `status=ready` и непустую фактически ответившую `model`; у dictionary/none `model=null`. Для pending/unknown источник `none`, `scheme=none`, все четыре bool false, `evidence=[]`; это отсутствие результата, а не заключение о безопасности. `session_id=null` допустим без сессии, `segment_seq=0` до первой реплики. Сохранённые сильные признаки после удаления полного текста хранятся отдельно сервером, не маскируются под новый готовый ответ.

`RiskView.score` — стартовый балл правил, не вероятность. Никогда не показывать его со знаком `%`. `questions=[]`, если вопросов нет. Reason.text приходит от сервера; evidence выводится обычным текстом, без HTML. При смене языка сервер повторно локализует причины. Логика порогов, критического правила и неполных данных реализуется C02/C03, не компонентами.

ReasonCode (каждому соответствует ключ `reason.<code>`):

```text
new_recipient, unusual_amount, active_urgent_request, secrecy_request,
safe_account_request, call_reported, remote_access_simulated,
strong_active_request, speech_pending, speech_unknown, dictionary_uncertain,
approval_expired, assessment_interrupted
```

ErrorCode (каждому соответствует ключ `errors.<code>`):

```text
invalid_request, invalid_amount, invalid_pin, insufficient_funds,
unauthorized, forbidden, not_found, method_not_allowed, idempotency_conflict,
revision_conflict, invalid_transition, approval_expired, dialogue_ended,
segment_conflict, demo_disabled, stt_unavailable, audio_invalid,
audio_too_large, internal_error
```

## Маршруты и команды

Пустой запрос — JSON `{}`, не `null`. Ответы без внешней обёртки `data`. Ошибки всех маршрутов — ErrorResponse.

| Маршрут | Роль | Запрос → успешный ответ | Статус / реализация |
|---|---|---|---|
| GET /api/health | любая | без тела → HealthResponse | 200 / C01 |
| GET /api/snapshot?language=ru | текущая | без тела → Snapshot | 200 / C04 |
| POST /api/dialogues | client | CreateDialogueRequest `{language}` → DialogueView | 201 / C03 |
| POST /api/dialogues/{id}/segments | client-владелец | AddSegmentRequest `{seq, speaker, text}` → SegmentResponse `{session_id, seq, accepted, speech}` | 200 / C03 |
| POST /api/dialogues/{id}/end | client-владелец | EndDialogueRequest `{}` → DialogueView | 200 / C03 |
| POST /api/transfers | client | CreateTransferRequest → TransferView; обязателен Idempotency-Key | 201 новый, 200 повтор / C02 |
| POST /api/transfers/{id}/answers | client-владелец | AnswerPauseRequest → TransferView | 200 / C02 |
| POST /api/transfers/{id}/cancel | client-владелец | CancelTransferRequest `{expected_revision}` → TransferView | 200 / C02 |
| POST /api/approvals/{id}/respond | назначенный trusted | RespondApprovalRequest `{expected_revision, approve}` → ApprovalView | 200 / C04 |
| POST /api/alerts/{id}/resolve | operator | ResolveAlertRequest `{expected_revision, action, note}` → AlertView | 200 / C04 |
| POST /api/demo/reset | demo, DEMO_MODE=true | ResetDemoRequest `{}` → ResetDemoResponse `{reset:true, snapshot_id}` | 200 / C04 |
| POST /api/demo/replay/{script_id} | demo, DEMO_MODE=true | ReplayDemoRequest `{}` → ReplayDemoResponse `{script_id, dialogue_id, status:"started"}` | 202 / C04 |
| PUT /api/demo/signals | demo, DEMO_MODE=true | DemoSignals → DemoSignals | 200 / C04 |
| POST /api/dialogues/{id}/audio | client-владелец | multipart, см. голос → AudioTranscriptionResponse | 200 / C06 |
| WS /ws | текущая | авторизация первым кадром, затем SnapshotChangedEvent | C04 |

Сервер не принимает role, balance, risk, score, policy, source=llm, allowed_actions или решение о списании в командах клиента.

### Создание и изменение перевода

CreateTransferRequest:

```json
{"amount_tenge":25000,"recipient_id":"recipient-demo-2","pin":"0000","language":"ru","dialogue_id":null}
```

`amount_tenge: Money`, `recipient_id: EntityId`, `pin: string` (4–6 ASCII-цифр; пример синтетический), `language: Language` обязательны; `dialogue_id?: EntityId | null` по умолчанию null. PIN никогда не возвращается. Его длина — формат, правильность проверяется серверным хешем в C02.

`Idempotency-Key` — UUID v4, один на неизменённую отправку формы. Область — actor + тип команды; после reset новая эпоха данных. Повтор с тем же содержимым возвращает текущее представление исходного перевода; тот же ключ с изменённым содержимым → 409 `idempotency_conflict`. Для сравнения содержимого нельзя сохранять открытый PIN. Клиент сохраняет ключ для сетевого повтора, но очищает PIN после завершённого действия/ухода со страницы. Изменение суммы, получателя, PIN, языка или dialogue_id до новой отправки создаёт новый ключ.

AnswerPauseRequest: `{expected_revision, answers:[{question_id, value}]}`. answers — 1–2 уникальных вопроса; сервис требует ответы именно на текущие questions. `recipient_known` спрашивает о личном знакомстве, `request_context` — об активном побуждении к переводу/коду/установке. Ответ клиента не отменяет сильные доказательные признаки. Note оператора — 1–500 символов, непустая после проверки пробелов сервисом; без PIN, полного текста разговора и персональных данных.

Допустимые переходы:

```text
ASSESSING → COMPLETED | PAUSED | HELD
PAUSED → COMPLETED | HELD | CANCELLED
HELD → COMPLETED | REJECTED | CANCELLED
```

`answer` доступно владельцу PAUSED, `cancel` — владельцу PAUSED/HELD. Источник истины — серверный allowed_actions; чтение статуса не разрешает клиенту придумывать действие. При COMPLETED резерв списывается один раз, при REJECTED/CANCELLED освобождается; ожидание/повтор не списывает повторно. После перезапуска ASSESSING становится HELD с `assessment_interrupted` и `operator_required`.

### Диалоги и модели

AddSegmentRequest: seq с 1, финальный text длиной 1–6000 символов, speaker caller/customer/unknown; пустой после проверки пробелов текст не принимается. Повтор одинаковых seq/speaker/text возвращает `accepted=false`; новое принятие — true. Тот же seq с иным содержимым → 409 `segment_conflict`. Для текстового входа seq должен быть следующим; передача с пропуском → 409. Голосовая пустая транскрипция завершает обработку своего audio seq без создания текстового сегмента, поэтому следующие аудиофразы могут иметь пропуски относительно текстовых сегментов. Последовательность аудио контролирует C06, last_seq — наибольший принятый текстовый seq. Конец сессии повторяем, добавление новых реплик после него → 409 `dialogue_ended`.

Окно LLM: взять последние 40 принятых сегментов, собрать `— <text>` через `\n` без speaker, оставить последние 6000 символов полученной строки. Отсечение с начала может оставить неполную первую строку. Поле request_seq из обучающих данных в запрос модели не передаётся.

Системное сообщение — дословно файл M02; temperature=0, размышления выключены. `llm_schema.json` — сама JSON Schema, не response_format-обёртка. Адаптер/скрипты оборачивают её:

```text
response_format = {"type":"json_schema", "json_schema":{
  "name":"shield_classifier", "strict":true, "schema":<содержимое llm_schema.json>
}}
```

Вывод содержит только шесть полей ClassifierResult в объявленном порядке. Структурная ошибка → отказ ступени. Нормализация для evidence: каждую последовательность Unicode-пробелов заменить одним ASCII-пробелом, убрать пробелы по краям; регистр/буквы не менять. Проверять подстроку в том же окне. Несовпавшие evidence отбрасывать; цитаты не сочинять. Сильное доказательное правило требует сохранившихся цитат и однозначного контекста, а не одного слова.

Цепочка: основной LLM → запасной, если осталось ≥1000 мс → словарь → unknown. Общий срок DECISION_TIMEOUT_MS, основная попытка не дольше LLM_TIMEOUT_MS и остатка бюджета. model — реально ответившая модель. Логи не содержат запросы/ответы моделей. Код адаптера/фоновые проверки моделей раз в 15 секунд относятся к C03; в текущем C01 health отдаёт false/null до первой положительной проверки. `status=ok` означает доступность процесса приложения, не измеренное качество и не доступность моделей.

### Голос

`POST /api/dialogues/{id}/audio`: multipart `seq` (с 1), `language: ru|kk|auto`, `audio` (WAV PCM signed 16-bit little-endian, 16 кГц, моно). Фраза ≤8 секунд, пауза нарезки ≥600 мс. Лимит файла 300000 байт (с запасом на WAV-заголовок); превышение → 413 `audio_too_large`, неверный WAV/формат → 422 `audio_invalid`. Согласие обязательно в интерфейсе до открытия микрофона; источником является только демонстрационная сессия.

Ответ строго `{seq: integer, text: string, language: ru|kk}`. Пустой text не создаёт сегмент. Непустой добавляется в тот же DialogueService со speaker=unknown. Частичного текста нет, SpeechControls.partialText=""; во время запроса state=recognizing. Отказ STT → 503 `stt_unavailable`, текстовый вход остаётся доступен. Повтор audio seq обрабатывается без дублирования сегмента; контроллер C06 не посылает фразы параллельно. При подтверждении перевода уже отправленные фразы ждут в общем бюджете оценки, незавершённые учитываются как недостающие данные.

Сервер приложения пересылает в `STT_BASE_URL + /v1/audio/transcriptions`: multipart `file`, необязательный `language` (для auto поле не передавать); заголовок Authorization с STT_API_KEY. Внешний STT-ответ `{text:string, language:ru|kk, duration_ms:integer>=0}`. Аудио только в памяти на время запроса; `/api/stt/token` отсутствует. Браузеру не выдаются ключи или адреса моделей.

## Снимки и события

Общие поля Snapshot: `snapshot_id: EntityId` (новый непрозрачный ID версии видимого данной роли снимка), `server_time: UTC`, `language: Language`, `role` — дискриминатор.

| role | Дополнительные поля, без полей других ролей |
|---|---|
| client | `customer: CustomerView`, `recipients: RecipientView[]`, `transfers: TransferView[]`, `dialogue: DialogueView \| null` |
| trusted | `approvals: ApprovalView[]` (только адресованные ему) |
| operator | `alerts: AlertView[]` (без права создавать перевод) |
| demo | `signals: DemoSignals`, `scripts: DemoScriptView[]`, `active_dialogue_id: EntityId \| null` |

DemoSignals: `{call_reported:boolean, remote_access:boolean, source:"simulated"}`; PUT заменяет оба флага целиком. Они относятся к одному синтетическому клиенту демо. DemoScriptView: `{id: DemoScriptId, language: DialogueLanguage, intended_case:string}`. Пульт воспроизводит сегменты в новую сессию того же синтетического клиента через обычный DialogueService; `intended_case` в классификатор/скоринг не попадает. Уже активная сессия → 409 `invalid_transition`, сначала её завершить. Сброс удаляет операции, контекст, резервы, подтверждения и решения, затем восстанавливает синтетический сид; подтверждения/события прошлой эпохи недействительны. Публичного reset без демо-роли нет.

Для WS браузер открывает `/ws` и в течение 5 секунд посылает единственный кадр `{"type":"authenticate","token":"<demo-role-token>"}`. Нельзя передавать токен в URL. До проверки токена сервер не рассылает никаких данных. Неверный токен/кадр → закрытие 1008; токен и кадр не логируются. Это контракт будущего ws.py, не текущий маршрут.

Событие `SnapshotChangedEvent={type:"snapshot_changed", snapshot_id:EntityId, occurred_at:UTC}` содержит только указание перечитать снимок. Рассылка после commit и только ролям, чьи данные изменились. Дубликат/старое событие не является командой провести платёж. После открытия/восстановления WS и после 409 клиент всегда перечитывает snapshot. Для разрыва сети не требуется проигрывать историю событий.

## PhraseEntry — файлы F09/F10

Каждый файл — **JSON-массив** ровно из 16 объектов, не объект с полем entries. Серверная схема — PhraseEntry, TS — одноимённый интерфейс.

| Поле | Точное правило |
|---|---|
| id | ru-001…ru-016 или kk-001…kk-016; уникальный в файле, префикс совпадает с language |
| language | ru для ru.json, kk для kk.json; mixed здесь нет |
| scheme | Scheme; для этих наборов покрыть все четыре схемы, распределение — по четыре записи на схему |
| phrase | Непустая короткая буквальная фраза 1–120 символов; без regex и весов |
| feature | urgency / secrecy / safe_account / impersonation |
| context | request / warning / quotation |

Однозначное распределение для обеих карточек: 001–004 bank_security, 005–008 relative_in_trouble, 009–012 investment, 013–016 marketplace. В каждой группе первые две записи request, третья warning, четвёртая quotation. Всего 8 request, 4 warning, 4 quotation. Внутри схем выбирайте содержательные feature, весь файл покрывает все четыре feature; safe_account естественно относится прежде всего к bank_security. Контекст предупреждения/цитаты не меняет схему обсуждаемых слов: это словарный пример, не диагноз текущего разговора.

```json
{"id":"ru-001","language":"ru","scheme":"bank_security","phrase":"переведите деньги на безопасный счёт","feature":"safe_account","context":"request"}
```

Пример иллюстрирует формат, не заменяет 16 записей F09. Только синтетические фразы, без контактов и настоящих реквизитов. Словарь сам по себе не назначает балл, статус перевода или результат LLM; алгоритм C03 различает просьбу, предупреждение, цитату и uncertain.

## DemoDialogue — файлы F11

Каждый из шести файлов — **один JSON-объект**, без внешней обёртки. Не путать с обучающим JSONL M04/M05.

| Поле | Точное правило |
|---|---|
| id | Равно имени файла без .json: ru-fraud, ru-normal, kk-fraud, kk-normal, mixed-fraud, mixed-normal |
| language | ru / kk / mixed, совпадает с префиксом id |
| synthetic | Только JSON true |
| intended_case | Непустая строка 1–500 символов — описание ведущему; на языке сценария, для mixed допускается смешанный текст |
| segments | 4–8 объектов DemoSegment: seq, speaker, text, delay_ms |
| segments[].seq | 1…N подряд, без повторов и пропусков |
| segments[].speaker | caller / customer; unknown разрешён для живого STT, не для этих сценариев |
| segments[].text | 1–6000 символов, содержательная выдуманная реплика |
| segments[].delay_ms | Целое 500–1500; ожидание перед подачей соответствующего сегмента, включая первый |

F11 пишет ровно `data/demo/dialogues/{ru,kk,mixed}-{fraud,normal}.json`. Fraud содержит активную просьбу, давление и конкретные признаки схемы. Normal содержит срочность или обсуждение мошенников без активного обмана. Поля score, target, request_seq, expected_risk, predetermined_response запрещены в DemoDialogue. Ожидаемого ответа модели в этих файлах нет. Отдельная разметка учебного набора определена в плане M и не переносится сюда. Шесть диалогов показывают сценарии, не доказывают качество.

## Конфигурация и решения C01

Все имена/defaults таблицы ARCHITECTURE §6 сохранены в `.env.example` и Settings. `.env` читается из корня проекта; приложение запускать с корнем как cwd, чтобы SQLite default указывал на `data/app.db`. Секреты — SecretStr; дампы конфигурации не публиковать.

Дополнительно зафиксировано L3 (этого не было в исходных карточках):

1. URL LLM включает `/v1`, STT задаёт корень без `/v1`; адаптер не добавляет второй `/v1`. Запасной LLM использует тот же LLM_API_KEY: отдельного ключа в архитектуре нет. Если сервер требует иной ключ, изменение контракта выполняет L3 до подключения.
2. Явные ApprovalStatus/AlertStatus, Action, ReasonCode/ErrorCode, QuestionId/AnswerValue; поля revision и transfer_revision у подтверждений/тревог; risk содержит policy, speech и questions. `uncertain` принадлежит SpeechAssessment, не ответу модели.
3. Числа ограничены безопасным целым JS; PIN — 4–6 ASCII-цифр. UUID v4 для Idempotency-Key, ключ обновляется при изменении команды.
4. Ролевые дискриминированные снимки, безопасный первый WS-кадр, language-query; токены для seeded участников реализуются в C02/C04.
5. Ограничения длины текстов/заметок, аудиолимит, порядки seq/дедупликации; распределение словаря и точная структура F11.
6. Health каркаса возвращает false/null до фоновых проб C03.9; статус процесса не является подтверждением моделей. Реальные пробы остаются в C03, а не подменяются значением «URL настроен».

Неясности, требующие последующих данных: разные ключи основного/резервного LLM (если понадобятся); фактические model IDs и поддержка отключения размышлений каждым сервером (M01/M10/C03); способ выдачи демо-токенов пользователю в C02/C04; итоговая политика неполных данных и серверные критерии сильного признака в C02/C03. Ни один из этих вопросов не требует от F01–F12 проектирования или изменения общих файлов. Качество ru/kk/mixed и задержки пока не измерены.
