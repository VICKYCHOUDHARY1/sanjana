import tkinter as tk
from tkinter import messagebox
import csv
from pathlib import Path

# Constants
CSV_FILE = 'records.csv'
HEADERS = ['admission_no', 'student_name', 'student_class', 'roll', 'father_name', 
          'marks_s1', 'marks_s2', 'marks_s3', 'marks_s4', 'marks_s5', 'marks_s6', 'total_marks']
CREDENTIALS = {
    "student": {"username": "student", "password": "student"},
    "teacher": {"username": "teacher", "password": "teacher"}
}

# Database functions
def ensure_csv_exists():
    if not Path(CSV_FILE).exists():
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()

def get_all_records():
    ensure_csv_exists()
    with open(CSV_FILE, 'r', newline='') as file:
        return list(csv.DictReader(file))

def add_record(record):
    ensure_csv_exists()
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writerow(record)

def update_record(admission_no, updated_record):
    records = get_all_records()
    new_records = []
    for record in records:
        if record['admission_no'] == admission_no:
            new_records.append(updated_record)
        else:
            new_records.append(record)
    
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(new_records)

def delete_record(admission_no):
    records = get_all_records()
    new_records = [r for r in records if r['admission_no'] != admission_no]
    
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(new_records)
    
    return len(records) != len(new_records)

def get_record_by_admission(admission_no):
    records = get_all_records()
    return next((r for r in records if r['admission_no'] == admission_no), None)

def authenticate_user(username, password, role):
    return (username == CREDENTIALS[role]['username'] and 
            password == CREDENTIALS[role]['password'])

class StudentManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Student Management System")
        self.setup_main_window()
        
    def setup_main_window(self):
        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack()
        
        tk.Label(self.frame, text="Student Management System", 
                font=("Arial", 16)).pack(pady=10)
        tk.Button(self.frame, text="Student Login", width=20, 
                 command=self.student_login).pack(pady=5)
        tk.Button(self.frame, text="Teacher Login", width=20, 
                 command=self.teacher_login).pack(pady=5)

    def student_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Student Login")
        
        tk.Label(login_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(login_window)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(login_window, text="Admission No:").grid(row=1, column=0, padx=5, pady=5)
        admission_entry = tk.Entry(login_window)
        admission_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def verify():
            record = get_record_by_admission(admission_entry.get())
            if record and record['student_name'] == name_entry.get():
                self.show_result(record)
                login_window.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials!")
        
        tk.Button(login_window, text="View Result", 
                 command=verify).grid(row=2, column=0, columnspan=2, pady=10)

    def teacher_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Teacher Login")

        tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        username_entry = tk.Entry(login_window)
        username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def verify():
            if authenticate_user(username_entry.get(), password_entry.get(), 'teacher'):
                self.show_admin_panel()
                login_window.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials!")
        
        tk.Button(login_window, text="Login", 
                 command=verify).grid(row=2, column=0, columnspan=2, pady=10)

    def show_result(self, record):
        result_window = tk.Toplevel(self.root)
        result_window.title("Student Result")
        
        details = [("Name", record['student_name']), 
                  ("Class", record['student_class']),
                  ("Admission No", record['admission_no']), 
                  ("Father's Name", record['father_name'])]
        
        for i, (label, value) in enumerate(details):
            tk.Label(result_window, text=f"{label}: {value}").pack(pady=2)
        
        tk.Label(result_window, text="Marks", 
                font=("Arial", 12, "bold")).pack(pady=5)
        total = 0
        for i in range(1, 7):
            marks = int(record[f'marks_s{i}'])
            total += marks
            tk.Label(result_window, text=f"Subject {i}: {marks}").pack()
        
        tk.Label(result_window, text=f"Total Marks: {total}", 
                font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(result_window, text="Close", 
                 command=result_window.destroy).pack(pady=10)

    def show_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        admin_window.title("Admin Panel")
        
        buttons = [("Add Record", self.add_record), 
                  ("View Records", self.view_records),
                  ("Update Record", self.update_record), 
                  ("Delete Record", self.delete_record)]
        
        for text, command in buttons:
            tk.Button(admin_window, text=text, width=20, 
                     command=command).pack(pady=5)

    def add_record(self):
        window = tk.Toplevel(self.root)
        window.title("Add Record")
        entries = {}
        
        fields = ['Student Name', 'Class', 'Roll', "Father's Name", 'Admission No'] + \
                [f'Subject {i} Marks' for i in range(1, 7)]
        
        for i, field in enumerate(fields):
            tk.Label(window, text=field + ":").grid(row=i, column=0, padx=5, pady=2)
            entries[field] = tk.Entry(window)
            entries[field].grid(row=i, column=1, padx=5, pady=2)
        
        def save():
            try:
                record = {
                    'student_name': entries['Student Name'].get(),
                    'student_class': entries['Class'].get(),
                    'roll': entries['Roll'].get(),
                    'father_name': entries["Father's Name"].get(),
                    'admission_no': entries['Admission No'].get()
                }
                for i in range(1, 7):
                    record[f'marks_s{i}'] = entries[f'Subject {i} Marks'].get()
                
                add_record(record)
                messagebox.showinfo("Success", "Record added successfully!")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(window, text="Save", 
                 command=save).grid(row=len(fields), column=0, columnspan=2, pady=10)

    def view_records(self):
        window = tk.Toplevel(self.root)
        window.title("View Records")
        
        records = get_all_records()
        if not records:
            tk.Label(window, text="No records found!").pack(pady=20)
            return
        
        table_frame = tk.Frame(window)
        table_frame.pack(padx=10, pady=10)
        
        for col, header in enumerate(HEADERS):
            tk.Label(table_frame, text=header.title(), 
                    font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=5)
        
        for row, record in enumerate(records, 1):
            for col, header in enumerate(HEADERS):
                tk.Label(table_frame, 
                        text=record.get(header, '')).grid(row=row, column=col, padx=5, pady=2)

    def update_record(self):
        window = tk.Toplevel(self.root)
        window.title("Update Record")
        
        tk.Label(window, text="Admission No:").pack(pady=5)
        admission_entry = tk.Entry(window)
        admission_entry.pack(pady=5)
        
        def fetch():
            record = get_record_by_admission(admission_entry.get())
            if not record:
                messagebox.showerror("Error", "Record not found!")
                return
            
            update_frame = tk.Frame(window)
            update_frame.pack(pady=10)
            entries = {}
            
            for i, (key, value) in enumerate(record.items()):
                if key != 'admission_no':
                    tk.Label(update_frame, text=key.title() + ":").grid(row=i, column=0, padx=5, pady=2)
                    entries[key] = tk.Entry(update_frame)
                    entries[key].insert(0, value)
                    entries[key].grid(row=i, column=1, padx=5, pady=2)
            
            def save():
                try:
                    updated_record = {'admission_no': admission_entry.get()}
                    updated_record.update({k: entries[k].get() for k in entries})
                    update_record(admission_entry.get(), updated_record)
                    messagebox.showinfo("Success", "Record updated successfully!")
                    window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            tk.Button(update_frame, text="Save", 
                     command=save).grid(row=len(record), column=0, columnspan=2, pady=10)
        
        tk.Button(window, text="Fetch Record", command=fetch).pack(pady=5)

    def delete_record(self):
        window = tk.Toplevel(self.root)
        window.title("Delete Record")
        
        tk.Label(window, text="Admission No:").pack(pady=5)
        admission_entry = tk.Entry(window)
        admission_entry.pack(pady=5)
        
        def delete():
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
                if delete_record(admission_entry.get()):
                    messagebox.showinfo("Success", "Record deleted successfully!")
                    window.destroy()
                else:
                    messagebox.showerror("Error", "Record not found!")
        
        tk.Button(window, text="Delete", command=delete).pack(pady=5)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StudentManagementSystem()
    app.run()
