import os
import pymysql
from dotenv import load_dotenv
from pathlib import Path

# Load env
BASE_DIR = Path(__file__).resolve().parent.parent / 'ez_request'
load_dotenv(BASE_DIR / '.env')

# Connect and drop
connection = pymysql.connect(
    host=os.getenv('DB_HOST', '127.0.0.1'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'ez_request'),
    port=int(os.getenv('DB_PORT', 3306))
)

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables:
        print(f"Dropping table {table[0]}")
        cursor.execute(f"DROP TABLE IF EXISTS `{table[0]}`")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    connection.commit()

print("All tables dropped.")
