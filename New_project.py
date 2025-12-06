import pymysql
import pandas as pd
import boto3
from io import StringIO
import cryptography
import os
from datetime import datetime



# 1. Establish connection
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="sakila"
)


# 2. Define query
query = "SELECT * FROM country"

# 3. Load data into DataFrame
df = pd.read_sql(query, con=connection)

# 4. Display DataFrame
print(df)

#AWS Credentials
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
BUCKET_NAME = 'vedantanerao101'


LAST_ID_FILE = 'last_id.txt'
# 1. Read last uploaded ID
if os.path.exists(LAST_ID_FILE):
    with open(LAST_ID_FILE, 'r') as f:
        last_id = int(f.read().strip())
else:
    last_id = 0  # Default for first run


# 3. If new data exists
if not df.empty:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    S3_FILE_KEY = f'new_raw_data/audit_data_{timestamp}.csv'
    # Update last ID
    new_last_id = df['country_id'].max()
    with open(LAST_ID_FILE, 'w') as f:
        f.write(str(new_last_id))

    # Convert DataFrame to CSV in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    # Upload to S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    s3.put_object(Bucket=BUCKET_NAME, Key=S3_FILE_KEY, Body=csv_buffer.getvalue())

# 4. Close DB connection
connection.close()
