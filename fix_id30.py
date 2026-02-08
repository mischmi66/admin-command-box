import sqlite3
import os

def get_db_path():
    """Prüft verschiedene mögliche Datenbankpfade"""
    paths = [
        "/Volumes/app-data/db/commands.db",  # MacBook Pfad
        "/Volumes/daten/it-service/datenbanken/commands.db",  # Mac Mini Pfad
        "commands.db"  # Lokale Fallback-DB
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return "commands.db"  # Finaler Fallback

def fix_id30():
    """Tauscht Befehl und Beschreibung für ID 30"""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Aktuelle Werte von ID 30 holen
        cursor.execute("SELECT befehl, beschreibung FROM commands WHERE id = 30")
        row = cursor.fetchone()
        
        if not row:
            print("Fehler: ID 30 nicht gefunden")
            return False
        
        befehl, beschreibung = row
        
        # Werte tauschen
        cursor.execute("""
            UPDATE commands 
            SET befehl = ?, beschreibung = ?
            WHERE id = 30
        """, (beschreibung, befehl))
        
        conn.commit()
        print(f"Erfolgreich: ID 30 wurde aktualisiert (Befehl: {beschreibung}, Beschreibung: {befehl})")
        return True
        
    except sqlite3.Error as e:
        print(f"Datenbankfehler: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starte Korrektur für ID 30...")
    if fix_id30():
        print("Vorgang erfolgreich abgeschlossen")
    else:
        print("Vorgang mit Fehlern abgebrochen")
