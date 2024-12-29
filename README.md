# Project Title: FDA Approved Drug Submission Data Processor

## Overview

This project is a Python-based AWS Lambda function that processes FDA approved drug submission data. It queries data using the FDA Open API, processes the results, and sends the processed records to an AWS Firehose delivery stream for further analysis or storage. The results are stored in S3, and AWS Glue is used for orchestration and processing, while Athena is used for querying and Grafana for dashboard visualization.

## Features

- Fetches data from the FDA Open API based on specified date ranges.
- Processes and reformats JSON data, including extracting key fields.
- Sends processed data to an Amazon Kinesis Firehose delivery stream.
- Stores results in S3 buckets for further processing and querying.
- Utilizes Parquet tables for optimized data storage and retrieval, ensuring:
  - Faster query performance in Athena due to columnar storage.
  - Reduced storage costs in S3 with compression.
  - nhanced compatibility with various AWS tools.
- Uses AWS Glue for data crawling, transformations, and workflow orchestration.
- Leverages AWS Athena for querying and Grafana for visualization.

## Grafana Dashboard
**[Snapshot](https://vivisanchez.grafana.net/dashboard/snapshot/Mq6bP6tsIyzT458pwjoYJ9Vpan4d2Vsi)**

![image](https://github.com/user-attachments/assets/adb30ce2-bf2a-4e6b-bee9-f514db8ddfbc)

## Data Processing Workflow
![data_ingestion_diagram](https://github.com/user-attachments/assets/77da436a-f987-45bc-bb57-7ba0b0135e60)

## Resources

- **[Postman](https://www.postman.com/)**: Postman is a popular API platform that allows users to interact with APIs by sending HTTP requests, testing endpoints, and visualizing responses. It can be used to efficiently explore and test the FDA API calls before implementing them in your workflow.
- **Example API Call**: The following API call is used to fetch FDA drug approval data for a specific date range with a status of 'Approved' or 'Tentative Approval':

```plaintext
https://api.fda.gov/drug/drugsfda.json?search=(submissions.submission_status_date:[2024-12-01+TO+2024-12-31]+AND+submissions.submission_status:(AP+OR+TA))&limit=1000
```

### Breakdown of the API Call:
- **Base URL**: `https://api.fda.gov/drug/drugsfda.json`
- **Query Parameters**:
  - `search`: Defines the filtering criteria.
    - `submissions.submission_status_date:[2024-12-01+TO+2024-12-31]`: Filters submissions within the specified date range.
    - `submissions.submission_status:(AP+OR+TA)`: Filters submissions with statuses of 'Approved' (`AP`) or 'Tentative Approval' (`TA`).
  - `limit=1000`: Limits the number of records returned in a single request to 1000.

- **[FDA Open API Overview](https://open.fda.gov/apis/drug/drugsfda/)**: Provides comprehensive documentation for accessing FDA drug data via the API.
- **[FDA Drug Approvals Month by Month](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=reportsSearch.process)**: A front-end view of FDA drug approvals organized by month.
- **[FDA Data Status Updates](https://open.fda.gov/about/status/)**: Official updates about the FDA data refresh schedule (typically weekly).

- **[Example API Call](https://api.fda.gov/drug/drugsfda.json?search=(submissions.submission_status_date:[2024-12-01+TO+2024-12-31]+AND+submissions.submission_status:(AP+OR+TA))&limit=1000)**: Used to fetch FDA drug approval data for a specific date range with a status of 'Approved' or 'Tentative Approval'.

- **[FDA Open API Overview](https://open.fda.gov/apis/drug/drugsfda/)**: Provides comprehensive documentation for accessing FDA drug data via the API.
- **[FDA Drug Approvals Month by Month](https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=reportsSearch.process)**: A front-end view of FDA drug approvals organized by month.
- **[FDA Data Status Updates](https://open.fda.gov/about/status/)**: Official updates about the FDA data refresh schedule (typically weekly).

## Requirements

- Python 3.8 or later
- AWS services:
  - Lambda
  - Kinesis Firehose
  - S3
  - Glue
  - Athena
  - Grafana

## Configuration

1. **Set AWS Credentials:** Ensure AWS credentials are configured locally or assigned via an IAM role in AWS Lambda.
2. **Update Constants in Code:**
   - Replace `FIREHOSE_STREAM_NAME` with your actual Firehose delivery stream name.
   - Adjust `URL`, `START_DATE`, and `END_DATE` as needed.
3. **Setup S3 Buckets:**
   - `vs-fda-approved-drugs-2024`: Store raw results from Lambda function.
   - `vs-athena-query-results-first-di-proj-dec-2024`: Cache Athena query results.
   - `vs-fda-approved-drugs-2024-parquet-bucket-1`: Parquet file storage.
   - `parquet-vs-fda-approved-drugs-2024-table-prod-1`: Production Parquet data storage.

## Usage

1. Deploy the Python code to an AWS Lambda function.
   - `vs_fda_approved_drugs_2024_function.py`
3. Configure the Lambda function with an appropriate execution role with permission to access Firehose and S3.
4. Use AWS Glue for crawling, transformations, and workflows:
    - `crawl_vs_fda_approved_drugs`: Crawler name (Schedule: Weekly or On Demand)
   - Use the crawler to catalog the data.
   - Run the workflows for Parquet table creation and cleanup.
     - Jobs:
       - `delete_parquet_fda_approved_drugs_2024_table_s3_athena`: Deletes the parquet S3 files and the Parquet version of the fda table.
       - `create_parquet_fda_approved_drugs_2024_table_glue_job`: Creates a table and refreshes of the Parquet fda data table.
       - `publish_prod_parquet_fda_approved_drugs_2024_table`: Copies the table to a "prod" location appending the date.
     - Triggers:
       - `start_fda_approved_drugs_2024_pqt_pipeline`
       - `delete_parquet_fda_approved_drugs_2024_table_s3_athena`
       - `create_parquet_fda_approved_drugs_2024_table_glue_job`
       - `publish_prod_parquet_fda_approved_drugs_2024_table`
6. Query the data using Athena.
7. Visualize the data in Grafana by connecting it to the Athena data source.

### Notes:
- EventBridge rules can automatically pass a structured payload to the Lambda function when triggered by a schedule.

## Troubleshooting

- **API Errors**: Ensure the FDA API endpoint and query parameters are correct.
- **AWS Firehose Issues**: Verify Firehose permissions and delivery stream configuration.
- **Date Parsing Issues**: Check the format of the `submission_status_date` field.
- **Athena Query Errors**: Verify that the S3 bucket contains the expected data format.
