import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DATABASE = "DB/medicine.db"

class HospitalDB:
    def __init__(self, db_name=DATABASE):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Medicine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT,
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


class Medicine:
    def __init__(self, db):
        self.db = db

    def create_medicine(self, name, dosage, price):
        self.db.execute_query("INSERT INTO Medicine (name, dosage, price) VALUES (?, ?, ?)", (name, dosage, price))

    def get_all_medicines(self):
        return self.db.fetch_query("SELECT id, name, dosage, price FROM Medicine")

    def delete_medicine(self, id):
        self.db.execute_query("DELETE FROM Medicine WHERE id = ?", (id,))


class GUIMedicine:
    def __init__(self, root, medicine):
        self.root = root
        self.medicine = medicine
        self.root.title("Medicine")
        self.root.geometry("800x600")

        self.root.config(bg="#34495E")

        self.create_input_fields()
        self.create_table()

    def create_input_fields(self):
        input_frame = tk.Frame(self.root, bg="#2C3E50")
        input_frame.pack(side="top", fill="y")

        labels = ["Name", "Dosage", "Price"]
        self.entries = {}

        for idx, label in enumerate(labels):
            tk.Label(input_frame, text=label, bg="#2C3E50",foreground="white", font=("times", 12,"bold")).grid(row=idx, column=0)
            if label == "Dosage":
                entry = ttk.Combobox(input_frame, values=["Tablets", "Capsules", "Poders", "Oral Solution", "Injectable Solutions"], state="readonly", width=37)
            else:
                entry = tk.Entry(input_frame, width=30, font=("times", 12), relief="solid")
            entry.grid(row=idx, column=1, padx=5, pady=20)
            self.entries[label.lower().replace(" ", "_")] = entry

        self.add_button = tk.Button(input_frame, text="Add Medicine", command=self.add_medicine, bg="#89CFF0", bd=10,
                                    relief="flat", activebackground="#E0FAFF", activeforeground="white",
                                    font=("times", 12, "bold"), cursor="hand2", state="normal", pady=5)
        self.add_button.grid(row=len(labels), column=1, pady=10)

    def create_table(self):
        self.table = ttk.Treeview(self.root, columns=("ID", "Name", "Dosage", "Price"), show="headings")

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("times", 12, "bold"))
        style.configure("Treeview", background="#CEF6FF", foreground="black", rowheight=25, fieldbackground="#CEF6FF")
        style.map("Treeview", background=[('selected', '#D1D8E0')])

        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, anchor="center", width=150)

        self.table.pack(fill=tk.BOTH, expand=True)

        self.load_medicine()

        self.table.bind("<Button-1>", self.handle_delete)

    def add_medicine(self):
        try:
            data = {key: entry.get() for key, entry in self.entries.items()}
            self.medicine.create_medicine(data["name"], data["dosage"], float(data["price"]))
            messagebox.showinfo("Success", "Medicine added successfully.")
            self.load_medicine()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_medicine(self):
        for row in self.table.get_children():
            self.table.delete(row)

        for row in self.medicine.get_all_medicines():
            self.table.insert("", tk.END, values=row)

    def handle_delete(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)

        if column == "#1":
            values = self.table.item(item, "values")
            if values:
                medicine_id = values[0]
                confirm = messagebox.askyesno("Confirm", "Delete medicine with ID {medicine_id}?")
                if confirm:
                    self.medicine.delete_medicine(medicine_id)
                    self.load_medicine()


if __name__ == "__main__":
    db = HospitalDB()
    medicine = Medicine(db)
    root = tk.Tk()
    gui = GUIMedicine(root, medicine)
    root.mainloop()
    db.close()