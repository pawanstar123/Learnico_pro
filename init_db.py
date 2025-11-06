import MySQLdb

# Configure these if your MySQL uses a password or different user
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''  # Add password if you use one
MYSQL_DB = 'mydatabase'

# Connect to MySQL server (not a specific DB yet)
db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD)
cursor = db.cursor()

# Create database if it doesn't exist
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
cursor.execute(f"USE {MYSQL_DB}")

# Create users table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        email VARCHAR(150) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    )
""")

print("Database and users table are ready!")
cursor.close()
db.close()
