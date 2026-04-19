# DynamoDB Tables Module

# Approval Artifacts Table
resource "aws_dynamodb_table" "approval_artifacts" {
  name           = "${var.environment}-approval-artifacts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "approval_id"
  
  attribute {
    name = "approval_id"
    type = "S"
  }
  
  attribute {
    name = "request_id"
    type = "S"
  }
  
  # GSI for querying by request_id
  global_secondary_index {
    name            = "RequestIdIndex"
    hash_key        = "request_id"
    projection_type = "ALL"
  }
  
  # TTL for 90 days retention
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # Encryption at rest
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-approval-artifacts"
    }
  )
}

# Audit Events Table
resource "aws_dynamodb_table" "audit_events" {
  name           = "${var.environment}-audit-events"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "event_id"
  
  attribute {
    name = "event_id"
    type = "S"
  }
  
  attribute {
    name = "request_id"
    type = "S"
  }
  
  attribute {
    name = "trace_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  attribute {
    name = "event_type"
    type = "S"
  }
  
  # GSI1: Query by request_id + timestamp
  global_secondary_index {
    name            = "RequestIdTimestampIndex"
    hash_key        = "request_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  # GSI2: Query by trace_id + timestamp
  global_secondary_index {
    name            = "TraceIdTimestampIndex"
    hash_key        = "trace_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  # GSI3: Query by timestamp + event_type
  global_secondary_index {
    name            = "TimestampEventTypeIndex"
    hash_key        = "timestamp"
    range_key       = "event_type"
    projection_type = "ALL"
  }
  
  # TTL for 7 years retention (2555 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }
  
  # Encryption at rest
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-audit-events"
    }
  )
}

# Session State Table
resource "aws_dynamodb_table" "session_state" {
  name           = "${var.environment}-session-state"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"
  
  attribute {
    name = "session_id"
    type = "S"
  }
  
  # TTL for 24 hours retention
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Encryption at rest
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-session-state"
    }
  )
}

# Memory Consolidation Queue Table
resource "aws_dynamodb_table" "memory_consolidation_queue" {
  name           = "${var.environment}-memory-consolidation-queue"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "consolidation_id"
  
  attribute {
    name = "consolidation_id"
    type = "S"
  }
  
  attribute {
    name = "consolidation_status"
    type = "S"
  }
  
  attribute {
    name = "created_at"
    type = "S"
  }
  
  # GSI for querying by status
  global_secondary_index {
    name            = "StatusCreatedAtIndex"
    hash_key        = "consolidation_status"
    range_key       = "created_at"
    projection_type = "ALL"
  }
  
  # TTL for 30 days retention
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
  
  # Encryption at rest
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb.arn
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-memory-consolidation-queue"
    }
  )
}

# KMS Key for DynamoDB encryption
resource "aws_kms_key" "dynamodb" {
  description             = "KMS key for DynamoDB table encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-dynamodb-kms-key"
    }
  )
}

resource "aws_kms_alias" "dynamodb" {
  name          = "alias/${var.environment}-dynamodb"
  target_key_id = aws_kms_key.dynamodb.key_id
}
