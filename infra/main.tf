provider "aws" {
  region = "eu-north-1"
}

resource "aws_s3_bucket" "bucket1" {
  bucket = "temu-event-log-simulation-terraform-bucket"
}


