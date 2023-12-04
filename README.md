# Terraform and Ansible Deployment Documentation

## Overview

This document outlines the steps, configurations, and scripts used to deploy a Flask application with a MySQL database on AWS EC2 instances using Terraform and Ansible.

## Terraform Configuration for Ubuntu Servers in AWS

Terraform is used to provision AWS infrastructure resources, EC2 backend(flask app API) and database(MySQL application-todo database) instances, sec-grps, IAM roles/polices, and the S3 bucket(Front end serves our HTML).

### Terraform Files

- `variables.tf`: Defines variables used across Terraform configurations.
- `terraform.tfvars`: Specifies values for the defined variables.
- `providers.tf`: Sets up the Terraform provider, AWS in this case.
- `outputs.tf`: Defines output variables post Terraform execution.
- `main.tf`: Main Terraform configuration file for provisioning resources.
- `iam.tf`: IAM resources for granting EC2 instances access to S3 bucket.
- `modules/ubuntu_servers/main.tf`: Module for provisioning Ubuntu servers.
- `modules/ubuntu_servers/outputs.tf`: Output configuration for the Ubuntu servers module.
- `modules/ubuntu_servers/variables.tf`: Variable definitions for the Ubuntu servers module.

### Ubuntu Servers Module (`main.tf`)

This Terraform module creates Ubuntu servers in AWS. It retrieves the latest Ubuntu AMI and provisions instances in a specified subnet, associating them with a given security group, key pair, and IAM instance profile. Each instance is uniquely tagged.

---

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

---

### Variables for Ubuntu Servers (`variables.tf`)

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

---

### Outputs for Ubuntu Servers (`outputs.tf`)

Outputs the public IPs of the instances.

```hcl
output "instance_public_ips" {
  value = aws_instance.ubuntu_server[*].public_ip
}
```

---

### Root Configuration (`main.tf`)

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

---

### IAM Configuration (`iam.tf`)

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

---

### Terraform Providers (`providers.tf`)

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

---

### Terraform Variable Values (`terraform.tfvars`)

Variable values for the Terraform configuration.

```hcl
vpc_id    = "vpc-095a1ee516e12f7ba"
subnet_id = "subnet-0394725cdbfd85d65"
key_name  = "cpdevopsew-eu-west-2"
aws_region = "eu-west-2"
```

---

### Variable Definitions (`variables.tf`)

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

---

### Outputs Configuration (`outputs.tf`)

This section of the Terraform configuration (`outputs.tf`) specifies the outputs for your infrastructure, including the IP addresses of backend and database servers, and the name of the frontend S3 bucket.

```hcl
output "backend_server_ip" {
  value = module.backend_server.instance_public_ips
}

output "database_server_ip" {
  value = module.database_server.instance_public_ips
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend_bucket.bucket
}
```

---

## Ansible Configuration for Flask Application Deployment

Ansible automates the deployment and configuration of the Flask application and MySQL database on AWS.

### Ansible Playbooks

#### Main Playbook (`/Ansible-project/site.yml`)

```yaml
---
- hosts: type_database
  become: true
  vars_files:
    - roles/mysql/vars/secret.yml
  roles:
    - common
    - mysql

- hosts: type_backend
  become: true
  vars_files:
    - roles/mysql/vars/secret.yml
    - roles/flask_backend/vars/main.yml
  roles:
    - common
    - flask_backend
    - s3_upload
```

### Ansible Configuration File (`/ansible-project/ansible.cfg`)

```ini
[defaults]
private_key_file = /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/cpdevopsew-eu-west-2.pem
remote_user = ubuntu
host_key_checking = False
```

---

## Ansible Tasks for Flask Application Deployment

---

### MySQL Role Configuration

#### Tasks (`/ansible-project/roles/mysql/tasks/main.yml`)

```yaml
- name: Install MySQL server
  apt:
    name: "mysql-server"
    state: present
  become: true

- name: Start MySQL service and enable on boot
  systemd:
    name: mysql
    state: started
    enabled: yes
  become: true

- name: Check MySQL root user's authentication method
  command: mysql -u root -p'{{ vault_mysql_root_password }}' -e "SELECT plugin FROM mysql.user WHERE User = 'root'"
  register: root_auth_method
  ignore_errors: true
  become: true

- name: Change MySQL root user's authentication method
  mysql_query:
    login_user: root
    login_unix_socket: /var/run/mysqld/mysqld.sock
    query:
      - ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{{ vault_mysql_root_password }}';
      - FLUSH PRIVILEGES;
  become: true
  when: "'mysql_native_password' not in root_auth_method.stdout"

- name: Allow remote connections to MySQL
  lineinfile:
    path: /etc/mysql/mysql.conf.d/mysqld.cnf
    line: "bind-address = 0.0.0.0"
    regexp: "^bind-address"
  become: true

- name: Restart MySQL service
  systemd:
    name: mysql
    state: restarted
  become: true

- name: Create todo_db database
  mysql_db:
    name: todo_db
    state: present
    login_user: root
    login_password: "{{ vault_mysql_root_password }}"
  become: true

- name: Create MySQL user for Flask application
  mysql_user:
    login_user: root
    login_password: "{{ vault_mysql_root_password }}"
    name: "{{ vault_mysql_user }}"
    password: "{{ vault_mysql_user_password }}"
    host: "%"
    state: present
  become: true

- name: Grant all privileges to MySQL user for Flask application
  mysql_user:
    login_user: root
    login_password: "{{ vault_mysql_root_password }}"
    name: "{{ vault_mysql_user }}"
    host: "%"
    priv: "*.*:ALL"
    state: present
  become: true
```

### Flask Backend Role Configuration

#### Tasks (`/ansible-project/roles/flask_backend/tasks/main.yml`)

```yaml
- name: Get backend host IP
  set_fact:
    backend_host_ip: "{{ (hostvars[groups['type_backend'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"

- name: Debug env_vars
  debug:
    var: env_vars

- name: Debug MYSQL_DATABASE_IP
  debug:
    msg: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"
  run_once: true

- name: Install MySQL client
  apt:
    name: mysql-client
    state: present
  become: true

- name: Clone the Flask application repository
  git:
    repo: "{{ git_repo }}"
    dest: "{{ project_path }}"
    version: "env"
  become: true

- name: Update API_URL in index.html
  lineinfile:
    path: "{{ project_path }}/index.html"
    regexp: 'const API_URL\s*=\s*"http://localhost"; // replace with your API endpoint'
    line: "        const API_URL = 'http://{{ backend_host_ip }}';"
  become: true

- name: Display the contents of index.html
  command: cat "{{ project_path }}/index.html"
  register: output
  changed_when: false

- name: Print the contents of index.html
  debug:
    var: output.stdout_lines

- name: Copy gunicorn_config.py
  copy:
    src: "{{ role_path }}/templates/gunicorn_config.py"
    dest: "{{ project_path }}/gunicorn_config.py"
    owner: ubuntu
    group: ubuntu
    mode: "0644"
  become: true

- name: Create a virtual environment
  command:
    cmd: python3 -m venv "{{ virtualenv_path }}"
    creates: "{{ virtualenv_path }}"
  become: true

- name: Install Python dependencies
  pip:
    requirements: "{{ project_path }}/{{ requirements_file }}"
    virtualenv: "{{ virtualenv_path }}"
  become: true

- name: Install Gunicorn
  pip:
    name: gunicorn
    virtualenv: "{{ virtualenv_path }}"
  become: true

- name: Debug MYSQL_DATABASE_PORT
  debug:
    var: env_vars.MYSQL_DATABASE_PORT

- name: Set environment variables
  lineinfile:
    path: "{{ virtualenv_path }}/bin/activate"
    line: "export {{ item.key }}={{ item.value }}"
    state: present
  loop: "{{ env_vars | dict2items }}"
  become: true

- name: Print environment variables
  debug:
    msg: "{{ ansible_env }}"

- name: Create environment file
  template:
    src: env.j2
    dest: "{{ project_path }}/.env"
  vars:
    MYSQL_DATABASE_HOST: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"
    MYSQL_DATABASE_USER: "{{ vault_mysql_user }}"
    MYSQL_DATABASE_PASSWORD: "{{ vault_mysql_user_password }}"
    MYSQL_DATABASE_PORT: "{{ vault_mysql_database_port }}"
    MYSQL_DATABASE_DB: "{{ vault_mysql_database_name }}"
  become: true

- name: Print .env file
  command: cat "{{ project_path }}/.env"
  register: env_file
  changed_when: false

- name: Show .env file
  debug:
    var: env_file.stdout_lines

- name: Create systemd service file for the todolist
  template:
    src: todolist.service.j2
    dest: /etc/systemd/system/todolist.service
    mode: "0644"
  vars:
    MYSQL_DATABASE_HOST: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '')) | replace('-', '.') }}"
    MYSQL_DATABASE_USER: "{{ vault_mysql_user }}"
    MYSQL_DATABASE_PASSWORD: "{{ vault_mysql_user_password }}"
    MYSQL_DATABASE_PORT: "{{ vault_mysql_database_port }}"
    MYSQL_DATABASE_DB: "{{ vault_mysql_database_name }}"
  become: true

- name: Reload systemd to read new todolist service
  systemd:
    daemon_reload: yes
  become: true

- name: Enable and start todolist service
  systemd:
    name: todolist
    enabled: yes
    state: started
  become: true

- name: Check todolist service status
  command: systemctl status todolist
  register: todolist_status
  changed_when: false
  ignore_errors: true
```

---

#### Templates

- **Gunicorn Configuration (`/ansible-project/roles/flask_backend/templates/gunicorn_config.py`):**

```python
bind = "0.0.0.0:80"
workers = 4
preload_app = True
```

- **Systemd Service File (`/ansible-project/roles/flask_backend/templates/todolist.service.j2`):**

```jinja

  [Unit]
Description=Gunicorn instance to serve todolist flask app

Wants=network.target
After=syslog.target network-online.target

[Service]
Type=simple
WorkingDirectory={{ project_path }}
ExecStart={{ virtualenv_path }}/bin/gunicorn todo:app -c {{ project_path }}/gunicorn_config.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Environment File Template (`/ansible-project/roles/flask_backend/templates/env.j2`)

This template file creates an environment configuration file for the Flask application:

```jinja
MYSQL_DATABASE_HOST={{ MYSQL_DATABASE_HOST }}
MYSQL_DATABASE_USER={{ MYSQL_DATABASE_USER }}
MYSQL_DATABASE_PASSWORD={{ MYSQL_DATABASE_PASSWORD }}
MYSQL_DATABASE_DB={{ MYSQL_DATABASE_DB }}
MYSQL_DATABASE_PORT={{ MYSQL_DATABASE_PORT }}
```

This template is used to set up necessary environment variables required by the Flask application, ensuring that it can connect to the MySQL database correctly.

---

#### Variables

(`/ansible-project/roles/flask_backend/vars/main.yml`)

```yaml
system_packages:
  - python3-pip
  - python3-venv
  - git
  - build-essential
  - libmysqlclient-dev
git_repo: "https://github.com/chandradeoarya/todolist-flask.git"
project_path: "/home/ubuntu/todolist-flask"
virtualenv_path: "{{ project_path }}/venv"
gunicorn_bind: "0.0.0.0:80"
requirements_file: "requirements.txt"
env_vars:
  FLASK_APP: "todo.py"
  FLASK_ENV: "development"
  MYSQL_DATABASE_HOST: "{{ (hostvars[groups['type_database'][0]]['inventory_hostname'] | regex_replace('ec2-', '') | regex_replace('.eu-west-2.compute.amazonaws.com', '') | replace('-', '.') }}"
  MYSQL_DATABASE_USER: "{{ vault_mysql_user }}"
  MYSQL_DATABASE_PASSWORD: "{{ vault_mysql_user_password }}"
  MYSQL_DATABASE_PORT: "{{ vault_mysql_database_port }}"
  MYSQL_DATABASE_DB: "{{ vault_mysql_database_name }}"
```

(`/ansible-project/roles/mysql/vars/main.yml`)

This file contains variables specific to the MySQL role:

```yaml
system_packages:
  - mysql-server
  - python3-pymysql

mysql_root_password: "{{ vault_mysql_root_password }}"
mysql_user: "{{ vault_mysql_user }}"
mysql_user_password: "{{ vault_mysql_user_password }}"
```

These variables include the system packages needed for MySQL setup, the root password, and the user credentials for the MySQL database. The `vault_mysql_root_password`, `vault_mysql_user`, and `vault_mysql_user_password` are stored in an Ansible Vault for security.

---

### Common Role Configuration

#### Tasks (`/ansible-project/roles/common/tasks/main.yml`)

```yaml
- name: Update all system packages to latest version
  apt:
    update_cache: yes
    upgrade: "dist"
    cache_valid_time: 3600
  become: true

- name: Install required system packages
  apt:
    name: "{{ item }}"
    state: latest
  loop: "{{ system_packages }}"
  become: true
  register: package_install

- name: Output result of package installation
  debug:
    var: package_install.results
```

---

### Inventory Configuration (`/ansible-project/inventory/aws_ec2.yml`)

```yaml
plugin: aws_ec2
regions:
  - eu-west-2
filters:
  tag:Environment: dev
keyed_groups:
  - key: tags['Environment']
    prefix: env
  - key: tags['Type']
    prefix: type
  - key: tags['Team']
    prefix: team
```

---

### Conclusion

This README provides a comprehensive guide for deploying and managing the Todo-List Flask application using Terraform and Ansible on AWS

---
