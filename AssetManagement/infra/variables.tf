# Bedrock Multi-Agent Portfolio Platform - Variables

variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, test, pre-prod, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "test", "pre-prod", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, pre-prod, prod"
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "bedrock-portfolio-platform"
}

# DynamoDB Variables
variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "dynamodb_point_in_time_recovery" {
  description = "Enable point-in-time recovery for DynamoDB tables"
  type        = bool
  default     = true
}

# Bedrock Variables
variable "bedrock_model_id" {
  description = "Bedrock model ID for agents"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "bedrock_guardrail_id" {
  description = "Bedrock Guardrail ID (optional)"
  type        = string
  default     = ""
}

# API Gateway Variables
variable "api_gateway_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "v1"
}

variable "api_gateway_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 5000
}

variable "api_gateway_throttle_rate_limit" {
  description = "API Gateway throttle rate limit"
  type        = number
  default     = 10000
}

# CloudWatch Variables
variable "cloudwatch_log_retention_days" {
  description = "CloudWatch Logs retention period in days"
  type        = number
  default     = 30
}

variable "cloudwatch_alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = ""
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
