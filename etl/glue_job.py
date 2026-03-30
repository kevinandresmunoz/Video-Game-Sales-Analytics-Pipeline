"""
AWS Glue Python Shell Job
--------------------------
Pipeline: Kaggle API -> S3 (Parquet)

This script downloads the Video Game Sales dataset from Kaggle,
cleans and transforms it with pandas, converts it to Parquet
using PyArrow, and uploads it to S3.

Job parameters (set in Glue Job > Advanced properties > Job parameters):
    --SECRET_NAME   Name of the Secrets Manager secret with Kaggle credentials
    --S3_BUCKET     Target S3 bucket name
    --S3_PREFIX     Target S3 prefix (e.g. raw/videogames/)

Additional Python modules required:
    pandas, pyarrow, requests
"""

import sys
import json
import io
import zipfile

import boto3
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from awsglue.utils import getResolvedOptions


# ---------------------------------------------------------------------------
# 1. Read job parameters
# ---------------------------------------------------------------------------
args = getResolvedOptions(sys.argv, [
    'SECRET_NAME',
    'S3_BUCKET',
    'S3_PREFIX',
])

SECRET_NAME = args['SECRET_NAME']
S3_BUCKET   = args['S3_BUCKET']
S3_PREFIX   = args['S3_PREFIX'].rstrip('/') + '/'


# ---------------------------------------------------------------------------
# 2. Retrieve Kaggle credentials from Secrets Manager
# ---------------------------------------------------------------------------
sm_client    = boto3.client('secretsmanager')
secret_value = sm_client.get_secret_value(SecretId=SECRET_NAME)
kaggle_creds = json.loads(secret_value['SecretString'])

KAGGLE_USER = kaggle_creds['username']
KAGGLE_KEY  = kaggle_creds['key']

print(f"[INFO] Kaggle credentials retrieved for user: {KAGGLE_USER}")


# ---------------------------------------------------------------------------
# 3. Download dataset from Kaggle API
# ---------------------------------------------------------------------------
DATASET = "gregorut/videogamesales"
url     = f"https://www.kaggle.com/api/v1/datasets/download/{DATASET}"

print(f"[INFO] Downloading dataset: {DATASET}")

response = requests.get(
    url,
    auth=(KAGGLE_USER, KAGGLE_KEY),
    stream=True,
    timeout=60,
)
response.raise_for_status()

# The response is a ZIP archive - extract in memory
zip_bytes = io.BytesIO(response.content)
with zipfile.ZipFile(zip_bytes) as z:
    csv_filename = [f for f in z.namelist() if f.endswith('.csv')][0]
    print(f"[INFO] CSV found inside ZIP: {csv_filename}")
    with z.open(csv_filename) as csv_file:
        df = pd.read_csv(csv_file, encoding='utf-8')

print(f"[INFO] Rows loaded: {len(df)} | Columns: {list(df.columns)}")


# ---------------------------------------------------------------------------
# 4. Clean and transform
# ---------------------------------------------------------------------------
# Drop rows without name or year
df = df.dropna(subset=['Name', 'Year'])

# Convert Year from float to int (NaN values caused float dtype)
df['Year'] = df['Year'].astype(int)

# Fill missing publisher
df['Publisher'] = df['Publisher'].fillna('Unknown')

# Ensure numeric types for all sales columns
sales_cols = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']
for col in sales_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

print(f"[INFO] Rows after cleaning: {len(df)}")


# ---------------------------------------------------------------------------
# 5. Convert to Parquet and upload to S3
# ---------------------------------------------------------------------------
parquet_buffer = io.BytesIO()
table = pa.Table.from_pandas(df, preserve_index=False)
pq.write_table(table, parquet_buffer, compression='snappy')
parquet_buffer.seek(0)

s3_key = f"{S3_PREFIX}videogames_sales.parquet"
s3_client = boto3.client('s3')
s3_client.put_object(
    Bucket=S3_BUCKET,
    Key=s3_key,
    Body=parquet_buffer.getvalue(),
    ContentType='application/octet-stream',
)

file_size_kb = parquet_buffer.getbuffer().nbytes / 1024
print(f"[SUCCESS] Parquet uploaded to s3://{S3_BUCKET}/{s3_key} ({file_size_kb:.1f} KB)")
