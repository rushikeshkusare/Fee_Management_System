import sqlite3

def setup():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    # Create Admissions Table (if not exists)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            age INTEGER,
            class TEXT,
            guardian_name TEXT,
            contact TEXT,
            email TEXT,
            address TEXT,
            admission_date TEXT
        )
    ''')

    # Add missing columns if they do not exist
    try:
        cursor.execute("ALTER TABLE admissions ADD COLUMN secondary_guardian_name TEXT")
        cursor.execute("ALTER TABLE admissions ADD COLUMN secondary_contact TEXT")
        cursor.execute("ALTER TABLE admissions ADD COLUMN secondary_email TEXT")
    except sqlite3.OperationalError:
        pass  # Columns already exist

    # Create or modify Fees Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            total_fees REAL,
            payment_type REAL,
            number_of_installments INTEGER,
            amount_paid REAL DEFAULT 0,
            due_date TEXT,
            FOREIGN KEY(student_id) REFERENCES admissions(id)
        )
    ''')

    # Create Installments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS installments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fee_id INTEGER,
            installment_amount REAL,
            payment_date TEXT,
            payment_method TEXT,
            FOREIGN KEY(fee_id) REFERENCES fees(id)
        )
    ''')

    conn.commit()
    conn.close()

    print("Database setup complete.")
