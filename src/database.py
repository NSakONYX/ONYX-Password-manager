import sqlite3

class Database:
    def __init__(self, db_path: str = 'data/vault.db'):
        self.db_path = db_path

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            vault_tab = """
                CREATE TABLE IF NOT EXISTS vault (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    username TEXT NOT NULL, 
                    encrypted_password BLOB NOT NULL
                )
            """
            cursor.execute(vault_tab) #service np netflix itp, username np login lub email
            
            master_secrets_tab = """
                CREATE TABLE IF NOT EXISTS master_secrets (
                    id INTEGER PRIMARY KEY CHECK (id=1),
                    salt BLOB NOT NULL,
                    master_hash BLOB NOT NULL
                    
                )
            """
            cursor.execute(master_secrets_tab)

        conn.close()
        
    def get_master_hash(self):
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
        

        

            