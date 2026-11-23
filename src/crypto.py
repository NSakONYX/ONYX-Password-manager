import base64
import hashlib
import hmac
import os

from cryptography.fernet import Fernet


class CryptoEngine:
    ITERATIONS = 600_000

    def __init__(self) -> None:
        self.lock: Fernet | None = None

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Wyprowadza 32-bajtowy klucz z hasła i soli za pomocą PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.ITERATIONS,
            dklen=32,
        )

    def create_master_credentials(
        self, master_password: str
    ) -> tuple[bytes, bytes, bytes]:
        """
        Wywołujesz raz przy rejestracji.
        Zwraca (auth_salt, auth_hash, enc_salt) do zapisania w SQLite.
        """
        auth_salt = os.urandom(16)
        enc_salt = os.urandom(16)
        auth_hash = self._derive_key(master_password, auth_salt)

        return auth_salt, auth_hash, enc_salt

    def authenticate(
        self,
        master_password: str,
        auth_salt: bytes,
        stored_auth_hash: bytes,
        enc_salt: bytes,
    ) -> bool:
        """
        Weryfikuje Master Password i odblokowuje sejf (ładuje Fernet do self.lock).
        Zwraca True jeśli hasło się zgadza, False w przeciwnym razie.
        """
        candidate_hash = self._derive_key(master_password, auth_salt)

        if not hmac.compare_digest(candidate_hash, stored_auth_hash):
            return False

        raw_enc_key = self._derive_key(master_password, enc_salt)
        fernet_key = base64.urlsafe_b64encode(raw_enc_key)
        self.lock = Fernet(fernet_key)
        return True

    def lock_vault(self) -> None:
        """Czyści klucz z pamięci RAM."""
        self.lock = None

    def encrypt_data(self, text: str) -> bytes:
        if not self.lock:
            raise ValueError("Brak klucza w pamięci RAM")

        return self.lock.encrypt(text.encode("utf-8"))

    def decrypt_data(self, encrypted_bytes: bytes) -> str:
        """Przyjmuje bytes z bazy danych i zwraca odszyfrowane hasło."""
        if not self.lock:
            raise ValueError("Brak klucza w pamięci RAM")

        return self.lock.decrypt(encrypted_bytes).decode("utf-8")
