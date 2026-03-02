# 🚀 AWS Auto-Deploy: Static Website with EC2 + Application Load Balancer

<p align="center">
  <img src="https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Boto3-20232A?style=for-the-badge&logoColor=white" alt="Boto3" />
</p>

<p align="center">
  <strong>Automated infrastructure deployment on AWS using Python and Boto3.</strong><br>
  This project provisions a scalable architecture to host a modern static portfolio.
</p>

---

## 🏗️ Architecture Overview
The script automates the creation of:
1.  **Security Groups**: Tiered access (ALB allows HTTP; EC2 allows traffic only from ALB and SSH from your IP).
2.  **EC2 Instance**: Provisioned with Amazon Linux 2023.
3.  **User Data**: Bash script to auto-install Apache, download the **Titan Folio** template, and configure the web server.
4.  **Application Load Balancer (ALB)**: Acts as the entry point, forwarding traffic to the EC2 instance.

---

## 📂 Project Structure

* `deploy_web_ec2_alb.py`: **Main script**. Orchestrates the full infrastructure deployment.
* `upload_to_s3.py`: **Practice script**. A simple utility to upload files to an S3 bucket (great for initial Boto3 testing).

---

## 🛠️ Technologies & Services

* **Language**: Python 3.8+
* **SDK**: Boto3 (AWS SDK for Python)
* **Compute**: Amazon EC2 (t2.micro - Free Tier)
* **Networking**: AWS VPC (Default), Application Load Balancer, Target Groups.
* **Web Server**: Apache (httpd).
* **Template**: [Titan Folio](https://www.tooplate.com/view/2147-titan-folio) by Tooplate.

---

## 🚀 Getting Started

Before running the scripts, ensure you have the following setup:

### 1. AWS Account
You need an active AWS account. If you are using the **Free Tier**, most resources in this project (t2.micro, 750hrs of ALB) will be covered, but stay alert!

### 2. IAM User (Optional but HIGHLY Recommended) 🛡️
For security, do not use your Root account credentials. Create a dedicated IAM user:
* **Name**: `python-admin` (or any name you prefer).
* **Permissions**: Attach the `AdministratorAccess` policy or specific permissions for `EC2`, `ELB`, etc. 
* **Access Type**: Select **Security Credentials** to generate an **Access Key ID** and **Secret Access Key**.

> 

### 3. AWS CLI & Authentication
Install the [AWS CLI](https://aws.amazon.com/cli/) and configure your environment with the previous credentials:

```bash
# Run this command in your terminal
aws configure
```

### Installation & Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/DavidFG16/aws-titanfolio-alb-ec2-boto3.git
   cd aws-titanfolio-alb-ec2-boto3
   ```
2. **Setup Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```
3. **Install Dependencies**
   ```bash
   pip install boto3 requests
   ```
4. **Run Deployment**
   ```bash
   python deploy_web_ec2_alb.py
   ```

## 🌐 Final Result

Once the script finishes, it will output the ALB DNS name. 
Example: `http://titan-folio-alb-123456789.us-east-1.elb.amazonaws.com`

> **Tip**: It may take 1-2 minutes for the ALB health checks to pass. If you see a 503 error initially, just wait a moment for the instance to be marked as 'Healthy'.

---

## 🧹 Clean Up (Cost Awareness)

To avoid unexpected charges, delete the resources in this recommended order (to handle dependencies):

1.  **Terminate the EC2 instance** (This stops the compute costs immediately).
2.  **Delete the Application Load Balancer** (ALBs have a fixed hourly cost).
3.  **Delete the Target Group** (Must be done after the ALB).
4.  **Delete the Security Groups** (Remove the EC2 one first, then the ALB one).
5.  **Delete the Key Pair** (Both the `.pem` file and the entry in the AWS Console).

---

## 🎯 Key Learning Objectives

* **Infrastructure as Code (IaC) Fundamentals**: Replacing manual AWS Console clicks with repeatable Boto3 scripts.
* **Security Layering**: Implementing a "Least Privilege" model by restricting SSH access to a specific public IP and isolating the EC2 instance behind a Load Balancer.
* **Asynchronous Handling**: Using **Waiters** (`get_waiter`) to synchronize Python execution with AWS resource availability.
* **Automated Bootstrapping**: Mastering `UserData` to perform "Day 0" configurations (installing software, fetching templates, and setting permissions) without manual intervention.
* **Resource Interdependency**: Understanding how VPCs, Subnets, Target Groups, and Listeners connect to form a web-facing architecture.