import boto3
import requests
import time

region = "us-east-1"
template_name = "titan-folio-tooplate"

ec2 = boto3.client("ec2", region_name=region)
elbv2 = boto3.client("elbv2", region_name=region)

# 1. Get My Public IP
my_ip = requests.get("https://api.ipify.org").text
print(f"My IP detected: {my_ip}")

# 2. Create Key Pair
key_name = f"{template_name}-key"
key_pair = ec2.create_key_pair(KeyName=key_name)

with open(f"{key_name}.pem", "w") as file:
    file.write(key_pair["KeyMaterial"])

print("Key pair created.")

# 3. Get default VPC
vpc_id = ec2.describe_vpcs()["Vpcs"][0]["VpcId"]

# 4. Create Security Group for EC2
ec2_sg = ec2.create_security_group(
    GroupName=f"{template_name}-ec2-sg",
    Description="EC2 Security Group",
    VpcId=vpc_id
)

ec2.authorize_security_group_ingress(
    GroupId=ec2_sg["GroupId"],
    IpPermissions=[
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": f"{my_ip}/32"}]
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
        }
    ]
)

print("EC2 Security Group created.")

# 5. Create Security Group for ALB
alb_sg = ec2.create_security_group(
    GroupName=f"{template_name}-alb-sg",
    Description="ALB Security Group",
    VpcId=vpc_id
)

ec2.authorize_security_group_ingress(
    GroupId=alb_sg["GroupId"],
    IpPermissions=[
        {
            "IpProtocol": "tcp",
            "FromPort": 80,
            "ToPort": 80,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
        }
    ]
)

print("ALB Security Group created.")

# 6. Get latest Amazon Linux 2023 AMI
images = ec2.describe_images(
    Owners=["amazon"],
    Filters=[
        {"Name": "name", "Values": ["al2023-ami-*-x86_64"]},
        {"Name": "state", "Values": ["available"]}
    ]
)["Images"]

ami_id = sorted(images, key=lambda x: x["CreationDate"], reverse=True)[0]["ImageId"]

# 7. User Data Script for Titan Folio
user_data_script = """#!/bin/bash
dnf update -y
dnf install -y httpd unzip wget

systemctl start httpd
systemctl enable httpd

cd /tmp
wget https://www.tooplate.com/zip-templates/2147_titan_folio.zip
unzip 2147_titan_folio.zip

# Remove default Apache content
rm -rf /var/www/html/*

# Copy template content to Apache root directory 
cp -r 2147_titan_folio/* /var/www/html/

# Set correct permissions
chown -R apache:apache /var/www/html
chmod -R 755 /var/www/html

# Restart Apache
systemctl restart httpd
"""

# 8. Get all subnets (for ALB across all AZs)
subnets = ec2.describe_subnets()["Subnets"]
subnet_ids = [sub["SubnetId"] for sub in subnets]

# Use first subnet for EC2
instance_subnet = subnet_ids[0]

# 9. Launch EC2
instance = ec2.run_instances(
    ImageId=ami_id,
    InstanceType="t2.micro",
    KeyName=key_name,
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[ec2_sg["GroupId"]],
    SubnetId=instance_subnet,
    UserData=user_data_script,
    TagSpecifications=[
        {
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": template_name}]
        }
    ]
)

instance_id = instance["Instances"][0]["InstanceId"]
print(f"Instance launched: {instance_id}")

ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])

# 10. Create ALB
alb = elbv2.create_load_balancer(
    Name=f"{template_name}-alb",
    Subnets=subnet_ids,
    SecurityGroups=[alb_sg["GroupId"]],
    Scheme="internet-facing",
    Type="application",
    IpAddressType="ipv4",
    Tags=[{"Key": "Name", "Value": template_name}]
)

alb_arn = alb["LoadBalancers"][0]["LoadBalancerArn"]
alb_dns = alb["LoadBalancers"][0]["DNSName"]

# 11. Create Target Group
tg = elbv2.create_target_group(
    Name=f"{template_name}-tg",
    Protocol="HTTP",
    Port=80,
    VpcId=vpc_id,
    TargetType="instance",
    HealthCheckPath="/"
)

tg_arn = tg["TargetGroups"][0]["TargetGroupArn"]

# Register instance
elbv2.register_targets(
    TargetGroupArn=tg_arn,
    Targets=[{"Id": instance_id}]
)

# 12. Create Listener
elbv2.create_listener(
    LoadBalancerArn=alb_arn,
    Protocol="HTTP",
    Port=80,
    DefaultActions=[{
        "Type": "forward",
        "TargetGroupArn": tg_arn
    }]
)

print("\n=== DEPLOYMENT COMPLETE ===")
print(f"Access your site via ALB:")
print(f"http://{alb_dns}")
