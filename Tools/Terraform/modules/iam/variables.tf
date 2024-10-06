variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
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
