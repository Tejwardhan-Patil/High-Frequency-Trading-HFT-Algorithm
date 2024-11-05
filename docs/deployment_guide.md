# Deployment Guide

## Overview

The HFT system supports deployment in cloud and on-premise environments using Docker and Infrastructure-as-Code tools. The system can be deployed with minimal latency for optimized performance.

### Deployment Options

1. **Cloud Deployment**:
   - The system can be deployed on AWS or Google Cloud Platform.
   - Deployment scripts for AWS: `deployment/scripts/deploy_aws.py`.
   - Deployment scripts for GCP: `deployment/scripts/deploy_gcp.py`.

2. **On-Premise Deployment**:
   - For environments requiring dedicated hardware, an on-premise deployment script is provided.
   - File: `deployment/scripts/deploy_on_premise.py`.

### Docker Setup

1. **Docker Container**:
   - The system is containerized using Docker for easy deployment across environments.
   - Dockerfile: `deployment/docker/Dockerfile`.

2. **Docker Compose**:
   - Orchestrates multiple services (e.g., market data feed, execution engine).
   - File: `deployment/docker/docker-compose.yml`.

### Infrastructure as Code (IaC)

- Terraform scripts are provided for setting up infrastructure on AWS.
  - Main script: `deployment/infrastructure_as_code/main.tf`.
  - Variables: `deployment/infrastructure_as_code/variables.tf`.
  - Outputs: `deployment/infrastructure_as_code/outputs.tf`.
