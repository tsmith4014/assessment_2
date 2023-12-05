#modules/ubuntu_servers/main.tf
# This Terraform module creates Ubuntu servers in AWS using the specified AMI and instance type.
# It retrieves the latest Ubuntu AMI from AWS and provisions the specified number of instances in the specified subnet.
# The instances are associated with the specified security group, key pair, and IAM instance profile.
# Each instance is tagged with a unique name based on the server type and index.

data "aws_ami" "latest_ubuntu" {
  # Set most_recent to true to retrieve the most recent version of the resource,this will apply to the filter block below.
  most_recent = true

  # The `owners` attribute specifies the AWS account IDs that have ownership of the AMI.
  # In this case, the value ["099720109477"] indicates that the AMI is owned by Canonical, Ubuntu's producer.
  owners = ["099720109477"] # Canonical
 


  # This block specifies the values for the Ubuntu server images.
  # The values are set to match the pattern "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*".
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

/*
  This resource block defines an AWS EC2 instance of Ubuntu Server.
  It creates multiple instances based on the value of the "instance_count" variable.
  The instance uses the latest Ubuntu AMI provided by AWS.
  The instance type, subnet ID, security group ID, key name, and other parameters are configurable through variables.
  The instances are tagged with a name in the format "UbuntuServer-{server_type}-{index}".
*/

resource "aws_instance" "ubuntu_server" {
  count                         = var.instance_count
  ami                           = data.aws_ami.latest_ubuntu.id
  instance_type                 = var.instance_type
  subnet_id                     = var.subnet_id
  # This configuration specifies the VPC security group IDs for the Ubuntu servers.
  # The security group IDs are provided as a list, with var.security_group_id being the variable that holds the value.
  vpc_security_group_ids = [var.security_group_id]
  key_name                      = var.key_name
  associate_public_ip_address   = var.associate_public_ip
  iam_instance_profile          = var.iam_instance_profile_name

  # This code merges the instance_tags variable with a dynamically generated "Name" tag for each Ubuntu server.
  # The "Name" tag is formatted as "UbuntuServer-{server_type}-{index}", where {server_type} is the value of the server_type variable and {index} is the current index of the server in the count loop.
  # The resulting merged tags are assigned to the tags attribute of the resource.
  tags = merge(
    var.instance_tags,
    { "Name": "UbuntuServer-${var.server_type}-${count.index}" }
  )
}