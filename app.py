import streamlit as st
import sqlite3
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database_setup import setup


setup()
# Email Configuration
EMAIL_ADDRESS = "teast@mail.com"
EMAIL_PASSWORD = "user@123"

# Function to Connect to Database
def connect_db():
    return sqlite3.connect("school.db")

# Function to Add New Student Admission
def add_student(name, age, class_, guardian, contact, email, sec_guardian, sec_contact, sec_email, address, admission_date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO admissions 
        (student_name, age, class, guardian_name, contact, email, secondary_guardian_name, secondary_contact, secondary_email, address, admission_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, age, class_, guardian, contact, email, sec_guardian, sec_contact, sec_email, address, admission_date))
    conn.commit()
    conn.close()


def add_fee(student_id, total_fees, due_date):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO fees (student_id, total_fees, due_date) VALUES (?, ?, ?)",
                   (student_id, total_fees, due_date))
    conn.commit()
    conn.close()


def add_installment_payment(fee_id, installment_amount, payment_date, method):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO installments (fee_id, installment_amount, payment_date, payment_method) VALUES (?, ?, ?, ?)",
                   (fee_id, installment_amount, payment_date, method))

    # Update total amount paid in the fees table
    cursor.execute("UPDATE fees SET amount_paid = amount_paid + ? WHERE id = ?", (installment_amount, fee_id))

    conn.commit()
    conn.close()


# Function to Fetch Students
def fetch_students():
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM admissions", conn)
    conn.close()
    return df

# Function to Fetch Fees
def fetch_fees():
    conn = connect_db()
    df = pd.read_sql_query("SELECT f.id, a.student_name, a.email, f.total_fees, f.amount_paid, f.due_date FROM fees f JOIN admissions a ON f.student_id = a.id", conn)
    conn.close()
    return df

# Function to Record Fee Payment
def update_fee_payment(fee_id, amount_paid, payment_date, method):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE fees SET amount_paid = ?, payment_date = ?, payment_method = ? WHERE id = ?", 
                   (amount_paid, payment_date, method, fee_id))
    conn.commit()
    conn.close()

# Function to Send Fee Reminder Email
def send_email(to_email, student_name, due_amount, due_date):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = f"Fee Payment Reminder for {student_name}"

        body = f"""
        Dear {student_name}'s Parent/Guardian,

        This is a reminder that a fee payment of ₹{due_amount} is due on {due_date}. 
        Kindly make the payment to avoid late fees.

        Regards,
        School Administration
        """

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return f"Reminder sent to {to_email}"
    except Exception as e:
        return f"Failed to send email: {e}"

# Streamlit UI
st.set_page_config(page_title="T.R.Agarwal",
                page_icon=None, 
                layout="wide",
                initial_sidebar_state="auto",
                menu_items=None)
_, col = st.columns([0.2, 0.8])
with col:
    st.title("Admission & Fee Management System")
    st.subheader("")

tab1, tab2, tab3 = st.tabs(["Admission Form", "Fee Collection", "Send Reminders"])

# Admission Form
with tab1:
    st.header("New Student Admission Form")
    name = st.text_input("**Student Name**")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("**Age**", min_value=3, max_value=18)
    with col2:
        class_ = st.selectbox("**Class**", ["Nursery", "LKG", "UKG"] + [str(i) for i in range(1, 12)])

    # Primary Guardian Details
    col1, col2, col3 = st.columns([0.5, 0.2, 0.3])
    with col1:
        guardian = st.text_input("Primary Guardian Name")
    with col2:
        contact = st.text_input("Primary Contact Number")
    with col3:
        email = st.text_input("Primary Email")

    if st.checkbox("Add Another Guardian"):
        # Secondary Guardian Details
        col1, col2, col3 = st.columns([0.5, 0.2, 0.3])
        with col1:
            sec_guardian = st.text_input("Secondary Guardian Name (Optional)")
        with col2:
            sec_contact = st.text_input("Secondary Contact Number (Optional)")
        with col3:
            sec_email = st.text_input("Secondary Email (Optional)")

    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        address = st.text_area("Address")
    with col2:
        admission_date = st.date_input("Admission Date")
    
    # Fee Details
    st.subheader("Fees: Rs. 50000")
    col1, col2 = st.columns(2)
    with col1:
        selected = st.selectbox("Fees Type", ["Complete Payment", "Installment"])
    if selected == "Installment":
        with col2:
            installment_count = st.number_input("Number of Installments", min_value=1, max_value=5, value=1, step=1, key='installment_count')
            
        columns = st.columns(installment_count)
        for i, col in enumerate(columns):
            with col:
                st.date_input(label=f"{i+1} Installment Date", value="today", format="YYYY/MM/DD")
                st.number_input(f"{i+1} Installments Amount", min_value=500, max_value=50000, value=25000, step=1000, key=f'installment_amount_{i}')
                
            
    if st.button("Submit Admission"):
        add_student(name, age, class_, guardian, contact, email, sec_guardian, sec_contact, sec_email, address, admission_date)
        st.success("Admission Recorded Successfully!")


# Fee Collection
with tab2:
    st.header("Fee Collection Tracking")
    students = fetch_students()
    fees = fetch_fees()

    st.dataframe(fees)

    student_id = st.selectbox("Select Student", students['id'].astype(str) + " - " + students['student_name'])
    total_fees = st.number_input("Total Fee Amount", min_value=0)
    due_date = st.date_input("Final Due Date")

    if st.button("Add Fee Record"):
        add_fee(student_id.split(" - ")[0], total_fees, due_date)
        st.success("Fee Record Added Successfully!")

    # Installment Payments
    st.subheader("Installment Payments")
    fee_id = st.selectbox("Select Fee Record for Installment", fees['id'].astype(str))
    installment_amount = st.number_input("Installment Amount", min_value=0)
    payment_date = st.date_input("Payment Date")
    method = st.selectbox("Payment Method", ["Cash", "UPI", "Card", "Bank Transfer"])

    if st.button("Add Installment Payment"):
        add_installment_payment(fee_id, installment_amount, payment_date, method)
        st.success("Installment Recorded Successfully!")

    

# Fee Reminders
with tab3:
    st.header("Send Fee Reminders")
    due_fees = fees[fees['total_fees'] > fees['amount_paid'].fillna(0)]
    st.dataframe(due_fees)

    if st.button("Send Reminders"):
        for _, row in due_fees.iterrows():
            response = send_email(row['email'], row['student_name'], row['total_fees'] - row['amount_paid'], row['due_date'])
            st.success(response)

