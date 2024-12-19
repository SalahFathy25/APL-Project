import sqlite3

DATABASE = "DB/projectDatabase.db"

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
        self.execute_query("INSERT INTO Hospital (h_name, h_address) VALUES (?, ?)", (h_name, h_address))

    def read_hospital(self, h_id):
       return self.fetch_query("SELECT * FROM Hospital WHERE h_id = ?", (h_id,))

    def update_hospital(self, h_id, field, value):
        self.execute_query(f"UPDATE Hospital SET {field} = ? WHERE h_id = ?", (value, h_id))

    def delete_hospital(self, h_id):
        self.execute_query("DELETE FROM Hospital WHERE h_id = ?", (h_id,))

#GUI for Hospital
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from PIL import Image, ImageTk

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
        self.geometry("800x600")
        self.hospital_db = db
        self.hospital = Hospital(db)

        self.original_background_image = Image.open("images\hoss.jpg")
        self.background_image = ImageTk.PhotoImage(self.original_background_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_widgets()
        self.populate_table()

    def create_widgets(self):
        button_style = {'bg': 'skyblue', 'font': ('Arial', 14, 'bold'), 'padx': 15, 'pady': 10}

        # Hospital Name Section
        self.label_name = tk.Label(self, text="Hospital Name:", bg='lightblue', font=("Arial", 12, 'bold'))
        self.label_name.pack(pady=5, anchor='w')

        self.entry_name = tk.Entry(self, font=("Arial", 14), width=25)
        self.entry_name.pack(pady=5, anchor='w')

        # Hospital Address Section
        self.label_address = tk.Label(self, text="Hospital Address:", bg='lightblue', font=("Arial", 12, 'bold'))
        self.label_address.pack(pady=5, anchor='w')

        self.entry_address = tk.Entry(self, font=("Arial", 14), width=25)
        self.entry_address.pack(pady=5, anchor='w')

        # Action Buttons
        self.button_create = self.create_styled_button("Create Hospital", self.create_hospital)
        self.button_update = self.create_styled_button("Update Hospital", self.update_hospital)
        self.button_delete = self.create_styled_button("Delete Hospital", self.delete_hospital)
        self.next_page_button = self.create_styled_button("More Features", self.show_more_features)

        # Treeview to display hospital data
        self.tree = ttk.Treeview(self, columns=("Name", "Address"), show='headings')
        self.tree.heading("Name", text="Hospital Name")
        self.tree.heading("Address", text="Hospital Address")
        self.tree.pack(pady=10, anchor='w', fill='x')

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def create_styled_button(self, text, command):
        button = tk.Button(self, text=text, command=command, bg='skyblue', activebackground='lightblue',
                            font=("Arial", 14, 'bold'), padx=15, pady=10, relief='raised', bd=3)
        button.pack(pady=5, anchor='w')

        button.bind("<Enter>", lambda event: button.configure(bg='deepskyblue'))
        button.bind("<Leave>", lambda event: button.configure(bg='skyblue'))

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

        for hospital in self.hospital.get_all_hospitals():
            self.tree.insert("", tk.END, values=hospital)

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