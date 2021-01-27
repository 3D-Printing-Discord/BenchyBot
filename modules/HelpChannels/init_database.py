import sqlite3
import sys

#DB Name
conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE HelpChannels_demand (timestamp date, active_channels integer)''')
c.execute('''CREATE TABLE HelpChannels_log (timestamp date, close_type text, owner integer, timestamp_open date)''')


# Save (commit) the changes
conn.commit()

# close connection 
conn.close()