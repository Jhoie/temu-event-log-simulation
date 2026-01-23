resource "aws_key_pair" "temu_key" {
  key_name   = "temu-ec2-key"
  public_key = file("~/.ssh/temu-ec2.pub")
}

resource "aws_security_group" "ssh_only" {
  name        = "temu-ssh-only"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create instance
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_instance" "temu_ec2" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.temu_key.key_name
  vpc_security_group_ids = [aws_security_group.ssh_only.id]

  iam_instance_profile = aws_iam_instance_profile.ec2_instance_profile.name

  tags = {
    Name = "temu-ec2-instance"
  }
}

output "ec2_public_ip" {
  value = aws_instance.temu_ec2.public_ip
}


