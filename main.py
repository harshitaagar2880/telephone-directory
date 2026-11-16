"""
main.py
--------
Entry point for Smart Contact Manager.
Run this file to launch the application:
    python main.py

What this file does:
1. Initialises the SQLite database (creates tables if they don't exist).
2. Opens the main application window.
"""

import sys
import os

# Make sure Python can find our packages when run from any working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.connection import initialize_database
from gui.app_window import AppWindow


def main():
    # Step 1: Set up / verify the database
    initialize_database()

    # Step 2: Launch the GUI
    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
