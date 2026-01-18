# TG Summarizer

Суммаризация непрочитанных сообщений в Telegram с помощью локальной LLM.

**Всё работает локально** — никакие данные не отправляются в облако.

## Быстрый старт (3 шага)

### 1. Установка

```bash
./install.sh
```

Скрипт автоматически:
- Проверит Python 3.8+
- Установит Ollama (если нет)
- Скачает AI модель (~4.7 GB)
- Установит зависимости Python

### 2. Настройка Telegram

```bash
source .venv/bin/activate
python setup.py
```

Тебе нужно будет:
1. Зайти на https://my.telegram.org/apps
2. Создать приложение и получить `api_id` + `api_hash`
3. Залогиниться с номером телефона

> **Это безопасно**: используется официальный Telegram API, все данные остаются на твоём компьютере.

### 3. Использование

```bash
./summarize --unread
```

## Примеры

```bash
# Суммаризация непрочитанных (топ 5 чатов)
./summarize --unread

# Больше чатов
./summarize --unread --max-chats 15

# Последние N сообщений
./summarize --last 50

# Конкретный чат
./summarize --chat "Работа" --last 100

# Список чатов
./summarize --list-chats
```

## Вывод

```
╭───────────────────────────────────────╮
│ TG Summarizer                         │
│ Found 127 messages in 5 chats         │
╰───────────────────────────────────────╯

Работа (45 messages)
├── Обсуждали дедлайн — перенесли на пятницу
├── Нужно ревью PR #234
└── Иван спрашивал про доступы

Семья (12 messages)
├── Мама напомнила про ДР бабушки
└── Брат скинул фото с отпуска

Summarized with qwen2.5:7b in 8.2s
```

## Требования

- macOS или Linux
- Python 3.8+
- ~8 GB свободного места (модель + зависимости)
- 8 GB RAM (рекомендуется)

## Тесты

```bash
source .venv/bin/activate
python tests.py
```

## Файлы

| Файл | Описание |
|------|----------|
| `install.sh` | Установщик (запусти первым) |
| `setup.py` | Настройка Telegram API |
| `summarize.py` | Основной скрипт |
| `summarize` | Удобный лаунчер |
| `tests.py` | Тесты |
| `.env` | Твои credentials (не в git) |
| `*.session` | Telegram сессия (не в git) |

## Troubleshooting

**Ollama не запущен:**
```bash
ollama serve
```

**Модель не найдена:**
```bash
ollama pull qwen2.5:7b
```

**Telegram rate limit:**
Подожди пару минут и попробуй снова. Telegram ограничивает частоту запросов.
