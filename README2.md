# Terraform Configuration for Ubuntu Servers in AWS

## Ubuntu Servers Module (`main.tf`)

This Terraform module creates Ubuntu servers in AWS. It retrieves the latest Ubuntu AMI and provisions instances in a specified subnet, associating them with a given security group, key pair, and IAM instance profile. Each instance is uniquely tagged.

```hcl

data "aws_ami" "latest_ubuntu" {
  most_recent = true
  owners = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

resource "aws_instance" "ubuntu_server" {
  count                         = var.instance_count
  ami                           = data.aws_ami.latest_ubuntu.id
  instance_type                 = var.instance_type
  subnet_id                     = var.subnet_id
  vpc_security_group_ids        = [var.security_group_id]
  key_name                      = var.key_name
  associate_public_ip_address   = var.associate_public_ip
  iam_instance_profile          = var.iam_instance_profile_name
  tags = merge(
    var.instance_tags,
    { "Name": "UbuntuServer-${var.server_type}-${count.index}" }
  )
}
```

## Variables for Ubuntu Servers (`variables.tf`)

Variable declarations for the Ubuntu server module.

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "subnet_id" {
  description = "Subnet ID for the instances"
  type        = string
}

variable "instance_tags" {
  description = "Tags for the instances"
  type        = map(string)
}

variable "key_name" {
  description = "Key pair name"
  type        = string
}

variable "server_type" {
  description = "Type of server (backend or database)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for the instances"
  type        = string
}

variable "iam_instance_profile_name" {
  type        = string
  description = "IAM Instance Profile name for the EC2 instance"
  default     = null
}

variable "instance_count" {
  description = "Number of instances to create"
  type        = number
}

variable "security_group_id" {
  description = "Security group ID to associate with the instance"
  type        = string
}

variable "associate_public_ip" {
  description = "Whether to associate a public IP with the instance"
  type        = bool
  default     = true
}
```

## Outputs for Ubuntu Servers (`outputs.tf`)

Outputs the public IPs of the instances.

```hcl
output "instance_public_ips" {
  value = aws_instance.ubuntu_server[*].public_ip
}
```

## Root Configuration (`main.tf`)

Security group and module definitions for backend and database servers.

```hcl
# Security Group for Backend Server
resource "aws_security_group" "backend_sg" {
  name        = "backend-sg"
  description = "Security group for backend server"
  vpc_id      = var.vpc_id

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP Access
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
}

# Security Group for Database Server
resource "aws_security_group" "database_sg" {
  name        = "database-sg"
  description = "Security group for database server"
  vpc_id      = var.vpc_id

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # MySQL Access from the Backend Server's IP
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["${module.backend_server.instance_public_ips[0]}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Define backend and database modules
module "backend_server" {
  vpc_id                  = var.vpc_id
  source                  = "./modules/ubuntu_servers"
  instance_count          = 1
  security_group_id       = aws_security_group.backend_sg.id
  subnet_id               = var.subnet_id
  key_name                = var.key_name
  server_type             = "backend"
  instance_tags           = {
    Team        = "mobile-app"
    Type        = "backend"
    Environment = "dev"
  }
  iam_instance_profile_name = aws_iam_instance_profile.ec2_s3_profile.name
}

module "database_server" {
  vpc_id                  = var.vpc_id
  source                  = "./modules/ubuntu_servers"
  instance_count          = 1
  security_group_id       = aws_security_group.database_sg.id
  subnet_id               = var.subnet_id
  key_name                = var.key_name
  server_type             = "database"
  instance_tags           = {
    Team        = "mobile-app"
    Type        = "database"
    Environment = "dev"
  }
}

# S3 bucket resource
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "vegas-todo-bucket"
  tags = {
    Name        = "Frontend"
    Team        = "mobile-app"
    Environment = "dev"
  }
  cors_rule {
    allowed_origins = ["https://vegas-todo-bucket.s3.eu-west-2.amazonaws.com/index.html"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_headers = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Data source for the S3 bucket
data "aws_s3_bucket" "frontend_bucket_data" {
  bucket = aws_s3_bucket.frontend_bucket.bucket
}

# S3 Bucket Ownership Controls
resource "aws_s3_bucket_ownership_controls" "frontend_bucket_ownership" {
  bucket = aws_s3_bucket.frontend_bucket.bucket
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "frontend_bucket_access_block" {
  bucket = aws_s3_bucket.frontend_bucket.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 Bucket ACL
resource "aws_s3_bucket_acl" "frontend_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.frontend_bucket_ownership,
    aws_s3_bucket_public_access_block.frontend_bucket_access_block,
  ]
  bucket = aws_s3_bucket.frontend_bucket.id
  acl    =

 "public-read"
}

# S3 Bucket Website Configuration
resource "aws_s3_bucket_website_configuration" "frontend_bucket_website_config" {
  bucket = aws_s3_bucket.frontend_bucket.bucket
  index_document {
    suffix = "index.html"
  }
}

# S3 Bucket Policy
resource "aws_s3_bucket_policy" "frontend_bucket_policy" {
  bucket = aws_s3_bucket.frontend_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject",
          "s3:GetObjectTagging"
        ]
        Resource = [
          "${aws_s3_bucket.frontend_bucket.arn}/*"
        ]
      }
    ]
  })
}
```

## IAM Configuration (`iam.tf`)

Defines IAM resources for EC2 instances' access to S3 bucket.

```hcl
resource "aws_iam_role" "ec2_s3_role" {
  name = "ec2_s3_access_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "s3_access" {
  name        = "S3AccessPolicy"
  description = "Policy that allows EC2 to access specific S3 Bucket"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          aws_s3_bucket.frontend_bucket.arn,
          "${aws_s3_bucket.frontend_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.ec2_s3_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_instance_profile" "ec2_s3_profile" {
  name = "ec2_s3_profile"
  role = aws_iam_role.ec2_s3_role.name
}
```

## Terraform Providers (`providers.tf`)

Configuration for required Terraform providers.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.24.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

## Terraform Variable Values (`terraform.tfvars`)

Variable values for the Terraform configuration.

```hcl
vpc_id    = "vpc-095a1ee516e12f7ba"
subnet_id = "subnet-0394725cdbfd85d65"
key_name  = "cpdevopsew-eu-west-2"
aws_region = "eu-west-2"
```

## Variable Definitions (`variables.tf`)

Definitions of variables used in Terraform configuration.

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID"
  type        = string
}

variable "key_name" {
  description = "Key pair name"
  type        = string
}
```
