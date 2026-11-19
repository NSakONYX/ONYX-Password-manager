import pytest
from cryptography.fernet import InvalidToken
from src.crypto import CryptoEngine


@pytest.fixture
def crypto():
    return CryptoEngine()


def test_generate_salt_is_unique_and_16_bytes():
    salt1 = CryptoEngine.generate_salt()
    salt2 = CryptoEngine.generate_salt()

    assert isinstance(salt1, bytes)
    assert len(salt1) == 16
    assert salt1 != salt2


def test_verify_master_password(crypto):
    salt = crypto.generate_salt()
    master_hash = crypto.create_master_hash("TajneHaslo123!", salt)

    assert crypto.verify_master_password("TajneHaslo123!", salt, master_hash) is True
    assert crypto.verify_master_password("ZleHaslo", salt, master_hash) is False


def test_encrypt_and_decrypt_roundtrip(crypto):
    salt = crypto.generate_salt()
    crypto.unlock_vault("MojeMasterHaslo", salt)

    original_text = "SuperHasloDoBanku!@#"
    encrypted = crypto.encrypt_data(original_text)

    assert isinstance(encrypted, bytes)
    assert encrypted != original_text.encode("utf-8")
    assert crypto.decrypt_data(encrypted) == original_text


def test_locked_vault_raises_error(crypto):

    with pytest.raises(ValueError):
        crypto.encrypt_data("test")

    with pytest.raises(ValueError):
        crypto.decrypt_data(b"jakies_bajty")


def test_decrypt_with_wrong_key_raises_invalid_token():
    salt = CryptoEngine.generate_salt()

    engine_a = CryptoEngine()
    engine_a.unlock_vault("PoprawneHaslo", salt)
    encrypted = engine_a.encrypt_data("sekret")

    engine_b = CryptoEngine()
    engine_b.unlock_vault("InneHaslo", salt)

    with pytest.raises(InvalidToken):
        engine_b.decrypt_data(encrypted)