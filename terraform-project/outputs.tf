#outputs.tf
output "backend_server_ip" {
  value = module.backend_server.instance_public_ips
}

output "database_server_ip" {
  value = module.database_server.instance_public_ips
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend_bucket.bucket
}