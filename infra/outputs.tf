output "s3_bucket_name" {
  description = "S3 bucket where synthetic event logs are stored."
  value       = aws_s3_bucket.event_logs
}

output "ec2_public_ip" {
  description = "Public IPv4 address of the EC2 instance."
  value       = aws_instance.temu_ec2.public_ip
}
