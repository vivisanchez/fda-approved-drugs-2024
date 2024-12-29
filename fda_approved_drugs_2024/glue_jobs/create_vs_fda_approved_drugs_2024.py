import sys
import boto3

client = boto3.client('athena')

SOURCE_TABLE_NAME = 'fda_vs_fda_approved_drugs_2024'
NEW_TABLE_NAME = 'fda_vs_fda_approved_drugs_2024_parquet_tbl'
NEW_TABLE_S3_BUCKET = 's3://vs-fda-approved-drugs-2024-parquet-bucket-1/'
MY_DATABASE = 'de_proj_database'
QUERY_RESULTS_S3_BUCKET = 's3://vs-athena-query-results-first-di-proj-dec-2024'

# Refresh the table
queryStart = client.start_query_execution(
    QueryString = f"""
    CREATE TABLE {NEW_TABLE_NAME} WITH
    (external_location='{NEW_TABLE_S3_BUCKET}',
    format='PARQUET',
    write_compression='SNAPPY',
    partitioned_by = ARRAY['yr_mo_partition'])
    AS

    SELECT 
        date_parse(submission_status_date, '%Y%m%d') AS "submission_status_date"
        ,application_number
        ,submission_number
        ,submission_type
        ,CASE 
            WHEN submission_status = 'AP' THEN 'APPROVED'
            WHEN submission_status = 'TA' THEN 'TENTATIVE APPROVAL'
            ELSE 'UNKNOWN'
        END AS submission_status
        ,sponsor_name
        ,products
        ,product_type
        ,submission_class_code
        ,submission_class_code_description
        ,manufacturer_name
        ,brand_name
        ,generic_name
        ,route
        ,SUBSTRING(submission_status_date, 1, 6) AS yr_mo_partition
    FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"
    ORDER BY submission_status_date

    ;
    """,
    QueryExecutionContext = {
        'Database': f'{MY_DATABASE}'
    }, 
    ResultConfiguration = { 'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET}'}
)

# list of responses
resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

# get the response
response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

# wait until query finishes
while response["QueryExecution"]["Status"]["State"] not in resp:
    response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])
    
# if it fails, exit and give the Athena error message in the logs
if response["QueryExecution"]["Status"]["State"] == 'FAILED':
    sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])
