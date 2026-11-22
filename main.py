import os

from src.database import Database
from src.ui import TerminalUI


def main():
    os.makedirs("data", exist_ok=True)
    db = Database("data/vault.db")

    TerminalUI.clear_screen()
    TerminalUI.show_banner()

    # TODO: logowanie - master passw

    while True:
        TerminalUI.show_main_menu()
        choice = TerminalUI.get_input()

        match choice:
            case "1":
                TerminalUI.clear_screen()
                # TODO: pobranie wpisow z bazy
                entries = []
                TerminalUI.show_entries(entries)
                TerminalUI.pause()
                TerminalUI.clear_screen()

            case "2":
                TerminalUI.clear_screen()
                TerminalUI.show_info("Ustawienia – w budowie.")
                TerminalUI.pause()
                TerminalUI.clear_screen()

            case "3":
                TerminalUI.show_info("Zamykanie skarbca...")
                break

            case _:
                TerminalUI.show_error("Nieprawidłowa opcja. Wybierz 1, 2 lub 3.\n")


if __name__ == "__main__":
    main()
