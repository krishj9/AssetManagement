# Bedrock Agents Module

# Bedrock Guardrail
resource "aws_bedrockagent_guardrail" "portfolio_platform" {
  name                      = "${var.environment}-portfolio-platform-guardrail"
  description               = "Guardrail for portfolio platform agents - prevents harmful content, unsupported claims, and sensitive information leakage"
  blocked_input_messaging   = "I cannot process this request as it contains content that violates our policies."
  blocked_outputs_messaging = "I cannot provide this response as it contains content that violates our policies."
  
  # Content policy configuration
  content_policy_config {
    # Block harmful content
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "HATE"
    }
    
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "VIOLENCE"
    }
    
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
      type            = "SEXUAL"
    }
    
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
      type            = "MISCONDUCT"
    }
  }
  
  # Sensitive information policy
  sensitive_information_policy_config {
    # Block PII
    pii_entities_config {
      action = "BLOCK"
      type   = "EMAIL"
    }
    
    pii_entities_config {
      action = "BLOCK"
      type   = "PHONE"
    }
    
    pii_entities_config {
      action = "BLOCK"
      type   = "SSN"
    }
    
    pii_entities_config {
      action = "BLOCK"
      type   = "CREDIT_DEBIT_CARD_NUMBER"
    }
    
    # Block financial account numbers
    pii_entities_config {
      action = "BLOCK"
      type   = "US_BANK_ACCOUNT_NUMBER"
    }
  }
  
  # Topic policy - denied topics
  topic_policy_config {
    topics_config {
      name       = "unsupported-performance-claims"
      definition = "Claims about guaranteed returns, risk-free investments, or specific future performance outcomes"
      examples   = [
        "This investment will definitely return 20% annually",
        "This is a risk-free opportunity",
        "You will make money with this strategy"
      ]
      type = "DENY"
    }
    
    topics_config {
      name       = "fabricated-market-facts"
      definition = "Invented or unverifiable market data, statistics, or financial information"
      examples   = [
        "According to a study I just made up",
        "The market always goes up in Q4",
        "This stock has never lost value"
      ]
      type = "DENY"
    }
    
    topics_config {
      name       = "mandate-bypass-attempts"
      definition = "Attempts to circumvent investment mandates, suitability rules, or compliance constraints"
      examples   = [
        "Let's ignore the mandate for this one trade",
        "We can work around the suitability rules",
        "The compliance check doesn't apply here"
      ]
      type = "DENY"
    }
  }
  
  # Word policy - blocked terms
  word_policy_config {
    words_config {
      text = "guaranteed returns"
    }
    
    words_config {
      text = "risk-free"
    }
    
    words_config {
      text = "can't lose"
    }
    
    managed_word_lists_config {
      type = "PROFANITY"
    }
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-portfolio-platform-guardrail"
    }
  )
}

# Supervisor Agent
resource "aws_bedrockagent_agent" "supervisor" {
  agent_name              = "${var.environment}-supervisor-agent"
  agent_resource_role_arn = var.bedrock_agent_execution_role_arn
  foundation_model        = var.bedrock_model_id
  description             = "Supervisor Agent - orchestrates collaborator agents and consolidates outputs"
  
  instruction = file("${path.module}/instructions/supervisor_instructions.txt")
  
  guardrail_configuration {
    guardrail_identifier = aws_bedrockagent_guardrail.portfolio_platform.guardrail_id
    guardrail_version    = "DRAFT"
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-supervisor-agent"
      Role = "Supervisor"
    }
  )
}

# Research Agent
resource "aws_bedrockagent_agent" "research" {
  agent_name              = "${var.environment}-research-agent"
  agent_resource_role_arn = var.bedrock_agent_execution_role_arn
  foundation_model        = var.bedrock_model_id
  description             = "Research Agent - retrieves market data and generates sentiment summaries"
  
  instruction = file("${path.module}/instructions/research_instructions.txt")
  
  guardrail_configuration {
    guardrail_identifier = aws_bedrockagent_guardrail.portfolio_platform.guardrail_id
    guardrail_version    = "DRAFT"
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-research-agent"
      Role = "Research"
    }
  )
}

# Memory & Personalization Agent
resource "aws_bedrockagent_agent" "memory" {
  agent_name              = "${var.environment}-memory-agent"
  agent_resource_role_arn = var.bedrock_agent_execution_role_arn
  foundation_model        = var.bedrock_model_id
  description             = "Memory & Personalization Agent - retrieves and manages client memory"
  
  instruction = file("${path.module}/instructions/memory_instructions.txt")
  
  guardrail_configuration {
    guardrail_identifier = aws_bedrockagent_guardrail.portfolio_platform.guardrail_id
    guardrail_version    = "DRAFT"
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-memory-agent"
      Role = "Memory"
    }
  )
}

# Risk & Compliance Agent
resource "aws_bedrockagent_agent" "compliance" {
  agent_name              = "${var.environment}-compliance-agent"
  agent_resource_role_arn = var.bedrock_agent_execution_role_arn
  foundation_model        = var.bedrock_model_id
  description             = "Risk & Compliance Agent - evaluates portfolio drift and compliance"
  
  instruction = file("${path.module}/instructions/compliance_instructions.txt")
  
  guardrail_configuration {
    guardrail_identifier = aws_bedrockagent_guardrail.portfolio_platform.guardrail_id
    guardrail_version    = "DRAFT"
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-compliance-agent"
      Role = "Compliance"
    }
  )
}

# Execution Agent
resource "aws_bedrockagent_agent" "execution" {
  agent_name              = "${var.environment}-execution-agent"
  agent_resource_role_arn = var.bedrock_agent_execution_role_arn
  foundation_model        = var.bedrock_model_id
  description             = "Execution Agent - generates trade proposals and calculates impacts"
  
  instruction = file("${path.module}/instructions/execution_instructions.txt")
  
  guardrail_configuration {
    guardrail_identifier = aws_bedrockagent_guardrail.portfolio_platform.guardrail_id
    guardrail_version    = "DRAFT"
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-execution-agent"
      Role = "Execution"
    }
  )
}

# Agent Aliases for environment-specific deployment
resource "aws_bedrockagent_agent_alias" "supervisor" {
  agent_alias_name = var.environment
  agent_id         = aws_bedrockagent_agent.supervisor.agent_id
  description      = "Alias for ${var.environment} environment"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-supervisor-alias"
    }
  )
}

resource "aws_bedrockagent_agent_alias" "research" {
  agent_alias_name = var.environment
  agent_id         = aws_bedrockagent_agent.research.agent_id
  description      = "Alias for ${var.environment} environment"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-research-alias"
    }
  )
}

resource "aws_bedrockagent_agent_alias" "memory" {
  agent_alias_name = var.environment
  agent_id         = aws_bedrockagent_agent.memory.agent_id
  description      = "Alias for ${var.environment} environment"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-memory-alias"
    }
  )
}

resource "aws_bedrockagent_agent_alias" "compliance" {
  agent_alias_name = var.environment
  agent_id         = aws_bedrockagent_agent.compliance.agent_id
  description      = "Alias for ${var.environment} environment"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-compliance-alias"
    }
  )
}

resource "aws_bedrockagent_agent_alias" "execution" {
  agent_alias_name = var.environment
  agent_id         = aws_bedrockagent_agent.execution.agent_id
  description      = "Alias for ${var.environment} environment"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-execution-alias"
    }
  )
}
