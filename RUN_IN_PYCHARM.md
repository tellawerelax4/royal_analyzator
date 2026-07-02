# Как запустить Royal Analyzer AI в PyCharm

Эта инструкция рассчитана на Windows 10/11, Python 3.12 и PyCharm.

## 1. Установите системные компоненты

1. Установите Python 3.12 с официального сайта: <https://www.python.org/downloads/>.
2. При установке включите опцию **Add python.exe to PATH**.
3. Установите PyCharm Community или Professional.

## 2. Откройте проект

1. Скачайте или распакуйте папку проекта.
2. Откройте PyCharm.
3. Нажмите **File → Open**.
4. Выберите корневую папку проекта `royal_analyzator`, где лежат `pyproject.toml`, `requirements.txt` и папка `RoyalAnalyzer`.

## 3. Создайте виртуальное окружение

В PyCharm:

1. Откройте **File → Settings → Project → Python Interpreter**.
2. Нажмите **Add Interpreter → Add Local Interpreter**.
3. Выберите **Virtualenv Environment**.
4. В поле **Base interpreter** выберите Python 3.12.
5. Нажмите **OK**.

Или через терминал PyCharm:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 4. Установите зависимости

В терминале PyCharm выполните:

```powershell
pip install -r requirements.txt
```

Затем установите браузер Playwright:

```powershell
playwright install chromium
```

Если позже будет включён OCR через EasyOCR, установите дополнительный пакет:

```powershell
pip install easyocr
```

## 5. Запустите приложение

### Вариант A: через терминал PyCharm

```powershell
python -m RoyalAnalyzer.app.main
```

### Вариант B: через Run Configuration

1. Нажмите **Run → Edit Configurations**.
2. Нажмите **+ → Python**.
3. Укажите:
   - **Name**: `Royal Analyzer AI`
   - **Module name**: `RoyalAnalyzer.app.main`
   - **Working directory**: корневая папка проекта `royal_analyzator`
   - **Python interpreter**: виртуальное окружение `.venv`
4. Нажмите **Apply → OK**.
5. Запустите конфигурацию зелёной кнопкой **Run**.

## 6. Проверьте, что проект установлен корректно

Запустите тесты:

```powershell
python -m pytest
```

Если тесты проходят, базовые модули проекта импортируются и работают корректно.

## 7. Сборка в один `.exe`

Когда нужно собрать приложение для пользователя без установленного Python:

```powershell
pyinstaller --onefile --name RoyalAnalyzerAI RoyalAnalyzer/app/main.py
```

Готовый файл появится в папке:

```text
dist/RoyalAnalyzerAI.exe
```

## Важно о текущем состоянии проекта

Текущая версия — это рабочий стартовый каркас приложения: открывается PySide6-окно, есть доменные модели, SQLite-хранилище, статистика, предикторы, backtesting и заготовка Playwright-сборщика. Полная автоматическая интеграция с реальной страницей игры и все продвинутые ML/OCR-модели должны дорабатываться следующими итерациями.
