import streamlit as st
import pandas as pd
import plotly.express as px
import toml
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime


st.set_page_config(page_title="Work Time Tracker", layout="wide")

@st.cache_resource
def init_connection():
    try:
        # Try to use secrets, if not available, use direct connection
        if "mongo_uri" in st.secrets:
            uri = st.secrets["mongo_uri"]
            
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Test connection
        client.admin.command('ping')
        st.success("✅ Connected to MongoDB Atlas!")
        return client
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

client = init_connection()
if client is None:
    st.stop()

db = client["work-time-tracker"]  # Database name
collection = db["work-time"]

# --- FUNCTIONS ---
def add_entry(person, task, task_type, time, productivity, date):
    try:
        entry = {
            "person": person,
            "task": task,
            "task_type": task_type,
            "time": time,
            "productivity": productivity,
            "date": date
        }
        collection.insert_one(entry)
        return True
    except Exception as e:
        st.error(f"Error while saving: {e}")
        return False

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    try:
        data = list(collection.find({}, {"_id": 0}))  # Exclude _id from results
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error while loading data: {e}")
        return pd.DataFrame()

# --- MAIN PAGE ---
st.title("🕒 Work Time Tracker")

with st.form("add_entry"):
    st.subheader("Add Entry")
    col1, col2, col3 = st.columns(3)

    person = col1.selectbox("Person", ["John", "Anna", "Tom", "Eva", "Other..."])
    if person == "Other...":
        person = col1.text_input("Enter name:", placeholder="Enter name")
    
    task = col1.text_input("Task", placeholder="Describe task")
    task_type = col2.selectbox("Task Type", ["Analysis", "Coding", "Meeting", "Email", "Other"])
    time = col2.number_input("Time (minutes)", min_value=1, max_value=480, value=30)
    productivity = col3.radio("Productivity", ["productive", "unproductive"])
    date = col3.date_input("Date", value=datetime.today())

    submitted = st.form_submit_button("Save")
    if submitted:
        # Data validation
        if not task.strip():
            st.error("❌ Please provide task name!")
        elif person == "Other..." or not person.strip():
            st.error("❌ Please provide person name!")
        else:
            success = add_entry(person, task, task_type, time, productivity, datetime.combine(date, datetime.min.time()))
            if success:
                st.success("✅ Entry saved!")
                st.cache_data.clear()  # Clear cache after adding new entry

# --- SHOW DATA ---
st.subheader("📋 Registered Entries")
data = load_data()

if not data.empty:
    # Date conversion with error handling
    try:
        if "data" in data.columns:
            data["date"] = pd.to_datetime(data["data"])
            data["date_str"] = data["date"].dt.strftime("%Y-%m-%d")
        elif "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"])
            data["date_str"] = data["date"].dt.strftime("%Y-%m-%d")
    except:
        st.error("Error in date conversion. Check data format in database.")
        st.stop()

    with st.expander("📁 Filtering"):
        col1, col2 = st.columns(2)
        
        # Filtering with safe default values - handle both Polish and English column names
        person_col = "person" if "person" in data.columns else "osoba"
        productivity_col = "productivity" if "productivity" in data.columns else "produktywnosc"
        
        person_options = data[person_col].unique().tolist() if person_col in data.columns else []
        productivity_options = data[productivity_col].unique().tolist() if productivity_col in data.columns else []
        
        person_filter = col1.multiselect("Filter by person", options=person_options)
        productivity_filter = col2.multiselect("Productivity", options=productivity_options)

        if person_filter:
            data = data[data[person_col].isin(person_filter)]
        if productivity_filter:
            data = data[data[productivity_col].isin(productivity_filter)]

    # Display data with handling of missing columns - support both languages
    display_columns = []
    column_mappings = {
        "person": "osoba",
        "task": "zadanie", 
        "task_type": "typ_zadania",
        "time": "czas",
        "productivity": "produktywnosc"
    }
    
    for eng_col, pol_col in column_mappings.items():
        if eng_col in data.columns:
            display_columns.append(eng_col)
        elif pol_col in data.columns:
            display_columns.append(pol_col)
    
    if "date_str" in data.columns:
        display_columns.append("date_str")
    
    if display_columns:
        st.dataframe(data[display_columns])
    else:
        st.warning("No appropriate columns to display.")

    # --- CHARTS ---
    st.subheader("📊 Summary")
    
    if len(data) > 0:
        col1, col2 = st.columns(2)

        # Productivity chart - handle both column names
        productivity_col = "productivity" if "productivity" in data.columns else "produktywnosc"
        time_col = "time" if "time" in data.columns else "czas"
        
        if productivity_col in data.columns and time_col in data.columns:
            productivity_sum = data.groupby(productivity_col)[time_col].sum().reset_index()
            if not productivity_sum.empty:
                fig1 = px.pie(productivity_sum, names=productivity_col, values=time_col, title="Productivity (time)")
                col1.plotly_chart(fig1, use_container_width=True)

        # Time by days chart
        if "date_str" in data.columns and time_col in data.columns:
            time_by_day = data.groupby(["date_str"])[time_col].sum().reset_index()
            if not time_by_day.empty:
                fig2 = px.bar(time_by_day, x="date_str", y=time_col, title="Work time by day")
                col2.plotly_chart(fig2, use_container_width=True)

        # Time by task type chart
        task_type_col = "task_type" if "task_type" in data.columns else "typ_zadania"
        if task_type_col in data.columns and time_col in data.columns:
            st.subheader("🔍 Time by task type")
            time_by_type = data.groupby(task_type_col)[time_col].sum().reset_index()
            if not time_by_type.empty:
                fig3 = px.bar(time_by_type, x=task_type_col, y=time_col, title="Time by task type")
                st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data after filtering.")
else:
    st.info("No data to display. Add your first entry above.")
