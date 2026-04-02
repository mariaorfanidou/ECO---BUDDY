import sqlite3
import os
from datetime import date

DB_PATH = "eco_buddy.db"

LEVELS = {
    1: "Beginner",
    2: "Green Learner",
    3: "Active Citizen",
    4: "Eco Hero",
    5: "EcoMaster",
    6: "EcoLegend",
    7: "Planet Guardian"
}

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT,
            age INTEGER,
            score INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            nickname TEXT
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            suggestion TEXT,
            description TEXT,
            tips TEXT
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS user_habits (
            user_id INTEGER,
            habit_id INTEGER,
            PRIMARY KEY (user_id, habit_id)
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS daily_logs (
            user_id INTEGER,
            habit_id INTEGER,
            log_date TEXT,
            success INTEGER,
            note TEXT
        )""")
        conn.commit()

def preload_habits():
    habits = [
        ("🥩 Daily meat consumption", "Diet",
         "Try 1–2 vegetarian meals per week.",
         "Excessive meat consumption has serious environmental consequences. Livestock farming requires huge amounts of water, energy, and land, while producing significant greenhouse gases.",
         "1. Introduce one meatless day per week.\n2. Try plant-based substitutes.\n3. Learn about sustainable eating."),

        ("🧴 Use of single-use plastics", "Consumption",
         "Replace plastics with reusable items.",
         "Single-use plastics often end up in oceans, harming marine life. They are made from oil and can persist for hundreds of years in the environment.",
         "1. Carry your own water bottle.\n2. Use your own shopping bags.\n3. Choose plastic-free stores."),

        ("🚗 Daily car use", "Transportation",
         "Use a bike, public transport or walk.",
         "Cars are one of the biggest polluters. Dependence on them increases CO₂ emissions and city congestion.",
         "1. Walk for short distances.\n2. Carpool with friends.\n3. Support public transport."),

        ("💡 Energy waste at home", "Consumption",
         "Turn off lights and devices when not needed.",
         "Unnecessary energy use increases your carbon footprint and utility bills.",
         "1. Use LED bulbs.\n2. Unplug chargers.\n3. Adjust the thermostat properly."),

        ("🗑️ Littering in nature", "Environment",
         "Always use a bin or take your trash with you.",
         "Litter in nature destroys ecosystems and harms animals and plants.",
         "1. Join clean-up efforts.\n2. Avoid outdoor littering.\n3. Educate friends and family."),

        ("🚿 Water waste", "Consumption",
         "Reduce water use in daily habits.",
         "Water is a precious and limited resource. Waste affects access to clean water for other regions and future generations.",
         "1. Turn off the tap while brushing teeth.\n2. Take shorter showers.\n3. Fix leaks promptly."),

        ("👕 Buying unnecessary clothes (fast fashion)", "Consumption",
         "Buy fewer, higher-quality clothes.",
         "Fast fashion pollutes, consumes resources, and supports labor exploitation.",
         "1. Shop at second-hand stores.\n2. Organize clothing swaps.\n3. Support sustainable brands."),

        ("♻️ Not recycling", "Waste management",
         "Start sorting materials at home.",
         "Recycling reduces the need for raw materials and lowers waste output.",
         "1. Learn what can be recycled.\n2. Use the bins correctly.\n3. Teach your household."),

        ("🚱 Drinking bottled water", "Consumption",
         "Prefer a reusable bottle and filtered tap water.",
         "Plastic bottles require energy to produce and transport, and are often not recycled.",
         "1. Use a metal water bottle.\n2. Install a tap filter.\n3. Use public fountains."),

        ("🚶‍♂️ Daily elevator use", "Energy & Health",
         "Take the stairs for short distances.",
         "Elevators consume electricity and reduce physical activity.",
         "1. Start with one floor.\n2. Set step goals.\n3. Avoid elevators at home."),

        ("📺 Excessive use of electronic devices", "Energy",
         "Limit use to essential devices.",
         "Heavy use of electronics wastes electricity and stresses the environment.",
         "1. Unplug when not in use.\n2. Use timers.\n3. Avoid multitasking with multiple screens."),

        ("📱 Excessive social media use", "Digital behavior",
         "Start with one hour a day without your phone.",
         "Social media increases energy use via servers and devices, affects focus, and lowers time sustainability.",
         "1. Set screen time limits.\n2. Take offline walks.\n3. Use eco-mode.\n4. Turn off notifications.\n5. Spend time screen-free."),

        ("🍽️ Delivery orders with plastic packaging", "Consumption",
         "Request no plastic or choose eco-friendly businesses.",
         "Plastic from delivery services ends up in waste and seriously pollutes oceans and cities.",
         "1. Ask for no cutlery.\n2. Support eco-packaging vendors.\n3. Cook at home more often."),

        ("🛒 Impulse buying", "Consumption",
         "Make a shopping list and buy mindfully.",
         "Unnecessary consumption increases waste, supports polluting industries, and burdens the planet.",
         "1. Wait 24 hours before buying.\n2. Shop second-hand.\n3. Avoid boredom-shopping.\n4. Set a monthly budget."),

        ("📦 Excessive online shopping", "Consumption",
         "Reduce online purchases and buy locally.",
         "Online shopping increases plastic use, transport emissions, and carbon footprint.",
         "1. Make fewer, combined orders.\n2. Choose eco-friendly shipping.\n3. Support local businesses.")
    ]
    with get_connection() as conn:
        c = conn.cursor()
        for h in habits:
            c.execute("""
                INSERT OR IGNORE INTO habits (name, category, suggestion, description, tips)
                VALUES (?, ?, ?, ?, ?)""", h)
        conn.commit()


def calculate_level(score):
    if score >= 100:
        return 7
    elif score >= 70:
        return 6
    elif score >= 50:
        return 5
    elif score >= 40:
        return 4
    elif score >= 25:
        return 3
    elif score >= 10:
        return 2
    return 1

def update_user_level(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT score FROM users WHERE id = ?", (user_id,))
        score = c.fetchone()[0]
        level = calculate_level(score)
        nickname = LEVELS[level]
        c.execute("UPDATE users SET level = ?, nickname = ? WHERE id = ?", (level, nickname, user_id))
        conn.commit()

def create_user_profile():
    with get_connection() as conn:
        c = conn.cursor()
        username = input("Choose a username: ")
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            print("Username already exists.")
            return None
        password = input("Password: ")
        name = input("Your name: ")
        age = input("Your age: ")
        c.execute("INSERT INTO users (username, password, name, age) VALUES (?, ?, ?, ?)",
                  (username, password, name, age))
        conn.commit()
        return c.lastrowid

def login_user():
    username = input("Username: ")
    password = input("Password: ")
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()
        return result[0] if result else None

def show_user_profile(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT username, name, age, score, level, nickname FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if user:
            print(f"\nUsername: {user[0]} | Name: {user[1]} | Age: {user[2]}")
            print(f"Score: {user[3]} | Level: {user[4]} - {user[5]}")
            c.execute("SELECT habits.name FROM user_habits JOIN habits ON user_habits.habit_id = habits.id WHERE user_habits.user_id = ?", (user_id,))
            habits = c.fetchall()
            print("\nYour selected habits:")
            for h in habits:
                print(f"- {h[0]}")
        else:
            print("User not found.")

def edit_user_profile(user_id):
    name = input("New name: ")
    age = input("New age: ")
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET name = ?, age = ? WHERE id = ?", (name, age, user_id))
        conn.commit()

def delete_user_profile(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        c.execute("DELETE FROM user_habits WHERE user_id = ?", (user_id,))
        c.execute("DELETE FROM daily_logs WHERE user_id = ?", (user_id,))
        conn.commit()

def delete_user_habit(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT habits.id, habits.name FROM user_habits JOIN habits ON user_habits.habit_id = habits.id WHERE user_habits.user_id = ?", (user_id,))
        habits = c.fetchall()
        for h in habits:
            print(f"{h[0]}: {h[1]}")
        choice = input("Enter habit ID to delete: ")
        c.execute("DELETE FROM user_habits WHERE user_id = ? AND habit_id = ?", (user_id, choice))
        conn.commit()

def select_user_habits(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        while True:
            c.execute("SELECT id, name FROM habits")
            all_habits = c.fetchall()
            print("\nAvailable habits:")
            for h in all_habits:
                print(f"{h[0]}. {h[1]}")
            habit_id_input = input("Enter habit ID to add (or press Enter to return): ")
            if not habit_id_input.strip():
                break
            if not habit_id_input.isdigit():
                print("Invalid input.")
                continue
            habit_id = int(habit_id_input)
            c.execute("SELECT 1 FROM user_habits WHERE user_id = ? AND habit_id = ?", (user_id, habit_id))
            if c.fetchone():
                print("Habit already added.")
            else:
                c.execute("INSERT INTO user_habits (user_id, habit_id) VALUES (?, ?)", (user_id, habit_id))
                conn.commit()
                print("Habit added!")

def log_user_daily_actions(user_id):
    today = date.today().isoformat()
    success_count = 0
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT h.id, h.name FROM habits h JOIN user_habits uh ON h.id = uh.habit_id WHERE uh.user_id = ?", (user_id,))
        habits = c.fetchall()
        if not habits:
            print("No habits selected.")
            return
        for h in habits:
            response = input(f"Did you follow '{h[1]}' today? (y/n): ").lower()
            success = 1 if response == 'y' else 0
            if success:
                success_count += 1
            note = input("Add note (optional): ")
            c.execute("INSERT INTO daily_logs (user_id, habit_id, log_date, success, note) VALUES (?, ?, ?, ?, ?)",
                      (user_id, h[0], today, success, note))
        if success_count > 0:
            c.execute("UPDATE users SET score = score + 10 WHERE id = ?", (user_id,))
        conn.commit()
        update_user_level(user_id)
        print("Actions logged.")

def display_user_calendar(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT h.name, l.log_date, l.success, l.note FROM daily_logs l JOIN habits h ON l.habit_id = h.id WHERE l.user_id = ? ORDER BY l.log_date DESC", (user_id,))
        entries = c.fetchall()
        if not entries:
            print("No logs found.")
            return
        for e in entries:
            status = "✅" if e[2] else "❌"
            print(f"{e[1]} | {status} {e[0]}")
            if e[3]:
                print(f"   Note: {e[3]}")

def admin_login():
    username = input("Admin username: ")
    password = input("Admin password: ")
    if username == "admin" and password == "admin123":
        print("\n✅ Admin access granted.")
        admin_menu()
    else:
        print("❌ Invalid admin credentials.")

def admin_menu():
    while True:
        print("""
🛠️ Admin Panel
1. View All Users
2. Edit User Info
3. Delete User
4. View User Calendar
0. Back to Main Menu
""")
        choice = input("Choose: ").strip()

        if choice == "1":
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT id, username, name, age, score, level, nickname FROM users")
                users = c.fetchall()
                for u in users:
                    print(f"ID: {u[0]}, Username: {u[1]}, Name: {u[2]}, Age: {u[3]}, Score: {u[4]}, Level: {u[5]} ({u[6]})")

        elif choice == "2":
            uid = input("User ID to edit: ")
            new_name = input("New name: ")
            new_age = input("New age: ")
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET name = ?, age = ? WHERE id = ?", (new_name, new_age, uid))
                conn.commit()
                print("✅ Updated.")

        elif choice == "3":
            uid = input("User ID to delete: ")
            confirm = input(f"Are you sure you want to delete user {uid}? (y/n): ").lower()
            if confirm == "y":
                with get_connection() as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM users WHERE id = ?", (uid,))
                    c.execute("DELETE FROM user_habits WHERE user_id = ?", (uid,))
                    c.execute("DELETE FROM daily_logs WHERE user_id = ?", (uid,))
                    conn.commit()
                    print("🗑️ User deleted.")

        elif choice == "4":
            uid = input("User ID to view calendar: ")
            display_user_calendar(uid)

        elif choice == "0":
            break

        else:
            print("❌ Invalid option.")

# --- Ενημέρωση run_ecobuddy με επιλογή admin ---
def run_ecobuddy():
    if not os.path.exists(DB_PATH):
        initialize_database()
        preload_habits()
    print("\nWelcome to EcoBuddy!")
    while True:
        print("\n1. Login\n2. Create Profile\n3. Admin Login\n0. Exit")
        option = input("Choose an option: ").strip()
        if option == "1":
            user_id = login_user()
            if user_id:
                show_main_menu(user_id)
            else:
                print("Wrong credentials.")
        elif option == "2":
            user_id = create_user_profile()
            if user_id:
                print("Profile created.")
                show_main_menu(user_id)
        elif option == "3":
            admin_login()
        elif option == "0":
            print("Exiting EcoBuddy.")
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    run_ecobuddy()


def show_main_menu(user_id):
    while True:
        print("""
EcoBuddy Menu
1. View/Edit Profile
2. Select Habits
3. Log Today's Actions
4. View Calendar
0. Exit
""")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_user_profile(user_id)
            print("a. Edit profile\nb. Delete habit\nc. Delete profile\nEnter to return")
            sub = input("Option: ").strip().lower()
            if sub == "a":
                edit_user_profile(user_id)
            elif sub == "b":
                delete_user_habit(user_id)
            elif sub == "c":
                delete_user_profile(user_id)
                print("Profile deleted. Exiting.")
                break
        elif choice == "2":
            select_user_habits(user_id)
        elif choice == "3":
            log_user_daily_actions(user_id)
        elif choice == "4":
            display_user_calendar(user_id)
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

def run_ecobuddy():
    if not os.path.exists(DB_PATH):
        initialize_database()
        preload_habits()
    print("\nWelcome to EcoBuddy!")
    while True:
        print("\n1. Login\n2. Create Profile\n0. Exit")
        option = input("Choose an option: ").strip()
        if option == "1":
            user_id = login_user()
            if user_id:
                show_main_menu(user_id)
            else:
                print("Wrong credentials.")
        elif option == "2":
            user_id = create_user_profile()
            if user_id:
                print("Profile created.")
                show_main_menu(user_id)
        elif option == "0":
            print("Exiting EcoBuddy.")
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    run_ecobuddy()
