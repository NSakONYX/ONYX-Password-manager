import sqlite3


class Database:
    def __init__(self, db_path: str = "data/vault.db"):
        """Inicjalizacja - tworzenie bazy danych vault i tworzenie tabeli"""

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
            cursor.execute(vault_tab)  # service np netflix itp

            master_secrets_tab = """
                CREATE TABLE IF NOT EXISTS master_secrets (
                    id INTEGER PRIMARY KEY CHECK (id=1),
                    salt BLOB NOT NULL,
                    master_hash BLOB NOT NULL
                    
                )
            """
            cursor.execute(master_secrets_tab)

        conn.close()

    def get_master_hash(self) -> bytes | None:
        """Metoda zwracajaca master_hash z tabeli master_secrets. Zwracany typ - bytes"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT master_hash FROM master_secrets WHERE id=1"
            cursor.execute(command)
            output = cursor.fetchone()

        conn.close()

        if output:
            return output[0]
        else:
            return None

    def get_master_salt(self) -> bytes | None:
        """Metoda zwracajaca salt z tabeli master_secrets. Zwracany typ - bytes"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT salt FROM master_secrets WHERE id=1"
            cursor.execute(command)
            output = cursor.fetchone()

        conn.close()

        if output:
            return output[0]
        else:
            return None

    def save_hash_salt(self, master_hash: bytes, salt: bytes):
        """Metoda przyjmująca wygenerowany master_hash i salt, ktora zapisuje je w tabeli master_secrets.
        !UWAGA - UZYWAC TYLKO PRZY PUSTEJ TABELI master_secrets!
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = (
                "INSERT INTO master_secrets (id, salt, master_hash) VALUES (1,?,?)"
            )
            values = (salt, master_hash)
            cursor.execute(command, values)

        conn.close()

    def update_hash_salt(self, master_hash: bytes, salt: bytes):
        """Metoda ktora nadpisuje master_hash i salt w tabeli master_secrets. Do uzycia przy zmianie master_password"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE master_secrets SET salt=?, master_hash=? WHERE id=1"
            values = (salt, master_hash)
            cursor.execute(command, values)

        conn.close()

    def add_entry(self, service_name: str, login: str, passw: bytes):
        """Metoda dodajaca wpis do vault, przyjmujaca nazwe serwisu (np. netflix), login (np. email) i haslo"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = (
                "INSERT INTO vault (service, login, encrypted_password) VALUES (?,?,?)"
            )
            values = (service_name, login, passw)
            cursor.execute(command, values)

        conn.close()

    def get_all_services(self):
        """Metoda zwracajaca wszystkie zapisane serwisy w tabeli vault, wraz z ich id"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT id, service FROM vault"
            cursor.execute(command)
            output = cursor.fetchall()

        conn.close()

        return output

    def get_entry_by_id(self, index: int):
        """Metoda zwracajaca caly wiersz z vault o danym id"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "SELECT * FROM vault WHERE id=?"
            cursor.execute(command, (index,))
            output = cursor.fetchone()

        conn.close()

        return output

    def delete_entry(self, index: int):
        """Metoda, ktora usunie wiersz o danym id z tabeli vault"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "DELETE FROM vault WHERE id=?"
            cursor.execute(command, (index,))

        conn.close()

    def update_service_name(self, index: int, service_name: str):
        """Metoda nadpisujaca nazwe serwisu w tabeli vault dla wiersza o danym id"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE vault SET service=? WHERE id=?"
            cursor.execute(command, (service_name, index))

        conn.close()

    def update_password(self, index: int, passw: bytes):
        """Metoda nadpisujaca haslo w tabeli vault dla wiersza o danym id"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE vault SET encrypted_password=? WHERE id=?"
            cursor.execute(command, (passw, index))

        conn.close()

    def update_login(self, index: int, new_login: int):
        """Metoda nadpisujaca login w tabeli vault dla wiersza o danym id"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            command = "UPDATE vault SET login=? WHERE id=?"
            cursor.execute(command, (new_login, index))

        conn.close()
