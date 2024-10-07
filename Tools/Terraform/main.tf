terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "iam" {
  source = "./modules/iam"


  aws_region  = "us-west-2"
  environment = "dev"
  aws_region  = var.aws_region 
  environment = var.environment
  groups      = var.groups
  users       = var.users
}
