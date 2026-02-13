Heute wurde die Admin-Command-Box auf ein neues Level gehoben. Hier sind die wichtigsten Änderungen:

Zentrale TrueNAS-Datenbank: Die Datenbank (commands.db) wurde erfolgreich auf dein SMB-Share verschoben. Die App erkennt nun automatisch, ob das Share unter /Volumes/app-data/ gemountet ist.

Intelligente History: Dank der neuen Tabelle placeholder_history merkt sich die App deine Eingaben. Wenn du z. B. einmal eine IP-Adresse für einen Befehl eingibst, wird diese beim nächsten Mal automatisch als Vorschlag im Dialogfeld angezeigt.

Echtzeit-Konsole: Das Output-Fenster streamt den Text nun live. Das verhindert, dass die App bei Befehlen wie caffeinate einfriert, und zeigt dir mit einem Zeitstempel genau an, wann ein Prozess gestartet wurde.

Sicherheit & Kontrolle: Wir haben einen Abbrechen-Button hinzugefügt, um hängende Prozesse zu stoppen. Außerdem warnt dich die App jetzt beim Speichern, falls du versehentlich runde Klammern () statt geschweifter Klammern {} für Platzhalter nutzt, um Shell-Fehler zu vermeiden.

Finaler Build: Die App wurde erfolgreich als macOS-Bundle (Admin-Command-Box.app) kompiliert.


Today the Admin-Command-Box was upgradet to a professional level. Here are the key highlights:

Centralized TrueNAS Database: The commands.db was moved to your SMB share. The app now automatically checks if the share is mounted at /Volumes/app-data/.

Smart History: Using the new placeholder_history table, the app remembers your previous inputs. For example, if you enter an IP address once, it will be pre-filled as a suggestion next time.

Live Console Output: The output window now streams command results in real-time. This prevents the UI from freezing during long-running tasks like caffeinate and provides a start-time timestamp.

Safety & Control: An Abort Button was added to safely terminate background processes. Additionally, the app now warns you when saving a command if you mistakenly use parentheses () instead of curly braces {} for placeholders.

Final Build: The application was successfully compiled into a macOS app bundle (Admin-Command-Box.app).
