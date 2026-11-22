import os

from src.database import Database
from src.ui import TerminalUI

TerminalUI.clear_screen()
TerminalUI.show_banner()
TerminalUI.show_main_menu()

os.makedirs("data", exist_ok=True)
db = Database("data/vault.db")
