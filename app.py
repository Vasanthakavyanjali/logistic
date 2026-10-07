import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="MediCare Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 MediCare Hospital Management System")

st.write(
    """
    Welcome to the MediCare Hospital Management System.

    Use the sidebar to manage:

    - Patients
    - Doctors
    - Appointments
    - Billing
    """
)

PATIENT_FILE = "data/patients.csv"
DOCTOR_FILE = "data/doctors.csv"
APPOINTMENT_FILE = "data/appointments.csv"
BILL_FILE = "data/bills.csv"


def count_records(file_path):

    if os.path.exists(file_path):

        df = pd.read_csv(file_path)

        return len(df)

    return 0


patients_count = count_records(PATIENT_FILE)
doctors_count = count_records(DOCTOR_FILE)
appointments_count = count_records(APPOINTMENT_FILE)
bills_count = count_records(BILL_FILE)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Patients", patients_count)

with col2:
    st.metric("Doctors", doctors_count)

with col3:
    st.metric("Appointments", appointments_count)

with col4:
    st.metric("Bills", bills_count)