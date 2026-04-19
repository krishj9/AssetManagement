# IAM Module Outputs

output "bedrock_agent_execution_role_arn" {
  description = "ARN of the Bedrock Agent execution role"
  value       = aws_iam_role.bedrock_agent_execution.arn
}

output "bedrock_agent_execution_role_name" {
  description = "Name of the Bedrock Agent execution role"
  value       = aws_iam_role.bedrock_agent_execution.name
}

output "backend_application_role_arn" {
  description = "ARN of the Backend application role"
  value       = aws_iam_role.backend_application.arn
}

output "backend_application_role_name" {
  description = "Name of the Backend application role"
  value       = aws_iam_role.backend_application.name
}
