# API Gateway Module Variables

variable "environment" {
  description = "Environment name (dev, test, pre-prod, prod)"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "v1"
}

variable "throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 5000
}

variable "throttle_rate_limit" {
  description = "API Gateway throttle rate limit (requests per second)"
  type        = number
  default     = 10000
}

variable "backend_endpoint_url" {
  description = "Backend FastAPI endpoint URL for API Gateway integration"
  type        = string
  default     = "http://localhost:8000"
}

variable "cloudwatch_log_group_arn" {
  description = "ARN of CloudWatch log group for API Gateway access logs"
  type        = string
  default     = ""
}
