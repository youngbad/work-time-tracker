from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import streamlit as st
from typing import Optional

def get_mongo_client() -> Optional[MongoClient]:
    """Initialize and return a MongoDB client using Streamlit secrets."""
    try:
        if "mongo_uri" in st.secrets:
            uri = st.secrets["mongo_uri"]
            client = MongoClient(uri, server_api=ServerApi('1'))
            client.admin.command('ping')
            return client
        else:
            st.error("MongoDB URI not found in secrets.")
            return None
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def get_collection(client: MongoClient, db_name: str = "work-time-tracker", collection_name: str = "work-time"):
    return client[db_name][collection_name]

def add_entry(collection, person: str, task: str, task_type: str, time: int, productivity: str, date) -> bool:
    """Add a work entry to MongoDB."""
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

def load_data(collection) -> pd.DataFrame:
    """Load all work entries from MongoDB as a DataFrame."""
    try:
        data = list(collection.find({}, {"_id": 0}))
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error while loading data: {e}")
        return pd.DataFrame()

def get_recent_entries_for_context(collection, n: int = 10) -> str:
    """Fetch the latest n entries from MongoDB for LLM context."""
    try:
        df = load_data(collection)
        if df.empty:
            return "No work entries available."
        date_col = "date" if "date" in df.columns else ("data" if "data" in df.columns else None)
        if date_col:
            df = df.sort_values(date_col, ascending=False)
        cols = [c for c in ["person", "task", "task_type", "time", "productivity", "date"] if c in df.columns]
        context_df = df[cols].head(n)
        context_text = context_df.to_string(index=False)
        return f"Recent work entries:\n{context_text}"
    except Exception as e:
        return f"Error fetching context: {e}"
