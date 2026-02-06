terraform {
  backend "s3" {
    bucket         = "temu-simulation-terraform-state"
    key            = "temu-event-log-simulation/dev/terraform.tfstate"
    region         = "eu-north-1"
    use_lockfile   = true
    encrypt        = true
  }
}
