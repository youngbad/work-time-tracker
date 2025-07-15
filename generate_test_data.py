#!/usr/bin/env python3
"""
Test Data Generator for Work Time Tracker

This script generates sample data for testing the Work Time Tracker application.
It creates realistic work entries with various persons, tasks, and time periods.

Usage:
    python testing_data.py

Requirements:
    - MongoDB Atlas connection (same as main app)
    - pymongo package
"""

if __name__ == "__main__":
    print("🚀 Starting test data generation...")
    print("This will add sample entries to your MongoDB Atlas database.")
    
    response = input("Continue? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        print("Proceeding with data generation...")
        # The main script will run here
    else:
        print("❌ Data generation cancelled.")
        exit()
