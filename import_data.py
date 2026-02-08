import sqlite3
import os

def get_db_path():
    nas_path = "/Volumes/app-data/db/commands.db"
    if os.path.exists(os.path.dirname(nas_path)):
        return nas_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "commands.db")

def setup_database():
    db_path = get_db_path()
    print(f"📦 Nutze Datenbank unter: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Alte Tabelle löschen und mit EXAKT den Namen neu erstellen, die main.py will
    cursor.execute("DROP TABLE IF EXISTS commands")
    cursor.execute('''
        CREATE TABLE commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kategorie TEXT NOT NULL,
            beschreibung TEXT NOT NULL,
            befehl TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def import_my_data():
    conn = setup_database()
    cursor = conn.cursor()
    
    # Hier sind deine echten Daten für FreePBX 17 und Easybell
    commands = [
        ("FreePBX 17", "Asterisk Konsole öffnen", "asterisk -rvvv"),
        ("FreePBX 17", "FWConsole Reload", "fwconsole reload"),
        ("FreePBX 17", "Dashboard/System-Status", "fwconsole dashboard"),
        ("FreePBX 17", "Modul-Status prüfen", "fwconsole ma list"),
        ("Easybell", "PJSIP Registrierungen", "pjsip show registrations"),
        ("Easybell", "PJSIP Endpunkte (Trunks)", "pjsip show endpoints"),
        ("Easybell", "SIP History/Logs", "pjsip set logger on"),
        ("System", "Netzwerk-Schnittstellen (Mac)", "networksetup -listallnetworkservices")
    ]
    
    cursor.executemany(
        "INSERT INTO commands (kategorie, beschreibung, befehl) VALUES (?, ?, ?)",
        commands
    )
    
    conn.commit()
    conn.close()
    print("🚀 Erfolg! Die Datenbank auf dem MacBook ist jetzt identisch mit dem Mac Mini.")

if __name__ == "__main__":
    import_my_data()
