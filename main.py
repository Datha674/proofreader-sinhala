# -*- coding: utf-8 -*-
"""
main.py — entry point for the Sinhala Proofreader desktop app.

    python main.py
"""

import os
import sys

# Make the project root importable both in dev and inside a PyInstaller build.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from gui.main_window import MainWindow


def main():
    config = Config()
    app = MainWindow(config)
    app.mainloop()


if __name__ == "__main__":
    main()
