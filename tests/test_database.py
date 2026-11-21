import sqlite3

import pytest

from src.database import Database


@pytest.fixture
def db(tmp_path):

    db_file = tmp_path / "test_vault.db"
    return Database(str(db_file))


def test_empty_database_on_init(db):

    assert db.get_master_hash() is None
    assert db.get_master_salt() is None
    assert db.get_all_services() == []


def test_save_hash_salt_blocks_overwrite(db):
    fake_hash = b"1234567890"
    fake_salt = b"abcdefghij"

    db.save_hash_salt(fake_hash, fake_salt)

    assert db.get_master_hash() == fake_hash
    assert db.get_master_salt() == fake_salt

    with pytest.raises(sqlite3.IntegrityError):
        db.save_hash_salt(b"nowy_hash", b"nowa_sol")


def test_update_hash_salt(db):
    db.save_hash_salt(b"stary_hash", b"stara_sol")
    db.update_hash_salt(b"nowy_hash", b"nowa_sol")

    assert db.get_master_hash() == b"nowy_hash"
    assert db.get_master_salt() == b"nowa_sol"


def test_add_and_get_entry(db):
    db.add_entry("Netflix", "jan@kowalski.pl", b"zaszyfrowane_haslo_123")

    services = db.get_all_services()
    assert services == [(1, "Netflix")]

    entry = db.get_entry_by_id(1)
    assert entry == (1, "Netflix", "jan@kowalski.pl", b"zaszyfrowane_haslo_123")


def test_get_nonexistent_entry_returns_none(db):
    assert db.get_entry_by_id(999) is None


def test_update_entry_fields(db):
    db.add_entry("Netflix", "stary@mail.pl", b"stare_haslo")

    db.update_service_name(1, "HBO Max")
    db.update_login(1, "nowy@mail.pl")
    db.update_password(1, b"nowe_haslo")

    entry = db.get_entry_by_id(1)
    assert entry == (1, "HBO Max", "nowy@mail.pl", b"nowe_haslo")


def test_delete_entry(db):
    db.add_entry("Spotify", "user1", b"pass1")
    db.delete_entry(1)

    assert db.get_entry_by_id(1) is None
    assert db.get_all_services() == []
