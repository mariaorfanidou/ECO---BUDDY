cursor.execute("""
CREATE TABLE IF NOT EXISTS badhabits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    suggestion1 TEXT,
    suggestion2 TEXT
)
""")