import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pyperclip
import os

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TrueNAS Admin Tool")
        self.root.geometry("800x600")
        
        # Datenbankverbindung
        self.db_path = "/Volumes/app-data/db/commands.db"
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
        
        # Suchfeld
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind('<KeyRelease>', self.filter_data)
        
        # Treeview für Datenanzeige
        self.tree = ttk.Treeview(main_frame, columns=("ID", "Kategorie", "Befehl", "Beschreibung", "Copy"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Kategorie", text="Kategorie")
        self.tree.heading("Befehl", text="Befehl")
        self.tree.heading("Beschreibung", text="Beschreibung")
        self.tree.heading("Copy", text="")
        
        # Spaltenbreiten optimieren
        self.tree.column("ID", width=50, stretch=False)
        self.tree.column("Kategorie", width=100, stretch=False)
        self.tree.column("Befehl", width=300)
        self.tree.column("Beschreibung", width=200)
        self.tree.column("Copy", width=50, stretch=False)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Aktualisieren", command=self.load_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Hinzufügen", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Bearbeiten", command=self.edit_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Löschen", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        
        self.load_data()
    
    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM commands")
        for row in self.cursor.fetchall():
            # Füge Copy-X-Button hinzu
            self.tree.insert("", tk.END, values=row + ("📋",), tags=(f"copy_{row[0]}",))
            self.tree.tag_bind(f"copy_{row[0]}", "<Button-1>", lambda e, id=row[0]: self.copy_command(id))
    
    def filter_data(self, event=None):
        query = self.search_var.get()
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("""
            SELECT * FROM commands 
            WHERE kategorie LIKE ? OR befehl LIKE ? OR beschreibung LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
    
    def add_entry(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Neuen Befehl hinzufügen")
        
        # Kategorie Dropdown
        ttk.Label(add_window, text="Kategorie:").grid(row=0, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        category_menu = ttk.OptionMenu(add_window, self.category_var, "Mac", "Mac", "Linux", "fwconsole")
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
        category_menu = ttk.OptionMenu(edit_window, self.category_var, row[1], "Mac", "Linux", "fwconsole")
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
    
    def copy_command(self, item_id):
        try:
            # Befehl aus DB holen und kopieren
            self.cursor.execute("SELECT befehl FROM commands WHERE id=?", (item_id,))
            command = self.cursor.fetchone()[0]
            pyperclip.copy(command)
            
            # Visuelles Feedback
            self.tree.set(f"I00{item_id}", "Copy", "✅")  # Update Icon
            
            # Reset nach 2 Sekunden
            self.root.after(2000, lambda: self.tree.set(f"I00{item_id}", "Copy", "📋"))
            
        except Exception as e:
            # Fehlerfall: Icon kurz rot anzeigen
            self.tree.set(f"I00{item_id}", "Copy", "❌")
            self.root.after(1000, lambda: self.tree.set(f"I00{item_id}", "Copy", "📋"))
    
    def copy_to_clipboard(self):
        selected = self.tree.selection()
        if selected:
            value = self.tree.item(selected[0])['values'][2]
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
