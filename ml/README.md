# ПК моделей: установка и порядок M10

Инструкция для Windows с RTX 5080 16 ГБ. Сборка данных и обучение идут в **Ubuntu в WSL2**; два сервера моделей запускаются в **Windows**, чтобы к ним подключался ноутбук через Tailscale. Команды ниже выполняет пользователь на ПК, а не агент. Качество моделей и фактическое потребление памяти пока не измерены.

В примерах проект находится в `C:\AI-Shield\project`, модели для Windows — в `C:\AI-Shield\models`, программа llama.cpp — в `C:\AI-Shield\llama`. Эта же папка проекта доступна в WSL как `/mnt/c/AI-Shield/project`. Веса, виртуальные окружения, аудио и ключи держите вне Git; настоящий текст разговоров и настоящие банковские данные в примерах не используйте.

**Состояние зависимостей проекта:** при написании инструкции `ml/serve/stt_server.py` (M09), `ml/data_gen/build_dataset.py` (M06), `ml/eval/run_eval.py` (M07) и `ml/train/train_qlora.py` (M08) ещё не были готовы. Команды для них соответствуют карточкам, но их экспорт `app`, совместимость пакетов и фактический запуск нужно **проверить при запуске** после получения этих файлов. Тестовый набор M05 пишут люди: требуется `data/evaluation/test.jsonl`. Обучающие пакеты M04 должны быть скопированы в `data/training/raw/`; они исключены из Git.

## 1. Windows, WSL2 и расположение проекта

1. Установите актуальный [драйвер NVIDIA для Windows](https://www.nvidia.com/Download/index.aspx) для RTX 5080 и перезагрузите ПК. В WSL отдельный драйвер NVIDIA **не** устанавливайте: используется драйвер Windows ([руководство NVIDIA](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)).
2. Откройте PowerShell **от имени администратора**, выполните команду и перезагрузите ПК, если Windows попросит:

   ```powershell
   wsl --install -d Ubuntu-24.04
   ```

   После перезагрузки откройте Ubuntu 24.04 из меню «Пуск», создайте пользователя и пароль Linux. Если WSL уже установлен, команду повторять не нужно; проверьте в PowerShell `wsl --list --verbose`: у Ubuntu должна быть версия 2. Подробности — в [документации Microsoft](https://learn.microsoft.com/en-us/windows/wsl/install).
3. В обычном PowerShell создайте папки, затем скопируйте **содержимое существующего проекта** в `C:\AI-Shield\project` через Проводник. В корне должны находиться `AGENTS.md`, `ml` и `docs`. Скопируйте также нужные локальные обучающие данные, которых нет в Git. Не копируйте чужие `.env`, ключи и реальные разговоры.

   ```powershell
   New-Item -ItemType Directory -Force C:\AI-Shield\project, C:\AI-Shield\models, C:\AI-Shield\llama, C:\AI-Shield\venvs
   ```

4. Установите Python 3.12 x64 для Windows с [python.org](https://www.python.org/downloads/windows/) и установите [Tailscale](https://tailscale.com/download) на ПК и на ноутбук. Войдите на обоих устройствах в одну разрешённую сеть Tailscale. В Windows-пакете Python должен быть установлен launcher `py`.

## 2. Установка окружения обучения в WSL2

Следующий блок выполняйте в **Ubuntu**, не в PowerShell. На Ubuntu 24.04 команды используют Python 3.12. Папка окружения находится в домашнем каталоге Linux, отдельно от проекта.

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip git build-essential
python3.12 -m venv ~/shield-ml-env
source ~/shield-ml-env/bin/activate
cd /mnt/c/AI-Shield/project
python -m pip install --upgrade pip uv
uv pip install -r ml/requirements.txt --torch-backend=cu128
```

Установка [Unsloth Core через `uv`](https://unsloth.ai/docs/get-started/install/pip-install) и `--torch-backend` соответствуют документации Unsloth и [uv](https://docs.astral.sh/uv/guides/integration/pytorch/). В `requirements.txt` PyTorch 2.11.0, torchvision 0.26.0 и torchaudio 2.11.0 закреплены по [таблице PyTorch](https://pytorch.org/get-started/previous-versions/) для CUDA 12.8; остальные версии не закреплены. Сочетание пакетов с конкретной версией M08 и видеодрайвером — **проверить при запуске**. Если установка завершилась ошибкой, не продолжайте до её устранения.

Для последующих команд в новом окне Ubuntu снова выполняйте:

```bash
source ~/shield-ml-env/bin/activate
cd /mnt/c/AI-Shield/project
```

Подготовьте модель для обучения и исходный GGUF для Windows. Скачивание займёт значительное место и время. Если Hugging Face запросит авторизацию или принятие условий модели, откройте страницу модели и выполните `hf auth login` в Ubuntu; не вставляйте токен в файл проекта.

```bash
hf download google/gemma-4-12B-it
hf download unsloth/gemma-4-12b-it-GGUF gemma-4-12b-it-Q4_K_M.gguf --local-dir /mnt/c/AI-Shield/models
```

Первая команда кладёт веса в кэш Hugging Face внутри WSL; скрипт M08 должен использовать идентификатор `google/gemma-4-12B-it`. Вторая кладёт исходный GGUF в Windows-папку `C:\AI-Shield\models`. Имя файла сверено с [репозиторием Unsloth](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF/tree/main); инструкция для Gemma 4 — [Unsloth](https://unsloth.ai/docs/models/gemma-4/train). Если версия `hf` отличается, см. [документацию CLI](https://huggingface.co/docs/huggingface_hub/guides/cli).

## 3. Окружение STT в Windows и модели Whisper

Все следующие команды этого раздела выполняйте в **обычном PowerShell Windows**:

```powershell
py -3.12 -m venv C:\AI-Shield\venvs\win
$WinPy = 'C:\AI-Shield\venvs\win\Scripts\python.exe'
& $WinPy -m pip install --upgrade pip
& $WinPy -m pip install torch==2.11.0 torchvision==0.26.0 torchaudio==2.11.0 --index-url https://download.pytorch.org/whl/cu128
& $WinPy -m pip install -r C:\AI-Shield\project\ml\requirements.txt
& C:\AI-Shield\venvs\win\Scripts\hf.exe download openai/whisper-large-v3-turbo
```

Колёса `cu128` нужны для RTX 5080; Unsloth в Windows по маркеру из `requirements.txt` не устанавливается. CUDA-сборка llama.cpp ниже самостоятельна и может использовать другой выпуск CUDA. Совместимость фактически установленных библиотек и M09 — **проверить при запуске**.

Вторая модель необязательна. Идентификатор `issai/whisper-turbo`, приведённый как кандидат в плане, подтвердить не удалось. Указанный в архитектуре запасной кандидат существует: [abilmansplus/whisper-turbo-ksc2](https://huggingface.co/abilmansplus/whisper-turbo-ksc2), дообучен на казахском корпусе ISSAI; это не публикация самого ISSAI. Скачать его для сравнения можно командой:

```powershell
& C:\AI-Shield\venvs\win\Scripts\hf.exe download abilmansplus/whisper-turbo-ksc2
```

Начинайте с исходного `openai/whisper-large-v3-turbo` без второй модели. Включайте кандидат только после M10.1 и сравнения на своих синтетических фразах. Качество на казахском и смешанной речи для этого проекта неизвестно.

## 4. Готовая CUDA-сборка llama.cpp в Windows

Откройте [релизы llama.cpp](https://github.com/ggml-org/llama.cpp/releases), выберите актуальный выпуск с поддержкой Gemma 4 и скачайте два архива **из одного выпуска**: `Windows x64 (CUDA 13)` и соответствующие `CUDA 13.x DLLs`. Распакуйте содержимое обоих в `C:\AI-Shield\llama`, так чтобы `llama-server.exe` и CUDA DLL лежали в одной папке. Если архив создаёт внутреннюю папку, перенесите её содержимое на этот уровень. Сборка и драйвер для RTX 5080 — **проверить при запуске**.

## 5. Ключи и запуск двух серверов

На обоих устройствах должен быть включён Tailscale. В одном **обычном PowerShell Windows** выполните блок: он получает адрес ПК в Tailscale и создаёт два независимых случайных ключа только в окружении текущего окна. Строки с ключами потребуются в `.env` ноутбука; не записывайте их в проектные документы, Git, журналы или скриншоты.

```powershell
$env:SHIELD_PC_IP = (& "$env:ProgramFiles\Tailscale\tailscale.exe" ip -4 | Select-Object -First 1).Trim()
if (-not $env:SHIELD_PC_IP) { throw 'Подключите этот ПК к Tailscale' }
$Rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$Bytes = New-Object byte[] 32
$Rng.GetBytes($Bytes)
$env:LLAMA_API_KEY = -join ($Bytes | ForEach-Object { $_.ToString('x2') })
$Rng.GetBytes($Bytes)
$env:STT_API_KEY = -join ($Bytes | ForEach-Object { $_.ToString('x2') })
$Rng.Dispose()
$env:STT_MODEL_DEFAULT = 'openai/whisper-large-v3-turbo'
$env:STT_MODEL_KK = ''
$env:SHIELD_GGUF = 'C:\AI-Shield\models\gemma-4-12b-it-Q4_K_M.gguf'
Write-Host "Адрес ПК в Tailscale: $env:SHIELD_PC_IP"
Write-Host "LLM_API_KEY=$env:LLAMA_API_KEY"
Write-Host "STT_API_KEY=$env:STT_API_KEY"
Start-Process powershell.exe -ArgumentList '-NoExit'
Start-Process powershell.exe -ArgumentList '-NoExit'
```

Откроются два дочерних PowerShell-окна, наследующих эти переменные. Оставьте исходное окно открытым: в нём можно запустить новые дочерние окна с теми же ключами. При новом создании ключей их нужно заново внести в `.env` ноутбука. Для сохранения между перезагрузками используйте защищённое хранилище пользователя и при следующем запуске задайте `LLAMA_API_KEY` и `STT_API_KEY` в исходном окне до создания дочерних окон.

В **первом дочернем окне Windows** запустите LLM:

```powershell
Set-Location C:\AI-Shield\llama
.\llama-server.exe --model $env:SHIELD_GGUF --alias gemma-4-12b-shield --host $env:SHIELD_PC_IP --port 8080 --n-gpu-layers all --ctx-size 8192 --parallel 1 --jinja --reasoning off --no-webui --log-disable
```

`LLAMA_API_KEY` читается сервером из окружения: передавать ключ в аргументе не нужно. Доступ ограничен адресом интерфейса Tailscale; `--log-disable` выключает журнал llama.cpp. Значения `--alias`, `--n-gpu-layers all`, `--ctx-size`, `--reasoning off` и переменная ключа сверены с [документацией llama-server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md). Шаблон чата берётся из GGUF. Поддержку конкретной модели, шаблона и структурированного ответа этой сборкой нужно **проверить при запуске**.

Во **втором дочернем окне Windows**, после готовности M09, запустите STT:

```powershell
Set-Location C:\AI-Shield\project
& C:\AI-Shield\venvs\win\Scripts\python.exe -m uvicorn ml.serve.stt_server:app --host $env:SHIELD_PC_IP --port 8081 --no-access-log
```

Окна серверов должны оставаться открытыми. Для отключения используйте `Ctrl+C` в соответствующем окне. Если M10.1 покажет, что казахский кандидат нужен, остановите STT, задайте во втором окне `$env:STT_MODEL_KK = 'abilmansplus/whisper-turbo-ksc2'` и снова запустите команду STT. При `language=auto` язык сначала определяет исходная модель; при обнаруженном `kk` M09 должен использовать заданную казахскую модель.

### Ручной запрос к обоим серверам

В исходном PowerShell после загрузки моделей отправьте синтетический текстовый запрос:

```powershell
$Headers = @{ Authorization = "Bearer $env:LLAMA_API_KEY" }
$Body = @{ model = 'gemma-4-12b-shield'; messages = @(@{ role = 'user'; content = 'Ответь одним словом: привет.' }); temperature = 0; max_tokens = 64 } | ConvertTo-Json -Depth 6 -Compress
Invoke-RestMethod -Method Post -Uri "http://$($env:SHIELD_PC_IP):8080/v1/chat/completions" -Headers $Headers -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes($Body))
Invoke-RestMethod -Uri "http://$($env:SHIELD_PC_IP):8081/health"
```

Для голосового запроса подключите микрофон, разрешите его использование в Windows и произнесите короткую выдуманную фразу. Код удерживает WAV только в памяти; он не создаёт файл с аудио. При необходимости повторите для пяти казахских фраз.

```powershell
$env:SHIELD_STT_URL = "http://$($env:SHIELD_PC_IP):8081"
$Record = @'
import io
import os
import requests
import sounddevice as sd
import soundfile as sf

print("Говорите: запись 5 секунд...")
audio = sd.rec(5 * 16000, samplerate=16000, channels=1, dtype="int16")
sd.wait()
wav = io.BytesIO()
sf.write(wav, audio, 16000, format="WAV", subtype="PCM_16")
wav.seek(0)
response = requests.post(
    os.environ["SHIELD_STT_URL"] + "/v1/audio/transcriptions",
    headers={"Authorization": "Bearer " + os.environ["STT_API_KEY"]},
    files={"file": ("phrase.wav", wav, "audio/wav")},
    data={"language": "auto"},
    timeout=120,
)
response.raise_for_status()
print(response.json())
'@
$Record | & C:\AI-Shield\venvs\win\Scripts\python.exe -
```

Ожидается ответ STT с `text`, `language`, `duration_ms`. Это ручная проверка пользователя после готовности M09; сам сервер и качество распознавания в рамках написания инструкции не проверялись.

## 6. Подключение ноутбука и запасной Qwen

На ноутбуке убедитесь, что Tailscale подключён к той же сети. В `.env` приложения укажите адрес ПК, показанный в разделе 5, и соответствующие ключи. Если `.env` ещё нет, создайте его из `.env.example`; существующий файл не перезаписывайте. Значения ниже — образец: замените адрес и ключи своими, без угловых скобок.

```dotenv
LLM_BASE_URL=http://<TAILSCALE_IP_ПК>:8080/v1
LLM_MODEL=gemma-4-12b-shield
LLM_API_KEY=<LLM_API_KEY_ИЗ_WINDOWS>
STT_BASE_URL=http://<TAILSCALE_IP_ПК>:8081
STT_API_KEY=<STT_API_KEY_ИЗ_WINDOWS>
```

У LLM адрес заканчивается на `/v1`, у STT — нет. Не открывайте порты моделей в интернет. Если ноутбук не видит серверы, проверьте соединение Tailscale и разрешения локального брандмауэра именно для закрытой сети; не создавайте публичное правило.

Для запасного LLM установите [Ollama](https://ollama.com/download) на ноутбук. Команды ниже предполагают `qwen3:4b`; если уже скачанная Qwen 4B имеет другое имя в `ollama list`, используйте именно его в командах и `.env`.

```bash
ollama list
ollama run qwen3:4b
```

Если модель ещё не скачана, `ollama run` сначала скачает её; затем выйдите из диалога командой `/bye`. Если сервер Ollama не запущен, запустите `ollama serve` в отдельном окне; если он уже работает, второй экземпляр не нужен. Модель и сервер остаются на ноутбуке, обычный локальный адрес:

```dotenv
LLM_FALLBACK_BASE_URL=http://127.0.0.1:11434/v1
LLM_FALLBACK_MODEL=qwen3:4b
```

Ollama на локальном адресе игнорирует переданный API-ключ ([документация Ollama](https://docs.ollama.com/api/openai-compatibility)). Отдельной переменной `LLM_FALLBACK_API_KEY` в контракте приложения нет. Качество Qwen и совместимость её структурированного ответа с адаптером нужно **проверить при запуске**.

## 7. M10: порядок действий и точные команды

Не начинайте обучение, пока не готовы данные и соответствующие скрипты. При отсутствии файла из карточки дождитесь его; не подменяйте набор измерений сгенерированными диалогами.

### M10.1 — исходная модель и голос

Выполните разделы 1–6. После запуска серверов вручную проговорите 12–15 синтетических диалогов и произнесите пять казахских фраз через запрос из раздела 5. Сравните исходный Whisper с кандидатом при необходимости. По фактическим ответам решите, нужна ли вторая STT-модель и остаётся ли Gemma 4; при слабом казахском рассмотрите Sherkala-8B с учётом её некоммерческой лицензии. Это ручной выбор, а не измеренная метрика.

### M10.2 — отчёты исходной Gemma и Qwen

Необходимы M02, M05 и M07: системная подсказка, написанный людьми `data/evaluation/test.jsonl` и `ml/eval/run_eval.py`. Исходная Gemma должна работать по разделу 5. В Ubuntu на ПК:

```bash
source ~/shield-ml-env/bin/activate
cd /mnt/c/AI-Shield/project
read -r -p 'IPv4 Tailscale этого ПК: ' SHIELD_PC_IP
read -r -s -p 'LLM_API_KEY из Windows: ' SHIELD_LLM_KEY
echo
python ml/eval/run_eval.py --base-url "http://$SHIELD_PC_IP:8080/v1" --model gemma-4-12b-shield --api-key "$SHIELD_LLM_KEY" --data data/evaluation/test.jsonl --label base-gemma4-12b
```

Для Qwen выполните M07 **на ноутбуке**, где доступен `127.0.0.1:11434`. На Linux-ноутбуке пример ниже использует отдельное лёгкое окружение; проект, подсказка M02 и тот же человеческий файл M05 должны находиться в нём. Проверить при запуске: после реализации M07 могут потребоваться дополнительные библиотеки.

```bash
cd '/home/museki/Документы/ИИ-Щит'
python3 -m venv ~/shield-eval-env
source ~/shield-eval-env/bin/activate
python -m pip install requests httpx jsonschema
python ml/eval/run_eval.py --base-url http://127.0.0.1:11434/v1 --model qwen3:4b --api-key ollama --data data/evaluation/test.jsonl --label base-qwen-4b
```

При другом имени локальной модели замените `qwen3:4b`. Отчёты образуются в `ml/eval/reports/`; для сравнения перенесите файлы отчёта Qwen на ПК или отчёт Gemma на ноутбук по защищённому каналу. Не переносите реальные записи или ключи.

### M10.3 — сборка, обучение и отчёт дообученной модели

Необходимы M02, M04, M06, M07 и M08. Перед обучением остановите оба Windows-сервера с помощью `Ctrl+C`, чтобы освободить видеопамять. В Ubuntu:

```bash
source ~/shield-ml-env/bin/activate
cd /mnt/c/AI-Shield/project
python ml/data_gen/build_dataset.py
python ml/train/train_qlora.py
cp ml/out/gemma-4-12b-shield.Q4_K_M.gguf /mnt/c/AI-Shield/models/
```

В исходном PowerShell Windows замените путь модели и откройте новое дочернее окно:

```powershell
$env:SHIELD_GGUF = 'C:\AI-Shield\models\gemma-4-12b-shield.Q4_K_M.gguf'
Start-Process powershell.exe -ArgumentList '-NoExit'
```

В новом окне выполните команду llama-server из раздела 5. Имя API остаётся `gemma-4-12b-shield`. В Ubuntu, в том же активированном окружении и с переменными `SHIELD_PC_IP` и `SHIELD_LLM_KEY` из M10.2, выполните:

```bash
python ml/eval/run_eval.py --base-url "http://$SHIELD_PC_IP:8080/v1" --model gemma-4-12b-shield --api-key "$SHIELD_LLM_KEY" --data data/evaluation/test.jsonl --label tuned-gemma4-12b
```

Если окно Ubuntu закрывали, повторите две команды `read` из M10.2. Используйте дообученную модель в демо только если в отчёте её F1 по `active_request` выше исходной, а доля ложных тревог на `hard_normal` не выше. Иначе верните исходный GGUF через `SHIELD_GGUF` и перезапустите llama-server. Измерение и сравнение выполняет пользователь; значения заранее неизвестны.

### M10.4 — подготовка к демо

Запустите выбранный llama-server и STT по разделу 5, убедитесь, что в `.env` ноутбука актуальные адрес и ключи, и повторите ручные запросы с ноутбука через Tailscale. Доступность в приложении отображается через `/api/health`. Оставьте ПК включённым; на ноутбуке держите готовой локальную Qwen. Если GPU не хватает памяти для двух серверов одновременно, это ограничение нужно решить до демонстрации; оценки памяти в архитектуре не являются замерами.
