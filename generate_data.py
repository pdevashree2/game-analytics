import sqlite3
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

NUM_PLAYERS = 500
NUM_GAMES = 10
NUM_SESSIONS = 5000
NUM_PURCHASES = 2000

countries = ["India", "USA", "Brazil", "Germany", "Japan", "UK", "Canada"]
platforms = ["Mobile", "PC", "Console"]

players = []
for i in range(1, NUM_PLAYERS + 1):
    players.append({
        "player_id": i,
        "username": fake.user_name(),
        "country": random.choice(countries),
        "platform": random.choice(platforms),
        "registration_date": fake.date_between(start_date="-2y", end_date="-6m")
    })

genres = ["Action", "RPG", "Puzzle", "Sports", "Strategy"]
game_names = ["Shadow Strike", "Neon Quest", "Pixel Legends",
              "Speed Rush", "Dark Realm", "Star Arena",
              "Block Blast", "Turbo Race", "Myth Wars", "Cyber Hunt"]

games = []
for i in range(1, NUM_GAMES + 1):
    games.append({
        "game_id": i,
        "game_name": game_names[i - 1],
        "genre": random.choice(genres),
        "platform": random.choice(platforms),
        "release_date": fake.date_between(start_date="-3y", end_date="-1y")
    })

sessions = []
for i in range(1, NUM_SESSIONS + 1):
    start = fake.date_time_between(start_date="-1y", end_date="now")
    duration = random.randint(5, 120)
    end = start + timedelta(minutes=duration)
    sessions.append({
        "session_id": i,
        "player_id": random.randint(1, NUM_PLAYERS),
        "game_id": random.randint(1, NUM_GAMES),
        "start_time": start,
        "end_time": end,
        "duration_minutes": duration,
        "score": random.randint(100, 10000)
    })

items = ["Skin Pack", "Extra Lives", "Power Boost", "Weapon Pack", "Gold Coins", "VIP Pass"]

purchases = []
for i in range(1, NUM_PURCHASES + 1):
    purchases.append({
        "purchase_id": i,
        "player_id": random.randint(1, NUM_PLAYERS),
        "game_id": random.randint(1, NUM_GAMES),
        "item_name": random.choice(items),
        "amount": round(random.uniform(0.99, 49.99), 2),
        "purchase_date": fake.date_between(start_date="-1y", end_date="today")
    })

conn = sqlite3.connect("data/game_analytics.db")

pd.DataFrame(players).to_sql("players", conn, if_exists="replace", index=False)
pd.DataFrame(games).to_sql("games", conn, if_exists="replace", index=False)
pd.DataFrame(sessions).to_sql("sessions", conn, if_exists="replace", index=False)
pd.DataFrame(purchases).to_sql("purchases", conn, if_exists="replace", index=False)

conn.close()
print("✅ Database created successfully with sample game data!")