import os
from getpass import getpass
import time


class TerminalUI:

    @staticmethod
    def type_print(text: str, delay: float = 0.002):
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print()

    @staticmethod
    def show_banner():
        PURPLE = "\033[95m"
        DARK_PURPLE = "\033[35m"
        RESET = "\033[0m"

        banner = r"""
 ██████╗ ███╗   ██╗██╗   ██╗██╗  ██╗
██╔═══██╗████╗  ██║╚██╗ ██╔╝╚██╗██╔╝
██║   ██║██╔██╗ ██║ ╚████╔╝  ╚███╔╝ 
██║   ██║██║╚██╗██║  ╚██╔╝   ██╔██╗ 
╚██████╔╝██║ ╚████║   ██║   ██╔╝ ██╗
 ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝"""

        subtitle = "     ━━━  K E Y C H A I N  ━━━"

        TerminalUI.type_print(f"{PURPLE}{banner}{RESET}")
        TerminalUI.type_print(f"{DARK_PURPLE}{subtitle}{RESET}\n",0.04)


    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def show_main_menu():
        print("      1. Pokaż zapisane hasła")
        print("      2.     Ustawienia")
        print("      3.       Wyjdź\n\n")
        
