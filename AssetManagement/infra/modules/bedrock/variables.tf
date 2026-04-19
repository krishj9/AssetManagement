# Bedrock Module Variables

variable "environment" {
  description = "Environment name (dev, test, pre-prod, prod)"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "bedrock_model_id" {
  description = "Bedrock foundation model ID for agents"
  type        = string
  default     = "anthropic.claude-3-sonnet-20240229-v1:0"
}

variable "bedrock_agent_execution_role_arn" {
  description = "ARN of the IAM role for Bedrock agent execution"
  type        = string
}
