import sqlite3
import sys

#DB Name
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE GCode (flavour text, command text, name text)''')

# Save (commit) the changes
conn.commit()

# close connection 
conn.close()