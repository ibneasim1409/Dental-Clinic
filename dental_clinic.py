### dental_clinic_app.py

from database_handler import DatabaseHandler
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from fpdf import FPDF
import os


class DentalClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dental Clinic Management")
        self.root.geometry("1200x800")

        # Initialize Database Handler
        self.db_handler = DatabaseHandler()

        # Center Elements Frame
        self.center_frame = tk.Frame(root)
        self.center_frame.pack(expand=True)

        # UI Elements
        tk.Label(self.center_frame, text="Contact:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.contact_entry = tk.Entry(self.center_frame, width=30)
        self.contact_entry.grid(row=0, column=1, pady=5)
        self.contact_entry.bind("<FocusOut>", self.load_patient_data)

        tk.Label(self.center_frame, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.name_entry = tk.Entry(self.center_frame, width=30)
        self.name_entry.grid(row=1, column=1, pady=5)

        tk.Label(self.center_frame, text="Age:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.age_entry = tk.Entry(self.center_frame, width=30)
        self.age_entry.grid(row=2, column=1, pady=5)

        tk.Label(self.center_frame, text="Address:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.address_entry = tk.Entry(self.center_frame, width=30)
        self.address_entry.grid(row=3, column=1, pady=5)

        tk.Label(self.center_frame, text="Date of Visit:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.date_picker = ttk.Combobox(self.center_frame, values=self.get_date_options(), width=27)
        self.date_picker.grid(row=4, column=1, pady=5)
        self.date_picker.set(self.get_date_options()[0])

        tk.Label(self.center_frame, text="Invoice Amount:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.invoice_entry = tk.Entry(self.center_frame, width=30)
        self.invoice_entry.grid(row=5, column=1, pady=5)

        tk.Button(self.center_frame, text="Save Visit", command=self.save_visit, bg="green", fg="white").grid(row=6, column=0, columnspan=2, pady=10)

        # Scrollable Patients Table
        patients_frame = tk.Frame(self.center_frame)
        patients_frame.grid(row=8, column=0, columnspan=2, pady=5)

        patients_scroll_y = tk.Scrollbar(patients_frame, orient=tk.VERTICAL)
        patients_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        patients_scroll_x = tk.Scrollbar(patients_frame, orient=tk.HORIZONTAL)
        patients_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.patients_table = ttk.Treeview(
            patients_frame,
            columns=("ID", "Name", "Contact", "Age", "Address"),
            show="headings",
            height=10,
            yscrollcommand=patients_scroll_y.set,
            xscrollcommand=patients_scroll_x.set,
        )
        self.patients_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        patients_scroll_y.config(command=self.patients_table.yview)
        patients_scroll_x.config(command=self.patients_table.xview)

        # Define Patients Table Columns
        self.patients_table.heading("ID", text="ID")
        self.patients_table.heading("Name", text="Name")
        self.patients_table.heading("Contact", text="Contact")
        self.patients_table.heading("Age", text="Age")
        self.patients_table.heading("Address", text="Address")

        self.patients_table.column("ID", width=50, anchor="center")
        self.patients_table.column("Name", width=150, anchor="center")
        self.patients_table.column("Contact", width=150, anchor="center")
        self.patients_table.column("Age", width=50, anchor="center")
        self.patients_table.column("Address", width=200, anchor="center")
        self.patients_table.bind("<<TreeviewSelect>>", self.load_visits_for_selected_patient)

        # Scrollable Visits Table
        visits_frame = tk.Frame(self.center_frame)
        visits_frame.grid(row=10, column=0, columnspan=2, pady=5)

        visits_scroll_y = tk.Scrollbar(visits_frame, orient=tk.VERTICAL)
        visits_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.visits_table = ttk.Treeview(
            visits_frame,
            columns=("ID", "Visit Number", "Date", "Invoice"),
            show="headings",
            height=10,
            yscrollcommand=visits_scroll_y.set,
        )
        self.visits_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        visits_scroll_y.config(command=self.visits_table.yview)

        # Define Visits Table Columns
        self.visits_table.heading("ID", text="Visit ID")
        self.visits_table.heading("Visit Number", text="Visit Number")
        self.visits_table.heading("Date", text="Date of Visit")
        self.visits_table.heading("Invoice", text="Invoice Amount")

        self.visits_table.column("ID", width=50, anchor="center")
        self.visits_table.column("Visit Number", width=100, anchor="center")
        self.visits_table.column("Date", width=150, anchor="center")
        self.visits_table.column("Invoice", width=150, anchor="center")
        self.visits_table.bind("<<TreeviewSelect>>", self.show_print_button)

        # Print Button
        self.print_button = tk.Button(self.center_frame, text="Print Invoice", command=self.print_invoice, bg="blue", fg="white")
        self.print_button.grid(row=11, column=0, columnspan=2, pady=10)
        self.print_button.grid_remove()  # Hide the button initially

        # Load Patients
        self.load_patients()

    def get_date_options(self):
        return [(datetime.now().date() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    def load_patient_data(self, event):
        contact = self.contact_entry.get()
        if contact:
            patient = self.db_handler.get_patient_by_contact(contact)
            if patient:
                # Populate patient data
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, patient[1])

                self.age_entry.delete(0, tk.END)
                self.age_entry.insert(0, patient[2])

                self.address_entry.delete(0, tk.END)
                self.address_entry.insert(0, patient[3])
            else:
                # Clear fields if no patient found
                self.name_entry.delete(0, tk.END)
                self.age_entry.delete(0, tk.END)
                self.address_entry.delete(0, tk.END)

    def save_visit(self):
        contact = self.contact_entry.get()
        name = self.name_entry.get()
        age = self.age_entry.get()
        address = self.address_entry.get()
        date_of_visit = self.date_picker.get()
        invoice = self.invoice_entry.get()

        if not contact or not name or not date_of_visit or not invoice:
            messagebox.showerror("Validation Error", "All fields are required!")
            return

        try:
            invoice = float(invoice)
        except ValueError:
            messagebox.showerror("Validation Error", "Invoice Amount must be a number!")
            return

        patient_id = self.db_handler.save_or_get_patient(contact, name, age, address)

        # Generate visit number for the visit
        visit_number = self.db_handler.get_next_visit_number(patient_id)

        # Save visit record
        self.db_handler.save_visit(patient_id, visit_number, date_of_visit, invoice)

        messagebox.showinfo("Success", f"Visit saved for patient {name} (ID: {patient_id}, Visit: {visit_number})")
        self.clear_fields()
        self.load_patients()  # Refresh patients list

    def load_patients(self):
        # Clear existing records
        for row in self.patients_table.get_children():
            self.patients_table.delete(row)

        # Fetch patients from database
        patients = self.db_handler.get_all_patients()

        for patient in patients:
            self.patients_table.insert("", tk.END, values=patient)

    def load_visits_for_selected_patient(self, event):
        selected_item = self.patients_table.selection()
        if not selected_item:
            return

        patient_id = self.patients_table.item(selected_item)["values"][0]

        # Clear existing visits
        for row in self.visits_table.get_children():
            self.visits_table.delete(row)

        # Fetch visits for the selected patient
        visits = self.db_handler.get_visits_by_patient_id(patient_id)

        for visit in visits:
            self.visits_table.insert("", tk.END, values=visit)

    def show_print_button(self, event):
        selected_item = self.visits_table.selection()
        if selected_item:
            self.print_button.grid()
        else:
            self.print_button.grid_remove()
    def print_invoice(self):
        selected_item = self.visits_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "No visit selected!")
            return

        visit = self.visits_table.item(selected_item)["values"]
        visit_id, visit_number, date_of_visit, invoice = visit

        patient_id = self.db_handler.get_patient_id_by_visit_id(visit_id)
        patient = self.db_handler.get_patient_by_id(patient_id)

        pdf = FPDF()
        pdf.add_page()

        # Add each copy (Patient, Hospital, Doctor)
        for idx, header in enumerate(["Patient Copy", "Hospital Copy", "Doctor Copy"]):
            if idx > 0:
                pdf.line(10, 95 * idx, 200, 95 * idx)  # Add separating line

            y_offset = 10 + (95 * idx)  # Adjust Y-offset for each copy

            # Add Logo
            pdf.set_fill_color(255, 255, 255)  # Ensure a white background behind the logo
            pdf.rect(10, y_offset, 190, 25, style="F")  # Draw a rectangle for the logo area
            pdf.image("header_logo.png", x=10, y=y_offset + 2, w=30, h=20)  # Adjust the logo size and position

            # Add Header Text
            pdf.set_xy(50, y_offset + 5)  # Adjust header text position
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 8, header, ln=True, align="L")

            # Add Patient and Visit Details
            pdf.set_font("Arial", size=10)
            pdf.set_xy(10, y_offset + 30)  # Adjust details position below the logo
            pdf.cell(0, 6, f"Patient ID: {patient[0]}", ln=True)
            pdf.cell(0, 6, f"Patient Name: {patient[1]}", ln=True)
            pdf.cell(0, 6, f"Age: {patient[2]}", ln=True)
            pdf.cell(0, 6, f"Address: {patient[3]}", ln=True)
            pdf.cell(0, 6, f"Visit Number: {visit_number}", ln=True)
            pdf.cell(0, 6, f"Date of Visit: {date_of_visit}", ln=True)
            pdf.cell(0, 6, f"Invoice Amount: ${invoice}", ln=True)

        pdf_file = f"invoice_patient_{patient_id}_visit_{visit_number}.pdf"
        pdf.output(pdf_file)

        # Open the PDF
        if os.name == "posix":
            os.system(f"xdg-open {pdf_file}")
        elif os.name == "nt":
            os.startfile(pdf_file)

        messagebox.showinfo("Success", f"Invoice saved to {pdf_file} and opened for printing!")

    def clear_fields(self):
        self.contact_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.invoice_entry.delete(0, tk.END)
        self.date_picker.set(self.get_date_options()[0])


if __name__ == "__main__":
    root = tk.Tk()
    app = DentalClinicApp(root)
    root.mainloop()