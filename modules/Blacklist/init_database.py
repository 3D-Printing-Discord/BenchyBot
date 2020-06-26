import sqlite3
import sys

#DB Name
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE Blacklist (term text)''')

# Save (commit) the changes
conn.commit()

# close connection 
conn.close()