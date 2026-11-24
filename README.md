# Onyx Keychain

![Python](https://img.shields.io/badge/Python-3.10%2B-8A2BE2?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Lokalna%20Baza-4B0082?style=for-the-badge&logo=sqlite&logoColor=white)
![Cryptography](https://img.shields.io/badge/Kryptografia-Fernet%20%2F%20PBKDF2-6A0DAD?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Testy-Pytest-9370DB?style=for-the-badge&logo=pytest&logoColor=white)

Lekki, w 100% offline'owy menedżer haseł działający w terminalu, napisany w Pythonie. Zaprojektowany z naciskiem na czystą architekturę, dobre praktyki kryptograficzne oraz bezpieczne lokalne przechowywanie danych.

---

## Funkcjonalności

- **100% Offline i Local-First:** Wszystkie dane logowania zostają na Twoim komputerze w lokalnej bazie SQLite (`data/vault.db`) — bez chmury i bez połączeń sieciowych.
- **Silne szyfrowanie:** Hasła są szyfrowane za pomocą Fernet (AES-128-CBC + uwierzytelnianie HMAC-SHA256), a klucze wyprowadzane przy użyciu funkcji PBKDF2-HMAC-SHA256.
- **Separacja kluczy (Key Separation):** Aplikacja używa dwóch niezależnych soli kryptograficznych (`auth_salt` i `enc_salt`), rozdzielając weryfikację hasła głównego od szyfrowania skarbca.
- **Bezpieczna obsługa schowka:** Kopiowanie haseł bezpośrednio do schowka bez wypisywania ich w historii terminala, wraz z bezpiecznym czyszczeniem (schowek jest czyszczony tylko wtedy, gdy nadal znajduje się w nim skopiowane hasło).
- **Czytelny interfejs CLI:** Autorski interfejs terminalowy z kolorowaniem ANSI, maskowaniem wpisywanych haseł (`getpass`) i prostą nawigacją.

---

## Architektura bezpieczeństwa

Onyx Keychain został zaprojektowany przy założeniu, że atakujący może uzyskać dostęp do pliku `vault.db` oraz kodu źródłowego:

1. **Brak hasła głównego i kluczy na dysku:** Ani Master Password, ani klucz szyfrujący Fernet nigdy nie są zapisywane w bazie danych. Klucz szyfrujący jest wyliczany w locie przy logowaniu i istnieje wyłącznie w pamięci RAM przez czas trwania sesji.
2. **Separacja kluczy kryptograficznych:**
   - `auth_salt` + Master Password → wylicza `auth_hash` (zapisany w tabeli `master_secrets` wyłącznie do sprawdzania poprawności logowania).
   - `enc_salt` + Master Password → wylicza klucz szyfrujący Fernet (trzymany wyłącznie w pamięci operacyjnej).
   - Znajomość `auth_hash` nie pozwala w żaden sposób wyliczyć klucza szyfrującego skarbiec.
3. **Unikalność każdego wpisu:** Fernet automatycznie generuje losowy wektor inicjalizujący (IV) dla każdego szyfrowanego hasła, dzięki czemu dwa identyczne hasła zapisane w bazie wyglądają zupełnie inaczej.

---

## Struktura projektu

```text
ONYX-Password-manager/
├── data/
│   └── vault.db            # Lokalna baza SQLite (generowana automatycznie, w .gitignore)
├── src/
│   ├── clipboard.py        # Kopiowanie i bezpieczne czyszczenie schowka
│   ├── crypto.py           # Wyprowadzanie kluczy (PBKDF2) i szyfrowanie Fernet
│   ├── database.py         # Warstwa dostępu do bazy SQLite
│   └── ui.py               # Interfejs terminalowy, style ANSI i obsługa wejścia
├── tests/
│   ├── test_crypto.py      # Testy jednostkowe warstwy kryptograficznej
│   └── test_database.py    # Testy jednostkowe operacji na bazie danych
├── main.py                 # Punkt startowy aplikacji i logika menu
└── requirements.txt        # Zależności projektu


## Uruchomienie projektu

### Wymagania

- Python 3.10 lub nowszy (wykorzystuje `match-case` oraz nowe adnotacje typów)

### Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone [https://github.com/](https://github.com/)<twoj-nick>/ONYX-Password-manager.git
   cd ONYX-Password-manager
   ```

2. Utwórz i aktywuj środowisko wirtualne (`venv`):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux / macOS:
   source venv/bin/activate
   ```

3. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

4. Uruchom aplikację:
   ```bash
   python main.py
   ```



