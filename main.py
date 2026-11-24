import os

from src.app import OnyxApp


def main() -> None:
    os.makedirs("data", exist_ok=True)
    app = OnyxApp("data/vault.db")
    app.run()


if __name__ == "__main__":
    main()
