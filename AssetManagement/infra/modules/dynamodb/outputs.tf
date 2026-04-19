# DynamoDB Module Outputs

output "approval_artifacts_table_name" {
  description = "Name of the Approval Artifacts DynamoDB table"
  value       = aws_dynamodb_table.approval_artifacts.name
}

output "approval_artifacts_table_arn" {
  description = "ARN of the Approval Artifacts DynamoDB table"
  value       = aws_dynamodb_table.approval_artifacts.arn
}

output "audit_events_table_name" {
  description = "Name of the Audit Events DynamoDB table"
  value       = aws_dynamodb_table.audit_events.name
}

output "audit_events_table_arn" {
  description = "ARN of the Audit Events DynamoDB table"
  value       = aws_dynamodb_table.audit_events.arn
}

output "session_state_table_name" {
  description = "Name of the Session State DynamoDB table"
  value       = aws_dynamodb_table.session_state.name
}

output "session_state_table_arn" {
  description = "ARN of the Session State DynamoDB table"
  value       = aws_dynamodb_table.session_state.arn
}

output "memory_consolidation_queue_table_name" {
  description = "Name of the Memory Consolidation Queue DynamoDB table"
  value       = aws_dynamodb_table.memory_consolidation_queue.name
}

output "memory_consolidation_queue_table_arn" {
  description = "ARN of the Memory Consolidation Queue DynamoDB table"
  value       = aws_dynamodb_table.memory_consolidation_queue.arn
}

output "kms_key_id" {
  description = "ID of the KMS key used for DynamoDB encryption"
  value       = aws_kms_key.dynamodb.id
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for DynamoDB encryption"
  value       = aws_kms_key.dynamodb.arn
}

output "table_names" {
  description = "Map of all DynamoDB table names"
  value = {
    approval_artifacts          = aws_dynamodb_table.approval_artifacts.name
    audit_events                = aws_dynamodb_table.audit_events.name
    session_state               = aws_dynamodb_table.session_state.name
    memory_consolidation_queue  = aws_dynamodb_table.memory_consolidation_queue.name
  }
}

output "table_arns" {
  description = "Map of all DynamoDB table ARNs"
  value = {
    approval_artifacts          = aws_dynamodb_table.approval_artifacts.arn
    audit_events                = aws_dynamodb_table.audit_events.arn
    session_state               = aws_dynamodb_table.session_state.arn
    memory_consolidation_queue  = aws_dynamodb_table.memory_consolidation_queue.arn
  }
}
