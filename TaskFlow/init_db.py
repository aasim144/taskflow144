import sqlite3


conn = sqlite3.connect("taskflow.db")
cursor = conn.cursor()


cursor.execute(""" 
  CREATE TABLE project_members (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER,
  user_email TEXT,
  role TEXT DEFAULT 'member'
);
 """)

conn.commit()
conn.close()

print("Database created correctly")
