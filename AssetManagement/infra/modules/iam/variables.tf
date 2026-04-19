# IAM Module Variables

variable "environment" {
  description = "Environment name (dev, test, pre-prod, prod)"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "dynamodb_table_arns" {
  description = "List of DynamoDB table ARNs for IAM policy"
  type        = list(string)
  default     = []
}

variable "kms_key_arns" {
  description = "List of KMS key ARNs for IAM policy"
  type        = list(string)
  default     = []
}
