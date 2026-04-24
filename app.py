import os
import sqlite3
import pandas as pd
from faker import Faker
import random
from datetime import timedelta

# Auto-generate database if it doesn't exist
if not os.path.exists("data/game_analytics.db"):
    os.makedirs("data", exist_ok=True)
    fake = Faker()
    random.seed(42)
    
    players = [{"player_id": i, "username": fake.user_name(),
        "country": random.choice(["India","USA","Brazil","Germany","Japan","UK","Canada"]),
        "platform": random.choice(["Mobile","PC","Console"]),
        "registration_date": str(fake.date_between(start_date="-2y", end_date="-6m"))}
        for i in range(1, 501)]
    
    game_names = ["Shadow Strike","Neon Quest","Pixel Legends","Speed Rush","Dark Realm",
                  "Star Arena","Block Blast","Turbo Race","Myth Wars","Cyber Hunt"]
    games = [{"game_id": i, "game_name": game_names[i-1],
        "genre": random.choice(["Action","RPG","Puzzle","Sports","Strategy"]),
        "platform": random.choice(["Mobile","PC","Console"]),
        "release_date": str(fake.date_between(start_date="-3y", end_date="-1y"))}
        for i in range(1, 11)]
    
    sessions = [{"session_id": i, "player_id": random.randint(1,500),
        "game_id": random.randint(1,10),
        "start_time": str(fake.date_time_between(start_date="-1y", end_date="now")),
        "duration_minutes": random.randint(5,120),
        "score": random.randint(100,10000)}
        for i in range(1, 5001)]
    
    purchases = [{"purchase_id": i, "player_id": random.randint(1,500),
        "game_id": random.randint(1,10),
        "item_name": random.choice(["Skin Pack","Extra Lives","Power Boost","Weapon Pack","Gold Coins","VIP Pass"]),
        "amount": round(random.uniform(0.99, 49.99), 2),
        "purchase_date": str(fake.date_between(start_date="-1y", end_date="today"))}
        for i in range(1, 2001)]
    
    conn = sqlite3.connect("data/game_analytics.db")
    pd.DataFrame(players).to_sql("players", conn, if_exists="replace", index=False)
    pd.DataFrame(games).to_sql("games", conn, if_exists="replace", index=False)
    pd.DataFrame(sessions).to_sql("sessions", conn, if_exists="replace", index=False)
    pd.DataFrame(purchases).to_sql("purchases", conn, if_exists="replace", index=False)
    conn.close()


import streamlit as st
import plotly.express as px
conn = sqlite3.connect("data/game_analytics.db")

st.set_page_config(page_title="Game Analytics Dashboard", page_icon="🎮", layout="wide")
st.title("🎮 Game Analytics Dashboard")
st.markdown("Insights from player sessions, revenue, and game performance.")

total_players = pd.read_sql("SELECT COUNT(*) AS c FROM players", conn).iloc[0, 0]
total_sessions = pd.read_sql("SELECT COUNT(*) AS c FROM sessions", conn).iloc[0, 0]
total_revenue = pd.read_sql("SELECT ROUND(SUM(amount),2) AS c FROM purchases", conn).iloc[0, 0]
avg_duration = pd.read_sql("SELECT ROUND(AVG(duration_minutes),1) AS c FROM sessions", conn).iloc[0, 0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Players", f"{total_players:,}")
col2.metric("Total Sessions", f"{total_sessions:,}")
col3.metric("Total Revenue", f"${total_revenue:,}")
col4.metric("Avg Session Duration", f"{avg_duration} mins")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Players by Country")
    df = pd.read_sql("SELECT country, COUNT(*) AS player_count FROM players GROUP BY country ORDER BY player_count DESC", conn)
    fig = px.bar(df, x="country", y="player_count", color="country")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Players by Platform")
    df = pd.read_sql("SELECT platform, COUNT(*) AS player_count FROM players GROUP BY platform", conn)
    fig = px.pie(df, names="platform", values="player_count", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Played Games")
    df = pd.read_sql("""SELECT g.game_name, COUNT(s.session_id) AS total_sessions
        FROM sessions s JOIN games g ON s.game_id = g.game_id
        GROUP BY s.game_id ORDER BY total_sessions DESC""", conn)
    fig = px.bar(df, x="total_sessions", y="game_name", orientation="h", color="game_name")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Revenue by Game")
    df = pd.read_sql("""SELECT g.game_name, ROUND(SUM(p.amount),2) AS total_revenue
        FROM purchases p JOIN games g ON p.game_id = g.game_id
        GROUP BY p.game_id ORDER BY total_revenue DESC""", conn)
    fig = px.pie(df, names="game_name", values="total_revenue")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Country")
    df = pd.read_sql("""SELECT pl.country, ROUND(SUM(p.amount),2) AS total_revenue
        FROM purchases p JOIN players pl ON p.player_id = pl.player_id
        GROUP BY pl.country ORDER BY total_revenue DESC""", conn)
    fig = px.bar(df, x="country", y="total_revenue", color="country")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top 10 Players by Score")
    df = pd.read_sql("""SELECT p.username, p.country, SUM(s.score) AS total_score
        FROM sessions s JOIN players p ON s.player_id = p.player_id
        GROUP BY s.player_id ORDER BY total_score DESC LIMIT 10""", conn)
    fig = px.bar(df, x="username", y="total_score", color="country")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Daily Active Users (Last 30 Days)")
df = pd.read_sql("""SELECT DATE(start_time) AS date,
    COUNT(DISTINCT player_id) AS daily_active_users
    FROM sessions WHERE start_time >= DATE('now', '-30 days')
    GROUP BY DATE(start_time) ORDER BY date""", conn)
fig = px.line(df, x="date", y="daily_active_users", markers=True)
st.plotly_chart(fig, use_container_width=True)

conn.close()