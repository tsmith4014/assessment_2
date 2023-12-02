#!/bin/bash
#deploy.sh

# Navigate to Terraform directory and run Terraform
cd /Users/chadthompsonsmith/DevOpsAlpha/assessment_2
terraform init
terraform apply -auto-approve

# Navigate to Ansible directory and run Ansible
cd /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/ansible-project
ansible-playbook -i inventory/aws_ec2.yml site.yml --vault-password-file /Users/chadthompsonsmith/DevOpsAlpha/assessment_2/ansible-project/pw.txt
