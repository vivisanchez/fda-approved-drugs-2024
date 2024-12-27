import json
import urllib3
import boto3
from datetime import datetime, timedelta

# Function to generate date ranges for one-month intervals
def generate_date_ranges(start_date, end_date):
    date_ranges = []
    current_start = start_date
    while current_start < end_date:
        current_end = current_start + timedelta(days=30)  # One-month range
        if current_end > end_date:
            current_end = end_date
        date_ranges.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)
    return date_ranges

# Function to fetch data for a specific date range
def fetch_data(url, date_range):
    http = urllib3.PoolManager()
    all_results = []
    start_date = date_range[0].strftime('%Y-%m-%d')
    end_date = date_range[1].strftime('%Y-%m-%d')
    query = f"search=(submissions.submission_status_date:[{start_date}+TO+{end_date}]+AND+submissions.submission_status:(AP+OR+TA))&limit=1000"
    response = http.request('GET', f"{url}?{query}")
    if response.status == 200:
        data = json.loads(response.data.decode('utf-8'))
        all_results.extend(data.get('results', []))
    else:
        print(f"Failed to fetch data: {response.status}")
        print(f"Failed to fetch data: {query}")
    return all_results

# Firehose configuration
FIREHOSE_STREAM_NAME = "PUT-S3-R4n3z"

# Constants
URL = "https://api.fda.gov/drug/drugsfda.json"
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

def lambda_handler(event, context):
    # Generate date ranges for one-month intervals
    date_ranges = generate_date_ranges(START_DATE, END_DATE)

    # Fetch data for all date ranges
    data = []
    for date_range in date_ranges:
        data.extend(fetch_data(URL, date_range))

    # Initialize the Firehose client
    firehose = boto3.client('firehose')

    # Process the JSON data
    for entry in data:
        application_number = entry.get('application_number', 'N/A')
        sponsor_name = entry.get('sponsor_name', 'N/A')
        products = ', '.join([prod.get('brand_name', 'Unknown') for prod in entry.get('products', [])])

        # Extract openFDA fields
        openfda = entry.get('openfda', {})
        brand_name = ', '.join(openfda.get('brand_name', ['N/A']))
        generic_name = ', '.join(openfda.get('generic_name', ['N/A']))
        manufacturer_name = ', '.join(openfda.get('manufacturer_name', ['N/A']))
        product_type = ', '.join(openfda.get('product_type', ['N/A']))
        route = ', '.join(openfda.get('route', ['N/A']))

        for submission in entry.get('submissions', []):
            submission_status_date = submission.get('submission_status_date', '')
            
            # Filter submissions where the date starts with 2024
            if submission_status_date.startswith('2024'):
                # Collect all submission details
                submission_type = submission.get('submission_type', 'N/A')
                submission_number = submission.get('submission_number', 'N/A')
                submission_status = submission.get('submission_status', 'N/A')
                submission_class_code = submission.get('submission_class_code', 'N/A')
                submission_class_code_description = submission.get('submission_class_code_description', 'N/A')

                # Create the formatted output
                record = {
                    "submission_status_date": submission_status_date,
                    "application_number": application_number,
                    "submission_number": submission_number,
                    "submission_type": submission_type,
                    "submission_status": submission_status,
                    "sponsor_name": sponsor_name,
                    "products": products,
                    "product_type": product_type,
                    "submission_class_code": submission_class_code,
                    "submission_class_code_description": submission_class_code_description,
                    "manufacturer_name": manufacturer_name,
                    "brand_name": brand_name,
                    "generic_name": generic_name,
                    "route": route
                }

                # Send record to Firehose
                firehose.put_record(
                    DeliveryStreamName=FIREHOSE_STREAM_NAME,
                    Record={"Data": json.dumps(record) + "\n"}
                )

    return {
        "statusCode": 200,
        "body": "Data successfully sent to Firehose stream."
    }