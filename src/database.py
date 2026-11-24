import sqlite3


class Database:
    def __init__(self, db_path: str = "data/vault.db"):
        """Inicjalizacja - tworzenie bazy danych vault i tabel."""
        self.db_path = db_path

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            vault_tab = """
                CREATE TABLE IF NOT EXISTS vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    login TEXT NOT NULL,
                    encrypted_password BLOB NOT NULL
                )
            """
            cursor.execute(vault_tab)

            master_secrets_tab = """
                CREATE TABLE IF NOT EXISTS master_secrets (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    auth_salt BLOB NOT NULL,
                    auth_hash BLOB NOT NULL,
                    enc_salt BLOB NOT NULL
                )
            """
            cursor.execute(master_secrets_tab)

        conn.close()

    def save_master_credentials(
        self, auth_salt: bytes, auth_hash: bytes, enc_salt: bytes
    ) -> None:
        """Zapisuje (lub nadpisuje) dane uwierzytelniające Master Password."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = """
                INSERT OR REPLACE INTO master_secrets (id, auth_salt, auth_hash, enc_salt)
                VALUES (1, ?, ?, ?)
            """
            cursor.execute(command, (auth_salt, auth_hash, enc_salt))

        conn.close()

    def get_master_credentials(self) -> tuple[bytes, bytes, bytes] | None:
        """Zwraca (auth_salt, auth_hash, enc_salt) albo None, jeśli tabela jest pusta."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = (
                "SELECT auth_salt, auth_hash, enc_salt FROM master_secrets WHERE id = 1"
            )
            cursor.execute(command)
            output = cursor.fetchone()

        conn.close()

        if output:
            return (output[0], output[1], output[2])
        return None

    def add_entry(self, service_name: str, login: str, passw: bytes) -> None:
        """Dodaje wpis do tabeli vault (serwis, login, zaszyfrowane hasło)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "INSERT INTO vault (service, login, encrypted_password) VALUES (?, ?, ?)"
            cursor.execute(command, (service_name, login, passw))

        conn.close()

    def get_all_services(self) -> list[tuple[int, str, str]]:
        """Zwraca wszystkie zapisane serwisy w tabeli vault wraz z ich id oraz loginem."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT id, service, login FROM vault"
            cursor.execute(command)
            output = list(cursor.fetchall())

        conn.close()

        return output

    def get_entry_by_id(self, index: int) -> tuple | None:
        """Zwraca cały wiersz z vault o danym id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT * FROM vault WHERE id = ?"
            cursor.execute(command, (index,))
            output = cursor.fetchone()

        conn.close()

        return output

    def delete_entry(self, index: int) -> None:
        """Usuwa wiersz o danym id z tabeli vault."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "DELETE FROM vault WHERE id = ?"
            cursor.execute(command, (index,))

        conn.close()

    def update_service_name(self, index: int, service_name: str) -> None:
        """Nadpisuje nazwę serwisu w tabeli vault dla wiersza o danym id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE vault SET service = ? WHERE id = ?"
            cursor.execute(command, (service_name, index))

        conn.close()

    def update_password(self, index: int, passw: bytes) -> None:
        """Nadpisuje zaszyfrowane hasło w tabeli vault dla wiersza o danym id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE vault SET encrypted_password = ? WHERE id = ?"
            cursor.execute(command, (passw, index))

        conn.close()

    def update_login(self, index: int, new_login: str) -> None:
        """Nadpisuje login w tabeli vault dla wiersza o danym id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE vault SET login = ? WHERE id = ?"
            cursor.execute(command, (new_login, index))

        conn.close()

    def get_password(self, index: int) -> bytes:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT encrypted_password FROM vault where id=?"
            cursor.execute(command, (index,))
            passw = cursor.fetchone()

        conn.close()

        return passw[0] if passw else None
