import sqlite3
import os

def get_db_path():
    """Gibt den Pfad zur Datenbank zurück"""
    return "/Volumes/daten/it-service/datenbanken/commands.db"

def swap_columns():
    """Tauscht die Inhalte der Spalten 'befehl' und 'beschreibung'"""
    db_path = get_db_path()
    
    if not os.path.exists(db_path):
        print(f"Fehler: Datenbankdatei nicht gefunden unter {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sicherung der aktuellen Daten erstellen
        cursor.execute("SELECT id, befehl, beschreibung FROM commands")
        rows = cursor.fetchall()
        
        # Spalteninhalte tauschen
        for row in rows:
            id, befehl, beschreibung = row
            cursor.execute("""
                UPDATE commands 
                SET befehl = ?, beschreibung = ?
                WHERE id = ?
            """, (beschreibung, befehl, id))
        
        conn.commit()
        print(f"Erfolgreich: {len(rows)} Einträge wurden aktualisiert")
        return True
        
    except sqlite3.Error as e:
        print(f"Datenbankfehler: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Starte Spaltentausch für commands.db...")
    if swap_columns():
        print("Vorgang erfolgreich abgeschlossen")
    else:
        print("Vorgang mit Fehlern abgebrochen")
