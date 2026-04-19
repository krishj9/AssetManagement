# Bedrock Module Outputs

output "guardrail_id" {
  description = "ID of the Bedrock Guardrail"
  value       = aws_bedrockagent_guardrail.portfolio_platform.guardrail_id
}

output "guardrail_arn" {
  description = "ARN of the Bedrock Guardrail"
  value       = aws_bedrockagent_guardrail.portfolio_platform.guardrail_arn
}

output "supervisor_agent_id" {
  description = "ID of the Supervisor Agent"
  value       = aws_bedrockagent_agent.supervisor.agent_id
}

output "supervisor_agent_arn" {
  description = "ARN of the Supervisor Agent"
  value       = aws_bedrockagent_agent.supervisor.agent_arn
}

output "supervisor_alias_id" {
  description = "ID of the Supervisor Agent alias"
  value       = aws_bedrockagent_agent_alias.supervisor.agent_alias_id
}

output "research_agent_id" {
  description = "ID of the Research Agent"
  value       = aws_bedrockagent_agent.research.agent_id
}

output "research_agent_arn" {
  description = "ARN of the Research Agent"
  value       = aws_bedrockagent_agent.research.agent_arn
}

output "research_alias_id" {
  description = "ID of the Research Agent alias"
  value       = aws_bedrockagent_agent_alias.research.agent_alias_id
}

output "memory_agent_id" {
  description = "ID of the Memory & Personalization Agent"
  value       = aws_bedrockagent_agent.memory.agent_id
}

output "memory_agent_arn" {
  description = "ARN of the Memory & Personalization Agent"
  value       = aws_bedrockagent_agent.memory.agent_arn
}

output "memory_alias_id" {
  description = "ID of the Memory & Personalization Agent alias"
  value       = aws_bedrockagent_agent_alias.memory.agent_alias_id
}

output "compliance_agent_id" {
  description = "ID of the Risk & Compliance Agent"
  value       = aws_bedrockagent_agent.compliance.agent_id
}

output "compliance_agent_arn" {
  description = "ARN of the Risk & Compliance Agent"
  value       = aws_bedrockagent_agent.compliance.agent_arn
}

output "compliance_alias_id" {
  description = "ID of the Risk & Compliance Agent alias"
  value       = aws_bedrockagent_agent_alias.compliance.agent_alias_id
}

output "execution_agent_id" {
  description = "ID of the Execution Agent"
  value       = aws_bedrockagent_agent.execution.agent_id
}

output "execution_agent_arn" {
  description = "ARN of the Execution Agent"
  value       = aws_bedrockagent_agent.execution.agent_arn
}

output "execution_alias_id" {
  description = "ID of the Execution Agent alias"
  value       = aws_bedrockagent_agent_alias.execution.agent_alias_id
}

output "agent_ids" {
  description = "Map of all agent IDs"
  value = {
    supervisor  = aws_bedrockagent_agent.supervisor.agent_id
    research    = aws_bedrockagent_agent.research.agent_id
    memory      = aws_bedrockagent_agent.memory.agent_id
    compliance  = aws_bedrockagent_agent.compliance.agent_id
    execution   = aws_bedrockagent_agent.execution.agent_id
  }
}

output "agent_arns" {
  description = "Map of all agent ARNs"
  value = {
    supervisor  = aws_bedrockagent_agent.supervisor.agent_arn
    research    = aws_bedrockagent_agent.research.agent_arn
    memory      = aws_bedrockagent_agent.memory.agent_arn
    compliance  = aws_bedrockagent_agent.compliance.agent_arn
    execution   = aws_bedrockagent_agent.execution.agent_arn
  }
}

output "alias_ids" {
  description = "Map of all agent alias IDs"
  value = {
    supervisor  = aws_bedrockagent_agent_alias.supervisor.agent_alias_id
    research    = aws_bedrockagent_agent_alias.research.agent_alias_id
    memory      = aws_bedrockagent_agent_alias.memory.agent_alias_id
    compliance  = aws_bedrockagent_agent_alias.compliance.agent_alias_id
    execution   = aws_bedrockagent_agent_alias.execution.agent_alias_id
  }
}
