groups = [
  {
    name     = "admin"
    policies = ["AdministratorAccess"]
  },
  {
    name     = "read-only"
    policies = ["ReadOnlyAccess"]
  },
  {
    name     = "s3-full-access"
    policies = ["AmazonS3FullAccess"]
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
  },
  {
    name  = "user3"
    group = "s3-full-access"
  }
]
