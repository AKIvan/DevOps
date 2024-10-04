output "iam_user_arns" {
  description = "ARNs of the created IAM users"
  value       = { for user_name, user in aws_iam_user.users : user_name => user.arn }
}

output "iam_group_arns" {
  description = "ARNs of the created IAM groups"
  value       = { for group_name, group in aws_iam_group.groups : group_name => group.arn }
}
