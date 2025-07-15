import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime
from db_utils import get_mongo_client, get_collection, add_entry, load_data, get_recent_entries_for_context
from llm_utils import query_llm_agent_openrouter
from streamlit_free_text_select import st_free_text_select


st.set_page_config(page_title="Work Time Tracker", layout="wide", page_icon="🕒")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🕒 Work Time Tracker")
    st.markdown("**Track your work, analyze productivity, and get AI-powered insights!**")
    st.markdown("---")
    st.info("💡 Tip: Use the AI Assistant below to ask about your productivity or work trends.")
    st.markdown("---")
    st.write("Made with ❤️ using Streamlit and MongoDB Atlas.")

    # --- LLM AGENT SECTION (RAG) ---
    st.subheader("🤖 AI Assistant (LLM Agent with Data Context)")
    st.markdown("Ask the AI about your work data, productivity, or anything! (RAG)")
    user_question_rag = st.text_area("Type your question for the AI agent:", "What can I do to be more productive?", key="llm_rag_text_area_sidebar")
    if st.button("Ask AI", key="llm_rag_button_sidebar"):
        with st.spinner("AI is thinking..."):
            answer = query_llm_agent_rag(user_question_rag)
        st.markdown(f"**AI Answer:**\n{answer}")
        st.markdown(f"**AI Answer:**\n{answer}")

# --- INIT DB CONNECTION ---
client = get_mongo_client()
if client is None:
    st.stop()
else:
    st.toast("Connected to MongoDB Atlas!", icon="✅")
collection = get_collection(client)

st.markdown("<h1 style='text-align: center; color: #FF6B6B;'>🕒 Work Time Tracker</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #FF6B6B'>", unsafe_allow_html=True)

with st.form("add_entry"):
    st.markdown("<h3 style='color: #262730;'>➕ Add New Work Entry</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #F0F2F6'>", unsafe_allow_html=True)

    # New layout: task description (wide) and person (narrow) on one row, below: task type, productivity, minutes, date
    col_task, col_person = st.columns([3,1])
    task = col_task.text_input("📝 Task Description", placeholder="Describe task or add new task")
    person_options = ["John", "Anna", "Tom", "Eva"]
    person = col_person_free = st_free_text_select(
        label="👤 Person",
        options=person_options,
        index=None,
        format_func=None,
        placeholder="Type or select a name",
        disabled=False,
        delay=300,
        key="person_free_text_select",
        label_visibility="visible"
    )
    if person:
        person = person.strip()

    col_type, col_prod, col_time, col_date = st.columns(4)
    task_type_options = ["Analysis", "Coding", "Meeting", "Email"]
    task_type_select = col_type.selectbox("📂 Task Type", task_type_options + ["Add new..."])
    task_type_input = ""
    if task_type_select == "Add new...":
        task_type_input = col_type.text_input("Enter new task type:", placeholder="Enter task type")
        task_type = task_type_input.strip()
    else:
        task_type = task_type_select
    productivity = col_prod.selectbox("🌟 Productivity", ["productive", "unproductive"], index=0)
    time = col_time.number_input("⏱️ Time (minutes)", min_value=1, max_value=480, value=30)
    date = col_date.date_input("📅 Date", value=datetime.today())

    submitted = st.form_submit_button("💾 Save Entry")
    if submitted:
        # Data validation
        if not task.strip():
            st.error("❌ Please provide task description!")
        elif not person:
            st.error("❌ Please provide person name!")
        elif not task_type:
            st.error("❌ Please provide task type!")
        else:
            success = add_entry(collection, person, task, task_type, time, productivity, datetime.combine(date, datetime.min.time()))
            if success:
                st.markdown("<span style='color: #FF6B6B;'>✅ Entry saved!</span>", unsafe_allow_html=True)
                st.cache_data.clear()  # Clear cache after adding new entry

st.markdown("<h3 style='color: #262730;'>📋 Registered Entries</h3>", unsafe_allow_html=True)
st.markdown("<hr style='border:1px solid #F0F2F6'>", unsafe_allow_html=True)
data = load_data(collection)

if not data.empty:
    # Date conversion with error handling
    try:
        if "date" in data.columns:
            # Convert to datetime, coerce errors to NaT
            data["date"] = pd.to_datetime(data["date"], errors="coerce")
            data["date_str"] = data["date"].dt.strftime("%Y-%m-%d")
        else:
            st.warning("No 'date' column found in data.")
    except Exception:
        st.error("Error in date conversion. Check data format in database.")
        st.stop()

    with st.expander("� Filter Entries"):
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
        st.dataframe(data[display_columns], use_container_width=True)
    else:
        st.warning("No appropriate columns to display.")

    # --- CHARTS ---
    st.markdown("<h3 style='color: #262730;'>📊 Summary & Charts</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #F0F2F6'>", unsafe_allow_html=True)
    
    if len(data) > 0:
        col1, col2 = st.columns(2)

        # Productivity chart 
        productivity_col = "productivity" if "productivity" in data.columns else "produktywnosc"
        time_col = "time" if "time" in data.columns else "czas"
        if productivity_col in data.columns and time_col in data.columns:
            productivity_sum = data.groupby(productivity_col)[time_col].sum().reset_index()
            if not productivity_sum.empty:
                fig1 = px.pie(productivity_sum, names=productivity_col, values=time_col, title="🌟 Productivity (time)", color_discrete_sequence=["#FF6B6B", "#F0F2F6"])
                col1.plotly_chart(fig1, use_container_width=True)
        # Time by days chart
        if "date_str" in data.columns and time_col in data.columns:
            time_by_day = data.groupby(["date_str"])[time_col].sum().reset_index()
            if not time_by_day.empty:
                fig2 = px.bar(time_by_day, x="date_str", y=time_col, title="📅 Work time by day", color_discrete_sequence=["#FF6B6B"])
                col2.plotly_chart(fig2, use_container_width=True)
        # Time by task type chart
        task_type_col = "task_type" if "task_type" in data.columns else "typ_zadania"
        if task_type_col in data.columns and time_col in data.columns:
            st.markdown("<h4 style='color: #262730;'>🔍 Time by Task Type</h4>", unsafe_allow_html=True)
            time_by_type = data.groupby(task_type_col)[time_col].sum().reset_index()
            if not time_by_type.empty:
                fig3 = px.bar(time_by_type, x=task_type_col, y=time_col, title="Time by task type", color_discrete_sequence=["#FF6B6B"])
                st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data after filtering.")
else:
    st.info("No data to display. Add your first entry above.")


# --- LLM AGENT SECTION (RAG) ---
def query_llm_agent_rag(user_question):
    """Query LLM agent with RAG: include recent MongoDB data as context."""
    context = get_recent_entries_for_context(collection, 10)
    prompt = f"You are an assistant for work time tracking. Here is recent data from the database:\n{context}\n\nUser question: {user_question}\n\nAnswer based on the data and your own knowledge."
    return query_llm_agent_openrouter(prompt)
