'''To create the database'''
import sqlite3

# Connect to database

conn = sqlite3.connect('tower_service.db')

# Create a cursor
c = conn.cursor()

# Create Tower Table

c.execute(""" DROP TABLE tower
          """)

c.execute(""" DROP TABLE shell
          """)


c.execute(""" CREATE TABLE tower (
    tower_id INTEGER PRIMARY KEY,
    bottom_diameter INTEGER,
    top_diameter INTEGER,
    number_of_shells INTEGER)
          """)

c.execute(""" CREATE TABLE shell (
    shell_id INTEGER PRIMARY KEY,
    position INTEGER,
    height REAL,
    bottom_diameter REAL,
    top_diameter REAL,
    thickness REAL,
    steel_density REAL,
    shell_tower_id INTEGER,
    FOREIGN KEY(shell_tower_id) REFERENCES tower (tower_id)
)
          """)

conn.commit()

conn.close()
