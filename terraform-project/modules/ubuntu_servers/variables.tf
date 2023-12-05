#modules/ubuntu_servers/variables.tf
# This file contains the variable declarations for the Ubuntu server module.

# EC2 instance type
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

# Subnet ID for the instances
variable "subnet_id" {
  description = "Subnet ID for the instances"
  type        = string
}

# Tags for the instances
variable "instance_tags" {
  description = "Tags for the instances"
  type        = map(string)
}

# Key pair name
variable "key_name" {
  description = "Key pair name"
  type        = string
}

# Type of server (backend or database)
variable "server_type" {
  description = "Type of server (backend or database)"
  type        = string
}

# VPC ID for the instances
variable "vpc_id" {
  description = "VPC ID for the instances"
  type        = string
}

# IAM Instance Profile name for the EC2 instance
variable "iam_instance_profile_name" {
  type        = string
  description = "IAM Instance Profile name for the EC2 instance"
  default     = null  # Set a default of null to make this variable optional
}

# Number of instances to create
variable "instance_count" {
  description = "Number of instances to create"
  type        = number
}

# Security group ID to associate with the instance
variable "security_group_id" {
  description = "Security group ID to associate with the instance"
  type        = string
}

# Whether to associate a public IP with the instance
variable "associate_public_ip" {
  description = "Whether to associate a public IP with the instance"
  type        = bool
  default     = true
}


