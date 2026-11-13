# UI-контракты для C01 и F01–F13

12 ноября 2026. Типы данных: `frontend/src/api/types.ts`; единственные props: `frontend/src/components/contracts.ts`; ключи: `frontend/src/i18n/keys.ts` (`messageSpec`, `Messages`, `MessageKey`, `MessageParams`, `Translate`). Эти общие файлы меняет L3. L1/L2 пишут только файлы своей карточки. Компоненты экспортируются как **default function с именем компонента** и принимают один объект соответствующего Props. Новых библиотек нет.

## Оболочка и общий принцип

Написаны адреса `/client`, `/trusted`, `/operator`, `/demo`. `/` показывает оболочку клиента. Пока это описания будущих экранов, без операций/сетевых имитаций. Переход между адресами — обычная ссылка, дополнительный router не нужен. Выбор адреса не авторизует роль.

Оформление использует заданную проектом палитру, системный шрифт 18px, ограничение 1120px и мобильную колонку. `shell.css` обслуживает только C01; файлы F01 подключатся через уже объявленные eager glob в main.tsx. Никаких сторонних шрифтов, метрик или вымышленных балансов. C05 соединит реальные компоненты и API. Основные классы F01 могут применяться компонентами уже при написании.

Компоненты управляемые: props → отображение, callbacks → намерение пользователя. Нет API, роутера, localStorage, скоринга или смены статуса. Родитель передаёт `busy`, локализованную `error: string|null` и стабильные callbacks, сам выполняет действие и обновляет snapshot. Callback возвращает void: компонент не ожидает Promise и не придумывает состояние успеха. Async-обработчик страницы ловит ошибку и передаёт её через props.

Ошибки API отображаются по `errors.<code>`, неизвестная/сетевая — `common.networkError` или безопасный общий текст. Request ID можно показать через common.requestId. Нельзя показывать сырые исключения и делать автоматические повторы решений после ошибки. Render-boundary C01 показывает общий текст и перезагрузку, не exception.message.

## F01: CSS

Точные классы: `page`, `stack`, `grid`, `card`, `field`, `field-label`, `field-input`, `hint`, `button`, `button-primary`, `button-danger`, `button-secondary`, `notice`, `notice-low`, `notice-medium`, `notice-high`, `badge`, `actions`, `sr-only`. `grid` переходит в одну колонку на узком экране; `page` ограничена 1120px. Никакие компоненты F не добавляют собственные CSS-файлы.

Переменные в tokens.css:

| Переменная | Значение |
|---|---|
| --color-bg / --color-surface / --color-text | #F5F7FA / #FFFFFF / #172033 |
| --color-muted / --color-border / --color-accent | #526079 / #D3D9E1 / #135E73 |
| --color-low / --color-medium / --color-high | #166534 / #92400E / #991B1B |
| --space-1 / --space-2 / --space-3 / --space-4 / --space-6 / --space-8 | 4px / 8px / 12px / 16px / 24px / 32px |
| --radius-sm / --radius-md / --radius-lg | 6px / 10px / 14px |
| --font-body / --font-size-base / --content-width | system-ui, sans-serif / 18px / 1120px |
| --focus-ring | 3px solid #135E73 |

base.css задаёт body, заголовки, формы, перечисленные классы, видимый focus-visible, disabled, перенос длинных строк и reduced-motion. Уровень состояния всегда подписан текстом. `button` дополняется одним из primary/danger/secondary; `notice` — классом уровня. Скрытые подписи — sr-only. Порядок подключения tokens → base; shell имеет только префикс shell, кроме базового шрифта/box-sizing/body.

## F02: форматирование

Файл `frontend/src/lib/format.ts`, именованные экспорты:

```ts
formatMoney(amountTenge: number, lang: Language): string
formatTime(isoUtc: string, lang: Language): string
```

Импорт Language через `import type { Language } from "../api/types"`. Локали ru-KZ и kk-KZ, валюта KZT, дробных знаков 0. Время Asia/Almaty, hour/minute двухзначные, 24 часа. Некорректное/нечисловое значение → `—`. Нет преобразования amountText или вычислений баланса. F05/F06 импортируют `../lib/format`; пока F02 не записан, они ждут только его файл.

## F03: TransferFormProps

`recipients: readonly RecipientView[]`, `amountText: string`, `recipientId: string`, `pin: string`, `busy: boolean`, `error: string|null`, `labels: TransferFormLabels`.

Callbacks: `onAmountChange(value:string):void`, `onRecipientChange(value:string):void`, `onPinChange(value:string):void`, `onSubmit():void`. Обработчик submit предотвращает обычную отправку формы и вызывает onSubmit; не передаёт React event. Если busy, не вызывает callback повторно. Все поля и кнопка отключены при busy. У суммы input type=text, inputMode=numeric: исходная строка остаётся строкой; у PIN type=password, inputMode=numeric, autoComplete=off, без автозаполнения настоящих данных. Допустимы семантические required/описания, собственных денежных правил нет.

| labels | Ключ t |
|---|---|
| title | transfer.title |
| recipient / recipientPlaceholder | transfer.recipient / transfer.recipientPlaceholder |
| amount / amountHint | transfer.amount / transfer.amountHint |
| pin / pinHint | transfer.pin / transfer.pinHint |
| submit / submitting | transfer.submit / transfer.submitting |

Текст option — recipient.label, value — recipient.id. Пустая option с recipientPlaceholder. Использовать useId для label/htmlFor; error — role=alert, hint связан aria-describedby. Отправка Enter поддерживается обычной form. Никакого хранения PIN вне входного prop и состояния родительской формы.

## F04: RiskNoticeProps

`level: RiskLevel`, `levelLabel: string`, `reasons: readonly Reason[]`, `sourceLabel: string`, `dataStatusLabel: string`, `title: string`, `scoreLabel?: string`, `emptyReasonsLabel: string`, `evidenceLabel: string`. Callbacks отсутствуют.

Parent передаёт title=t(risk.title), levelLabel=t(risk.level.<level>), emptyReasonsLabel=t(risk.emptyReasons), evidenceLabel=t(risk.evidence). sourceLabel — t(signal.source.<source>); при llm родитель добавляет t(risk.sourceModel,{model}) с фактической model. dataStatusLabel — t(signal.status.<status>); при uncertain добавляется t(reason.dictionary_uncertain). scoreLabel, если нужен, целиком подготовлен страницей через t(risk.score,{score}), без `%`.

Класс `notice notice-${level}`, текстовый levelLabel обязателен. Причины — список reason.text, при наличии reason.evidence — текстовая цитата с evidenceLabel. Не показывать пустые/null evidence. Нет причин → emptyReasonsLabel. Отсутствующий scoreLabel не заменять баллом/нулём. Сырые HTML-вставки запрещены. Никаких выводов «безопасно» из unknown.

## F05: ApprovalCardProps

`approval: ApprovalView`, `language: Language`, `busy: boolean`, `error: string|null`, `labels: ApprovalCardLabels`; `onRespond(approvalId:string, approve:boolean):void`.

| labels | Ключ/набор ключей |
|---|---|
| title / amount / recipient | approval.title / approval.amount / approval.recipient |
| question / expiresAt | approval.question / approval.expiresAt |
| approve / reject / responding | approval.approve / approval.reject / approval.responding |
| status | Record<ApprovalStatus,string>, `approval.status.<STATUS>` для всех 5 значений |
| operatorRequired | approval.operatorRequired |

Показать labels.status[approval.status], сумму formatMoney(approval.amount_tenge,language), recipient_label, вопрос, formatTime(expires_at,language). При policy=operator_required показать operatorRequired. Кнопки только если approval.can_respond; при busy disabled и видим responding. «Да» передаёт true, «Нет» false. Компонент не сравнивает expires_at с локальными часами, не правит approval и не проводит деньги. Страница C05 подставит approval.revision в API-команду; callback компонента ревизию не принимает.

## F06: AlertCardProps

`alert: AlertView`, `language: Language`, `labels: AlertCardLabels`, `busy: boolean`, `error: string|null`; `onResolve(alertId:string, action:AlertAction, note:string):void`.

| labels | Ключ/набор ключей |
|---|---|
| title / transferId / amount / recipient | alert.title / alert.transferId / alert.amount / alert.recipient |
| priority | Record<AlertPriority,string>, `alert.priority.medium/high` |
| kind | Record<AlertKind,string>, `alert.kind.<kind>` для всех 3 значений |
| status | Record<AlertStatus,string>, `alert.status.OPEN/RESOLVED` |
| actions | Record<AlertAction,string>, `alert.action.release/reject/mark_fraud` |
| note / noteHint / noActions / resolving | alert.note / alert.noteHint / alert.noActions / alert.resolving |
| reasons / emptyReasons / evidence | alert.reasons / alert.emptyReasons / alert.evidence |

Идентификатор alert.transfer_id, подписи через Record; сумма через F02. Причины/evidence обычным текстом; пустой список → labels.emptyReasons. Компонент вправе хранить только редактируемый note (`useState`), не результат операции. При смене alert.id очищает note. textarea с maxLength=500, label/aria-describedby. Кнопки создаёт только по alert.allowed_actions, каждая вызывает onResolve с текущим note. Пустая после trim заметка и busy отключают кнопки как UX; окончательная проверка заметки/прав на сервере. Пустые действия → noActions. Ошибка не повторяет callback и не очищает заметку; серверные статусы не меняются локально. Страница подставит alert.revision.

## F07/F08: локализация

Файлы — плоские JSON-объекты `Record<MessageKey,string>`: ключи с точками буквально, **без вложенных объектов**, комментариев, новых ключей и служебных заметок. Заполнить каждый ключ messageSpec из keys.ts. `description` объясняет смысл на русском; для kk переводится смысл, а не имя ключа. Возвращаемые сервером Reason.text/PauseQuestion.text не переводятся компонентом повторно. Название продукта можно сохранить ИИ-щит в обоих языках.

Подстановки заданы только в `messageSpec[key].params`. Точный синтаксис и имена:

| Ключ | Подстановки |
|---|---|
| common.requestId | {requestId} |
| risk.score | {score} |
| risk.sourceModel | {model} |
| transfer.operationId | {transferId} |
| demo.replayStarted | {scriptId} |

У всех остальных ключей подстановок нет. Их добавлять нельзя. Источники, схемы, причины, ошибки, все статусы и состояния микрофона уже объявлены; не удалять даже не используемый оболочкой ключ. Нет процентов, обещаний полной защиты и формулировок «мошенник установлен». Приватность: сервер команды, без сторонних сервисов, звук без записи; короткие evidence остаются до demo reset. Казахский текст — черновик, сомнительные фразы сообщаются исполнителем отдельно.

```ts
import { createTranslator } from "../i18n";
const t = createTranslator("ru");
t("transfer.submit");
t("risk.score", { score: 70 });
```

`createTranslator` интерполирует обычные строки, не HTML. Пока F07/F08 отсутствуют, C01 использует короткие тексты только для оболочки; отсутствующий будущий ключ показывается как `[key]`, без скрытой подмены казахского русским. Eager glob уже подхватит ru.json и kk.json при их создании. Для новых ключей сначала обращаются к L3.

## F09/F10/F11: данные

Точные схемы, ограничения и распределение записей — [api.md](./api.md), разделы PhraseEntry и DemoDialogue. Python/TS-типы уже объявлены. В файлах не используются локализованные label/score/status и не хранится ответ модели. Это готовые задания на содержимое, без алгоритмов или новых контрактов.

## F12: SpeechControlsProps

Контракт C06.1 зафиксирован заранее в C01, чтобы F12 мог написать изолированный UI. Сам голос, согласие на уровне страницы, STT-маршрут и hook остаются C06. Состояния: idle, recording, recognizing, error; отдельного pending нет.

`consent:boolean`, `state:SpeechState`, `partialText:string`, `finalText:string`, `error:string|null`, `labels:SpeechControlsLabels`; callbacks `onConsentChange(value:boolean):void`, `onStart():void`, `onStop():void`.

| labels | Ключ/набор ключей |
|---|---|
| title / consent / privacy | speech.title / speech.consent / speech.privacy |
| start / stop | speech.start / speech.stop |
| partialText / finalText | speech.partialText / speech.finalText |
| state | Record<SpeechState,string>, `speech.state.<state>` для всех 4 значений |

Checkbox управляется consent и onConsentChange. Начало доступно при consent=true и state=idle/error. В recording/recognizing начало disabled, остановка доступна и вызывает onStop (включая отмену очереди). Checkbox не блокируется при записи: снятие согласия вызывает callback, а родитель C06 закрывает микрофон и очередь. В idle/error остановка disabled. Компонент показывает labels.state[state], явный текстовый индикатор записи, privacy и error (role=alert). finalText/partialText показываются только при непустой строке с отдельными подписями, обновления через aria-live=polite. В текущей версии partialText всегда ""; состояние recognizing показывает ожидание STT. Компонент не использует getUserMedia, HTTP, ключи или аудиобуфер. При пустом STT_BASE_URL родитель скрывает весь компонент.

## F13 и границы готовности

F13 описывает фактически реализованный C05, не текущую оболочку. До C05 карточка не ready. Голос включается в сценарий только после C06. Баллы правил не являются измеренной вероятностью, шесть F11 не являются оценкой качества, обработка сторонних звонков не обещается.

Решения L3 сверх исходных карточек: именованные вложенные Labels и их Record-наборы; дополнительные levelLabel/emptyReasonsLabel/evidenceLabel F04; callback всегда void; controlled error=null; поведение busy/пустых заметок/согласия; точные CSS tokens и плоский словарь с параметрами. Эти решения приняты для автономного выполнения F без изменения общих файлов. Неясных имён props/ключей/полей для F01–F12 не осталось; подключение к сервисам относится к C02–C06.
