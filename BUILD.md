# Sinhala Proofreader — Build & Versioning

Gemini-powered Sinhala spell + grammar checker with a self-learning corrections
database. Two connection modes: **Direct** (Gemini API key on the PC) and
**LAN Proxy** (via a Control PC — see `DEPLOYMENT.md` / `proxy_server/`).
Modern UI with dark + light themes and English/Sinhala switching.

Python 3.9+ · Windows 10/11 64-bit.

## 1. Install dependencies
```powershell
pip install -r requirements.txt
```

## 2. Run (dev)
```powershell
python main.py
```
- Settings (top-right ⚙️) holds the API key, connection mode, model, theme and UI language.
- Shortcuts: **Ctrl+Enter** = check, **Ctrl+L** = clear.
- The corrected text opens in its own window; Input and Results split the main window 50/50.

## 3. Run tests (no key / no internet needed)
```powershell
$env:PYTHONUTF8=1; python tests/test_app.py      # engine + orchestrator + corrections DB
$env:PYTHONUTF8=1; python tests/test_engine.py   # LIVE Gemini (skips if no key)
```

## 4. Build the standalone .exe
One command (either form works):
```powershell
python -m PyInstaller build.spec --clean --noconfirm
```
…or just double-click **`build.bat`** (installs deps + builds).

Output: `dist/SinhalaProofreader.exe` — single-file, windowed, self-contained.
Before building, close any running `SinhalaProofreader.exe` (it locks the output file):
```powershell
Get-Process SinhalaProofreader -ErrorAction SilentlyContinue | Stop-Process -Force
```

## 5. Change the version
The version lives in one place: **`version.py`** (`__version__`). The window title
shows it. Use the script:
```powershell
python bump_version.py            # patch:  4.2.0 -> 4.2.1
python bump_version.py minor      # minor:  4.2.0 -> 4.3.0
python bump_version.py major      # major:  4.2.0 -> 5.0.0
python bump_version.py 4.5.2      # set an explicit version
```
Then rebuild (step 4). Typical release flow:
```powershell
python bump_version.py minor
python -m PyInstaller build.spec --clean --noconfirm
```

## Where settings live
Per-user, outside the app (survives restarts and .exe updates):
```
~/.sinhala_proofreader/config.json        settings + API key (Direct mode)
~/.sinhala_proofreader/corrections.json   learned corrections cache
```
For mass deployment you can instead drop a `gemini_key.txt` (one line) next to the
.exe, or set the `GEMINI_API_KEY` env var. In LAN Proxy mode the client needs no key.

## Project layout
```
version.py · main.py · config.py
engine/   gemini_engine.py · lan_proxy_engine.py · proofreader.py · corrections_db.py · utils.py
gui/      main_window.py · settings_dialog.py · welcome_dialog.py · widgets.py · theme.py · i18n.py
proxy_server/   Flask Control-PC server + admin panel (see README_CONTROL_PC.txt)
assets/ · requirements.txt · build.spec · build.bat · bump_version.py
```

## Notes
- **Encoding:** UTF-8 throughout. The GUI never prints to stdout, so the Windows
  cp1252 console limitation only affects test scripts (hence `PYTHONUTF8=1`).
- **Icon:** `build.spec` uses `assets/icon.png` if present (else no custom icon).
- **Quota:** 20 LAN users on a *free* key will hit 429 — enable billing and/or use
  `gemini-2.0-flash`. See `DEPLOYMENT.md`.
