# Define region variable
variable "region" {
  description = "The region where the infrastructure will be deployed"
  type        = string
  default     = "us-west-1"
}

# Define the AWS Key Pair
variable "key_name" {
  description = "Name of the AWS key pair to use for EC2 instances"
  type        = string
  default     = "hft-keypair"
}

# Define instance type
variable "instance_type" {
  description = "The EC2 instance type to use for deployment"
  type        = string
  default     = "c5.large"
}

# Define allowed IPs for SSH access
variable "allowed_ssh_ips" {
  description = "List of IPs allowed to SSH into the EC2 instances"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# Define VPC CIDR block
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Define Subnet CIDR block
variable "subnet_cidr" {
  description = "CIDR block for the Subnet"
  type        = string
  default     = "10.0.1.0/24"
}

# Define environment variable (dev, prod)
variable "environment" {
  description = "Environment for deployment (dev, prod)"
  type        = string
  default     = "dev"
}

# AMI ID for EC2 instance
variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance"
  type        = string
}

# Tags to apply to all resources
variable "tags" {
  description = "A map of tags to apply to the resources"
  type        = map(string)
  default     = {
    Project     = "HFT_System"
    Environment = "dev"
  }
}

# Define instance count for auto-scaling group
variable "instance_count" {
  description = "The number of instances to launch"
  type        = number
  default     = 2
}

# Define minimum and maximum instance counts for auto-scaling
variable "min_instance_count" {
  description = "Minimum number of instances for auto-scaling"
  type        = number
  default     = 1
}

variable "max_instance_count" {
  description = "Maximum number of instances for auto-scaling"
  type        = number
  default     = 5
}

# Define EBS volume size
variable "ebs_volume_size" {
  description = "The size of the EBS volume (in GB) attached to EC2 instances"
  type        = number
  default     = 100
}

# Define EBS volume type
variable "ebs_volume_type" {
  description = "The type of the EBS volume (gp2, io1, etc.)"
  type        = string
  default     = "gp2"
}

# Define security group IDs
variable "security_group_ids" {
  description = "List of security group IDs to attach to the EC2 instances"
  type        = list(string)
  default     = []
}

# Define availability zones
variable "availability_zones" {
  description = "List of availability zones to deploy into"
  type        = list(string)
  default     = ["us-west-1a", "us-west-1b"]
}

# Define load balancer type
variable "load_balancer_type" {
  description = "Type of load balancer to use (application, network)"
  type        = string
  default     = "application"
}

# Define load balancer listener port
variable "lb_listener_port" {
  description = "Port for the load balancer listener"
  type        = number
  default     = 80
}

# Define auto-scaling health check type
variable "health_check_type" {
  description = "Health check type for the auto-scaling group (EC2 or ELB)"
  type        = string
  default     = "EC2"
}

# Define the health check grace period
variable "health_check_grace_period" {
  description = "Grace period (in seconds) for health checks"
  type        = number
  default     = 300
}

# Define AMI name filter (to automatically select the latest AMI)
variable "ami_name_filter" {
  description = "Filter to use for selecting the AMI"
  type        = string
  default     = "hft-system-*"
}

# Define auto-scaling termination policy
variable "termination_policy" {
  description = "Termination policy for auto-scaling group (OldestInstance, NewestInstance, etc.)"
  type        = string
  default     = "OldestInstance"
}

# Define EC2 instance profile for IAM role
variable "instance_profile" {
  description = "IAM instance profile to attach to the EC2 instances"
  type        = string
}

# Define log retention period for CloudWatch logs
variable "log_retention_days" {
  description = "Retention period (in days) for CloudWatch logs"
  type        = number
  default     = 7
}

# Define SNS topic ARN for notifications
variable "sns_topic_arn" {
  description = "SNS topic ARN for notifications"
  type        = string
}

# Define enable CloudWatch monitoring
variable "enable_cloudwatch_monitoring" {
  description = "Enable CloudWatch monitoring for EC2 instances"
  type        = bool
  default     = true
}

# Define CloudWatch alarm CPU threshold
variable "cpu_alarm_threshold" {
  description = "CPU usage threshold to trigger CloudWatch alarm"
  type        = number
  default     = 80
}

# Define RDS instance class
variable "rds_instance_class" {
  description = "Instance class for the RDS database"
  type        = string
  default     = "db.t2.medium"
}

# Define RDS allocated storage
variable "rds_allocated_storage" {
  description = "The amount of storage (in GB) allocated for the RDS instance"
  type        = number
  default     = 20
}

# Define RDS backup retention period
variable "rds_backup_retention" {
  description = "The number of days to retain backups for RDS"
  type        = number
  default     = 7
}

# Define RDS multi-AZ deployment
variable "rds_multi_az" {
  description = "Enable multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

# Define RDS engine (MySQL, PostgreSQL)
variable "rds_engine" {
  description = "The database engine to use for the RDS instance"
  type        = string
  default     = "postgres"
}

# Define RDS engine version
variable "rds_engine_version" {
  description = "The version of the database engine for RDS"
  type        = string
  default     = "12.3"
}

# Define S3 bucket for backups
variable "s3_backup_bucket" {
  description = "The S3 bucket used for storing backups"
  type        = string
}

# Define S3 bucket versioning
variable "s3_bucket_versioning" {
  description = "Enable versioning for the S3 backup bucket"
  type        = bool
  default     = true
}

# Define S3 bucket lifecycle rules
variable "s3_lifecycle_rules" {
  description = "Lifecycle rules for the S3 bucket (transition to Glacier)"
  type        = list(map(string))
  default     = []
}

# Define IAM role for EC2 instances
variable "iam_role" {
  description = "IAM role to attach to EC2 instances"
  type        = string
}

# Define CloudFront distribution for website
variable "cloudfront_distribution" {
  description = "CloudFront distribution ID for website"
  type        = string
}

# Define DNS zone for Route53
variable "dns_zone" {
  description = "Route53 DNS zone for managing domain records"
  type        = string
}

# Define Route53 domain name
variable "domain_name" {
  description = "Domain name to associate with CloudFront distribution"
  type        = string
}

# Define Redis cache node type
variable "redis_node_type" {
  description = "Node type for Redis cache"
  type        = string
  default     = "cache.t2.micro"
}

# Define Redis number of nodes
variable "redis_num_nodes" {
  description = "Number of Redis nodes"
  type        = number
  default     = 1
}

# Define Redis cluster enabled
variable "redis_cluster_enabled" {
  description = "Enable clustering for Redis"
  type        = bool
  default     = false
}

# Define Redis snapshot retention period
variable "redis_snapshot_retention" {
  description = "Retention period for Redis snapshots"
  type        = number
  default     = 5
}