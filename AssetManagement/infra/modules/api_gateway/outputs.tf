# API Gateway Module Outputs

output "api_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.portfolio_platform.id
}

output "api_arn" {
  description = "ARN of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.portfolio_platform.arn
}

output "api_url" {
  description = "URL of the API Gateway endpoint"
  value       = aws_api_gateway_stage.portfolio_platform.invoke_url
}

output "stage_name" {
  description = "Name of the API Gateway stage"
  value       = aws_api_gateway_stage.portfolio_platform.stage_name
}

output "api_key_id" {
  description = "ID of the API Gateway API key"
  value       = aws_api_gateway_api_key.portfolio_platform.id
}

output "api_key_value" {
  description = "Value of the API Gateway API key"
  value       = aws_api_gateway_api_key.portfolio_platform.value
  sensitive   = true
}

output "usage_plan_id" {
  description = "ID of the API Gateway usage plan"
  value       = aws_api_gateway_usage_plan.portfolio_platform.id
}
