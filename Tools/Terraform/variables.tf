variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "groups" {
  description = "List of IAM groups with their associated policies"
  type = list(object({
    name     = string
    policies = list(string)
  }))
}

variable "users" {
  description = "List of IAM users with their group assignments"
  type = list(object({
    name  = string
    group = string
  }))
}
