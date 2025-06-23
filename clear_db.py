import sqlite3

# Connect to your database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Delete all entries from journal_entries and users
cursor.execute("DELETE FROM journal_entries")
cursor.execute("DELETE FROM users")

conn.commit()
conn.close()

print("✅ All data from 'journal_entries' and 'users' tables has been cleared!")
