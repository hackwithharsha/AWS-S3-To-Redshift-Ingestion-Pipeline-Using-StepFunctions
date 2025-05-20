# AWS `S3 To Redshift` - Ingestion Pipeline Using Step Functions

A serverless data pipeline that automatically ingests customer data into Amazon Redshift when files arrive in S3.

The pipeline ensures ACID-compliant data replacement by truncating existing data and performing atomic `COPY` operations.

It leverages `AWS Step Functions`, `Lambda`, and `Redshift Data API` to handle large files, monitor job status, and send branded success/failure email notifications using `Amazon SES`.

### Key Features

* **Auto-triggered** on file upload to S3
* **Scalable ingestion** into Amazon Redshift Data API using `COPY`
* **Polling pattern** with Step Functions for long-running operations
* **ACID-compliant**: safely truncates and replaces data
* **HTML email notifications** via SES

---

Install `awscli` if you haven't already to proceed with following steps.

And then run `aws configure` to configure awscli with `secret key` and `access key`.

### Sample Data Generation

Generate sample data using Python script `main.py`. This script create `customer.csv` file around `50MB`.

Install the dependencies listed in the `requirements.txt` file. You can do this using pip:

```bash
>>> python3 -m pip install -r requirements.txt
```

Then run the script:

```bash
>>> python3 main.py
```

### Amazon S3 Bucket

Create an `S3 Bucket` to store the generated files. You can do this using the `awscli`.

```bash
>>> aws s3 mb s3://hack-with-harsha-sales-data2
```

Upload the generated `customer.csv` file to the S3 bucket. You can do this using the `awscli`.

```bash
>>> aws s3 cp customer.csv s3://hack-with-harsha-sales-data2/customer/
```

### Create `AWS Redshift Cluster`

```bash
>>> aws redshift create-cluster \
    --cluster-identifier customer-analytics \
    --node-type dc2.large \
    --number-of-nodes 2 \
    --master-username admin \
    --master-user-password testPassword123 \
    --db-name customer
```

Create default vpc if required

```bash
>>> aws ec2 create-default-vpc
```

Create a following table through `AWS Redshift Query Editor v2`

```sql
CREATE TABLE customer_data (
    order_id   VARCHAR(36)          NOT NULL,
    order_date DATE          NOT NULL,
    country    VARCHAR(100)  NOT NULL,
    amount     DECIMAL(12,2) NOT NULL,
    currency   VARCHAR(10)   NOT NULL
)
DISTKEY (country)
SORTKEY (order_date);
```

Create IAM role for `Redshift` to access `S3` bucket.

```bash
>>> aws iam create-role \
  --role-name RedshiftCopyRole \
  --assume-role-policy-document file://trust-policy.json
```

Add `policy` to the role.

```bash
aws iam put-role-policy \
  --role-name RedshiftCopyRole \
  --policy-name RedshiftS3ReadPolicy \
  --policy-document file://s3-read-policy.json
```

Attach the IAM role to our Redshift cluster, Replace `<your-account-id>` with your actual AWS account ID.

```bash
>>> aws redshift modify-cluster-iam-roles \
    --cluster-identifier customer-analytics \
    --add-iam-roles arn:aws:iam::<your-account-id>:role/RedshiftCopyRole
```

Use `Copy` command to load data into `Redshift` table from `S3` bucket.

```sql
COPY customer_data
FROM 's3://hack-with-harsha-sales-data2/customer/customer.csv'
IAM_ROLE 'arn:aws:iam::<your-account-id>:role/RedshiftCopyRole'
FORMAT AS CSV
IGNOREHEADER 1
REGION 'us-east-1';
```

In the above command, replace `<your-account-id>` with your actual AWS account ID.

---

> So Far, we have created a `Redshift` cluster and loaded data into it using `COPY` command. Now we will create a `Step Function` to automate the process of loading data into `Redshift` when a file is uploaded to `S3`.

### Create `AWS Step Function`

Use `step-function.json` file to create a `Step Function` state machine.

And then attach `redshift-policy.json` policy to the `Step Function` role as `inline-policy`.

### AWS Event Bridge

Create an `Event Bridge` rule to trigger the `Step Function` when a file is uploaded to `S3`.

```bash
>>> aws events put-rule \
  --name TriggerStepFunctionOnS3Upload \
  --event-pattern file://s3-event-pattern.json \
  --state ENABLED
```
