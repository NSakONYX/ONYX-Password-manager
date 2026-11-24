import threading

import pyperclip


class ClipboardManager:
    _timer: threading.Timer | None = None

    @classmethod
    def copy(cls, text: str, timeout: int = 15) -> None:
        if cls._timer is not None:
            cls._timer.cancel()

        pyperclip.copy(text)

        if timeout > 0:
            cls._timer = threading.Timer(timeout, cls._clear_if_matches, args=[text])
            cls._timer.daemon = True
            cls._timer.start()

    @classmethod
    def _clear_if_matches(cls, expected_text: str) -> None:
        if pyperclip.paste() == expected_text:
            pyperclip.copy("")
        cls._timer = None

    @classmethod
    def clear(cls) -> None:
        if cls._timer is not None:
            cls._timer.cancel()
            cls._timer = None
        pyperclip.copy("")
