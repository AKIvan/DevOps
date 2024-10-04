aws_region  = "us-east-1"
environment = "dev"

groups = [
  {
    name     = "admin"
    policies = ["AdministratorAccess"]
  },
  {
    name     = "read-only"
    policies = ["ReadOnlyAccess"]
  }
]

users = [
  {
    name  = "user1"
    group = "admin"
  },
  {
    name  = "user2"
    group = "read-only"
  }
]
