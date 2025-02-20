import streamlit as st
import pandas as pd
import random
from datetime import datetime

# Sample data for students and fees
def generate_sample_data():
    students = ["John Doe", "Jane Smith", "Robert Brown", "Emily Davis", "Michael Johnson"]
    data = {
        "Student ID": [f"S{1000+i}" for i in range(len(students))],
        "Student Name": students,
        "Total Fees": [50000, 45000, 48000, 52000, 47000],
        "Paid Fees": [random.randint(20000, 40000) for _ in students],
    }
    df = pd.DataFrame(data)
    df["Due Fees"] = df["Total Fees"] - df["Paid Fees"]
    return df

st.set_page_config(page_title="School Fee Management System", layout="wide")

st.title("🏫 School Fee Management System")

# Sidebar: Fee Setup
st.sidebar.header("Customizable Fee Setup")
def set_fee_structure():
    st.sidebar.subheader("Set Fees for Different Classes")
    classes = ["Nursery", "LKG", "UKG", "Class 1", "Class 2"]
    fee_structure = {cls: st.sidebar.number_input(f"Fees for {cls}", min_value=1000, value=30000, step=1000) for cls in classes}
    return fee_structure

fee_structure = set_fee_structure()

# Main Dashboard Section
df_students = generate_sample_data()
st.dataframe(df_students)

# Individual Fee Check-Up
st.subheader("🔍 Check Individual Fee Details")
selected_student = st.selectbox("Select Student", df_students["Student Name"].tolist())
student_info = df_students[df_students["Student Name"] == selected_student]
st.write(student_info)

# Online Fee Collection
st.subheader("💳 Online Fee Collection")
payment_student = st.selectbox("Select Student for Payment", df_students["Student Name"].tolist())
payment_amount = st.number_input("Enter Payment Amount", min_value=500, step=500)
if st.button("Process Payment"):
    st.success(f"Payment of ₹{payment_amount} received for {payment_student}")
    # Here you can add database update logic

# Receipt Generation
st.subheader("🧾 Generate Fee Receipt")
receipt_student = st.selectbox("Select Student for Receipt", df_students["Student Name"].tolist())
if st.button("Generate Receipt"):
    receipt_id = random.randint(100000, 999999)
    date = datetime.now().strftime("%d-%m-%Y")
    st.write(f"**Receipt ID:** {receipt_id}")
    st.write(f"**Student:** {receipt_student}")
    st.write(f"**Date:** {date}")
    st.write("✅ Payment Recorded Successfully!")

# Dashboard Analysis
st.subheader("📊 Dashboard Analysis")
col1, col2, col3 = st.columns(3)
col1.metric("Total Students", len(df_students))
col2.metric("Total Fees Collected", f"₹{df_students['Paid Fees'].sum()}")
col3.metric("Total Pending Fees", f"₹{df_students['Due Fees'].sum()}")

# Automated Notifications
st.subheader("📢 Automated Notifications")
if st.button("Send Due Payment Reminders"):
    st.success("Due payment reminders sent successfully!")

# User Access Control (Basic Role Management)
st.sidebar.header("User Access Control")
user_role = st.sidebar.selectbox("Select Role", ["Admin", "Accountant", "Parent"])
if user_role == "Admin":
    st.sidebar.write("You have full access.")
elif user_role == "Accountant":
    st.sidebar.write("You can manage fee collection and reports.")
elif user_role == "Parent":
    st.sidebar.write("You can check and pay fees.")
