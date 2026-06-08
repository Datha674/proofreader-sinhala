# PyInstaller .exe Packaging

## Critical: Resource Path for Bundled Files
```python
import sys, os

def resource_path(relative_path):
    """Works both in dev and in .exe"""
    if hasattr(sys, '_MEIPASS'):
        base = sys._MEIPASS          # inside .exe
    else:
        base = os.path.dirname(__file__)  # during dev
    return os.path.join(base, relative_path)

# Usage:
dict_path = resource_path("data/sinhala_dictionary.txt")
```

## build.spec Template
```python
a = Analysis(
    ['main.py'],
    datas=[
        ('data', 'data'),
    ],
    hiddenimports=[
        'google.generativeai',
        'customtkinter',
    ],
)
exe = EXE(a.pex, a.scripts, a.binaries, a.datas,
    name='SinhalaProofreader',
    console=False,   # no black terminal window
    icon='assets/icon.ico'
)
```

## Build Command
```bash
pip install pyinstaller
pyinstaller build.spec --clean
# Output: dist/SinhalaProofreader.exe
```

## Config NOT inside .exe
- Save config to: ~/.sinhala_proofreader/config.json
- This persists after .exe updates
- User's API key is never lost when app updates