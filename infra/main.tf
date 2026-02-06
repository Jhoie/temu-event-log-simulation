locals {
  common_tags = {
    project = var.project_name
    environment = var.environment
    managed_by = "terraform"
  }
}

resource "aws_s3_bucket" "event_logs" {
  bucket = var.bucket_name
  force_destroy = true
  tags  = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-bucket"
  })
}

resource "aws_s3_bucket_versioning" "event_logs_versioning" {
  bucket = aws_s3_bucket.event_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "event_logs_access" {
  bucket = aws_s3_bucket.event_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "event_logs_encryption" {
    bucket = aws_s3_bucket.event_logs.id
    
    rule {
        apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
        }
    }
  
}

data "aws_iam_policy_document" "event_logs_bucket_policy" {
    statement {
        sid = "AllowEC2ListObject"
        effect = "Allow"

        principals {
        type        = "AWS"
        identifiers = [aws_iam_role.ec2_role.arn]
        }

        actions = ["s3:ListBucket"]
        resources = [aws_s3_bucket.event_logs.arn]
    }

    statement {
        sid = "AllowEC2PutObject"
        effect = "Allow"

        principals {
        type        = "AWS"
        identifiers = [aws_iam_role.ec2_role.arn]
        }

        actions = ["s3:PutObject", "s3:GetObject", "s3:AbortMultipartUpload"]
        resources = ["${aws_s3_bucket.event_logs.arn}/*"]
    } 
}

resource "aws_s3_bucket_policy" "event_logs_policy" {
  bucket = aws_s3_bucket.event_logs.id
  policy = data.aws_iam_policy_document.event_logs_bucket_policy.json

  depends_on = [aws_s3_bucket_public_access_block.event_logs_access]
}
