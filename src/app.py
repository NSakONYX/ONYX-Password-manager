import time
from getpass import getpass

from src.clipboard import ClipboardManager
from src.crypto import CryptoEngine
from src.database import Database
from src.ui import TerminalUI


class OnyxApp:
    MAX_LOGIN_ATTEMPTS = 3

    def __init__(self, db_path: str) -> None:
        """Inicjalizuje połączenie z bazą danych oraz silnik kryptograficzny."""
        self.db = Database(db_path)
        self.crypto = CryptoEngine()

    def run(self) -> None:
        """Uruchamia aplikację: wyświetla baner, autoryzuje użytkownika i otwiera menu."""
        TerminalUI.clear_screen()
        TerminalUI.show_banner()

        if not self._handle_auth():
            return

        self._main_loop()

    def _handle_auth(self) -> bool:
        """Obsługuje rejestrację przy pierwszym uruchomieniu lub logowanie (max 3 próby)."""
        creds = self.db.get_master_credentials()

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

                auth_salt, auth_hash, enc_salt = self.crypto.create_master_credentials(
                    passwd
                )
                self.db.save_master_credentials(auth_salt, auth_hash, enc_salt)
                self.crypto.authenticate(passwd, auth_salt, auth_hash, enc_salt)

                TerminalUI.show_info("Skarbiec utworzony i odblokowany.")
                return True

        auth_salt, auth_hash, enc_salt = creds

        for attempt in range(1, self.MAX_LOGIN_ATTEMPTS + 1):
            passwd = getpass("Podaj Master Password: ")
            TerminalUI.clear_screen()

            if self.crypto.authenticate(passwd, auth_salt, auth_hash, enc_salt):
                TerminalUI.show_info("Zalogowano pomyślnie.\n")
                return True

            remaining = self.MAX_LOGIN_ATTEMPTS - attempt
            if remaining > 0:
                TerminalUI.show_error(f"Błędne hasło. Pozostało prób: {remaining}")
            else:
                TerminalUI.show_error("Przekroczono limit prób. Zamykanie aplikacji.")

        return False

    def _main_loop(self) -> None:
        """Obsługuje główną pętlę nawigacji aplikacji."""
        while True:
            TerminalUI.show_main_menu()
            choice = TerminalUI.get_input()

            match choice:
                case "1":
                    self._vault_loop()
                case "2":
                    self._settings_loop()
                case "3":
                    self.crypto.lock_vault()
                    TerminalUI.show_info("Zamykanie skarbca...")
                    break
                case _:
                    TerminalUI.show_error("Nieprawidłowa opcja. Wybierz 1, 2 lub 3.\n")

    def _vault_loop(self) -> None:
        """Wyświetla listę wpisów i obsługuje akcje na skarbcu."""
        while True:
            TerminalUI.clear_screen()
            entries = self.db.get_all_services()
            TerminalUI.show_entries(entries)
            TerminalUI.show_vault_menu()

            option = input(
                f"{TerminalUI.GRAY}Naciśnij Enter, aby cofnąć lub wybierz: {TerminalUI.RESET}"
            ).strip()

            match option:
                case "1":
                    self._copy_password(entries)
                case "2":
                    self._show_password(entries)
                case "3":
                    self._edit_entry(entries)
                case "4":
                    self._delete_entry(entries)
                case "":
                    TerminalUI.clear_screen()
                    break
                case _:
                    TerminalUI.show_error("Nieprawidłowa opcja.")
                    TerminalUI.pause()

    def _prompt_entry_id(self, prompt: str) -> int | None:
        """Pobiera i waliduje ID wpisu od użytkownika; zwraca None przy anulowaniu lub błędzie."""
        chosen_id = input(f"{TerminalUI.GRAY}{prompt}{TerminalUI.RESET}").strip()

        if not chosen_id:
            return None

        if not chosen_id.isdigit():
            TerminalUI.show_error("ID musi być liczbą.")
            TerminalUI.pause()
            return None

        return int(chosen_id)

    def _copy_password(self, entries: list) -> None:
        """Odszyfrowuje wybrane hasło, kopiuje je do schowka i czyści schowek po potwierdzeniu."""
        TerminalUI.clear_screen()
        TerminalUI.show_entries(entries)

        entry_id = self._prompt_entry_id(
            "\nNaciśnij Enter, aby cofnąć lub wybierz ID: "
        )
        if entry_id is None:
            return

        encrypted_password = self.db.get_password(entry_id)
        if encrypted_password is None:
            TerminalUI.show_error("Nie znaleziono wpisu o takim ID.")
            TerminalUI.pause()
            return

        decrypted_password = self.crypto.decrypt_data(encrypted_password)
        ClipboardManager.copy(decrypted_password)
        TerminalUI.show_success("Hasło skopiowane do schowka.")
        TerminalUI.show_info(
            "Wklej je, a potem naciśnij Enter, aby wyczyścić schowek..."
        )
        TerminalUI.pause()
        ClipboardManager._clear_if_matches(decrypted_password)

    def _show_password(self, entries: list) -> None:
        """Wyświetla odszyfrowane hasło w terminalu przez 6 sekund, po czym czyści ekran."""
        TerminalUI.clear_screen()
        TerminalUI.show_entries(entries)

        entry_id = self._prompt_entry_id("\nWybierz ID usługi lub Enter, aby wyjść: ")
        if entry_id is None:
            return

        encrypted_password = self.db.get_password(entry_id)
        if encrypted_password is None:
            TerminalUI.show_error("Nie znaleziono wpisu o takim ID.")
            TerminalUI.pause()
            return

        decrypted_password = self.crypto.decrypt_data(encrypted_password)
        for i in range(6):
            TerminalUI.clear_screen()
            print(
                f"\n{TerminalUI.GREEN}Hasło to:  {TerminalUI.GRAY}'{decrypted_password}'"
                f"{TerminalUI.RED}  | hasło zniknie za: {6 - i}{TerminalUI.RESET}"
            )
            time.sleep(1)

        TerminalUI.clear_screen()

    def _edit_entry(self, entries: list) -> None:
        """Pozwala edytować istniejący wpis w skarbcu."""

    def _delete_entry(self, entries: list) -> None:
        """Trwale usuwa wybrany wpis po 3-sekundowym ostrzeżeniu i potwierdzeniu."""
        TerminalUI.clear_screen()
        TerminalUI.show_entries(entries)

        entry_id = self._prompt_entry_id("\nWybierz ID usługi lub Enter, aby wyjść: ")
        if entry_id is None:
            return

        if not self.db.get_entry_by_id(entry_id):
            TerminalUI.show_error("Nie znaleziono wpisu o takim ID.")
            TerminalUI.pause()
            return

        for i in range(3):
            TerminalUI.clear_screen()
            print(
                f"\n{TerminalUI.RED}!DZIAŁANIE NIEODWRACALNE!{TerminalUI.YELLOW} "
                f"- Zastanów się nad tą decyzją!{TerminalUI.GRAY} "
                f"Potwierdzenie za {3 - i}{TerminalUI.RESET}"
            )
            time.sleep(1)

        TerminalUI.clear_screen()
        second_chance = (
            input(
                f"{TerminalUI.GRAY}Czy potwierdzasz usunięcie usługi? [y/n]: {TerminalUI.RESET}"
            )
            .strip()
            .lower()
        )

        TerminalUI.clear_screen()
        if second_chance == "y":
            self.db.delete_entry(entry_id)
            TerminalUI.show_success("Wpis usunięty pomyślnie!")
            TerminalUI.pause()

    def _settings_loop(self) -> None:
        """Obsługuje podmenu ustawień skarbca."""
        TerminalUI.clear_screen()
        TerminalUI.show_info("Ustawienia – w budowie.")
        TerminalUI.pause()
        TerminalUI.clear_screen()
