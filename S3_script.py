import boto3
import os

# This variable allow us to use the AWS credentials 
# stored in the environment to access AWS services, in this case S3 
s3 = boto3.client('s3')

# This line creates a new S3 bucket named 'botopython0912' 
# using the create_bucket method of the S3 client.
s3.create_bucket(Bucket='botopython0912')

s3.upload_file('solarsystem.txt', 'botopython0912', 'solarsystem.txt')

