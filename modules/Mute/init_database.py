import sqlite3
import sys

#DB Name
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# Create table
c.execute('''DROP TABLE Mute_current_mutes''')
c.execute('''CREATE TABLE Mute_current_mutes (userid integer, expires_at integer)''')
 
# Save (commit) the changes
conn.commit()

# close connection 
conn.close()