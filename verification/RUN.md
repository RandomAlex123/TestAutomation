# Проверка проекта

Проверено 25 октября 2026 года в отдельной копии проекта с новым окружением
Python и установкой зависимостей из `requirements.txt` и `pnpm-lock.yaml`.
`pip check` не обнаружил конфликтов; `pnpm install --frozen-lockfile`
не потребовал изменений lock-файла.

| Среда | Версия | Результат | Время по JUnit XML |
|---|---|---|---:|
| Chrome | 156.0.8078.47 | 38 passed, 0 ошибок, 0 пропусков | 140,975 с |
| Firefox | 158.0 | 38 passed, 0 ошибок, 0 пропусков | 201,323 с |

ОС: Linux. Python 3.12.14, Selenium 4.51.0, Pytest 9.1.1,
Allure Pytest 2.16.2. Генератор: Allure Report 3.22.1,
Node.js 24.22.1, pnpm 11.25.0.

## Команды полных прогонов

```bash
# Chrome: подробный вывод, остановка при двух сбоях, XML и пять самых долгих этапов.
# --no-sandbox нужен для запуска Chrome в этой среде.
.venv/bin/python -m pytest -v --no-sandbox --maxfail=2 --junitxml=artifacts/chrome-junit.xml --durations=5

# Firefox: явно указать браузер и драйвер вместо Snap-оболочек.
# --alluredir отделяет его результаты от Chrome; --junitxml сохраняет отдельный XML.
.venv/bin/python -m pytest -v --browser=firefox --browser-binary=/snap/firefox/current/usr/lib/firefox/firefox --driver-path=/snap/firefox/current/usr/lib/firefox/geckodriver --maxfail=2 --alluredir=artifacts/firefox-results --junitxml=artifacts/firefox-junit.xml --durations=5
```

## Отчёты

- [allure-report.html](allure-report.html) — готовый отчёт полного прогона Chrome.
- [chrome-junit.xml](chrome-junit.xml) — машинный результат Chrome.
- [firefox-junit.xml](firefox-junit.xml) — машинный результат Firefox.

`pnpm run report` выполнена в чистой копии. Из результатов удалены метки
компьютера и процесса, из XML — `hostname`, из HTML — внешняя аналитика.
Результаты, названия и шаги тестов сохранены.
