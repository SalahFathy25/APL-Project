import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.ttk import Style

BUTTON_COLOR = '#1ABC9C'
HOVER_COLOR = '#1ABC9A'
FONT = ("Helvetica", 10, 'bold')
LABEL_FONT = ("Arial", 10, 'bold')

class HospitalDB:
    def __init__(self, db_name="projectDatabase.db"):
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
        self.conn.commit()

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

class Hospital:
    def __init__(self, db):
        self.db = db

    def create_hospital(self, h_name, h_address):
        self.db.execute_query("INSERT INTO Hospital (h_name, h_address) VALUES (?, ?)", (h_name, h_address))

    def update_hospital(self, old_name, new_name, new_address):
        self.db.execute_query("UPDATE Hospital SET h_name = ?, h_address = ? WHERE h_name = ?", (new_name, new_address, old_name))

    def delete_hospital(self, h_name):
        self.db.execute_query("DELETE FROM Hospital WHERE h_name = ?", (h_name,))

    def get_all_hospitals(self):
        return self.db.fetch_query("SELECT h_name, h_address FROM Hospital")

class HospitalApp(tk.Tk):
    def __init__(self, db):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("700x700")
        self.hospital_db = db
        self.hospital = Hospital(db)

        self.create_widgets()
        self.populate_table()

    def create_widgets(self):
        self.config(bg='#2C3E50')

        self.grid_rowconfigure(6, weight=1)

        self.label_name = tk.Label(self, text="Hospital Name:", bg='#2C3E50', fg="white", font=LABEL_FONT, width=20)
        self.label_name.grid(row=0, column=0, pady=2, sticky="n", padx=5)

        self.entry_name = tk.Entry(self, font=("Arial", 14), width=20, bd=3)
        self.entry_name.grid(row=0, column=1, pady=2, padx=5, sticky="n")

        self.label_address = tk.Label(self, text="Hospital Address:", bg='#2C3E50', fg="white", font=LABEL_FONT, width=20)
        self.label_address.grid(row=1, column=0, pady=2, sticky="n", padx=5)

        self.entry_address = tk.Entry(self, font=("Arial", 14), width=20, bd=3)
        self.entry_address.grid(row=1, column=1, pady=2, padx=5, sticky="n")

        self.button_create = self.create_styled_button("Create Hospital", self.create_hospital)
        self.button_create.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="n")

        self.button_update = self.create_styled_button("Update Hospital", self.update_hospital)
        self.button_update.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="n")

        self.button_delete = self.create_styled_button("Delete Hospital", self.delete_hospital)
        self.button_delete.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="n")

        self.next_page_button = self.create_styled_button("More Features", self.show_more_features)
        self.next_page_button.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="n")

        style = Style()
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1ABC9C", foreground="black")
        style.configure("Treeview", font=("Arial", 10), rowheight=30, fieldbackground="#EAF2F8")
        style.map("Treeview", background=[("selected", "#AED6F1")])

        self.tree = ttk.Treeview(self, columns=("Name", "Address"), show='headings', style="Treeview")
        self.tree.heading("Name", text="Hospital Name")
        self.tree.heading("Address", text="Hospital Address")
        self.tree.grid(row=6, column=0, columnspan=2, pady=5, sticky="ew", padx=15)

        self.tree.tag_configure("evenrow", background="#f2f2f2")
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def create_styled_button(self, text, command):
        button = tk.Button(self, text=text, command=command, bg=BUTTON_COLOR, activebackground=HOVER_COLOR, fg="white",
                            font=("Arial", 10, 'bold'), padx=6, pady=3, relief='raised', bd=2, width=30)
        button.bind("<Enter>", lambda event: button.configure(bg=HOVER_COLOR))
        button.bind("<Leave>", lambda event: button.configure(bg=BUTTON_COLOR))
        return button

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        hospital_data = self.tree.item(selected_item, "values")
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, hospital_data[0])
        self.entry_address.delete(0, tk.END)
        self.entry_address.insert(0, hospital_data[1])

    def create_hospital(self):
        name = self.entry_name.get()
        address = self.entry_address.get()
        if name and address:
            self.hospital.create_hospital(name, address)
            self.populate_table()
            self.clear_fields()
        else:
            messagebox.showerror("Input Error", "Please provide both name and address.")

    def update_hospital(self):
        selected_item = self.tree.selection()
        if selected_item:
            original_hospital_data = self.tree.item(selected_item[0], "values")
            original_name = original_hospital_data[0]
            original_address = original_hospital_data[1]

            new_name = self.entry_name.get()
            new_address = self.entry_address.get()

            if new_name or new_address:
                updated_name = new_name if new_name else original_name
                updated_address = new_address if new_address else original_address

                self.hospital.update_hospital(original_name, updated_name, updated_address)

                self.populate_table()
                self.clear_fields()
            else:
                messagebox.showerror("Input Error", "Please provide a new name or address to update.")
        else:
            messagebox.showerror("Selection Error", "Please select a hospital to update.")

    def delete_hospital(self):
        name = self.entry_name.get()
        if name:
            self.hospital.delete_hospital(name)
            self.populate_table()
            self.clear_fields()
        else:
            messagebox.showerror("Input Error", "Please provide a hospital name to delete.")

    def populate_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, hospital in enumerate(self.hospital.get_all_hospitals()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, values=hospital, tags=(tag,))

    def show_more_features(self):
        messagebox.showinfo("More Features", "This is where you could implement more functionalities!")

    def clear_fields(self):
        self.entry_name.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)

    def on_closing(self):
        self.hospital_db.close()
        self.destroy()

if __name__ == "__main__":
    db = HospitalDB()
    app = HospitalApp(db)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()