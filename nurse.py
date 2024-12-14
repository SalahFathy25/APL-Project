import sqlite3
from tkinter import *
from tkinter import ttk, messagebox


class NurseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nurse Management")
        self.root.geometry("1500x1000")
        self.root.configure(bg="#34495E")

        self.conn = sqlite3.connect("nurse.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        self.selected_id = None
        self.name_var = StringVar()
        self.phone_var = StringVar()
        self.gender_var = StringVar()
        self.age_var = StringVar()
        self.blood_group_var = StringVar()
        self.address_var = StringVar()
        self.joined_var = StringVar()
        self.certificates_var = StringVar()
        self.education_var = StringVar()

        self.create_form_frame()

        self.create_table_frame()

        self.fetch_data()

        self.age_var.trace("w", self.validate_age)

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Nurses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            gender TEXT,
            age INTEGER,
            blood_group TEXT,
            address TEXT,
            joined TEXT,
            certificates TEXT,
            education TEXT
        )""")
        self.conn.commit()

    def create_form_frame(self):
        form_frame = Frame(self.root, bg="#2C3E50", width=350)
        form_frame.pack(side=LEFT, fill=Y)

        fields = [
            ("Name", self.name_var),
            ("Phone", self.phone_var),
            ("Gender", self.gender_var),
            ("Age", self.age_var),
            ("Blood Group", self.blood_group_var),
            ("Address", self.address_var),
            ("Joined", self.joined_var),
            ("Certificates", self.certificates_var),
            ("Education", self.education_var),
        ]

        for i, (label_text, var) in enumerate(fields):
            Label(form_frame, text=label_text, bg="#2C3E50", fg="white", font=("Helvetica", 12)).grid(row=i, column=0, sticky=W, padx=10, pady=5)
            if label_text == "Gender":
                widget = ttk.Combobox(form_frame, textvariable=var, font=("Helvetica", 12), width=23, state="readonly")
                widget['values'] = ("Male", "Female", "Other")
            else:
                widget = Entry(form_frame, textvariable=var, font=("Helvetica", 12), width=25)
            widget.grid(row=i, column=1, pady=5, padx=10)

        self.action_button = Button(
            form_frame, text="Add nurse", font=("Helvetica", 12, "bold"), bg="#1ABC9C", fg="white", cursor="hand2", command=self.add_or_update_nurse
        )
        self.action_button.grid(row=len(fields), columnspan=2, pady=10)
        Button(
            form_frame, text="Delete nurse", font=("Helvetica", 12, "bold"), bg="#E74C3C", fg="white", cursor="hand2", command=self.delete_nurse
        ).grid(row=len(fields) + 1, columnspan=2, pady=10)

    def create_table_frame(self):
        table_frame = Frame(self.root, bg="#e3f2fd")
        table_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.nurse_table = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Phone", "Gender", "Age", "Blood Group", "Address", "Joined", "Certificates", "Education"),
            show="headings",
        )
        self.nurse_table.pack(fill=BOTH, expand=True)

        for col in self.nurse_table["columns"]:
            self.nurse_table.heading(col, text=col, anchor="center")
            self.nurse_table.column(col, anchor="center", stretch=True, width=100)

        self.nurse_table.bind("<ButtonRelease-1>", self.load_selected_row)

    def add_or_update_nurse(self):
        if self.selected_id:
            self.update_nurse()
        else:
            self.add_nurse()

    def add_nurse(self):
        if not all([self.name_var.get(), self.phone_var.get(), self.gender_var.get(), self.age_var.get(),
                    self.blood_group_var.get(), self.address_var.get(), self.joined_var.get(),
                    self.certificates_var.get(), self.education_var.get()]):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        try:
            self.cursor.execute("""
                INSERT INTO Nurses (name, phone, gender, age, blood_group, address, joined, certificates, education)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.name_var.get(), self.phone_var.get(), self.gender_var.get(),
                int(self.age_var.get()) if self.age_var.get().isdigit() else None,
                self.blood_group_var.get(), self.address_var.get(),
                self.joined_var.get(), self.certificates_var.get(), self.education_var.get()
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "nurse added successfully.")
            self.fetch_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding nurse: {e}")

    def update_nurse(self):
        if not all([self.name_var.get(), self.phone_var.get(), self.gender_var.get(), self.age_var.get(),
                    self.blood_group_var.get(), self.address_var.get(), self.joined_var.get(),
                    self.certificates_var.get(), self.education_var.get()]):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        try:
            self.cursor.execute("""
                UPDATE Nurses SET name = ?, phone = ?, gender = ?, age = ?, blood_group = ?, address = ?, joined = ?, certificates = ?, education = ?
                WHERE id = ?
            """, (
                self.name_var.get(), self.phone_var.get(), self.gender_var.get(),
                int(self.age_var.get()) if self.age_var.get().isdigit() else None,
                self.blood_group_var.get(), self.address_var.get(),
                self.joined_var.get(), self.certificates_var.get(), self.education_var.get(),
                self.selected_id
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "nurse updated successfully.")
            self.fetch_data()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Error updating nurse: {e}")

    def delete_nurse(self):
        if self.selected_id:
            self.cursor.execute("DELETE FROM Nurses WHERE id = ?", (self.selected_id,))
            self.conn.commit()
            messagebox.showinfo("Deleted", "nurse member deleted successfully.")
            self.fetch_data()
            self.clear_fields()
        else:
            messagebox.showerror("Error", "No nurse member selected to delete.")

    def fetch_data(self):
        self.nurse_table.delete(*self.nurse_table.get_children())
        self.cursor.execute("SELECT * FROM Nurses")
        for row in self.cursor.fetchall():
            self.nurse_table.insert("", END, values=row)

    def load_selected_row(self, event):
        selected_row = self.nurse_table.focus()
        if selected_row:
            data = self.nurse_table.item(selected_row, "values")
            if data:
                self.selected_id = data[0]
                self.name_var.set(data[1])
                self.phone_var.set(data[2])
                self.gender_var.set(data[3])
                self.age_var.set(data[4])
                self.blood_group_var.set(data[5])
                self.address_var.set(data[6])
                self.joined_var.set(data[7])
                self.certificates_var.set(data[8])
                self.education_var.set(data[9])

                self.action_button.config(text="Update")

    def validate_age(self):
        age = self.age_var.get()
        if age and not age.isdigit():
            messagebox.showwarning("Input Error", "Age must be a valid integer.")
            self.age_var.set("")

    def clear_fields(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.gender_var.set("")
        self.age_var.set("")
        self.blood_group_var.set("")
        self.address_var.set("")
        self.joined_var.set("")
        self.certificates_var.set("")
        self.education_var.set("")
        self.selected_id = None
        self.action_button.config(text="Add")


if __name__ == "__main__":
    root = Tk()
    app = NurseApp(root)
    root.mainloop()
