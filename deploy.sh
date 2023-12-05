#!/bin/bash
#deploy.sh

# Navigate to Terraform directory and run Terraform
cd /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/terraform-project
terraform init
terraform apply -auto-approve

# Wait for EC2 instance to initialize
echo "Waiting for EC2 instance to initialize..."
sleep 60

# Wait for IAM changes to propagate
echo "Waiting for IAM changes to propagate..."
sleep 120

# Navigate to Ansible directory and run Ansible
cd /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/ansible-project
ansible-playbook -i inventory/aws_ec2.yml site.yml --vault-password-file /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/ansible-project/pw.txt