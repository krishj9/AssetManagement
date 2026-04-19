# CloudWatch Module Outputs

output "backend_log_group_name" {
  description = "Name of the backend application log group"
  value       = aws_cloudwatch_log_group.backend_application.name
}

output "backend_log_group_arn" {
  description = "ARN of the backend application log group"
  value       = aws_cloudwatch_log_group.backend_application.arn
}

output "agents_log_group_name" {
  description = "Name of the agents log group"
  value       = aws_cloudwatch_log_group.bedrock_agents.name
}

output "agents_log_group_arn" {
  description = "ARN of the agents log group"
  value       = aws_cloudwatch_log_group.bedrock_agents.arn
}

output "audit_log_group_name" {
  description = "Name of the audit events log group"
  value       = aws_cloudwatch_log_group.audit_events.name
}

output "audit_log_group_arn" {
  description = "ARN of the audit events log group"
  value       = aws_cloudwatch_log_group.audit_events.arn
}

output "alarms_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value       = aws_sns_topic.alarms.arn
}

output "executive_dashboard_name" {
  description = "Name of the executive workflow dashboard"
  value       = aws_cloudwatch_dashboard.executive_workflow.dashboard_name
}

output "agent_performance_dashboard_name" {
  description = "Name of the agent performance dashboard"
  value       = aws_cloudwatch_dashboard.agent_performance.dashboard_name
}
