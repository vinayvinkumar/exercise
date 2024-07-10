import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to SQLite database
conn = sqlite3.connect('activities.db')
c = conn.cursor()

# Create tables
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    date TEXT,
    workout TEXT,
    junk_food TEXT,
    yoga TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')
conn.commit()

# Function to add a new user
def add_user(username):
    c.execute('INSERT INTO users (username) VALUES (?)', (username,))
    conn.commit()

# Function to get user id by username
def get_user_id(username):
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    return c.fetchone()[0]

# Streamlit app
st.set_page_config(page_title="Daily Routine Tracker", page_icon=":bar_chart:", layout="centered")
st.title("Daily Routine Tracker")

menu = ["Home", "Add User", "Log Activity", "Insights"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.image("landing_page_image.jpg", use_column_width=True)
    st.markdown("""
        # Welcome to the Daily Routine Tracker!
        This application helps you track your daily activities, including Workout, Junk Food, and Yoga. 
        You can add multiple users, log daily activities, and visualize your progress over time.
    """)

elif choice == "Add User":
    st.subheader("Add New User")
    new_user = st.text_input("Username")
    if st.button("Add"):
        add_user(new_user)
        st.success(f"User {new_user} added successfully")

elif choice == "Log Activity":
    st.subheader("Log Daily Activity")
    username = st.selectbox("Select User", [row[0] for row in c.execute('SELECT username FROM users')])
    user_id = get_user_id(username)
    date = st.date_input("Date", datetime.today())
    
    cols = st.columns(3)
    workout = cols[0].checkbox("Workout")
    junk_food = cols[1].checkbox("Junk Food")
    yoga = cols[2].checkbox("Yoga")
    
    if st.button("Submit"):
        c.execute('''
        INSERT INTO activities (user_id, date, workout, junk_food, yoga)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, date, 'Yes' if workout else 'No', 'Yes' if junk_food else 'No', 'Yes' if yoga else 'No'))
        conn.commit()
        st.success("Activity logged successfully")

elif choice == "Insights":
    st.subheader("Insights")
    
    # Filter options
    filter_option = st.selectbox("Filter by", ["Day", "Week", "Month"])
    username = st.selectbox("Select User", [row[0] for row in c.execute('SELECT username FROM users')])
    user_id = get_user_id(username)
    
    # Fetch data
    query = 'SELECT date, workout, junk_food, yoga FROM activities WHERE user_id = ?'
    df = pd.read_sql(query, conn, params=(user_id,))
    df['date'] = pd.to_datetime(df['date'])
    
    today = datetime.today().date()
    
    if filter_option == "Day":
        df_day = df[df['date'] == pd.to_datetime(today)]
        if not df_day.empty:
            workout = df_day['workout'].values[0]
            junk_food = df_day['junk_food'].values[0]
            yoga = df_day['yoga'].values[0]
            st.write(f"Date: {today}")
            st.write(f"Workout: {workout}")
            st.write(f"Junk Food: {junk_food}")
            st.write(f"Yoga: {yoga}")
        else:
            st.write(f"No data available for {today}")
    
    elif filter_option == "Week":
        current_week = today.isocalendar()[1]
        df_week = df[df['date'].dt.isocalendar().week == current_week]
        if not df_week.empty:
            total_days = df_week['date'].nunique()
            workout_days = df_week[df_week['workout'] == 'Yes'].shape[0]
            junk_food_days = df_week[df_week['junk_food'] == 'Yes'].shape[0]
            yoga_days = df_week[df_week['yoga'] == 'Yes'].shape[0]
            st.write(f"Week {current_week}")
            st.write(f"Workout: {workout_days}/{total_days} days")
            st.write(f"Junk Food: {junk_food_days}/{total_days} days")
            st.write(f"Yoga: {yoga_days}/{total_days} days")
        else:
            st.write(f"No data available for week {current_week}")
    
    elif filter_option == "Month":
        current_month = today.month
        df_month = df[df['date'].dt.month == current_month]
        if not df_month.empty:
            total_days = df_month['date'].nunique()
            workout_days = df_month[df_month['workout'] == 'Yes'].shape[0]
            junk_food_days = df_month[df_month['junk_food'] == 'Yes'].shape[0]
            yoga_days = df_month[df_month['yoga'] == 'Yes'].shape[0]
            st.write(f"Month: {today.strftime('%B')}")
            st.write(f"Workout: {workout_days}/{total_days} days")
            st.write(f"Junk Food: {junk_food_days}/{total_days} days")
            st.write(f"Yoga: {yoga_days}/{total_days} days")
        else:
            st.write(f"No data available for {today.strftime('%B')}")

conn.close()
