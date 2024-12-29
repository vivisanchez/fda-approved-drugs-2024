
-- Time Series: 2024 - FDA-Approved Drugs
SELECT
  CAST(DATE_ADD('hour', 5, PARSE_DATETIME(submission_status_date, 'yyyyMMdd')) AS TIMESTAMP) AS time,
  COUNT(*) AS approved_cases
FROM fda_vs_fda_approved_drugs_2024_parquet_tbl_prod_2024_12_29_05_34_27_007366
WHERE $__timeFilter(CAST(DATE_ADD('hour', 5, PARSE_DATETIME(submission_status_date, 'yyyyMMdd')) AS TIMESTAMP))
GROUP BY CAST(DATE_ADD('hour', 5, PARSE_DATETIME(submission_status_date, 'yyyyMMdd')) AS TIMESTAMP)
ORDER BY CAST(DATE_ADD('hour', 5, PARSE_DATETIME(submission_status_date, 'yyyyMMdd')) AS TIMESTAMP);


-- Bar chart: Approvals by License Application
SELECT 
    CASE 
        WHEN REGEXP_EXTRACT(application_number, '^[A-Za-z]+') = 'NDA' THEN 'New Drug Application (NDA)'
        WHEN REGEXP_EXTRACT(application_number, '^[A-Za-z]+') = 'ANDA' THEN 'Abbreviated New Drug Application (ANDA)'
        WHEN REGEXP_EXTRACT(application_number, '^[A-Za-z]+') = 'BLA' THEN 'Biologic License Application (BLA)'
        ELSE REGEXP_EXTRACT(application_number, '^[A-Za-z]+')
    END AS application_prefix, 
    COUNT(DISTINCT application_number) AS total_count
FROM fda_vs_fda_approved_drugs_2024_parquet_tbl_prod_2024_12_29_05_34_27_007366
WHERE REGEXP_EXTRACT(application_number, '^[A-Za-z]+') IS NOT NULL
GROUP BY 
    CASE 
        WHEN REGEXP_EXTRACT(application_number, '^[A-Za-z]+') = 'NDA' THEN 'New Drug Application (NDA)'
        WHEN REGEXP_EXTRACT(application_number, '^[A-Za-z]+') = 'ANDA' THEN 'Abbreviated New Drug Application (ANDA)'
        WHEN REGEXP_EXTRACT(application_number, '^[A-Za-z]+') = 'BLA' THEN 'Biologic License Application (BLA)'
        ELSE REGEXP_EXTRACT(application_number, '^[A-Za-z]+')
    END
ORDER BY total_count DESC;

-- Bar Chart: Top 50 Manufacturers
SELECT 
  COUNT(*) AS total_cases
  ,manufacturer_name
FROM fda_vs_fda_approved_drugs_2024_parquet_tbl_prod_2024_12_29_05_34_27_007366
WHERE manufacturer_name != 'N/A'
GROUP BY manufacturer_name
ORDER BY total_cases DESC
LIMIT 50;

-- Bar Chart: Top 50 Companies
SELECT 
    sponsor_name, 
    COUNT(CASE WHEN submission_status = 'APPROVED' THEN 1 END) AS "Approved",
    COUNT(CASE WHEN submission_status = 'TENTATIVE APPROVAL' THEN 1 END) AS "Tentative Approval"
FROM fda_vs_fda_approved_drugs_2024_parquet_tbl_prod_2024_12_29_05_34_27_007366
GROUP BY sponsor_name
ORDER BY "Approved" DESC, "Tentative Approval" DESC
LIMIT 50;

-- Bar Gauge: Submission Class Code Distribution
SELECT 
    CASE 
        WHEN submission_class_code_description = 'N/A' THEN 'Not Specified'
        ELSE submission_class_code_description
    END AS submission_class_code_description, 
    COUNT(*) AS total_count
FROM fda_vs_fda_approved_drugs_2024_parquet_tbl_prod_2024_12_29_05_34_27_007366
GROUP BY 
    CASE 
        WHEN submission_class_code_description = 'N/A' THEN 'Not Specified'
        ELSE submission_class_code_description
    END
ORDER BY total_count DESC;

-- Bar Gauge: Route of Administration
SELECT 
    CASE 
        WHEN route = 'N/A' THEN 'NOT SPECIFIED'
        ELSE route
    END AS route, 
    COUNT(*) AS total_count
FROM fda_vs_fda_approved_drugs_2024_parquet_tbl_prod_2024_12_29_05_34_27_007366
GROUP BY 
    CASE 
        WHEN route = 'N/A' THEN 'NOT SPECIFIED'
        ELSE route
    END
ORDER BY total_count DESC;