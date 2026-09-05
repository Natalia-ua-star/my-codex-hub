# my-codex-hub

## Агент пошуку winner-товарів

Щодня о 09:00 за Києвом шукає товари для дропшипінгу й відкриває issue
зі знахідками. Працює на GitHub Actions — комп'ютер вмикати не треба.

**Налаштування:** [docs/agent-setup.md](docs/agent-setup.md)

| Файл | Що це |
|---|---|
| `winner_hunt/config.yaml` | ключові слова, ринки, бюджет — редагувати тут |
| `winner_hunt/score.py` | формула оцінки товару |
| `winner_hunt/aisa.py` | клієнт AIsa (тренди, Amazon) |
| `winner_hunt/apify.py` | клієнт Apify (віральність у TikTok) |
| `reports/` | щоденні звіти: .md для читання, .csv для Google Sheets |

Ключі зберігаються в GitHub Secrets, у репозиторії їх немає.
