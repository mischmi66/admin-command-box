import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pyperclip
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

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrueNAS Admin Tool")
        self.root.geometry("800x600")
        
        # Datenbankverbindung
        self.db_path = get_db_path()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Tabelle erstellen falls nicht existiert
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategorie TEXT NOT NULL,
                befehl TEXT NOT NULL,
                beschreibung TEXT
            )
        """)
        self.conn.commit()
        
        # GUI Komponenten
        self.create_menu()
        self.create_main_interface()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Datei Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Beenden", command=self.root.quit)
        menubar.add_cascade(label="Datei", menu=file_menu)
        
        # Bearbeiten Menü
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Kopieren", command=self.copy_to_clipboard)
        edit_menu.add_command(label="Einfügen", command=self.paste_from_clipboard)
        menubar.add_cascade(label="Bearbeiten", menu=edit_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_interface(self):
        # Hauptframe
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter und Suche
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        # Kategorie Filter
        ttk.Label(filter_frame, text="Kategorie:").pack(side=tk.LEFT, padx=5)
        self.category_filter_var = tk.StringVar()
        self.category_filter_var.set("Alle")  # Standardwert
        category_filter = ttk.OptionMenu(filter_frame, self.category_filter_var, "Alle", "Alle", "GIT", "Mac", "Linux", "fwconsole")
        category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter_var.trace_add('write', lambda *args: self.update_filter())
        
        # Suchfeld
        ttk.Label(filter_frame, text="Suchen:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_data())
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Treeview für Datenanzeige
        self.tree = ttk.Treeview(main_frame, columns=("ID", "Kategorie", "Beschreibung", "Befehl", "Copy"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Kategorie", text="Kategorie")
        self.tree.heading("Beschreibung", text="Beschreibung")
        self.tree.heading("Befehl", text="Befehl")
        self.tree.heading("Copy", text="")
        
        # Spaltenbreiten optimieren
        self.tree.column("ID", width=50, stretch=False)
        self.tree.column("Kategorie", width=120, stretch=False)
        self.tree.column("Beschreibung", width=350)
        self.tree.column("Befehl", width=200)
        self.tree.column("Copy", width=50, stretch=False)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Globales Klick-Event
        self.tree.bind('<Button-1>', self.on_tree_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Aktualisieren", command=self.update_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hinzufügen", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bearbeiten", command=self.edit_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Löschen", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        
        self.load_data()
    
    def load_data(self, category="Alle"):
        self.tree.delete(*self.tree.get_children())
        
        if category == "Alle":
            self.cursor.execute("SELECT * FROM commands ORDER BY befehl ASC")
        else:
            self.cursor.execute("""
                SELECT * FROM commands 
                WHERE kategorie = ?
                ORDER BY befehl ASC
            """, (category,))
        
        for row in self.cursor.fetchall():
            # Korrekte Reihenfolge: ID, Kategorie, Beschreibung, Befehl, Copy
            self.tree.insert("", tk.END, values=(row[0], row[1], row[3], row[2], "📋"))
    
    def update_filter(self, *args):
        """Aktualisiert die Liste basierend auf aktuellem Filter"""
        self.tree.delete(*self.tree.get_children())
        selected_category = self.category_filter_var.get()
        search_query = self.search_var.get()
        
        if selected_category == "Alle":
            query = "SELECT * FROM commands WHERE beschreibung LIKE ? OR befehl LIKE ? ORDER BY befehl ASC"
            params = (f"%{search_query}%", f"%{search_query}%")
        else:
            query = """SELECT * FROM commands 
                    WHERE kategorie = ? 
                    AND (befehl LIKE ? OR beschreibung LIKE ?)
                    ORDER BY befehl ASC"""
            params = (selected_category, f"%{search_query}%", f"%{search_query}%")
        
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            # Korrekte Reihenfolge: ID, Kategorie, Beschreibung, Befehl, Copy
            self.tree.insert("", tk.END, values=(row[0], row[1], row[3], row[2], "📋"))
    
    def filter_data(self, event=None):
        """Trigger für die Suche - ruft einfach update_filter auf"""
        self.update_filter()
    
    def add_entry(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Neuen Befehl hinzufügen")
        
        # Kategorie Dropdown
        ttk.Label(add_window, text="Kategorie:").grid(row=0, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        category_menu = ttk.OptionMenu(add_window, self.category_var, "Mac", "Mac", "Linux", "fwconsole", "GIT")
        category_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(add_window, text="Befehl:").grid(row=1, column=0, padx=5, pady=5)
        command_entry = ttk.Entry(add_window)
        command_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_window, text="Beschreibung:").grid(row=2, column=0, padx=5, pady=5)
        description_entry = ttk.Entry(add_window)
        description_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save():
            self.cursor.execute("""
                INSERT INTO commands (kategorie, befehl, beschreibung)
                VALUES (?, ?, ?)
            """, (self.category_var.get(), command_entry.get(), description_entry.get()))
            self.conn.commit()
            self.load_data()
            add_window.destroy()
        
        ttk.Button(add_window, text="Speichern", command=save).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
    
    def edit_entry(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Eintrag zum Bearbeiten aus")
            return
        
        item_id = self.tree.item(selected[0])['values'][0]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Befehl bearbeiten")
        
        # Aktuelle Werte holen
        self.cursor.execute("SELECT * FROM commands WHERE id=?", (item_id,))
        row = self.cursor.fetchone()
        
        # Kategorie Dropdown
        ttk.Label(edit_window, text="Kategorie:").grid(row=0, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        category_menu = ttk.OptionMenu(edit_window, self.category_var, row[1], "Mac", "Linux", "fwconsole", "GIT")
        category_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(edit_window, text="Befehl:").grid(row=1, column=0, padx=5, pady=5)
        command_entry = ttk.Entry(edit_window)
        command_entry.insert(0, row[2])
        command_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(edit_window, text="Beschreibung:").grid(row=2, column=0, padx=5, pady=5)
        description_entry = ttk.Entry(edit_window)
        description_entry.insert(0, row[3])
        description_entry.grid(row=2, column=1, padx=5, pady=5)
        
        def save():
            self.cursor.execute("""
                UPDATE commands SET
                kategorie = ?,
                befehl = ?,
                beschreibung = ?
                WHERE id = ?
            """, (self.category_var.get(), command_entry.get(), description_entry.get(), item_id))
            self.conn.commit()
            self.load_data()
            edit_window.destroy()
        
        ttk.Button(edit_window, text="Speichern", command=save).grid(row=3, column=1, padx=5, pady=5, sticky=tk.E)
    
    def delete_entry(self):
        selected = self.tree.selection()
        if selected:
            item_id = self.tree.item(selected[0])['values'][0]
            self.cursor.execute("DELETE FROM commands WHERE id=?", (item_id,))
            self.conn.commit()
            self.load_data()
    
    def on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#5":  # Letzte Spalte (Copy)
                item = self.tree.identify_row(event.y)
                db_id = self.tree.item(item)['values'][0]
                self.copy_command(db_id)
    
    def copy_command(self, db_id):
        print('KLICK REGISTRIERT')
        print('\n==== COPY COMMAND CALLED ====')
        print(f'Copy-Funktion gestartet für ID: {db_id}')
        
        try:
            # Durch alle sichtbaren Zeilen im Treeview suchen
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id)['values']
                print(f'\nDEBUG: Werte der Zeile: {values}')
                print(f'DEBUG: Spalten: {self.tree["columns"]}')
                
                current_id = str(values[0])  # ID in erster Spalte
                if current_id == str(db_id):
                    print(f'DEBUG: Match gefunden für ID {db_id}')
                    command = values[3]  # Befehl ist jetzt Spalte 3 (Wert aus DB row[2])
                    print(f'DEBUG: Befehl "{command}" wird kopiert...')
                    
                    # 1. Zuerst kopieren
                    pyperclip.copy(command)
                    print('DEBUG: Befehl in Zwischenablage kopiert')
                    
                    # 2. Dann visuelles Feedback
                    self.tree.set(item_id, column=4, value="✅")  # Direkter Spaltenindex
                    self.tree.update_idletasks()  # Sofort aktualisieren
                    print('DEBUG: Icon auf ✅ aktualisiert')
                    
                    # 3. Reset Timer starten
                    self.root.after(2000, lambda i=item_id: self.tree.set(i, column=4, value="📋"))
                    print('DEBUG: Reset Timer gestartet (2 Sekunden)')
                    return
            
            # Falls nicht gefunden
            print('DEBUG: Befehl wurde nicht in sichtbaren Zeilen gefunden')
            messagebox.showwarning("Info", "Befehl ist im aktuellen Filter nicht sichtbar", parent=self.root)
            
        except Exception as e:
            print(f'DEBUG: FEHLER: {str(e)}')
            messagebox.showerror("Fehler", f"Kopieren fehlgeschlagen:\n{str(e)}", parent=self.root)
    
    def copy_to_clipboard(self):
        selected = self.tree.selection()
        if selected:
            value = self.tree.item(selected[0])['values'][3]  # Befehl in Spalte 3 (DB row[2])
            pyperclip.copy(value)
    
    def paste_from_clipboard(self):
        clipboard_content = pyperclip.paste()
        # Platzhalter für Paste-Logik
        messagebox.showinfo("Eingefügt", f"Zwischenablageinhalt: {clipboard_content}")
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
