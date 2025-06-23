import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE journal_entries ADD COLUMN mood TEXT")

conn.commit()
conn.close()

print("Mood column added!")
