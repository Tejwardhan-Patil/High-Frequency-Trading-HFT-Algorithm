import os
import subprocess
import argparse
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path):
    """Load deployment configuration."""
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    
    with open(config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
            logging.info("Deployment configuration loaded successfully.")
            return config
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

def check_prerequisites():
    """Check system prerequisites for deployment."""
    logging.info("Checking system prerequisites...")

    try:
        python_version = subprocess.check_output(["python3", "--version"]).decode().strip()
        logging.info(f"Python version detected: {python_version}")
    except subprocess.CalledProcessError:
        raise EnvironmentError("Python 3 is required for the deployment.")

    try:
        docker_version = subprocess.check_output(["docker", "--version"]).decode().strip()
        logging.info(f"Docker version detected: {docker_version}")
    except subprocess.CalledProcessError:
        raise EnvironmentError("Docker is required for the deployment.")
    
    try:
        docker_compose_version = subprocess.check_output(["docker-compose", "--version"]).decode().strip()
        logging.info(f"Docker Compose version detected: {docker_compose_version}")
    except subprocess.CalledProcessError:
        raise EnvironmentError("Docker Compose is required for the deployment.")

def setup_docker_environment(config):
    """Set up the Docker environment."""
    logging.info("Setting up Docker environment...")

    dockerfile_dir = config['docker']['dockerfile_dir']
    image_name = config['docker']['image_name']
    container_name = config['docker']['container_name']

    # Build Docker image
    build_cmd = f"docker build -t {image_name} {dockerfile_dir}"
    logging.info(f"Running command: {build_cmd}")
    try:
        subprocess.check_call(build_cmd, shell=True)
        logging.info(f"Docker image {image_name} built successfully.")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to build Docker image {image_name}.")

    # Run Docker container
    run_cmd = f"docker run -d --name {container_name} {image_name}"
    logging.info(f"Running command: {run_cmd}")
    try:
        subprocess.check_call(run_cmd, shell=True)
        logging.info(f"Docker container {container_name} started successfully.")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to run Docker container {container_name}.")

    # Check Docker container status
    status_cmd = f"docker ps -f name={container_name} --format '{{{{.Status}}}}'"
    status = subprocess.check_output(status_cmd, shell=True).decode().strip()
    if "Up" in status:
        logging.info(f"Container {container_name} is running.")
    else:
        raise RuntimeError(f"Container {container_name} failed to start properly.")

def configure_network(config):
    """Configure network settings for on-premise deployment."""
    logging.info("Configuring network settings...")

    network_config = config['network']
    network_name = network_config['name']

    # Create Docker network if it doesn't exist
    check_network_cmd = f"docker network ls --filter name={network_name} --format '{{{{.Name}}}}'"
    existing_networks = subprocess.check_output(check_network_cmd, shell=True).decode().strip()
    if network_name not in existing_networks:
        create_network_cmd = f"docker network create {network_name}"
        logging.info(f"Running command: {create_network_cmd}")
        try:
            subprocess.check_call(create_network_cmd, shell=True)
            logging.info(f"Network {network_name} created.")
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to create network {network_name}.")
    else:
        logging.info(f"Network {network_name} already exists.")

def deploy_services(config):
    """Deploy core HFT services."""
    logging.info("Deploying core services...")

    services = config['services']
    for service in services:
        container_name = service['container_name']
        service_cmd = f"docker-compose up -d {container_name}"
        
        logging.info(f"Deploying service {container_name} with command: {service_cmd}")
        try:
            subprocess.check_call(service_cmd, shell=True)
            logging.info(f"Service {container_name} deployed successfully.")
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to deploy service {container_name}.")

        # Check service status
        status_cmd = f"docker ps -f name={container_name} --format '{{{{.Status}}}}'"
        status = subprocess.check_output(status_cmd, shell=True).decode().strip()
        if "Up" in status:
            logging.info(f"Service {container_name} is running.")
        else:
            logging.warning(f"Service {container_name} may not have started correctly.")

def configure_monitoring(config):
    """Set up monitoring and alerting."""
    logging.info("Setting up performance monitoring...")

    monitoring_tool = config['monitoring']['tool']
    setup_cmd = config['monitoring']['setup_command']
    
    logging.info(f"Setting up monitoring tool {monitoring_tool} with command: {setup_cmd}")
    try:
        subprocess.check_call(setup_cmd, shell=True)
        logging.info(f"Monitoring tool {monitoring_tool} configured successfully.")
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to set up monitoring tool {monitoring_tool}.")

def cleanup_logs():
    """Clean up logs from the previous deployments."""
    logging.info("Cleaning up old logs...")

    logs_path = Path("/var/log/hft_deployment/")
    if logs_path.exists() and logs_path.is_dir():
        for log_file in logs_path.glob("*.log"):
            try:
                log_file.unlink()
                logging.info(f"Removed log file: {log_file}")
            except Exception as e:
                logging.warning(f"Failed to remove log file {log_file}: {e}")
    else:
        logging.info("No old logs found to clean.")

def backup_existing_containers():
    """Backup existing containers before deployment."""
    logging.info("Backing up existing containers...")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_cmd = f"docker ps -q | xargs -I {{}} docker commit {{}} hft_backup_{timestamp}_{{}}"
    try:
        subprocess.check_call(backup_cmd, shell=True)
        logging.info(f"All running containers backed up with timestamp {timestamp}.")
    except subprocess.CalledProcessError:
        logging.warning("Failed to back up some containers.")

def verify_configuration(config):
    """Verify the loaded configuration for missing or incorrect values."""
    logging.info("Verifying deployment configuration...")

    required_keys = ['docker', 'network', 'services', 'monitoring']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing key in configuration: {key}")

    docker_keys = ['dockerfile_dir', 'image_name', 'container_name']
    for key in docker_keys:
        if key not in config['docker']:
            raise ValueError(f"Missing Docker configuration key: {key}")
    
    logging.info("Configuration verified successfully.")

def main(config_path):
    """Main deployment workflow."""
    logging.info("Starting on-premise deployment...")

    # Load deployment configuration
    config = load_config(config_path)

    # Verify configuration
    verify_configuration(config)

    # Backup existing containers
    backup_existing_containers()

    # Check prerequisites
    check_prerequisites()

    # Set up Docker environment
    setup_docker_environment(config)

    # Configure network
    configure_network(config)

    # Deploy HFT services
    deploy_services(config)

    # Set up monitoring
    configure_monitoring(config)

    # Clean up old logs
    cleanup_logs()

    logging.info("On-premise deployment completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy HFT System on On-Premise Server")
    parser.add_argument("--config", type=str, required=True, help="Path to deployment configuration file")
    
    args = parser.parse_args()
    main(args.config)