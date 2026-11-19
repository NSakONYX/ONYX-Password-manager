import base64
import hashlib
import hmac
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    def __init__(self):
        self.lock = None


    @staticmethod
    def generate_salt() -> bytes:
        """Generuje losową 16-bajtową sól."""
        return os.urandom(16)


    def _generate_key(self, master_password: str, salt: bytes) -> bytes:
        """Metoda generująca klucz AES z hasła i 'soli' """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))


    def create_master_hash(self, master_password: str, salt: bytes) -> bytes:
        """Tworzy bezpieczny hash z klucza do zapisu w bazie (tabela master_secrets)."""
        key = self._generate_key(master_password, salt)
        return hashlib.sha256(key).digest()


    def verify_master_password(self, master_password: str, salt: bytes, stored_hash: bytes) -> bool:
        """Porównuje wpisane hasło z hashem zapisanym w bazie."""
        candidate_hash = self.create_master_hash(master_password, salt)
        return hmac.compare_digest(candidate_hash, stored_hash)


    def unlock_vault(self, master_password: str, salt: bytes):
        """Otwiera sejf i ładuje klucz szyfrujący do RAM'u"""
        key = self._generate_key(master_password, salt)
        self.lock = Fernet(key)


    def encrypt_data(self, text: str) -> bytes:
        if not self.lock:
            raise ValueError("Brak klucza w pamięci RAM")

        return self.lock.encrypt(text.encode('utf-8'))


    def decrypt_data(self, encrypted_bytes: bytes) -> str:
        """Przyjmuje bytes z bazy danych i zwraca gotowe do skopiowania, zapamiętane hasło"""
        if not self.lock:
            raise ValueError("Brak klucza w pamięci RAM")

        return self.lock.decrypt(encrypted_bytes).decode('utf-8')