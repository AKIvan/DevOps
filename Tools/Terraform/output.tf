output "iam_user_arns" {
  description = "ARNs of the created IAM users"
  value       = module.iam.iam_user_arns
}

output "iam_group_arns" {
  description = "ARNs of the created IAM groups"
  value       = module.iam.iam_group_arns
}
