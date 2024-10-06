locals {
  policy_arn_map = {
    "AdministratorAccess" = "arn:aws:iam::aws:policy/AdministratorAccess"
    "ReadOnlyAccess"      = "arn:aws:iam::aws:policy/ReadOnlyAccess"
    "AmazonS3FullAccess"  = "arn:aws:iam::aws:policy/AmazonS3FullAccess"

  }

  group_policy_attachments = flatten([
    for group in var.groups : [
      for policy in group.policies : {
        group_name  = group.name
        policy_name = policy
        policy_arn  = lookup(local.policy_arn_map, policy, policy)
      }
    ]
  ])
}

resource "aws_iam_group" "groups" {
  for_each = { for group in var.groups : group.name => group }

  name = each.value.name
}

resource "aws_iam_group_policy_attachment" "group_policies" {
  for_each = {
    for attachment in local.group_policy_attachments :
    "${attachment.group_name}-${attachment.policy_name}" => attachment
  }

  group      = aws_iam_group.groups[each.value.group_name].name
  policy_arn = each.value.policy_arn
}

resource "aws_iam_user" "users" {
  for_each = { for user in var.users : user.name => user }

  name = each.value.name

  tags = {
    Name        = each.value.name
    Environment = var.environment
  }
}

resource "aws_iam_user_group_membership" "user_group_membership" {
  for_each = { for user in var.users : user.name => user }

  user   = aws_iam_user.users[each.value.name].name
  groups = [aws_iam_group.groups[each.value.group].name]
}
