import sqlite3

# Pfad zu deiner Datenbank auf dem TrueNAS
db_path = "/Volumes/app-data/db/commands.db"

# Die vollständige Befehlsliste (Zusammenführung deiner Liste + Experten-Tipps)
commands = [
    # --- GIT ---
    ('GIT', 'git status', 'Status der Dateien im Repository prüfen'),
    ('GIT', 'git add .', 'Alle Änderungen für den nächsten Commit vormerken'),
    ('GIT', 'git commit -m "{Message}"', 'Änderungen lokal mit Nachricht speichern'),
    ('GIT', 'git push', 'Lokale Commits zum GitHub Repository hochladen'),
    ('GIT', 'git pull', 'Neueste Änderungen von GitHub herunterladen'),
    ('GIT', 'git log --oneline', 'Kompakte Ansicht der letzten Commits'),
    ('GIT', 'git checkout -b {Branchname}', 'Neuen Branch erstellen und dorthin wechseln'),
    ('GIT', 'git remote -v', 'Anzeigen der verknüpften Remote-Repositorys'),
    ('GIT', 'git reset --hard', 'ALLE lokalen Änderungen verwerfen (Vorsicht!)'),
    ('GIT', 'git branch', 'Liste aller lokalen Branches anzeigen'),

    # --- MAC ---
    ('Mac', 'softwareupdate -l', 'Nach verfügbaren macOS Updates suchen'),
    ('Mac', 'diskutil list', 'Übersicht aller angeschlossenen Laufwerke'),
    ('Mac', 'purge', 'Inaktiven RAM-Speicher zwangsweise freigeben'),
    ('Mac', 'networksetup -getairportnetwork en0', 'Aktuelles WLAN-Netzwerk anzeigen'),
    ('Mac', 'top -o cpu', 'Prozesse nach CPU-Last sortiert anzeigen'),
    ('Mac', 'caffeinate -u -t {Sekunden}', 'Verhindert den Ruhezustand für X Sekunden'),
    ('Mac', 'sudo lsof -iVP -n | grep LISTEN', 'Offene Ports und lauschende Apps anzeigen'),
    ('Mac', 'pmset -g', 'Aktuelle Energieeinstellungen prüfen'),
    ('Mac', 'tmutil status', 'Status des Time Machine Backups prüfen'),
    ('Mac', 'killall Finder', 'Finder neu starten (bei Hängern)'),

    # --- LINUX ---
    ('Linux', 'sudo apt update && sudo apt upgrade -y', 'System komplett aktualisieren'),
    ('Linux', 'df -h', 'Speicherplatzbelegung der Laufwerke (human-readable)'),
    ('Linux', 'free -m', 'Arbeitsspeicherbelegung in MB anzeigen'),
    ('Linux', 'htop', 'Interaktive Prozessübersicht (Task-Manager)'),
    ('Linux', 'journalctl -xe', 'Letzte Systemprotokolle zur Fehlersuche anzeigen'),
    ('Linux', 'lsblk', 'Blockgeräte und Partitionen auflisten'),
    ('Linux', 'systemctl status {Service}', 'Status eines Dienstes prüfen'),
    ('Linux', 'tail -f /var/log/syslog', 'Echtzeit-Ansicht der System-Logdatei'),
    ('Linux', 'ip a', 'Netzwerkschnittstellen und IP-Adressen anzeigen'),
    ('Linux', 'du -sh *', 'Größe der Ordner im aktuellen Verzeichnis anzeigen'),

    # --- FWCONSOLE (Deine FreePBX 17 Mitarbeiter-Liste) ---
    ('fwconsole', 'fwconsole restart', 'ACHTUNG: Startet Asterisk neu. Nutzen nach RTP-Port-Fix (Easybell) oder Systemhängern.'),
    ('fwconsole', 'fwconsole reload', 'Konfiguration neu laden (wie roter Apply Button). Aktiviert Console/DB Änderungen.'),
    ('fwconsole', 'fwconsole chown', 'Allheilmittel: Setzt Dateiberechtigungen auf asterisk zurück. Hilft bei Permission Denied.'),
    ('fwconsole', 'fwconsole motd', 'Message of the Day: Schnelle Prüfung von IP-Adresse und installierter Version.'),
    ('fwconsole', 'fwconsole ma list', 'Listet alle Module und Status (Enabled, Disabled, Broken, Upgrade Available).'),
    ('fwconsole', 'fwconsole ma upgradeall', 'Aktualisiert alle Module. Regelmäßig nutzen, um System aktuell zu halten.'),
    ('fwconsole', 'fwconsole ma install {modulname}', 'Installiert oder aktualisiert ein spezifisches Modul (z.B. core).'),
    ('fwconsole', 'fwconsole backup --restore {pfad/zu/datei.tar.gz}', 'Wiederherstellung via Konsole. Konvertiert v15/16 SIP zu PJSIP.'),
    ('fwconsole', 'fwconsole convert digit_to_pjsip -a', 'Kritisch v17: Konvertiert alle chan_sip Nebenstellen zu PJSIP (Asterisk 21 Pflicht).'),
    ('fwconsole', 'fwconsole validate', 'Integritätsprüfung: Vergleicht installierte Dateien mit Sangoma-Originalen (Sicherheitscheck).'),
    ('fwconsole', 'fwconsole firewall stop', 'STOPPT die Firewall. Nutzen, wenn man sich selbst ausgesperrt hat.'),
    ('fwconsole', 'fwconsole firewall start', 'Startet das Firewall-Modul wieder.'),
    ('fwconsole', 'fwconsole sa lock-repo', 'Sichert Debian 12 (Bookworm) Stand. Verhindert ungewolltes Update auf Debian 13.'),
    ('fwconsole', 'fwconsole trunks --list', 'Status aller SIP-Trunks anzeigen (Easybell Check).')
]

def import_now():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Wir nutzen INSERT OR IGNORE basierend auf Kategorie+Befehl, um Duplikate zu vermeiden
        for cat, cmd, desc in commands:
            cursor.execute("""
                INSERT INTO commands (kategorie, befehl, beschreibung) 
                SELECT ?, ?, ? WHERE NOT EXISTS 
                (SELECT 1 FROM commands WHERE kategorie = ? AND befehl = ?)
            """, (cat, cmd, desc, cat, cmd))
        
        conn.commit()
        conn.close()
        print(f"🚀 Erfolg: Die Datenbank wurde mit deiner FreePBX 17 Liste und den Experten-Tipps aktualisiert!")
    except Exception as e:
        print(f"❌ Fehler beim Import: {e}")

if __name__ == "__main__":
    import_now()
