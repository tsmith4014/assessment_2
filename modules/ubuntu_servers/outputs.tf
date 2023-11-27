#outputs.tf
output "instance_public_ips" {
  value = aws_instance.ubuntu_server[*].public_ip
}
