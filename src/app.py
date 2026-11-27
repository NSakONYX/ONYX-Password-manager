import sqlite3
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

    def seed_demo_entries(self) -> None:
        """Dodaje 15 przykładowych wpisów testowych do skarbca."""
        demo_data = [
            ("Netflix", "jan.kowalski@gmail.com", "N3tfl!x_Stream99"),
            ("Spotify", "jan.kowalski@gmail.com", "Sp0tify#Music2026"),
            ("GitHub", "nixon-dev", "Gh_Token!7721xZ"),
            ("Discord", "nixon#0001", "D1sc0rd_V0ice!88"),
            ("Steam", "nixon_pl", "St3am$Valve2025"),
            ("Allegro", "jan.kowalski@gmail.com", "All3gro_Zakupy44"),
            ("mBank", "10948271", "mB@nk_Secur3!09"),
            ("Revolut", "jan.kowalski@gmail.com", "R3v0lut#Card771"),
            ("XTB", "jan.kowalski@gmail.com", "XTB_Tr@ding2026!"),
            ("Gmail", "jan.kowalski@gmail.com", "G00gl3_Mail#912"),
            ("Instagram", "urbexowe_fotografie", "Inst@_Photo!551"),
            ("YouTube", "jan.kowalski@gmail.com", "YT_Ch@nnel8821"),
            ("Amazon", "jan.kowalski@gmail.com", "Am@zon_Prim3!22"),
            ("ChatGPT", "jan.kowalski@gmail.com", "Op3nAI_Key#404"),
            ("Binance", "jan.kowalski@gmail.com", "B1n@nce_Spot991"),
        ]

        for service, login, password in demo_data:
            encrypted = self.crypto.encrypt_data(password)
            self.db.add_entry(service, login, encrypted)

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
        TerminalUI.clear_screen()
        TerminalUI.show_edit_entry_menu()
        option = input(
            f"{TerminalUI.GRAY}\nCo chciałbyś edytować? Enter aby cofnąć: {TerminalUI.RESET}"
        ).strip()

        if not option:
            return

        if option not in ("1", "2", "3"):
            TerminalUI.show_error("Nieprawidłowa opcja.")
            TerminalUI.pause()
            return

        TerminalUI.clear_screen()
        TerminalUI.show_entries(entries)

        entry_id = self._prompt_entry_id(
            "\nWybierz ID usługi, którą chcesz edytować (Enter aby cofnąć): "
        )
        if entry_id is None:
            return

        entry = self.db.get_entry_by_id(entry_id)
        if entry is None:
            TerminalUI.show_error("Nie znaleziono wpisu o takim ID.")
            TerminalUI.pause()
            return

        _, old_service, old_login, encrypted_old_password = entry
        TerminalUI.clear_screen()

        match option:
            case "1":
                while True:
                    new_service = input(
                        f"{TerminalUI.PURPLE}\nNowa nazwa serwisu (Enter aby anulować): {TerminalUI.RESET}"
                    ).strip()

                    if not new_service:
                        return

                    if len(new_service) < 1:
                        print(
                            f"{TerminalUI.RED}Nazwa serwisu jest za krótka!{TerminalUI.GRAY} (min. 1 znaki){TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    if new_service.lower() == old_service.lower():
                        print(
                            f"{TerminalUI.RED}Nazwa serwisu jest taka sama jak poprzednia!{TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    new_service_checker = input(
                        f"{TerminalUI.PURPLE}\nPowtórz nazwę serwisu: {TerminalUI.RESET}"
                    ).strip()

                    if new_service != new_service_checker:
                        print(
                            f"{TerminalUI.RED}Podane nazwy są różne!{TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    if not self.db.update_service_name(entry_id, new_service):
                        TerminalUI.show_error("Taki serwis z tym loginem już istnieje.")
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    TerminalUI.clear_screen()
                    print(
                        f"{TerminalUI.GREEN}Nazwa serwisu zmieniona pomyślnie!{TerminalUI.RESET}"
                    )
                    time.sleep(2)
                    break

            case "2":
                while True:
                    new_login = input(
                        f"{TerminalUI.PURPLE}\nNowy login (Enter aby anulować): {TerminalUI.RESET}"
                    ).strip()

                    if not new_login:
                        return

                    if len(new_login) < 3:
                        print(
                            f"{TerminalUI.RED}Login jest za krótki!{TerminalUI.GRAY} (min. 3 znaki){TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    if new_login.lower() == old_login.lower():
                        print(
                            f"{TerminalUI.RED}Login jest taki sam jak poprzedni!{TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    new_login_checker = input(
                        f"{TerminalUI.PURPLE}\nPowtórz login: {TerminalUI.RESET}"
                    ).strip()

                    if new_login != new_login_checker:
                        print(
                            f"{TerminalUI.RED}Podane loginy są różne!{TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    if not self.db.update_login(entry_id, new_login):
                        TerminalUI.show_error(
                            "Taki login dla tego serwisu już istnieje."
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    TerminalUI.clear_screen()
                    print(
                        f"{TerminalUI.GREEN}Login zmieniony pomyślnie!{TerminalUI.RESET}"
                    )
                    time.sleep(2)
                    break

            case "3":
                decrypted_old_password = self.crypto.decrypt_data(
                    encrypted_old_password
                )

                while True:
                    new_password = getpass(
                        f"{TerminalUI.PURPLE}Podaj nowe hasło (Enter aby anulować): {TerminalUI.RESET}"
                    )

                    if not new_password:
                        return

                    if len(new_password) < 5:
                        print(
                            f"{TerminalUI.RED}Hasło jest za krótkie!{TerminalUI.GRAY} (min. 5 znaków){TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    if new_password == decrypted_old_password:
                        print(
                            f"{TerminalUI.RED}Nie można zmienić hasła na takie samo!{TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    new_password_checker = getpass(
                        f"{TerminalUI.PURPLE}Powtórz hasło: {TerminalUI.RESET}"
                    )

                    if new_password != new_password_checker:
                        print(
                            f"{TerminalUI.RED}Hasło jest niezgodne z podanym!{TerminalUI.RESET}"
                        )
                        time.sleep(2)
                        TerminalUI.clear_screen()
                        continue

                    encrypted_password = self.crypto.encrypt_data(new_password)
                    self.db.update_password(entry_id, encrypted_password)

                    TerminalUI.clear_screen()
                    print(
                        f"{TerminalUI.GREEN}Hasło zmienione pomyślnie!{TerminalUI.RESET}"
                    )
                    time.sleep(2)
                    break

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

    def _settings_menu(self):
        TerminalUI.clear_screen()

        options = [
            ("[1] ", "Zmiana hasla glownego"),
            ("[2] ", "Czas aut. czyszczenia schowka"),
            ("[3] ", "Audyt sily hasel"),
            ("[4] ", "Generator hasel"),
            ("[5] ", "Kopia zapasowa skarbca"),
            ("[6] ", "Eksport danych (JSON/CSV)"),
            ("[7] ", "Dead man switch"),
            ("[None] ", "Powrot"),
        ]

        print(f"{TerminalUI.PURPLE}{'━' * 35}{TerminalUI.RESET}")
        for index, menu_option in options:
            print(f"{TerminalUI.PURPLE}{index}{TerminalUI.RESET}{menu_option}")

    def change_main_password(self, new_password: str) -> bool:
        """Zmienia hasło główne i ponownie szyfruje cały skarbiec nowym kluczem."""
        if not new_password:
            return False

        encrypted_entries = self.db.get_all_encrypted_entries()
        decrypted_entries: list[tuple[int, str]] = [
            (entry_id, self.crypto.decrypt_data(enc_pass))
            for entry_id, enc_pass in encrypted_entries
        ]

        new_auth_hash, new_auth_salt, new_enc_salt = (
            self.crypto.create_master_credentials(new_password)
        )

        new_crypto = CryptoEngine()
        if not new_crypto.authenticate(
            new_password, new_auth_hash, new_auth_salt, new_enc_salt
        ):
            return False

        reencrypted_entries: list[tuple[bytes, int]] = [
            (new_crypto.encrypt_data(plain_pass), entry_id)
            for entry_id, plain_pass in decrypted_entries
        ]

        try:
            self.db.update_master_and_vault(
                new_auth_hash,
                new_auth_salt,
                new_enc_salt,
                reencrypted_entries,
            )
        except sqlite3.Error:
            return False

        self.crypto = new_crypto
        return True

    def _settings_loop(self) -> None:
        """Obsługuje podmenu ustawień skarbca."""
        TerminalUI.clear_screen()
        self._settings_menu()

        """
        #TODO: 
        === USTAWIENIA ===
        [1] Zmiana hasła głównego
        [2] Czas automatycznego czyszczenia schowka
        [3] Audyt siły haseł
        [4] Generator haseł
        [5] Kopia zapasowa skarbca (Backup)
        [6] Eksport danych (JSON / CSV)
        [7] Dead man switch
        [0] Powrót
        """

        TerminalUI.pause()
        TerminalUI.clear_screen()
