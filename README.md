# Work Time Tracker

A Streamlit web application for tracking work time and productivity analysis with MongoDB Atlas integration.

## Features

- ✅ **Add time entries** with person, task, task type, time, and productivity
- ✅ **Filter data** by person and productivity
- ✅ **Interactive charts** for productivity analysis
- ✅ **Time analysis** by task type and daily breakdown
- ✅ **Secure MongoDB Atlas** connection with error handling
- ✅ **Responsive design** with modern UI

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd work-time-tracker
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MongoDB connection:**
   - Copy `.streamlit/secrets_example.toml` to `.streamlit/secrets.toml`
   - Edit `.streamlit/secrets.toml` and add your MongoDB connection string

4. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## Configuration

### MongoDB Atlas Setup

1. Create a MongoDB Atlas account
2. Create a cluster and database user
3. Add your IP address to the whitelist
4. Get your connection string

### Environment Configuration

Create `.streamlit/secrets.toml`:
```toml
# MongoDB connection string
mongo_uri = "mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority"

# Optional theme settings
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## Usage

1. **Add entries:** Fill out the form with person, task, task type, time, and productivity
2. **View data:** All entries are displayed in a searchable table
3. **Filter data:** Use the expandable filter section to filter by person or productivity
4. **Analyze:** View interactive charts for productivity and time analysis

## Technology Stack

- **Frontend:** Streamlit
- **Database:** MongoDB Atlas
- **Charts:** Plotly Express
- **Data Processing:** Pandas
- **Backend:** Python 3.10+

## File Structure

```
work-time-tracker/
├── main.py                    # Main application
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── .streamlit/
    ├── secrets.toml          # MongoDB configuration (create this)
    └── secrets_example.toml  # Configuration template
```

## Features in Detail

### Data Entry
- Person selection with custom name option
- Task description
- Task type categorization (Analysis, Coding, Meeting, Email, Other)
- Time tracking in minutes
- Productivity rating (productive/unproductive)
- Date selection

### Data Visualization
- **Productivity Pie Chart:** Shows distribution of productive vs unproductive time
- **Daily Time Chart:** Bar chart showing work time by day
- **Task Type Analysis:** Time breakdown by task categories

### Error Handling
- MongoDB connection validation
- Data validation for required fields
- Graceful error messages
- Backward compatibility with existing data

## Development

### Fixed Issues
- ✅ MongoDB authentication with special characters in password
- ✅ URL encoding for connection strings
- ✅ Data validation and error handling
- ✅ Cache management for better performance
- ✅ Backward compatibility for existing Polish data
- ✅ Responsive UI with modern design

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues or questions, please open an issue on GitHub.
