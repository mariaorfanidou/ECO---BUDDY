import sqlite3
import datetime
import getpass
import random


conn = sqlite3.connect("eco_buddy.db")
cursor = conn.cursor()

#cursor.execute("DROP TABLE IF EXISTS user")
#cursor.execute("DROP TABLE IF EXISTS badhabits")
#cursor.execute("DROP TABLE IF EXISTS user_habits")
#cursor.execute("DROP TABLE IF EXISTS entries")


cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    first_name TEXT,
    last_name TEXT,
    level INTEGER DEFAULT 1,
    points INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_entry_date TEXT
  )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS badhabits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    suggestion1 TEXT,
    suggestion2 TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_habits (
    user_id INTEGER,
    habit_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(habit_id) REFERENCES badhabits(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    habit_id INTEGER,
    date TEXT,
    action TEXT,
    chosen_action TEXT,
    points INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(habit_id) REFERENCES badhabits(id)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS habit_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER,
    suggestion TEXT,
    FOREIGN KEY(habit_id) REFERENCES badhabits(id)
)
""")


def get_title_by_level(level):
    titles = {
        1: "Eco Novice",
        2: "Nature Friend",
        3: "Eco Advocate",
        4: "Green Hero",
        5: "Sustainability Mentor"
    }
    return titles.get(level, "Legend of Ecology")



DAILY_CHALLENGE_ACTIONS = []

default_habits = [
    ("Littering on the street",
     "Uncontrolled waste disposal pollutes the environment, clogs drains, and threatens marine life.",
     "Use public trash bins",
     "Carry a small bag and join cleanup actions"),

    ("Ordering delivery with plastic packaging",
     "Plastic containers are non-biodegradable and end up in landfills or oceans.",
     "Ask for 'no plastic'",
     "Use your own reusable containers"),

    ("Using a car for short distances",
     "Driving increases CO2 emissions and contributes to climate change.",
     "Walk instead",
     "Ride a bike or use public transportation"),

    ("Leaving lights on unnecessarily",
     "Wasting energy burdens the grid and increases air pollution.",
     "Install motion sensors",
     "Use LED bulbs and set reminders"),

    ("Using plastic bottles",
     "Plastic bottles remain in the environment for hundreds of years.",
     "Use a glass or metal water bottle",
     "Fill it at home or from public water fountains"),

    ("Washing clothes with small loads",
     "Wastes water and energy on unnecessary washing cycles.",
     "Wait until the drum is full",
     "Use eco mode and natural detergents"),

    ("Forgetting to recycle",
     "Valuable materials are lost and landfills fill up faster.",
     "Organize recycling bins at home",
     "Download a recycling app and learn the codes"),

    ("Buying fast fashion",
     "The fashion industry pollutes and exploits labor.",
     "Buy second-hand or sustainable brands",
     "Give your clothes a second life"),

    ("Overconsuming meat",
     "Intensive livestock farming causes deforestation and methane emissions.",
     "Try Meatless Monday",
     "Cook plant-based meals"),

    ("Using air conditioning too often",
     "A/C consumes a lot of energy and harms the environment.",
     "Open windows early in the morning",
     "Use fans and insulating shutters"),

    ("Not using rechargeable batteries",
     "Regular batteries contain toxic metals and are hard to recycle.",
     "Prefer rechargeable batteries",
     "Recycle used ones at designated points"),

    ("Wasting food",
     "Food waste means wasting energy, water, and transportation.",
     "Buy only what you need",
     "Use leftovers in new meals"),

    ("Buying plastic bags",
     "Single-use bags pollute both land and sea.",
     "Use reusable shopping bags",
     "Buy cloth or foldable alternatives"),

    ("Leaving devices on standby",
     "Devices in standby mode consume energy (phantom load).",
     "Turn them off completely",
     "Use power strips with switches or smart plugs"),

    ("Burning trash",
     "Burning waste releases toxic substances harmful to health and the environment.",
     "Dispose of trash in municipal bins",
     "Take hazardous materials to designated drop-off points")
]

cursor.executemany("INSERT INTO badhabits (title, description, suggestion1, suggestion2) VALUES (?, ?, ?, ?)", default_habits)
conn.commit()


def admin_panel():
    while True:
        print("\n🛠️ Admin Panel")
        cursor.execute("SELECT id, username, first_name, last_name FROM user")
        users = cursor.fetchall()
        for idx, u in enumerate(users, start=1):
            print(f"{idx}. {u[2]} {u[3]} (Username: {u[1]})")
        print("0. Exit")
        try:
            selection = int(input("\nSelect a user: "))
            if selection == 0:
                break
            selected_user = users[selection - 1]
            user_id = selected_user[0]

            cursor.execute("SELECT level, points, streak FROM user WHERE id = ?", (user_id,))
            level, points, streak = cursor.fetchone()
            title = get_title_by_level(level)
            print(f"\n👤 {selected_user[2]} {selected_user[3]} | Level: {level} ({title}) | Points: {points} | Streak: {streak}")

            print("[1] View Progress | [2] Edit | [3] Delete | [Enter] Back")
            choice = input("Choice: ")
            if choice == "1":
                cursor.execute("SELECT date, chosen_action, points FROM entries WHERE user_id = ? ORDER BY date DESC", (user_id,))
                entries = cursor.fetchall()
                if not entries:
                    print("📭 No entries found.")
                else:
                    for e in entries:
                        print(f"📅 {e[0]} | ➤ {e[1]} | ⭐ Points: {e[2]}")
            elif choice == "2":
                new_name = input("New first name (Enter to skip): ")
                new_surname = input("New last name (Enter to skip): ")
                new_level = input("New level (Enter to skip): ")
                new_points = input("New points (Enter to skip): ")
                if new_name:
                    cursor.execute("UPDATE user SET first_name = ? WHERE id = ?", (new_name, user_id))
                if new_surname:
                    cursor.execute("UPDATE user SET last_name = ? WHERE id = ?", (new_surname, user_id))
                if new_level:
                    cursor.execute("UPDATE user SET level = ? WHERE id = ?", (int(new_level), user_id))
                if new_points:
                    cursor.execute("UPDATE user SET points = ? WHERE id = ?", (int(new_points), user_id))
                conn.commit()
                print("✅ User information updated.")
            elif choice == "3":
                confirm = input("❗ Are you sure you want to delete this user? (yes/no): ")
                if confirm.lower() == "yes":
                    cursor.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))
                    cursor.execute("DELETE FROM user_habits WHERE user_id = ?", (user_id,))
                    cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
                    conn.commit()
                    print("🗑️ User deleted.")
        except (IndexError, ValueError):
            print("❌ Invalid selection.")






def register():
    print("\n--- Create Profile ---")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")

    try:
        cursor.execute("INSERT INTO user (username, password, first_name, last_name) VALUES (?, ?, ?, ?)",
                       (username, password, first_name, last_name))
        conn.commit()
        print("✅ Account successfully created!")
    except sqlite3.IntegrityError:
        print("❌ Username already exists.")

def login():
    print("\n--- Login ---")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    if username == "admin" and password == "12345":
        admin_panel()
        return

    cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    if user:
        print(f"👋 Welcome, {user[3]}!")
        main_menu(user)
    else:
        print("❌ Incorrect credentials.")



def main_menu(user):
    while True:
        print("\n--- Eco Buddy ---")
        print("1. Harmful Habits")
        print("2. View Journal")
        print("3. Daily Progress")
        print("4. Edit Profile")
        print("0. Exit")
        choice = input("Choice: ")
        if choice == "1":
            show_habits(user)
        elif choice == "2":
            show_log(user)
        elif choice == "3":
            user = daily_progress(user)
        elif choice == "4":
            edit_profile(user)
        elif choice == "0":
            break



def show_daily_challenge(user):
    global DAILY_CHALLENGE_ACTIONS
    cursor.execute("SELECT streak FROM user WHERE id = ?", (user[0],))
    streak = cursor.fetchone()[0]
    if streak >= 3:
        print("\n🌿 Your Daily Eco-Challenge:")
        cursor.execute("SELECT habit_id, suggestion FROM habit_suggestions")
        all_suggestions = cursor.fetchall()
        random.shuffle(all_suggestions)
        DAILY_CHALLENGE_ACTIONS = [s[1] for s in all_suggestions[:3]]
        for i, suggestion in enumerate(DAILY_CHALLENGE_ACTIONS, start=1):
            print(f"{i}. {suggestion}")
    else:
        DAILY_CHALLENGE_ACTIONS = []



def show_habits(user):
    cursor.execute("SELECT * FROM badhabits")
    habits = cursor.fetchall()
    for h in habits:
        print(f"\n{h[0]}. {h[1]}")
    while True:
        choice = input("\nSelect a habit to view details (or 0 to go back): ")
        if choice == "0":
            break
        cursor.execute("SELECT * FROM badhabits WHERE id = ?", (choice,))
        habit = cursor.fetchone()
        if habit:
            print(f"\n📌 {habit[1]}\n❗ {habit[2]}\n✅ Suggestions: {habit[3]}")
            cursor.execute("SELECT * FROM user_habits WHERE user_id = ? AND habit_id = ?", (user[0], habit[0]))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO user_habits (user_id, habit_id) VALUES (?, ?)", (user[0], habit[0]))
                conn.commit()
        else:
            print("❌ Invalid selection.")



def show_log(user):
    cursor.execute("""
        SELECT entries.date, badhabits.title, entries.action, entries.points
        FROM entries
        JOIN badhabits ON entries.habit_id = badhabits.id
        WHERE entries.user_id = ?
        ORDER BY entries.date DESC
    """, (user[0],))
    rows = cursor.fetchall()
    if not rows:
        print("📭 No entries found.")
    else:
        for row in rows:
            print(f"📅 {row[0]} | {row[1]} | Action: {row[2]} | Points: {row[3]}")





def daily_progress(user):
    today = str(datetime.date.today())
    cursor.execute("SELECT habit_id FROM user_habits WHERE user_id = ?", (user[0],))
    habits = cursor.fetchall()
    did_something = False
    total_points = 0

    for (habit_id,) in habits:
        cursor.execute("SELECT title, suggestion1, suggestion2 FROM badhabits WHERE id = ?", (habit_id,))
        title, s1, s2 = cursor.fetchone()
        print(f"\n➡️ {title}\n1. {s1}\n2. {s2}\n3. My own action")
        choice = input("What did you do? (1/2/3/Enter for none): ")
        if choice == "1":
            action = s1
            points = 5
            did_something = True
        elif choice == "2":
            action = s2
            points = 5
            did_something = True
        elif choice == "3":
            action = input("Describe your action: ")
            points = 5
            did_something = True
        else:
            action = "No action taken"
            points = 0
        total_points += points
        cursor.execute("INSERT INTO entries (user_id, habit_id, date, action, chosen_action, points) VALUES (?, ?, ?, ?, ?, ?)",
                       (user[0], habit_id, today, "Entry", action, points))

    cursor.execute("SELECT last_entry_date, streak, points, level FROM user WHERE id = ?", (user[0],))
    last_date, streak, current_points, level = cursor.fetchone()

    if did_something:
        if last_date == str(datetime.date.today() - datetime.timedelta(days=1)):
            streak += 1
        else:
            streak = 1
        new_points = max(0, current_points + total_points)
        new_level = (new_points // 20) + 1
        title = get_title_by_level(new_level)
        cursor.execute("UPDATE user SET points = ?, streak = ?, last_entry_date = ?, level = ? WHERE id = ?",
                       (new_points, streak, today, new_level, user[0]))
        print(f"\n🎉 Great job! You earned {total_points} points today.")
        print(f"⭐ Total Points: {new_points} | 🧱 Level: {new_level} ({title})")
    else:
        if streak >= 3:
            new_points = max(0, current_points - 1)
            streak = 0
            cursor.execute("UPDATE user SET points = ?, streak = ? WHERE id = ?", (new_points, streak, user[0]))
            print("⚠️ No actions taken today. -1 point due to broken streak.")

    conn.commit()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user[0],))
    return cursor.fetchone()


def edit_profile(user):
    title = get_title_by_level(user[5])
    print("\n--- User Profile ---")
    print(f"👤 Name: {user[3]} {user[4]}")
    print(f"📛 Username: {user[1]}")
    print(f"⭐ Points: {user[6]} | 🧱 Level: {user[5]} ({title}) | 🔁 Streak: {user[7]}")
    print("1. Change First Name")
    print("2. Change Last Name")
    print("3. Change Password")
    print("0. Back")
    choice = input("Choice: ")
    if choice == "1":
        new = input("New first name: ")
        cursor.execute("UPDATE user SET first_name = ? WHERE id = ?", (new, user[0]))
    elif choice == "2":
        new = input("New last name: ")
        cursor.execute("UPDATE user SET last_name = ? WHERE id = ?", (new, user[0]))
    elif choice == "3":
        new = getpass.getpass("New password: ")
        cursor.execute("UPDATE user SET password = ? WHERE id = ?", (new, user[0]))
    conn.commit()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user[0],))
    user = cursor.fetchone()
    print("✅ Profile updated successfully.")
    return user
  



def main():
    print("""
👋 Welcome to Eco Buddy!

🌿 An app that helps you live more sustainably – one day at a time!

🧭 How it works:
• Choose your daily bad environmental habits
• Learn why they are harmful and what you can do instead
• Log your actions each day → earn points and level up
• After a 3-day streak, unlock daily eco challenges!
• View your progress log, edit your profile info, and track your journey

🎯 Goal: Become the Legend of Sustainability!

    """)
    while True:
        print("\n--- Eco Buddy 🌱 ---")
        print("1. Create Profile")
        print("2. Login")
        print("0. Exit")
        choice = input("Choice: ")
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "0":
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()