provider "aws" {
  region = "eu-north-1"
}

resource "aws_s3_bucket" "bucket1" {
  bucket = "temu-event-log-simulation-terraform-bucket"
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket that stores event logs"
  value       = aws_s3_bucket.bucket1.arn
}
