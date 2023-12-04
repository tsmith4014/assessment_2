#iam.tf

/**
 * This Terraform code defines IAM resources for granting EC2 instances access to an S3 bucket.
 * 
 * Resources:
 * - aws_iam_role.ec2_s3_role: IAM role that allows EC2 instances to assume the role.
 * - aws_iam_policy.s3_access: IAM policy that grants access to specific S3 bucket actions.
 * - aws_iam_role_policy_attachment.s3_access_attachment: Attaches the IAM policy to the IAM role.
 * - aws_iam_instance_profile.ec2_s3_profile: IAM instance profile that associates the IAM role with EC2 instances.
 */
resource "aws_iam_role" "ec2_s3_role" {
  name = "ec2_s3_access_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "s3_access" {
  name        = "S3AccessPolicy"
  description = "Policy that allows EC2 to access specific S3 Bucket"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:DeleteObject",
          "s3:ListBucket"
        ],
        Resource = [
          aws_s3_bucket.frontend_bucket.arn,
          "${aws_s3_bucket.frontend_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.ec2_s3_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_instance_profile" "ec2_s3_profile" {
  name = "ec2_s3_profile"
  role = aws_iam_role.ec2_s3_role.name
}
