# DynamoDB Module Variables

variable "environment" {
  description = "Environment name (dev, test, pre-prod, prod)"
  type        = string
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "point_in_time_recovery" {
  description = "Enable point-in-time recovery for DynamoDB tables"
  type        = bool
  default     = true
}

variable "approval_artifacts_ttl_days" {
  description = "TTL retention period for approval artifacts in days"
  type        = number
  default     = 90
}

variable "audit_events_ttl_days" {
  description = "TTL retention period for audit events in days"
  type        = number
  default     = 2555  # 7 years
}

variable "session_state_ttl_hours" {
  description = "TTL retention period for session state in hours"
  type        = number
  default     = 24
}

variable "memory_consolidation_queue_ttl_days" {
  description = "TTL retention period for memory consolidation queue in days"
  type        = number
  default     = 30
}
