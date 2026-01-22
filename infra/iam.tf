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
  name               = "temu-event-log-simulation-terraform-role"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json
}

# Attach S3 write policy to the role
data "aws_iam_policy_document" "ec2_s3_policy" {
  statement {
    effect = "Allow"

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "${aws_s3_bucket.bucket1.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "ec2_s3_policy" {
  name   = "temu-event-log-simulation-s3-terraform-policy"
  policy = data.aws_iam_policy_document.ec2_s3_policy.json
}

resource "aws_iam_role_policy_attachment" "attach_policy" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_s3_policy.arn
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "ec2_instance_profile" {
  name = "temu-event-log-simulation-terraform-instance-profile"
  role = aws_iam_role.ec2_role.name
}
