import os
import streamlit as st
import pandas as pd

# Function to load users from CSV file
def load_users():
    if os.path.exists("users.csv"):
        df = pd.read_csv("users.csv")
        return df.to_dict(orient="list")
    return {"email": [], "password": []}

# Function to save users to CSV file
def save_users():
    df = pd.DataFrame(users_data)
    df.to_csv("users.csv", index=False)

# Initialize user data
users_data = load_users()

# Function to register new users
def register(email, password):
    if email in users_data["email"]:
        return False  # Email already exists
    users_data["email"].append(email)
    users_data["password"].append(password)
    save_users()
    return True

# Function to login users
def login(email, password):
    if email in users_data["email"]:
        index = users_data["email"].index(email)
        if str(users_data["password"][index]) == str(password):
            st.session_state.logged_in = True
            st.session_state.email = email
            return True
    return False

# Function to load doctors from CSV
def load_doctors():
    if os.path.exists("doctors.csv"):
        return pd.read_csv("doctors.csv")
    return pd.DataFrame(columns=["Name", "Specialty", "Rating"])

# Function to save doctors to CSV
def save_doctors(doctors_df):
    doctors_df.to_csv("doctors.csv", index=False)

# Load doctors data
doctors = load_doctors()

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.selected_doctor = None
    st.session_state.page = "Home"
    st.session_state.selected_specialty = None

# Login and Registration Page
def show_login():
    st.title("🔑 Login")
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(email, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
    
    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register(new_email, new_password):
                st.success("Account created successfully! You can now log in.")
            else:
                st.error("Email already exists!")

# Home Page
def home():
    st.title("🏥 Medical Appointment Booking")
    
    # Search bar for filtering doctors by name or specialty
    search_query = st.text_input("🔍 Search for a specialty or doctor")

    # List of medical specialties
    specializations = ["Dentistry", "Surgery", "Physiotherapy", "Internal Medicine"]
    st.subheader("Medical Specialties")
    
    # Display specialty buttons
    cols = st.columns(len(specializations))
    for i, spec in enumerate(specializations):
        with cols[i]:
            if st.button(spec):
                st.session_state.selected_specialty = spec
                st.success(f"Showing doctors specialized in {spec}")

    # Section for adding a new doctor
    st.subheader("➕ Add a New Doctor")

    # Input fields for doctor details
    new_doctor_name = st.text_input("Doctor's Name")
    new_doctor_specialty = st.selectbox("Specialty", specializations)
    new_doctor_rating = st.slider("Rating", 1.0, 5.0, 4.5, 0.1)

    if st.button("Add Doctor"):
        global doctors  
        
        # Create a new DataFrame with the doctor's details
        new_entry = pd.DataFrame([{
            "Name": new_doctor_name, 
            "Specialty": new_doctor_specialty, 
            "Rating": f"⭐ {new_doctor_rating}"
        }])

        # Append the new doctor to the existing doctors list
        doctors = pd.concat([doctors, new_entry], ignore_index=True)

        # Save the updated doctor list to the CSV file
        save_doctors(doctors)

        # Display success message and refresh the page
        st.success(f"Doctor {new_doctor_name} added successfully!")
        st.rerun()

    st.subheader("👨‍⚕️ Available Doctors")

    # Filter doctors based on selected specialty
    filtered_doctors = doctors
    if st.session_state.selected_specialty:
        filtered_doctors = doctors[doctors["Specialty"] == st.session_state.selected_specialty]

    # Display doctors based on search query and selected specialty
    for _, row in filtered_doctors.iterrows():
        if search_query.lower() in row['Specialty'].lower() or search_query.lower() in row['Name'].lower():
            with st.container():
                st.write(f"**{row['Name']}** ({row['Specialty']}) - {row['Rating']}")
                if st.button(f"Book with {row['Name']}"):
                    st.session_state.selected_doctor = row['Name']
                    st.session_state.page = "Book Appointment"
                    st.rerun()

    # Button to reset filters and return to home page
    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.session_state.selected_specialty = None
        st.rerun()
# Booking Page
def booking():
    st.title("📅 Book an Appointment")
    
    if not st.session_state.selected_doctor:
        st.warning("Please select a doctor first from the home page.")
        if st.button("🏠 Back to Home"):
            st.session_state.page = "Home"
            st.rerun()
        return
    
    doctor = st.session_state.selected_doctor
    st.subheader(f"Book an appointment with **{doctor}**")
    date = st.date_input("📆 Select Date")
    time = st.time_input("⏰ Select Time")

    if st.button("Confirm Booking"):
        st.success("✅ Appointment booked successfully!")

    if st.button("🏠 Back to Home"):
        st.session_state.page = "Home"
        st.rerun()

# Navigation between pages
if not st.session_state.logged_in:
    show_login()
else:
    if st.session_state.page == "Home":
        home()
    elif st.session_state.page == "Book Appointment":
        booking()