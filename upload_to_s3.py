#!/usr/bin/env python
import boto3
import os

# This variable allow us to use the AWS credentials 
# stored in the environment to access AWS services, in this case S3 
s3 = boto3.client('s3')

# Define the bucket name and the file to upload
bucket_name = 'botopython0912'
file_name = input("Enter the path of the file you want to upload: ") # File to upload
object_name = file_name # S3 object name

# Upload the file to S3
try:
    s3.upload_file(file_name, bucket_name, object_name)
    print(f'File {file_name} uploaded to bucket {bucket_name} as {object_name}')
except Exception as e:
    print(f'Error uploading file: {e}')