import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    def __init__(self):
        self.lock = None
        
    def _generate_key(self, master_password: str, salt: bytes) -> bytes:
        """Metoda generująca klucz AES z hasła i 'soli' """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))
    
    def unlock_value(self, master_password: str, salt: bytes):
        """Otwiera sejf i ładuje klucz szyfrujący do RAM'u"""
        key = self._derive_key(master_password, salt)
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