#modules/variables.tf
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

# Inside your module's variables.tf file
variable "iam_instance_profile_name" {
  type        = string
  description = "IAM Instance Profile name for the EC2 instance"
  default     = null  # Set a default of null to make this variable optional
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


