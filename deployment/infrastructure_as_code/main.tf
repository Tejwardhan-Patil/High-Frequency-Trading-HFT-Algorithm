provider "aws" {
  region = "us-west-2"
}

resource "aws_key_pair" "hft_key" {
  key_name   = "hft-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_vpc" "hft_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "HFT-VPC"
  }
}

resource "aws_subnet" "hft_subnet" {
  vpc_id             = aws_vpc.hft_vpc.id
  cidr_block         = "10.0.1.0/24"
  availability_zone  = "us-west-2a"
  tags = {
    Name = "HFT-Subnet"
  }
}

resource "aws_internet_gateway" "hft_igw" {
  vpc_id = aws_vpc.hft_vpc.id
  tags = {
    Name = "HFT-Internet-Gateway"
  }
}

resource "aws_route_table" "hft_route_table" {
  vpc_id = aws_vpc.hft_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.hft_igw.id
  }

  tags = {
    Name = "HFT-Route-Table"
  }
}

resource "aws_route_table_association" "hft_route_table_association" {
  subnet_id      = aws_subnet.hft_subnet.id
  route_table_id = aws_route_table.hft_route_table.id
}

resource "aws_security_group" "hft_security_group" {
  vpc_id      = aws_vpc.hft_vpc.id
  name        = "hft_security_group"
  description = "Allow inbound traffic for HFT"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "HFT-Security-Group"
  }
}

resource "aws_instance" "hft_instance_1" {
  ami             = "ami-0abcdef1234567890"
  instance_type   = "t3.micro"
  key_name        = aws_key_pair.hft_key.key_name
  subnet_id       = aws_subnet.hft_subnet.id
  security_groups = [aws_security_group.hft_security_group.name]

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install docker.io -y",
      "sudo service docker start",
      "sudo usermod -aG docker ubuntu",
      "docker run --name hft-container-1 -d website.com/hft-system:latest"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }

  tags = {
    Name = "HFT-Instance-1"
    Environment = "Production"
    Role = "Primary"
  }
}

resource "aws_instance" "hft_instance_2" {
  ami             = "ami-0abcdef1234567890"
  instance_type   = "t3.micro"
  key_name        = aws_key_pair.hft_key.key_name
  subnet_id       = aws_subnet.hft_subnet.id
  security_groups = [aws_security_group.hft_security_group.name]

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install docker.io -y",
      "sudo service docker start",
      "sudo usermod -aG docker ubuntu",
      "docker run --name hft-container-2 -d website.com/hft-system:latest"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }

  tags = {
    Name = "HFT-Instance-2"
    Environment = "Production"
    Role = "Secondary"
  }
}

resource "aws_instance" "hft_instance_3" {
  ami             = "ami-0abcdef1234567890"
  instance_type   = "t3.micro"
  key_name        = aws_key_pair.hft_key.key_name
  subnet_id       = aws_subnet.hft_subnet.id
  security_groups = [aws_security_group.hft_security_group.name]

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install docker.io -y",
      "sudo service docker start",
      "sudo usermod -aG docker ubuntu",
      "docker run --name hft-container-3 -d website.com/hft-system:latest"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }
  }

  tags = {
    Name = "HFT-Instance-3"
    Environment = "Production"
    Role = "Backup"
  }
}

output "instance_1_ip" {
  value = aws_instance.hft_instance_1.public_ip
}

output "instance_2_ip" {
  value = aws_instance.hft_instance_2.public_ip
}

output "instance_3_ip" {
  value = aws_instance.hft_instance_3.public_ip
}

resource "aws_s3_bucket" "hft_logs" {
  bucket = "hft-system-logs"

  tags = {
    Name        = "HFT-System-Logs"
    Environment = "Production"
  }
}

resource "aws_s3_bucket_versioning" "hft_logs_versioning" {
  bucket = aws_s3_bucket.hft_logs.bucket

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_cloudwatch_log_group" "hft_log_group" {
  name              = "hft-log-group"
  retention_in_days = 7

  tags = {
    Application = "HFT-System"
    Environment = "Production"
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu_alarm" {
  alarm_name          = "cpu-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "80"
  actions_enabled     = true
  alarm_actions       = [aws_sns_topic.hft_alerts.arn]
  dimensions = {
    InstanceId = aws_instance.hft_instance_1.id
  }
}

resource "aws_sns_topic" "hft_alerts" {
  name = "hft_alerts"
}

resource "aws_sns_topic_subscription" "hft_alerts_subscription" {
  topic_arn = aws_sns_topic.hft_alerts.arn
  protocol  = "email"
  endpoint  = "alert@website.com"
}