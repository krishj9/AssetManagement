# Infrastructure Outputs

# DynamoDB Outputs
output "dynamodb_table_names" {
  description = "Names of created DynamoDB tables"
  value       = module.dynamodb.table_names
}

output "dynamodb_table_arns" {
  description = "ARNs of created DynamoDB tables"
  value       = module.dynamodb.table_arns
}

output "dynamodb_kms_key_id" {
  description = "ID of the KMS key used for DynamoDB encryption"
  value       = module.dynamodb.kms_key_id
}

# IAM Outputs
output "bedrock_agent_execution_role_arn" {
  description = "ARN of the Bedrock Agent execution role"
  value       = module.iam.bedrock_agent_execution_role_arn
}

output "backend_application_role_arn" {
  description = "ARN of the Backend application role"
  value       = module.iam.backend_application_role_arn
}

# Bedrock Outputs
output "guardrail_id" {
  description = "ID of the Bedrock Guardrail"
  value       = module.bedrock_agents.guardrail_id
}

output "bedrock_agent_ids" {
  description = "IDs of created Bedrock agents"
  value       = module.bedrock_agents.agent_ids
  sensitive   = true
}

output "bedrock_agent_arns" {
  description = "ARNs of created Bedrock agents"
  value       = module.bedrock_agents.agent_arns
  sensitive   = true
}

output "bedrock_alias_ids" {
  description = "IDs of Bedrock agent aliases"
  value       = module.bedrock_agents.alias_ids
  sensitive   = true
}

output "supervisor_agent_id" {
  description = "ID of the Supervisor Agent"
  value       = module.bedrock_agents.supervisor_agent_id
  sensitive   = true
}

output "supervisor_alias_id" {
  description = "ID of the Supervisor Agent alias"
  value       = module.bedrock_agents.supervisor_alias_id
  sensitive   = true
}

# CloudWatch Outputs
output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = {
    backend = module.cloudwatch.backend_log_group_name
    agents  = module.cloudwatch.agents_log_group_name
    audit   = module.cloudwatch.audit_log_group_name
  }
}

output "cloudwatch_dashboards" {
  description = "CloudWatch dashboard names"
  value = {
    executive_workflow = module.cloudwatch.executive_dashboard_name
    agent_performance  = module.cloudwatch.agent_performance_dashboard_name
  }
}

output "alarms_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value       = module.cloudwatch.alarms_topic_arn
}

# API Gateway Outputs
output "api_gateway_url" {
  description = "API Gateway endpoint URL"
  value       = module.api_gateway.api_url
}

output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = module.api_gateway.api_id
}

output "api_key_value" {
  description = "Value of the API Gateway API key"
  value       = module.api_gateway.api_key_value
  sensitive   = true
}

# Summary Output
output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment         = var.environment
    region              = local.region
    dynamodb_tables     = module.dynamodb.table_names
    bedrock_agents      = keys(module.bedrock_agents.agent_ids)
    api_gateway_url     = module.api_gateway.api_url
    cloudwatch_dashboards = [
      module.cloudwatch.executive_dashboard_name,
      module.cloudwatch.agent_performance_dashboard_name
    ]
  }
}
