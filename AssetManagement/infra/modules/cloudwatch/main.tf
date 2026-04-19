# CloudWatch Module - Logs, Metrics, Dashboards, and Alarms

# Log Groups
resource "aws_cloudwatch_log_group" "backend_application" {
  name              = "/aws/portfolio-platform/${var.environment}/backend"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-backend-logs"
    }
  )
}

resource "aws_cloudwatch_log_group" "bedrock_agents" {
  name              = "/aws/portfolio-platform/${var.environment}/agents"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-agents-logs"
    }
  )
}

resource "aws_cloudwatch_log_group" "audit_events" {
  name              = "/aws/portfolio-platform/${var.environment}/audit"
  retention_in_days = 2555  # 7 years for audit logs
  kms_key_id        = aws_kms_key.cloudwatch_logs.arn
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-audit-logs"
    }
  )
}

# KMS Key for CloudWatch Logs encryption
resource "aws_kms_key" "cloudwatch_logs" {
  description             = "KMS key for CloudWatch Logs encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/aws/portfolio-platform/*"
          }
        }
      }
    ]
  })
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-cloudwatch-logs-kms-key"
    }
  )
}

resource "aws_kms_alias" "cloudwatch_logs" {
  name          = "alias/${var.environment}-cloudwatch-logs"
  target_key_id = aws_kms_key.cloudwatch_logs.key_id
}

data "aws_caller_identity" "current" {}

# SNS Topic for Alarms
resource "aws_sns_topic" "alarms" {
  name              = "${var.environment}-portfolio-platform-alarms"
  kms_master_key_id = aws_kms_key.cloudwatch_logs.id
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-alarms-topic"
    }
  )
}

resource "aws_sns_topic_subscription" "alarm_email" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# CloudWatch Dashboard - Executive Workflow
resource "aws_cloudwatch_dashboard" "executive_workflow" {
  dashboard_name = "${var.environment}-executive-workflow"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["PortfolioPlatform", "RequestVolume", { stat = "Sum", label = "Total Requests" }],
            [".", "SuccessfulRequests", { stat = "Sum", label = "Successful" }],
            [".", "FailedRequests", { stat = "Sum", label = "Failed" }]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Request Volume"
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["PortfolioPlatform", "RequestLatency", { stat = "Average", label = "Avg Latency" }],
            ["...", { stat = "p99", label = "P99 Latency" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Request Latency"
          yAxis = {
            left = {
              label = "Milliseconds"
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["PortfolioPlatform", "ErrorRate", { stat = "Average", label = "Error Rate" }],
            [".", "BlockedStateRate", { stat = "Average", label = "Blocked State Rate" }],
            [".", "DegradedModeRate", { stat = "Average", label = "Degraded Mode Rate" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Error and Degraded Rates"
          yAxis = {
            left = {
              label = "Percentage"
            }
          }
        }
      }
    ]
  })
}

data "aws_region" "current" {}

# CloudWatch Dashboard - Agent Performance
resource "aws_cloudwatch_dashboard" "agent_performance" {
  dashboard_name = "${var.environment}-agent-performance"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["PortfolioPlatform", "SupervisorLatency", { stat = "Average", label = "Supervisor" }],
            [".", "ResearchLatency", { stat = "Average", label = "Research" }],
            [".", "MemoryLatency", { stat = "Average", label = "Memory" }],
            [".", "ComplianceLatency", { stat = "Average", label = "Compliance" }],
            [".", "ExecutionLatency", { stat = "Average", label = "Execution" }]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Agent Latency"
          yAxis = {
            left = {
              label = "Milliseconds"
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["PortfolioPlatform", "SupervisorErrors", { stat = "Sum", label = "Supervisor" }],
            [".", "ResearchErrors", { stat = "Sum", label = "Research" }],
            [".", "MemoryErrors", { stat = "Sum", label = "Memory" }],
            [".", "ComplianceErrors", { stat = "Sum", label = "Compliance" }],
            [".", "ExecutionErrors", { stat = "Sum", label = "Execution" }]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Agent Errors"
        }
      }
    ]
  })
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.environment}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ErrorRate"
  namespace           = "PortfolioPlatform"
  period              = 300
  statistic           = "Average"
  threshold           = 5.0  # 5% error rate
  alarm_description   = "Error rate is above 5%"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-high-error-rate-alarm"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "high_blocked_state_rate" {
  alarm_name          = "${var.environment}-high-blocked-state-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "BlockedStateRate"
  namespace           = "PortfolioPlatform"
  period              = 300
  statistic           = "Average"
  threshold           = 10.0  # 10% blocked state rate
  alarm_description   = "Blocked state rate is above 10%"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-high-blocked-state-rate-alarm"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "high_latency" {
  alarm_name          = "${var.environment}-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RequestLatency"
  namespace           = "PortfolioPlatform"
  period              = 300
  statistic           = "Average"
  threshold           = 30000  # 30 seconds
  alarm_description   = "Request latency is above 30 seconds"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-high-latency-alarm"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "memory_failures" {
  alarm_name          = "${var.environment}-memory-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryErrors"
  namespace           = "PortfolioPlatform"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Memory agent errors exceed threshold"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-memory-failures-alarm"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "guardrail_spikes" {
  alarm_name          = "${var.environment}-guardrail-spikes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "GuardrailViolations"
  namespace           = "PortfolioPlatform"
  period              = 300
  statistic           = "Sum"
  threshold           = 20
  alarm_description   = "Guardrail violations exceed threshold"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-guardrail-spikes-alarm"
    }
  )
}
