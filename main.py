import os
import time
from getpass import getpass

from src.clipboard import ClipboardManager
from src.crypto import CryptoEngine
from src.database import Database
from src.ui import TerminalUI

MAX_LOGIN_ATTEMPTS = 3


def handle_auth(db: Database, crypto: CryptoEngine) -> bool:
    """Obsługuje rejestrację (pierwsze uruchomienie) lub logowanie (max 3 próby)."""
    creds = db.get_master_credentials()

    if creds is None:
        TerminalUI.show_info("Pierwsze uruchomienie. Ustaw Master Password.")

        while True:
            passwd = getpass("Nowe Master Password: ")
            if not passwd:
                TerminalUI.show_error("Hasło nie może być puste.")
                continue

            confirm = getpass("Powtórz Master Password: ")
            if passwd != confirm:
                TerminalUI.show_error("Hasła się nie zgadzają. Spróbuj ponownie.")
                continue

            auth_salt, auth_hash, enc_salt = crypto.create_master_credentials(passwd)
            db.save_master_credentials(auth_salt, auth_hash, enc_salt)
            crypto.authenticate(passwd, auth_salt, auth_hash, enc_salt)

            TerminalUI.show_info("Skarbiec utworzony i odblokowany.")
            return True

    auth_salt, auth_hash, enc_salt = creds

    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        passwd = getpass("Podaj Master Password: ")

        TerminalUI.clear_screen()

        if crypto.authenticate(passwd, auth_salt, auth_hash, enc_salt):
            TerminalUI.show_info("Zalogowano pomyślnie.\n")
            return True

        remaining = MAX_LOGIN_ATTEMPTS - attempt
        if remaining > 0:
            TerminalUI.show_error(f"Błędne hasło. Pozostało prób: {remaining}")
        else:
            TerminalUI.show_error("Przekroczono limit prób. Zamykanie aplikacji.")

    return False


def main():
    os.makedirs("data", exist_ok=True)
    db = Database("data/vault.db")
    crypto = CryptoEngine()

    TerminalUI.clear_screen()
    TerminalUI.show_banner()

    if not handle_auth(db, crypto):
        return

    while True:
        TerminalUI.show_main_menu()
        choice = TerminalUI.get_input()

        match choice:
            case "1":
                while True:
                    TerminalUI.clear_screen()
                    entries = db.get_all_services()
                    TerminalUI.show_entries(entries)
                    TerminalUI.show_vault_menu()

                    option = input(
                        f"{TerminalUI.GRAY}Naciśnij Enter, aby cofnac lub wybierz: {TerminalUI.RESET}"
                    )

                    match option:
                        case "1":
                            TerminalUI.clear_screen()
                            TerminalUI.show_entries(entries)

                            chosen_id = input(
                                f"\n{TerminalUI.GRAY}Naciśnij Enter, aby cofnac lub wybierz: {TerminalUI.RESET}"
                            )

                            if not chosen_id:
                                continue

                            if not chosen_id.isdigit():
                                TerminalUI.show_error("ID musi być liczbą")
                                TerminalUI.pause()
                                continue

                            encrypted_password = db.get_password(int(chosen_id))
                            if encrypted_password is None:
                                TerminalUI.show_error("Nie znaleziono wpisu o takim ID")
                                TerminalUI.pause()
                                continue

                            decrypted_password = crypto.decrypt_data(encrypted_password)

                            ClipboardManager.copy(decrypted_password)
                            TerminalUI.show_success("Hasło skopiowane do schowka.")
                            TerminalUI.show_info(
                                "Wklej je, a potem naciśnij Enter, aby wyczyścić schowek..."
                            )
                            TerminalUI.pause()
                            ClipboardManager._clear_if_matches(decrypted_password)
                            break

                        case "2":
                            TerminalUI.clear_screen()
                            entries = db.get_all_services()
                            TerminalUI.show_entries(entries)
                            TerminalUI.show_vault_menu()

                            chosen_id = input(
                                f"{TerminalUI.GRAY}Wybierz id uslugi lub Enter aby wyjsc: {TerminalUI.RESET}"
                            )

                            if chosen_id == "":
                                break

                            encrypted_password = db.get_password(int(chosen_id))
                            if encrypted_password is None:
                                TerminalUI.show_error("Nie znaleziono wpisu o takim ID")
                                TerminalUI.pause()
                                continue

                            decrypted_password = crypto.decrypt_data(encrypted_password)
                            for i in range(6):
                                TerminalUI.clear_screen()
                                print(
                                    f"\n{TerminalUI.GREEN}Haslo to:  {TerminalUI.GRAY}'{decrypted_password}'{TerminalUI.RED}  | haslo zniknie za: {6 - i}{TerminalUI.RESET}"
                                )
                                time.sleep(1)

                            TerminalUI.clear_screen()
                            continue

                        case "3":
                            pass

                        case "4":
                            second_chance: str
                            TerminalUI.clear_screen()
                            entries = db.get_all_services()
                            TerminalUI.show_entries(entries)

                            chosen_id = input(
                                f"{TerminalUI.GRAY}Wybierz id uslugi lub Enter aby wyjsc: {TerminalUI.RESET}"
                            )

                            if chosen_id == "":
                                break

                            if not chosen_id.isdigit():
                                TerminalUI.show_error("ID musi być liczbą.")
                                TerminalUI.pause()
                                continue

                            chosen_id = int(chosen_id)
                            if not db.get_entry_by_id(chosen_id):
                                TerminalUI.show_error(
                                    "Nie znaleziono wpisu o takim ID."
                                )
                                TerminalUI.pause()
                                continue

                            for i in range(3):
                                TerminalUI.clear_screen()
                                print(
                                    f"\n{TerminalUI.RED}!DZIALANIE NIEODWRACALNE!{TerminalUI.YELLOW} - Zastanow sie nad ta decyzja!{TerminalUI.GRAY} Potwierdzenie za {3 - i}{TerminalUI.RESET}"
                                )
                                time.sleep(1)
                            TerminalUI.clear_screen()
                            second_chance = input(
                                f"{TerminalUI.GRAY}Czy potwierdzasz usuniecie uslugi? [y/n]:  {TerminalUI.RESET}"
                            )

                            TerminalUI.clear_screen()
                            if second_chance == "y" and db.get_entry_by_id(chosen_id):
                                db.delete_entry(chosen_id)
                                print(
                                    f"{TerminalUI.GREEN}Wpis usuniety pomyslnie!{TerminalUI.RESET}"
                                )
                                TerminalUI.clear_screen()
                                continue
                            else:
                                continue

                        case "":
                            break
                        case _:
                            TerminalUI.show_error("Nieprawidlowa opcja")
                            continue

                    TerminalUI.clear_screen()

            case "2":
                TerminalUI.clear_screen()
                # TODO: """
                #   1: Change entry - przeniesione do sekcji 1
                #   2: Delete entry - przeniesione do sekcji 1
                #   3: Change master pasword
                #   4: Dead man switch option
                #   5: Backub vault
                #   6: Password audit
                #   7: Clipboard auto-clear time
                #   8: Export to JSON/CSV
                #   0: back
                # """

                TerminalUI.show_info("Ustawienia – w budowie.")
                TerminalUI.pause()
                TerminalUI.clear_screen()

            case "3":
                crypto.lock_vault()
                TerminalUI.show_info("Zamykanie skarbca...")
                break

            case _:
                TerminalUI.show_error("Nieprawidłowa opcja. Wybierz 1, 2 lub 3.\n")


if __name__ == "__main__":
    main()
