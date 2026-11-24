import os
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

        if crypto.authenticate(passwd, auth_salt, auth_hash, enc_salt):
            TerminalUI.show_info("Zalogowano pomyślnie.")
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

                    case "2":
                        pass

                    case "3":
                        pass

                    case "4":
                        pass

                    case "":
                        break
                    case _:
                        TerminalUI.show_error("Nieprawidlowa opcja")

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
