# IAM Module - Roles and Policies

# Bedrock Agent Execution Role
resource "aws_iam_role" "bedrock_agent_execution" {
  name = "${var.environment}-bedrock-agent-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = var.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock:*:${var.account_id}:agent/*"
          }
        }
      }
    ]
  })
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-bedrock-agent-execution-role"
    }
  )
}

# Policy for Bedrock Agent to invoke foundation models
resource "aws_iam_role_policy" "bedrock_agent_model_invocation" {
  name = "${var.environment}-bedrock-agent-model-invocation"
  role = aws_iam_role.bedrock_agent_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/*"
        ]
      }
    ]
  })
}

# Policy for Bedrock Agent to invoke other agents (collaborators)
resource "aws_iam_role_policy" "bedrock_agent_collaboration" {
  name = "${var.environment}-bedrock-agent-collaboration"
  role = aws_iam_role.bedrock_agent_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeAgent"
        ]
        Resource = [
          "arn:aws:bedrock:*:${var.account_id}:agent/*",
          "arn:aws:bedrock:*:${var.account_id}:agent-alias/*"
        ]
      }
    ]
  })
}

# Policy for Bedrock Agent to use Guardrails
resource "aws_iam_role_policy" "bedrock_agent_guardrails" {
  name = "${var.environment}-bedrock-agent-guardrails"
  role = aws_iam_role.bedrock_agent_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:ApplyGuardrail"
        ]
        Resource = [
          "arn:aws:bedrock:*:${var.account_id}:guardrail/*"
        ]
      }
    ]
  })
}

# Backend Application Role (for FastAPI)
resource "aws_iam_role" "backend_application" {
  name = "${var.environment}-backend-application-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = [
            "lambda.amazonaws.com",
            "ecs-tasks.amazonaws.com"
          ]
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-backend-application-role"
    }
  )
}

# Policy for Backend to access DynamoDB tables
resource "aws_iam_role_policy" "backend_dynamodb_access" {
  name = "${var.environment}-backend-dynamodb-access"
  role = aws_iam_role.backend_application.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem",
          "dynamodb:ConditionCheckItem"
        ]
        Resource = var.dynamodb_table_arns
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query"
        ]
        Resource = [
          for arn in var.dynamodb_table_arns : "${arn}/index/*"
        ]
      }
    ]
  })
}

# Policy for Backend to invoke Bedrock agents
resource "aws_iam_role_policy" "backend_bedrock_agent_invocation" {
  name = "${var.environment}-backend-bedrock-agent-invocation"
  role = aws_iam_role.backend_application.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeAgent"
        ]
        Resource = [
          "arn:aws:bedrock:*:${var.account_id}:agent/*",
          "arn:aws:bedrock:*:${var.account_id}:agent-alias/*"
        ]
      }
    ]
  })
}

# Policy for Backend to use Bedrock Guardrails
resource "aws_iam_role_policy" "backend_bedrock_guardrails" {
  name = "${var.environment}-backend-bedrock-guardrails"
  role = aws_iam_role.backend_application.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:ApplyGuardrail"
        ]
        Resource = [
          "arn:aws:bedrock:*:${var.account_id}:guardrail/*"
        ]
      }
    ]
  })
}

# Policy for Backend to write CloudWatch Logs
resource "aws_iam_role_policy" "backend_cloudwatch_logs" {
  name = "${var.environment}-backend-cloudwatch-logs"
  role = aws_iam_role.backend_application.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:*:${var.account_id}:log-group:/aws/portfolio-platform/*"
        ]
      }
    ]
  })
}

# Policy for Backend to publish CloudWatch Metrics
resource "aws_iam_role_policy" "backend_cloudwatch_metrics" {
  name = "${var.environment}-backend-cloudwatch-metrics"
  role = aws_iam_role.backend_application.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "PortfolioPlatform"
          }
        }
      }
    ]
  })
}

# Policy for Backend to access KMS keys for DynamoDB encryption
resource "aws_iam_role_policy" "backend_kms_access" {
  name = "${var.environment}-backend-kms-access"
  role = aws_iam_role.backend_application.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:GenerateDataKey"
        ]
        Resource = var.kms_key_arns
      }
    ]
  })
}

# Attach AWS managed policy for Lambda basic execution (if using Lambda)
resource "aws_iam_role_policy_attachment" "backend_lambda_basic_execution" {
  role       = aws_iam_role.backend_application.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
