# Build

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
pyinstaller --onefile --name RoyalAnalyzerAI RoyalAnalyzer/app/main.py
```
