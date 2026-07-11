import streamlit as st
import sqlite3
import joblib
import pandas as pd
from database import create_tables

create_tables()

model = joblib.load("model/spam_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")


def get_db():
    return sqlite3.connect("database.db")


st.set_page_config(page_title="Spam Detection System", layout="wide")

st.title("📧 AI Spam Detection System")

menu = ["Login", "Signup"]

if "user" not in st.session_state:
    choice = st.sidebar.selectbox("Menu", menu)
else:
    choice = st.sidebar.selectbox(
        "Menu",
        ["Dashboard", "Detect Spam", "History", "Feedback", "Logout"]
    )


# ---------------- SIGNUP ----------------

if choice == "Signup":

    st.subheader("Create Account")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()

        st.success("Account created successfully")


# ---------------- LOGIN ----------------

elif choice == "Login":

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        conn = get_db()
        c = conn.cursor()

        user = c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()

        if user:
            st.session_state.user = user[0]
            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid credentials")


# ---------------- DASHBOARD ----------------

elif choice == "Dashboard":

    st.subheader("📊 Dashboard")

    conn = get_db()
    c = conn.cursor()

    total = c.execute(
        "SELECT COUNT(*) FROM history WHERE user_id=?",
        (st.session_state.user,)
    ).fetchone()[0]

    spam = c.execute(
        "SELECT COUNT(*) FROM history WHERE prediction='Spam' AND user_id=?",
        (st.session_state.user,)
    ).fetchone()[0]

    ham = c.execute(
        "SELECT COUNT(*) FROM history WHERE prediction='Not Spam' AND user_id=?",
        (st.session_state.user,)
    ).fetchone()[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Messages", total)
    col2.metric("Spam Messages", spam)
    col3.metric("Safe Messages", ham)

    st.subheader("📈 Spam vs Safe Messages")

    chart_data = pd.DataFrame({
        "Category": ["Spam", "Safe"],
        "Count": [spam, ham]
    })

    chart_data = chart_data.set_index("Category")

    st.bar_chart(chart_data)


# ---------------- DETECT SPAM ----------------

elif choice == "Detect Spam":

    st.subheader("🔍 Spam Detection")

    msg = st.text_area("Enter Message")

    if st.button("Detect"):

        vec = vectorizer.transform([msg])
        pred = model.predict(vec)[0]

        result = "Spam" if pred == 1 else "Not Spam"

        st.success(f"Prediction: {result}")

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO history(user_id,message,prediction) VALUES(?,?,?)",
            (st.session_state.user, msg, result)
        )

        conn.commit()


# ---------------- HISTORY ----------------

elif choice == "History":

    st.subheader("📜 Prediction History")

    conn = get_db()
    c = conn.cursor()

    rows = c.execute(
        "SELECT message,prediction FROM history WHERE user_id=?",
        (st.session_state.user,)
    ).fetchall()

    df = pd.DataFrame(rows, columns=["Message", "Prediction"])

    st.dataframe(df)


# ---------------- FEEDBACK ----------------

elif choice == "Feedback":

    st.subheader("💬 Feedback")

    msg = st.text_area("Your feedback")

    if st.button("Submit"):

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO feedback(user_id,message) VALUES(?,?)",
            (st.session_state.user, msg)
        )

        conn.commit()

        st.success("Feedback submitted")


# ---------------- LOGOUT ----------------

elif choice == "Logout":

    st.session_state.clear()
    st.success("Logged out")
    st.rerun()