import boto3
import paramiko
import time
import os
import logging
from botocore.exceptions import ClientError

# Configuration
AMI_ID = os.getenv('HFT_AMI_ID', 'ami-0abcdef1234567890')  
INSTANCE_TYPE = os.getenv('HFT_INSTANCE_TYPE', 'c5n.large')  
KEY_NAME = os.getenv('HFT_KEY_NAME', 'hft-key-pair')
SECURITY_GROUP = os.getenv('HFT_SECURITY_GROUP', 'hft-security-group')
REGION = os.getenv('HFT_REGION', 'us-east-1') 
TAG = [{'Key': 'Name', 'Value': 'HFT-System'}]

# Logging Setup
LOG_FILE = 'deploy_aws.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

def create_security_group():
    """Create and configure security group for HFT system."""
    try:
        logging.info('Creating security group...')
        response = ec2_client.create_security_group(
            GroupName=SECURITY_GROUP,
            Description='Security group for HFT deployment'
        )
        security_group_id = response['GroupId']
        logging.info(f'Security Group Created: {security_group_id}')
        
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8080,
                    'ToPort': 8080,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        logging.info(f'Security Group {security_group_id} configured with ingress rules.')
        return security_group_id

    except ClientError as e:
        logging.error(f"Failed to create security group: {e}")
        return None

def launch_instance(security_group_id):
    """Launch EC2 instance with specified configurations."""
    try:
        logging.info('Launching EC2 instance...')
        instance = ec2_client.run_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            SecurityGroupIds=[security_group_id],
            MaxCount=1,
            MinCount=1,
            TagSpecifications=[{'ResourceType': 'instance', 'Tags': TAG}]
        )
        instance_id = instance['Instances'][0]['InstanceId']
        logging.info(f'Instance launched: {instance_id}')
        return instance_id

    except ClientError as e:
        logging.error(f"Failed to launch EC2 instance: {e}")
        return None

def wait_for_instance(instance_id):
    """Wait for the instance to be in running state."""
    logging.info(f'Waiting for instance {instance_id} to start...')
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    logging.info(f'Instance {instance_id} is running.')

def get_instance_public_ip(instance_id):
    """Retrieve the public IP of the running instance."""
    try:
        logging.info(f'Fetching public IP of instance {instance_id}...')
        instance_info = ec2_client.describe_instances(InstanceIds=[instance_id])
        public_ip = instance_info['Reservations'][0]['Instances'][0]['PublicIpAddress']
        logging.info(f'Instance public IP: {public_ip}')
        return public_ip
    except ClientError as e:
        logging.error(f"Failed to get public IP: {e}")
        return None

def deploy_hft_code(instance_ip):
    """Deploy HFT code onto the AWS instance."""
    try:
        logging.info(f'Starting deployment on instance {instance_ip}...')
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key_file = os.getenv('HFT_KEY_FILE', '/private-key.pem')
        private_key = paramiko.RSAKey.from_private_key_file(key_file)

        ssh_client.connect(hostname=instance_ip, username='ec2-user', pkey=private_key)
        logging.info('Connected to the instance via SSH.')

        # Install necessary dependencies
        stdin, stdout, stderr = ssh_client.exec_command('sudo yum update -y')
        stdout.channel.recv_exit_status()
        logging.info('System updated.')

        stdin, stdout, stderr = ssh_client.exec_command('sudo yum install -y docker git')
        stdout.channel.recv_exit_status()
        logging.info('Docker and Git installed.')

        # Start Docker service
        ssh_client.exec_command('sudo service docker start')
        logging.info('Docker service started.')

        # Clone the HFT system repository
        ssh_client.exec_command('git clone https://github.com/hft-repo/hft-system.git')
        logging.info('HFT system repository cloned.')

        # Start the Docker containers for HFT system
        ssh_client.exec_command('cd hft-system && docker-compose up -d')
        logging.info('Docker containers started.')

    except paramiko.SSHException as ssh_error:
        logging.error(f"SSH connection failed: {ssh_error}")
    except Exception as e:
        logging.error(f"Deployment failed: {e}")
    finally:
        ssh_client.close()
        logging.info('SSH connection closed.')

def terminate_instance(instance_id):
    """Terminate the EC2 instance after deployment."""
    try:
        logging.info(f'Terminating instance {instance_id}...')
        ec2_client.terminate_instances(InstanceIds=[instance_id])
        logging.info(f'Instance {instance_id} terminated.')
    except ClientError as e:
        logging.error(f"Failed to terminate instance: {e}")

def deploy():
    """Main function for AWS deployment of HFT system."""
    logging.info('Starting AWS deployment process...')
    security_group_id = create_security_group()

    if security_group_id:
        instance_id = launch_instance(security_group_id)
        if instance_id:
            wait_for_instance(instance_id)
            instance_ip = get_instance_public_ip(instance_id)
            if instance_ip:
                deploy_hft_code(instance_ip)
                logging.info(f'Deployment completed for instance {instance_ip}.')
            else:
                logging.error('Public IP retrieval failed, deployment aborted.')
        else:
            logging.error('Instance launch failed, deployment aborted.')
    else:
        logging.error('Security group creation failed, deployment aborted.')

    # Optional instance termination (for testing or non-persistent environments)
    terminate_after_deploy = os.getenv('TERMINATE_AFTER_DEPLOY', 'false').lower() == 'true'
    if terminate_after_deploy:
        terminate_instance(instance_id)

if __name__ == '__main__':
    # Initialize AWS EC2 client
    ec2_client = boto3.client('ec2', region_name=REGION)

    deploy()