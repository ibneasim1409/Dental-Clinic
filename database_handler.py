### database_handler.py

import sqlite3


class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect("dental_clinic.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT UNIQUE NOT NULL,
                age INTEGER,
                address TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                visit_number INTEGER NOT NULL,
                date_of_visit TEXT NOT NULL,
                invoice REAL NOT NULL,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
        """)
        self.conn.commit()

    def get_patient_by_contact(self, contact):
        self.cursor.execute("SELECT id, name, age, address FROM patients WHERE contact=?", (contact,))
        return self.cursor.fetchone()

    def save_or_get_patient(self, contact, name, age, address):
        patient = self.get_patient_by_contact(contact)
        if not patient:
            self.cursor.execute("""
                INSERT INTO patients (name, contact, age, address) VALUES (?, ?, ?, ?)
            """, (name, contact, age, address))
            self.conn.commit()
            return self.cursor.lastrowid
        return patient[0]

    def get_next_visit_number(self, patient_id):
        self.cursor.execute("SELECT MAX(visit_number) FROM visits WHERE patient_id=?", (patient_id,))
        return (self.cursor.fetchone()[0] or 0) + 1

    def save_visit(self, patient_id, visit_number, date_of_visit, invoice):
        self.cursor.execute("""
            INSERT INTO visits (patient_id, visit_number, date_of_visit, invoice) VALUES (?, ?, ?, ?)
        """, (patient_id, visit_number, date_of_visit, invoice))
        self.conn.commit()

    def get_all_patients(self):
        self.cursor.execute("SELECT id, name, contact, age, address FROM patients")
        return self.cursor.fetchall()

    def get_visits_by_patient_id(self, patient_id):
        self.cursor.execute("SELECT id, visit_number, date_of_visit, invoice FROM visits WHERE patient_id=?", (patient_id,))
        return self.cursor.fetchall()

    def get_patient_id_by_visit_id(self, visit_id):
        self.cursor.execute("SELECT patient_id FROM visits WHERE id=?", (visit_id,))
        return self.cursor.fetchone()[0]

    def get_patient_by_id(self, patient_id):
        self.cursor.execute("SELECT id, name, age, address FROM patients WHERE id=?", (patient_id,))
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()