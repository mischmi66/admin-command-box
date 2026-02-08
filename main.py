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
        self.db_path = "/mnt/truenas/database/admin.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
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
        
        # Treeview für Datenanzeige
        self.tree = ttk.Treeview(main_frame, columns=("ID", "Name", "Wert"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Wert", text="Wert")
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
        self.cursor.execute("SELECT * FROM entries")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
    
    def add_entry(self):
        # Platzhalter für Add-Logik
        messagebox.showinfo("Info", "Add-Funktion wird implementiert")
    
    def edit_entry(self):
        # Platzhalter für Edit-Logik
        messagebox.showinfo("Info", "Edit-Funktion wird implementiert")
    
    def delete_entry(self):
        selected = self.tree.selection()
        if selected:
            item_id = self.tree.item(selected[0])['values'][0]
            self.cursor.execute("DELETE FROM entries WHERE id=?", (item_id,))
            self.conn.commit()
            self.load_data()
    
    def copy_to_clipboard(self):
        selected = self.tree.selection()
        if selected:
            value = self.tree.item(selected[0])['values'][1]
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
