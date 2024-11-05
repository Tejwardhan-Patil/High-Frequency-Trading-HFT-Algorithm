output "instance_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.hft_instance.id
}

output "instance_public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.hft_instance.public_ip
}

output "instance_private_ip" {
  description = "The private IP address of the EC2 instance"
  value       = aws_instance.hft_instance.private_ip
}

output "security_group_id" {
  description = "The ID of the security group"
  value       = aws_security_group.hft_security_group.id
}

output "key_pair_name" {
  description = "The name of the key pair used for the instance"
  value       = aws_key_pair.hft_key_pair.key_name
}

output "instance_arn" {
  description = "The ARN of the EC2 instance"
  value       = aws_instance.hft_instance.arn
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.hft_vpc.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.hft_vpc.cidr_block
}

output "subnet_id" {
  description = "The ID of the subnet"
  value       = aws_subnet.hft_subnet.id
}

output "subnet_cidr_block" {
  description = "The CIDR block of the subnet"
  value       = aws_subnet.hft_subnet.cidr_block
}

output "internet_gateway_id" {
  description = "The ID of the internet gateway"
  value       = aws_internet_gateway.hft_internet_gateway.id
}

output "route_table_id" {
  description = "The ID of the route table"
  value       = aws_route_table.hft_route_table.id
}

output "elastic_ip" {
  description = "The Elastic IP associated with the instance"
  value       = aws_eip.hft_eip.public_ip
}

output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.hft_lb.dns_name
}

output "load_balancer_arn" {
  description = "The ARN of the load balancer"
  value       = aws_lb.hft_lb.arn
}

output "target_group_arn" {
  description = "The ARN of the target group for load balancing"
  value       = aws_lb_target_group.hft_target_group.arn
}

output "target_group_name" {
  description = "The name of the target group"
  value       = aws_lb_target_group.hft_target_group.name
}

output "autoscaling_group_name" {
  description = "The name of the Auto Scaling group"
  value       = aws_autoscaling_group.hft_asg.name
}

output "autoscaling_group_min_size" {
  description = "The minimum size of the Auto Scaling group"
  value       = aws_autoscaling_group.hft_asg.min_size
}

output "autoscaling_group_max_size" {
  description = "The maximum size of the Auto Scaling group"
  value       = aws_autoscaling_group.hft_asg.max_size
}

output "autoscaling_group_desired_capacity" {
  description = "The desired capacity of the Auto Scaling group"
  value       = aws_autoscaling_group.hft_asg.desired_capacity
}

output "scaling_policy_arn" {
  description = "The ARN of the scaling policy"
  value       = aws_autoscaling_policy.hft_scaling_policy.arn
}

output "launch_configuration_name" {
  description = "The name of the launch configuration"
  value       = aws_launch_configuration.hft_launch_config.name
}

output "cloudwatch_alarm_cpu_high_arn" {
  description = "The ARN of the CloudWatch alarm for high CPU usage"
  value       = aws_cloudwatch_metric_alarm.hft_cpu_high.arn
}

output "cloudwatch_alarm_cpu_low_arn" {
  description = "The ARN of the CloudWatch alarm for low CPU usage"
  value       = aws_cloudwatch_metric_alarm.hft_cpu_low.arn
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.hft_data_bucket.bucket
}

output "s3_bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.hft_data_bucket.arn
}

output "s3_bucket_region" {
  description = "The region of the S3 bucket"
  value       = aws_s3_bucket.hft_data_bucket.region
}

output "cloudfront_distribution_id" {
  description = "The ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.hft_cf.id
}

output "cloudfront_distribution_domain" {
  description = "The domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.hft_cf.domain_name
}

output "rds_instance_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.hft_rds.endpoint
}

output "rds_instance_arn" {
  description = "The ARN of the RDS instance"
  value       = aws_db_instance.hft_rds.arn
}

output "rds_instance_identifier" {
  description = "The identifier of the RDS instance"
  value       = aws_db_instance.hft_rds.identifier
}

output "rds_instance_status" {
  description = "The current status of the RDS instance"
  value       = aws_db_instance.hft_rds.status
}

output "rds_subnet_group_name" {
  description = "The name of the RDS subnet group"
  value       = aws_db_subnet_group.hft_rds_subnet_group.name
}

output "rds_parameter_group_name" {
  description = "The name of the RDS parameter group"
  value       = aws_db_parameter_group.hft_rds_param_group.name
}

output "redis_cluster_endpoint" {
  description = "The endpoint of the Redis cluster"
  value       = aws_elasticache_cluster.hft_redis.endpoint
}

output "redis_cluster_arn" {
  description = "The ARN of the Redis cluster"
  value       = aws_elasticache_cluster.hft_redis.arn
}

output "redis_cluster_id" {
  description = "The ID of the Redis cluster"
  value       = aws_elasticache_cluster.hft_redis.id
}

output "kms_key_id" {
  description = "The ID of the KMS key used for encryption"
  value       = aws_kms_key.hft_kms_key.id
}

output "kms_key_arn" {
  description = "The ARN of the KMS key"
  value       = aws_kms_key.hft_kms_key.arn
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic"
  value       = aws_sns_topic.hft_sns_topic.arn
}

output "sns_topic_name" {
  description = "The name of the SNS topic"
  value       = aws_sns_topic.hft_sns_topic.name
}

output "sns_subscription_arn" {
  description = "The ARN of the SNS subscription"
  value       = aws_sns_topic_subscription.hft_sns_subscription.arn
}

output "iam_role_name" {
  description = "The name of the IAM role"
  value       = aws_iam_role.hft_iam_role.name
}

output "iam_role_arn" {
  description = "The ARN of the IAM role"
  value       = aws_iam_role.hft_iam_role.arn
}

output "iam_policy_name" {
  description = "The name of the IAM policy"
  value       = aws_iam_policy.hft_iam_policy.name
}

output "iam_policy_arn" {
  description = "The ARN of the IAM policy"
  value       = aws_iam_policy.hft_iam_policy.arn
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.hft_lambda_function.function_name
}

output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.hft_lambda_function.arn
}

output "lambda_function_version" {
  description = "The version of the Lambda function"
  value       = aws_lambda_function.hft_lambda_function.version
}

output "api_gateway_url" {
  description = "The URL of the API Gateway"
  value       = aws_api_gateway_rest_api.hft_api_gateway.execution_arn
}

output "api_gateway_id" {
  description = "The ID of the API Gateway"
  value       = aws_api_gateway_rest_api.hft_api_gateway.id
}

output "api_gateway_stage" {
  description = "The stage name of the API Gateway"
  value       = aws_api_gateway_stage.hft_api_stage.stage_name
}

output "codepipeline_name" {
  description = "The name of the CodePipeline"
  value       = aws_codepipeline.hft_code_pipeline.name
}

output "codepipeline_arn" {
  description = "The ARN of the CodePipeline"
  value       = aws_codepipeline.hft_code_pipeline.arn
}

output "codebuild_project_name" {
  description = "The name of the CodeBuild project"
  value       = aws_codebuild_project.hft_codebuild.name
}

output "codebuild_project_arn" {
  description = "The ARN of the CodeBuild project"
  value       = aws_codebuild_project.hft_codebuild.arn
}

output "cloudformation_stack_id" {
  description = "The ID of the CloudFormation stack"
  value       = aws_cloudformation_stack.hft_cf_stack.id
}

output "cloudformation_stack_status" {
  description = "The status of the CloudFormation stack"
  value       = aws_cloudformation_stack.hft_cf_stack.status
}