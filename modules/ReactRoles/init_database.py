import sqlite3
import sys

#DB Name
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE ReactRoles (owning_message integer, role_id integer, reaction text)''')
c.execute('''CREATE TABLE ReactRoles_Banned_Users (user_id text)''')

# Save (commit) the changes
conn.commit()

# close connection 
conn.close()