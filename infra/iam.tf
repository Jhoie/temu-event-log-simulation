data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "ec2_role" {
  name               = "${var.project_name}-${var.environment}-ec2-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

    tags = merge(local.common_tags, {
        Name = "${var.project_name}-${var.environment}-ec2-role"
    })
}

# Attach S3 write policy to the role
data "aws_iam_policy_document" "ec2_s3_policy" {
  statement {
    effect = "Allow"
    actions = ["s3:ListBucket"]

    resources = [aws_s3_bucket.event_logs.arn]
  }

  statement {
    effect = "Allow"

    actions = ["s3:PutObject", "s3:GetObject", "s3:AbortMultipartUpload"]

    resources = ["${aws_s3_bucket.event_logs.arn}/*"]
  }
}

resource "aws_iam_policy" "ec2_s3_policy" {
  name   = "${var.project_name}-${var.environment}-ec2-s3-policy"
  description = "IAM policy for EC2 instance to access S3 bucket for event log storage"
  policy = data.aws_iam_policy_document.ec2_s3_policy.json

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-ec2-s3-policy"
  })
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_s3_policy.arn
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "${var.project_name}-${var.environment}-instance-profile"
  role = aws_iam_role.ec2_role.name

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-instance-profile"
  })
}
