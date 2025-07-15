import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse
import toml
import os

# MongoDB Atlas Configuration - matches main app
def init_connection():
    try:
        # Try to load from secrets.toml first
        secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
        
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r', encoding='utf-8') as f:
                secrets = toml.load(f)
                if 'mongo_uri' in secrets:
                    uri = secrets['mongo_uri']
                    print("✅ Using connection string from secrets.toml")
                else:
                    raise KeyError("mongo_uri not found in secrets.toml")
        else:
            # Fallback to environment variable or direct connection
            password = os.getenv('MONGO_PASSWORD')
            if not password:
                password = "Badylek.1997"  # Fallback password
                print("⚠️  Using fallback password - consider using secrets.toml")
            
            # URL encode the password to handle special characters
            encoded_password = urllib.parse.quote_plus(password)
            uri = f"mongodb+srv://jakubbadowskijb:{encoded_password}@cluster0.lyglqp9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        # Create client with ServerApi
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB Atlas!")
        return client
    except (ConnectionError, KeyError, FileNotFoundError) as e:
        print(f"❌ Database connection error: {e}")
        return None

def generate_test_data():T
    """Generate test data for the Work Time Tracker application"""
    
    # Initialize MongoDB connection
    mongo_client = init_connection()
    if mongo_client is None:
        return False

    # Use same database and collection as main app
    db = mongo_client["work-time-tracker"]
    collection = db["work-time"]

    # Sample data lists
    persons = ["John", "Anna", "Tom", "Eva", "Mike", "Sarah"]
    tasks = [
        "Login module development",
        "Client meeting",
        "Sales data analysis", 
        "Reporting feature implementation",
        "Mobile app testing",
        "Database optimization",
        "Code review",
        "API documentation",
        "Bug fixing",
        "System integration"
    ]
    task_types = ["Analysis", "Coding", "Meeting", "Email", "Other"]
    productivity_options = ["productive", "unproductive"]

    # Generate 50 test entries over the last 30 days
    print("Generating test data...")
    start_date = datetime.now() - timedelta(days=30)
    successful_entries = 0

    for _ in range(50):
        # Random date within last 30 days
        random_days = random.randint(0, 29)
        entry_date = start_date + timedelta(days=random_days)
        
        # Random time (15-480 minutes, realistic work periods)
        time_minutes = random.choice([15, 30, 45, 60, 90, 120, 180, 240, 300, 360, 420, 480])
        
        # Create entry matching main app structure
        entry = {
            "person": random.choice(persons),
            "task": random.choice(tasks),
            "task_type": random.choice(task_types),
            "time": time_minutes,
            "productivity": random.choice(productivity_options),
            "date": entry_date
        }
        
        try:
            collection.insert_one(entry)
            print(f"✅ Added entry: {entry['person']} - {entry['task']} ({entry['time']} min)")
            successful_entries += 1
        except (ConnectionError, ValueError) as insert_error:
            print(f"❌ Error adding entry: {insert_error}")

    print(f"\n🎉 Successfully generated {successful_entries} test entries!")
    print("You can now run your main app to see the test data.")

    # Show summary
    try:
        total_entries = collection.count_documents({})
        print(f"📊 Total entries in database: {total_entries}")
    except (ConnectionError, ValueError) as count_error:
        print(f"❌ Error counting documents: {count_error}")
    
    return True

if __name__ == "__main__":
    print("🚀 Test Data Generator for Work Time Tracker")
    print("This will add 50 sample entries to your MongoDB Atlas database.")
    
    response = input("Continue? (y/N): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Data generation cancelled.")
        exit()
    
    # Generate the test data
    success = generate_test_data()
    if success:
        print("\n✅ Test data generation completed successfully!")
    else:
        print("\n❌ Test data generation failed!")