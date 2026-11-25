import getpass
import os
import time


class TerminalUI:
    PURPLE = "\033[95m"
    DARK_PURPLE = "\033[35m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

    @staticmethod
    def type_print(text: str, delay: float = 0.002):
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print()

    @staticmethod
    def show_banner():
        banner = r"""
 ██████╗ ███╗   ██╗██╗   ██╗██╗  ██╗
██╔═══██╗████╗  ██║╚██╗ ██╔╝╚██╗██╔╝
██║   ██║██╔██╗ ██║ ╚████╔╝  ╚███╔╝ 
██║   ██║██║╚██╗██║  ╚██╔╝   ██╔██╗ 
╚██████╔╝██║ ╚████║   ██║   ██╔╝ ██╗
 ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝"""

        subtitle = "     ━━━  K E Y C H A I N  ━━━"

        TerminalUI.type_print(f"{TerminalUI.PURPLE}{banner}{TerminalUI.RESET}")
        TerminalUI.type_print(
            f"{TerminalUI.DARK_PURPLE}{subtitle}{TerminalUI.RESET}\n", 0.04
        )

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def show_main_menu():
        """
        1: pokaz hasla
        2: ustawienia
        3: wyjdz
        """

        print("      1. Pokaż zapisane hasła")
        print("      2.     Ustawienia")
        print("      3.       Wyjdź\n\n")

    @staticmethod
    def get_input(prompt: str = "Wybierz opcję: ") -> str:
        return input(f"{TerminalUI.PURPLE}❯ {TerminalUI.RESET}{prompt}").strip()

    @staticmethod
    def get_password(prompt: str = "Hasło główne: ") -> str:
        return getpass.getpass(f"{TerminalUI.PURPLE}❯ {TerminalUI.RESET}{prompt}")

    @staticmethod
    def show_success(message: str):
        print(f"{TerminalUI.GREEN}[✓] {message}{TerminalUI.RESET}")

    @staticmethod
    def show_error(message: str):
        print(f"{TerminalUI.RED}[✗] {message}{TerminalUI.RESET}")
        time.sleep(1)

    @staticmethod
    def show_info(message: str):
        print(f"{TerminalUI.YELLOW}[i] {message}{TerminalUI.RESET}")

    @staticmethod
    def pause():
        input(f"{TerminalUI.GRAY}Naciśnij Enter, aby kontynuować...{TerminalUI.RESET}")

    @staticmethod
    def show_entries(entries: list[tuple]):
        if not entries:
            TerminalUI.show_info("Skarbiec jest pusty.")
            return

        print(
            f"\n{TerminalUI.PURPLE}{'ID':<5} {'SERWIS':<20} {'LOGIN':<25}{TerminalUI.RESET}"
        )
        print(f"{TerminalUI.GRAY}{'─' * 52}{TerminalUI.RESET}")
        for entry_id, service, login in entries:
            print(
                f"{TerminalUI.PURPLE}{entry_id:<5}{TerminalUI.RESET} {service:<20} {login:<35}\n"
            )
            print(f"{TerminalUI.GRAY}{'─' * 52}{TerminalUI.RESET}")

    @classmethod
    def show_vault_menu(cls):
        """
        1. kopiuj haslo
        2. pokaz haslo
        3. edytuj
        4. usun
        """

        options = [
            ("[1]", "Kopiuj hasło", cls.PURPLE),
            ("[2]", "Pokaż hasło", cls.GREEN),
            ("[3]", "Edytuj", cls.YELLOW),
            ("[4]", "Usuń", cls.RED),
        ]

        menu = "   ".join(
            f"{color}{key}{cls.RESET} {label}" for key, label, color in options
        )
        print(f"\n{menu}")
