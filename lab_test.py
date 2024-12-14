import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DATABASE = "lab_test.db"

class HospitalDB:
    def __init__(self, db_name=DATABASE):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Hospital (
                h_id INTEGER PRIMARY KEY AUTOINCREMENT,
                h_name TEXT NOT NULL,
                h_address TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patient (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT,
                joined TEXT,
                certificates TEXT,
                education TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Doctor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT,
                joined TEXT,
                certificates TEXT,
                education TEXT,
                specialty TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Nurse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT,
                joined TEXT,
                certificates TEXT,
                education TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Medicine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT,
                price REAL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS PharmAssistant (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT,
                joined TEXT,
                certificates TEXT,
                education TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS LabAssistant (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT,
                joined TEXT,
                certificates TEXT,
                education TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Receptionist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                gender TEXT DEFAULT 'Unknown',
                age INTEGER,
                bloodgroup TEXT,
                address TEXT,
                joined TEXT,
                certificates TEXT,
                education TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS LabTest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL
            )
        """)

        self.conn.commit()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class LabTest:
    def __init__(self, db):
        self.db = db

    def create_lab_test(self, name, price):
        self.db.execute_query("INSERT INTO LabTest (name, price) VALUES (?, ?)", (name, price))

    def read_lab_test(self, lab_test_id):
        return self.db.fetch_query("SELECT * FROM LabTest WHERE id = ?", (lab_test_id,))

    def update_lab_test(self, lab_test_id, field, value):
        self.db.execute_query("UPDATE LabTest SET {field} = ? WHERE id = ?", (value, lab_test_id))

    def delete_lab_test(self, lab_test_id):
        self.db.execute_query("DELETE FROM LabTest WHERE id = ?", (lab_test_id,))

    def get_all_lab_tests(self):
        return self.db.fetch_query("SELECT * FROM LabTest")

class GUILabTest:
    def __init__(self, root, labTest):
        self.root = root
        self.labTest = labTest
        self.root.title("Lab Test Management")
        self.root.geometry("1500x1000")

        self.root.config(bg="#0047AB")

        self.create_input_fields()
        self.create_table()

    def create_input_fields(self):
        input_frame = tk.Frame(self.root, bg="#0047AB")
        input_frame.pack(side="left")

        labels = ["Name", "Price"]
        self.entries = {}

        for idx, label in enumerate(labels):
            tk.Label(input_frame, text=label, bg="#0047AB", font=("times", 12, "bold")).grid(row=idx, column=0, sticky="e")

            entry = tk.Entry(input_frame, width=30, font=("times", 12), relief="solid")
            entry.grid(row=idx, column=1, padx=5, pady=20)
            self.entries[label.lower().replace(" ", "_")] = entry

        self.add_button = tk.Button(input_frame, text="Add Test", command=self.add_lab_test, bg="#89CFF0", bd=10,
                                    relief="flat", activebackground="#E0FAFF", activeforeground="white",
                                    font=("times", 10, "bold", "italic"), cursor="heart", state="normal", pady=10)
        self.add_button.grid(row=len(labels), column=1, pady=10)

    def create_table(self):
        self.table = ttk.Treeview(self.root, columns=("ID", "Name", "Price"), show="headings", style="Treeview")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("times", 12, "bold"))

        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=100, anchor="center")

        style.configure("Treeview", background="#CEF6FF", foreground="black", rowheight=25, fieldbackground="#CEF6FF")
        style.map("Treeview", background=[('selected', '#D1D8E0')])

        self.table.pack(fill=tk.BOTH, expand=True)
        self.load_lab_tests()

    def add_lab_test(self):
        try:
            data = {key: entry.get() for key, entry in self.entries.items()}
            self.labTest.create_lab_test(data["name"], float(data["price"]))
            messagebox.showinfo("Success", "Test added successfully.")
            self.load_lab_tests()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_lab_tests(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for row in self.labTest.get_all_lab_tests():
            self.table.insert("", tk.END, values=row)

        self.table.bind("<Button-1>", self.handle_delete)

    def handle_delete(self, event):
        item = self.table.identify('item', event.x, event.y)
        column = self.table.identify_column(event.x)

        if column == '#1':
            values = self.table.item(item, "values")
            if values:
                lab_test_id = values[0]
                confirm = messagebox.askyesno("Confirm", "Delete lab test with ID {lab_test_id}?")
                if confirm:
                    self.labTest.delete_lab_test(lab_test_id)
                    self.load_lab_tests()

if __name__ == "__main__":
    db = HospitalDB()
    labTest = LabTest(db)
    root = tk.Tk()
    gui = GUILabTest(root, labTest)
    root.mainloop()
    db.close()
