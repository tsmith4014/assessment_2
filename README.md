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

### Security Group Configuration

Details of security groups for both backend and database servers are defined to control traffic to these instances.

### S3 Bucket Configuration

Configuration for S3 bucket creation, policy, and website hosting.

## Ansible Configuration

Ansible is used for configuring and deploying the Flask application and setting up the MySQL database.

### Ansible Playbooks

- `site.yml`: Main playbook for deploying the application and database.
- `roles/s3_upload/tasks/main.yml`: Tasks for uploading files to the S3 bucket.

### Roles and Handlers

- `roles/mysql`: Contains tasks, handlers, vars, and templates for MySQL setup.
- `roles/flask_backend`: Contains tasks, vars, and templates for Flask backend setup.
- `roles/common`: Common tasks for system package updates.

### Inventory Files

- `inventory/aws_ec2.yml`: Dynamic inventory configuration for AWS EC2 instances.

### Environment File Template

- `roles/flask_backend/templates/env.j2`: Template for the `.env` file used by the Flask application.

### Systemd Service File for Gunicorn

- `roles/flask_backend/templates/todolist.service.j2`: Template for the Gunicorn service file.

## Deployment Commands

List of all commands used in the terminal for successful deployment of the application.

## Variables and Secrets

Details of all Ansible vars and secrets used in the project, including the Ansible Vault for sensitive data.

---

## Additional Notes

- Ensure AWS credentials are configured correctly for Terraform and Ansible to interact with AWS services.
- Validate the syntax and paths in the Terraform and Ansible configurations before executing the scripts.
- Regularly update the Ansible roles and tasks as per the application's evolving requirements.

---

## Conclusion

This document serves as a comprehensive guide and reference for deploying and managing the Todo-List Flask application using Terraform and Ansible on AWS.
