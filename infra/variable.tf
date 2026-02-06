variable "aws_region" {
  type        = string
  description = "AWS region"
  default = "eu-north-1"
}

variable "project_name" {
  type        = string
  description = "Project name"
  default = "temu-event-log-simulation"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default = "dev"
}

variable "bucket_name" {
  type        = string
  description = "S3 bucket name"
}

variable "ssh_cidr" {
  type        = string
  description = "SSH CIDR"
}

variable "public_key_path" {
  type = string
  description = "Path to the public key for EC2 instance access"
}

variable "instance_type" {
    type        = string
    description = "EC2 instance type"
    default     = "t3.small"
}
