data "aws_ami" "latest_ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

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







# #main.tf module
# resource "aws_security_group" "todo_server_sg" {
#   name        = "server_sg"
#   description = "Security group for Ubuntu servers"
#   vpc_id      = var.vpc_id

#   # SSH access
#   ingress {
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   # Additional rules based on server type: backend or database
#   dynamic "ingress" {
#     for_each = var.server_type == "backend" ? [1] : []

#     content {
#       from_port   = 80
#       to_port     = 80
#       protocol    = "tcp"
#       cidr_blocks = ["0.0.0.0/0"]
#     }
#   }

#   dynamic "ingress" {
#     for_each = var.server_type == "database" ? [1] : []

#     content {
#       from_port   = 3306
#       to_port     = 3306
#       protocol    = "tcp"
#       cidr_blocks = ["0.0.0.0/0"] # Update with appropriate CIDR blocks for security
#     }
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }



# data "aws_ami" "latest_ubuntu" {
#   most_recent = true
#   owners      = ["099720109477"] # Canonical

#   filter {
#     name   = "name"
#     values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
#   }
# }

# resource "aws_instance" "ubuntu_server" {
#   count                      = 1
#   iam_instance_profile       = var.iam_instance_profile_name
#   ami                        = data.aws_ami.latest_ubuntu.id
#   instance_type              = var.instance_type
#   subnet_id                  = var.subnet_id
#   vpc_security_group_ids     = [aws_security_group.todo_server_sg.id]
#   key_name                   = var.key_name
#   associate_public_ip_address = true

#   tags = merge(
#     var.instance_tags,
#     { "Name": "UbuntuServer-${var.server_type}-${count.index}" }
#   )
# }

