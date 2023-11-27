# root main.tf

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
    cidr_blocks = ["${module.backend_server.instance_public_ips[0]}/32"] # Convert IP to CIDR block
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
  # iam_instance_profile_name = aws_iam_instance_profile.ec2_s3_profile.name
}

# S3 bucket resource
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "vegas-todo-bucket" # Replace with your unique bucket name
  tags = {
    Name        = "Frontend"
    Team        = "mobile-app"
    Environment = "dev"
  }
}






# # root main.tf
# # Security Group for Backend Server
# resource "aws_security_group" "backend_sg" {
#   name        = "backend-sg"
#   description = "Security group for backend server"
#   vpc_id      = var.vpc_id

#   # SSH Access
#   ingress {
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   # HTTP Access
#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   # Access to MySQL Database
#   ingress {
#     from_port   = 3306
#     to_port     = 3306
#     protocol    = "tcp"
#     cidr_blocks = [module.database_server.instance_public_ip]
#   }
  
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# # Security Group for Database Server
# resource "aws_security_group" "database_sg" {
#   name        = "database-sg"
#   description = "Security group for database server"
#   vpc_id      = var.vpc_id

#   # SSH Access
#   ingress {
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
  
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }




# # Define backend and database modules
# module "backend_server" {
#   source                  = "./modules/ubuntu_servers"
#   subnet_id               = var.subnet_id
#   vpc_id                  = var.vpc_id
#   key_name                = var.key_name
#   server_type             = "backend"
#   instance_tags           = {
#     Team        = "mobile-app"
#     Type        = "backend"
#     Environment = "dev"
#   }
#   iam_instance_profile_name = aws_iam_instance_profile.ec2_s3_profile.name
# }

# module "database_server" {
#   source                  = "./modules/ubuntu_servers"
#   subnet_id               = var.subnet_id
#   vpc_id                  = var.vpc_id
#   key_name                = var.key_name
#   server_type             = "database"
#   instance_tags           = {
#     Team        = "mobile-app"
#     Type        = "database"
#     Environment = "dev"
#   }
#   iam_instance_profile_name = aws_iam_instance_profile.ec2_s3_profile.name
# }

# # S3 bucket and ACL resources
# resource "aws_s3_bucket" "frontend_bucket" {
#   bucket = "vegas-todo-bucket" # Replace with your unique bucket name
#   tags = {
#     Name        = "Frontend"
#     Team        = "mobile-app"
#     Environment = "dev"
#   }
# }






# # Define IAM Role and Policy
# resource "aws_iam_role" "ec2_s3_role" {
#   name = "ec2_s3_access_role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Effect = "Allow",
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         },
#         Action = "sts:AssumeRole"
#       },
#     ]
#   })
# }

# resource "aws_iam_policy" "s3_access" {
#   name        = "S3AccessPolicy"
#   description = "Policy that allows EC2 to access specific S3 Bucket"

#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Effect   = "Allow",
#         Action   = [
#           "s3:GetObject",
#           "s3:PutObject",
#           "s3:DeleteObject",
#           "s3:ListBucket"
#         ],
#         Resource = [
#           "${aws_s3_bucket.frontend_bucket.arn}",
#           "${aws_s3_bucket.frontend_bucket.arn}/*"
#         ]
#       },
#     ]
#   })
# }

# resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
#   role       = aws_iam_role.ec2_s3_role.name
#   policy_arn = aws_iam_policy.s3_access.arn
# }

# resource "aws_iam_instance_profile" "ec2_s3_profile" {
#   name = "ec2_s3_profile"
#   role = aws_iam_role.ec2_s3_role.name
# }

# # Define backend and database modules
# module "backend_server" {
#   source             = "./modules/ubuntu_servers"
#   subnet_id          = var.subnet_id
#   vpc_id             = var.vpc_id
#   key_name           = var.key_name
#   server_type        = "backend"
#   instance_tags      = {
#     Team        = "mobile-app"
#     Type        = "backend"
#     Environment = "dev"
#   }
#   iam_instance_profile_name = aws_iam_instance_profile.ec2_s3_profile.name
# }

# module "database_server" {
#   source             = "./modules/ubuntu_servers"
#   subnet_id          = var.subnet_id
#   vpc_id             = var.vpc_id
#   key_name           = var.key_name
#   server_type        = "database"
#   instance_tags      = {
#     Team        = "mobile-app"
#     Type        = "database"
#     Environment = "dev"
#   }
#   iam_instance_profile_name = aws_iam_instance_profile.ec2_s3_profile.name
# }

# # S3 bucket and ACL resources
# resource "aws_s3_bucket" "frontend_bucket" {
#   bucket = "vegas-bucket" # Replace with your unique bucket name

#   tags = {
#     Name        = "Frontend"
#     Team        = "mobile-app"
#     Environment = "dev"
#   }
# }

# resource "aws_s3_bucket_acl" "frontend_bucket_acl" {
#   bucket = aws_s3_bucket.frontend_bucket.id
#   acl    = "public-read"
# }







# module "backend_server" {
#   source = "./modules/ubuntu_servers"
#   subnet_id      = var.subnet_id
#   vpc_id         = var.vpc_id
#   key_name       = var.key_name
#   server_type    = "backend"
#   instance_tags  = {
#     Team        = "mobile-app"
#     Type        = "backend"
#     Environment = "dev"
#   }
# }

# module "database_server" {
#   source = "./modules/ubuntu_servers"
#   subnet_id      = var.subnet_id
#   vpc_id         = var.vpc_id
#   key_name       = var.key_name
#   server_type    = "database"
#   instance_tags  = {
#     Team        = "mobile-app"
#     Type        = "database"
#     Environment = "dev"
#   }
# }

# resource "aws_s3_bucket" "frontend_bucket" {
#   bucket = "vegas-bucket" # Replace with your unique bucket name

#   tags = {
#     Name        = "Frontend"
#     Team        = "mobile-app"
#     Environment = "dev"
#   }
# }

# resource "aws_s3_bucket_acl" "frontend_bucket_acl" {
#   bucket = aws_s3_bucket.frontend_bucket.id
#   acl    = "public-read"
# }









#reference below
# resource "aws_security_group" "my_sg" {
#   name        = "server_sg"
#   description = "Allow SSH, HTTP, and HTTPS"
#   vpc_id      = "vpc-095a1ee516e12f7ba"

#   ingress {
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   ingress {
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# resource "aws_s3_bucket" "my_bucket" {
#   bucket = "vegasterraforms3"
#   acl    = "private"
# }

# resource "aws_s3_bucket_object" "index_html" {
#   bucket       = aws_s3_bucket.my_bucket.id
#   key          = "index.html"
#   content      = <<EOF
# <html>
# <head><title>Welcome</title></head>
# <body><h1>Welcome to Vegas Terraform S3!</h1></body>
# </html>
# EOF
#   content_type = "text/html"
# }

# resource "aws_iam_role" "ec2_s3_access" {
#   name = "ec2_s3_access_role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Action = "sts:AssumeRole",
#         Effect = "Allow",
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         },
#       },
#     ]
#   })
# }

# resource "aws_iam_policy" "s3_read_policy" {
#   name        = "s3_read_policy"
#   description = "A policy that allows read access to a specific S3 bucket"

#   policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [
#       {
#         Action = [
#           "s3:GetObject",
#           "s3:ListBucket"
#         ],
#         Effect = "Allow",
#         Resource = [
#           "${aws_s3_bucket.my_bucket.arn}",
#           "${aws_s3_bucket.my_bucket.arn}/*"
#         ],
#       },
#     ]
#   })
# }

# resource "aws_iam_role_policy_attachment" "attach_s3_read_policy" {
#   role       = aws_iam_role.ec2_s3_access.name
#   policy_arn = aws_iam_policy.s3_read_policy.arn
# }

# resource "aws_iam_instance_profile" "ec2_s3_profile" {
#   name = "ec2_s3_profile"
#   role = aws_iam_role.ec2_s3_access.name
# }

# resource "aws_instance" "ubuntu_server" {
#   ami                    = "ami-0505148b3591e4c07"
#   instance_type          = "t2.micro"
#   subnet_id              = "subnet-0394725cdbfd85d65"
#   vpc_security_group_ids = [aws_security_group.my_sg.id]
#   iam_instance_profile   = aws_iam_instance_profile.ec2_s3_profile.name
#   key_name               = "cpdevopsew-eu-west-2"

#   tags = {
#     Name = "UbuntuServerS3"
#   }

#   user_data = <<-EOF
#               #!/bin/bash
#               sudo apt update -y
#               sudo apt install -y apache2
#               sudo systemctl start apache2
#               sudo systemctl enable apache2
              
#               # Install AWS CLI
#               sudo apt install -y awscli
              
#               # Try to copy the file with a retry mechanism
#               for i in {1..5}; do
#                   aws s3 cp s3://${aws_s3_bucket.my_bucket.bucket}/index.html /var/www/html/index.html && break || sleep 10
#               done
#               EOF
# }

# output "ec2_instance_ip" {
#   value = aws_instance.ubuntu_server.public_ip
# }

# output "s3_bucket_name" {
#   value = aws_s3_bucket.my_bucket.bucket
# }
