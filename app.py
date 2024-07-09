# app.py
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
st.title("Daily Routine Tracker")

menu = ["Add User", "Log Activity", "Insights"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add User":
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
    workout = st.radio("Workout", ("Yes", "No"))
    junk_food = st.radio("Junk Food", ("Yes", "No"))
    yoga = st.radio("Yoga", ("Yes", "No"))
    
    if st.button("Submit"):
        c.execute('''
        INSERT INTO activities (user_id, date, workout, junk_food, yoga)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, date, workout, junk_food, yoga))
        conn.commit()
        st.success("Activity logged successfully")

elif choice == "Insights":
    st.subheader("Insights")
    
    # Filter options
    filter_option = st.selectbox("Filter by", ["Day", "Week", "Month", "Year"])
    username = st.selectbox("Select User", [row[0] for row in c.execute('SELECT username FROM users')])
    user_id = get_user_id(username)
    
    # Fetch data
    query = 'SELECT date, workout, junk_food, yoga FROM activities WHERE user_id = ?'
    df = pd.read_sql(query, conn, params=(user_id,))
    df['date'] = pd.to_datetime(df['date'])
    
    if filter_option == "Day":
        df = df[df['date'] == pd.to_datetime(datetime.today().date())]
    elif filter_option == "Week":
        df = df[df['date'].dt.isocalendar().week == datetime.today().isocalendar()[1]]
    elif filter_option == "Month":
        df = df[df['date'].dt.month == datetime.today().month]
    elif filter_option == "Year":
        df = df[df['date'].dt.year == datetime.today().year]
    
    # Visualization
    if not df.empty:
        melted_df = pd.melt(df, id_vars=['date'], value_vars=['workout', 'junk_food', 'yoga'], var_name='activity', value_name='status')
        count_df = melted_df[melted_df['status'] == 'Yes'].groupby('activity').count().reset_index()
        plt.figure(figsize=(10, 5))
        sns.barplot(x='activity', y='status', data=count_df)
        plt.title('Activity Insights')
        plt.ylabel('Count')
        plt.xlabel('Activity')
        st.pyplot(plt)
    else:
        st.write("No data available for the selected period")
        
conn.close()