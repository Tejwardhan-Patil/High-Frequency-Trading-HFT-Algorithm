import os
import subprocess
import time
import google.auth
import logging
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# Constants
PROJECT_ID = "gcp-project-id"
ZONE = "zone"
MACHINE_TYPE = "n1-standard-4"
INSTANCE_NAME = "hft-system-instance"
IMAGE_FAMILY = "debian-10"
IMAGE_PROJECT = "debian-cloud"
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
FIREWALL_NAME = "allow-ssh"
SSH_USER = "gcp-user"

# Path to the service account key file
SERVICE_ACCOUNT_FILE = "/service_account.json"

# Configure logging
logging.basicConfig(filename="deploy_gcp.log", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def authenticate_gcp():
    """Authenticate to Google Cloud using service account."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        logging.info("Successfully authenticated to GCP.")
        return credentials
    except Exception as e:
        logging.error(f"Failed to authenticate to GCP: {str(e)}")
        raise

def create_compute_engine(credentials):
    """Creates a Google Compute Engine instance for the HFT system."""
    compute = build('compute', 'v1', credentials=credentials)
    
    config = {
        'name': INSTANCE_NAME,
        'machineType': f"zones/{ZONE}/machineTypes/{MACHINE_TYPE}",
        'disks': [{
            'boot': True,
            'autoDelete': True,
            'initializeParams': {
                'sourceImage': f"projects/{IMAGE_PROJECT}/global/images/family/{IMAGE_FAMILY}"
            }
        }],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}]
        }]
    }

    try:
        operation = compute.instances().insert(
            project=PROJECT_ID,
            zone=ZONE,
            body=config
        ).execute()
        
        logging.info(f"Instance creation started: {operation['name']}")
        return operation
    except HttpError as e:
        logging.error(f"Failed to create instance: {str(e)}")
        raise

def create_firewall_rule(credentials):
    """Creates a firewall rule to allow SSH access."""
    compute = build('compute', 'v1', credentials=credentials)
    
    firewall_body = {
        "name": FIREWALL_NAME,
        "allowed": [{
            "IPProtocol": "tcp",
            "ports": ["22"]
        }],
        "direction": "INGRESS",
        "sourceRanges": ["0.0.0.0/0"],
        "targetTags": [INSTANCE_NAME]
    }

    try:
        firewall = compute.firewalls().insert(
            project=PROJECT_ID,
            body=firewall_body
        ).execute()
        
        logging.info(f"Firewall rule {FIREWALL_NAME} created.")
        return firewall
    except HttpError as e:
        logging.error(f"Failed to create firewall rule: {str(e)}")
        raise

def check_instance_status(compute, instance_name):
    """Check the status of the instance."""
    try:
        result = compute.instances().get(
            project=PROJECT_ID,
            zone=ZONE,
            instance=instance_name
        ).execute()

        status = result.get('status')
        logging.info(f"Instance {instance_name} status: {status}")
        return status
    except HttpError as e:
        logging.error(f"Error checking instance status: {str(e)}")
        raise

def wait_for_operation(compute, operation):
    """Waits for the operation to complete."""
    print(f"Waiting for operation {operation['name']} to complete...")
    while True:
        result = compute.zoneOperations().get(
            project=PROJECT_ID,
            zone=ZONE,
            operation=operation['name']
        ).execute()

        if result['status'] == 'DONE':
            logging.info(f"Operation {operation['name']} completed.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(5)

def ssh_into_instance():
    """SSH into the instance to configure the system."""
    instance_ip = get_instance_external_ip()
    if instance_ip:
        command = f"gcloud compute ssh {SSH_USER}@{INSTANCE_NAME} --zone {ZONE} --project {PROJECT_ID}"
        logging.info(f"Attempting SSH connection to {INSTANCE_NAME} at {instance_ip}")
        try:
            subprocess.run(command, shell=True, check=True)
            logging.info("SSH connection successful.")
        except subprocess.CalledProcessError as e:
            logging.error(f"SSH connection failed: {str(e)}")
            raise

def get_instance_external_ip():
    """Get the external IP address of the instance."""
    compute = build('compute', 'v1', credentials=authenticate_gcp())
    try:
        instance_info = compute.instances().get(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        ).execute()
        
        external_ip = instance_info['networkInterfaces'][0]['accessConfigs'][0]['natIP']
        logging.info(f"External IP of instance {INSTANCE_NAME}: {external_ip}")
        return external_ip
    except HttpError as e:
        logging.error(f"Failed to get external IP: {str(e)}")
        raise

def delete_instance():
    """Deletes the GCP instance to free resources."""
    compute = build('compute', 'v1', credentials=authenticate_gcp())
    try:
        operation = compute.instances().delete(
            project=PROJECT_ID,
            zone=ZONE,
            instance=INSTANCE_NAME
        ).execute()

        wait_for_operation(compute, operation)
        logging.info(f"Instance {INSTANCE_NAME} deleted successfully.")
    except HttpError as e:
        logging.error(f"Failed to delete instance: {str(e)}")
        raise

def deploy_hft_system():
    """Deploy the HFT system on the newly created GCP instance."""
    credentials = authenticate_gcp()
    
    compute = build('compute', 'v1', credentials=credentials)
    
    # Step 1: Create a GCP instance
    operation = create_compute_engine(credentials)
    wait_for_operation(compute, operation)
    
    # Step 2: Create firewall rule to allow SSH
    create_firewall_rule(credentials)
    
    # Step 3: Check instance status
    status = check_instance_status(compute, INSTANCE_NAME)
    if status != "RUNNING":
        logging.error(f"Instance {INSTANCE_NAME} is not running.")
        return
    
    # Step 4: SSH into the instance to deploy the system
    ssh_into_instance()

    logging.info("HFT system deployment completed on GCP.")

if __name__ == "__main__":
    try:
        deploy_hft_system()
    except Exception as e:
        logging.error(f"Deployment failed: {str(e)}")
        print(f"Deployment failed. Check logs for details.")