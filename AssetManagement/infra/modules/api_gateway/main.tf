# API Gateway Module - REST API for FastAPI Backend

# API Gateway REST API
resource "aws_api_gateway_rest_api" "portfolio_platform" {
  name        = "${var.environment}-portfolio-platform-api"
  description = "API Gateway for Portfolio Platform Backend"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-portfolio-platform-api"
    }
  )
}

# API Gateway Resource - Proxy for all paths
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.portfolio_platform.id
  parent_id   = aws_api_gateway_rest_api.portfolio_platform.root_resource_id
  path_part   = "{proxy+}"
}

# API Gateway Method - ANY for proxy
resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.portfolio_platform.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "AWS_IAM"
}

# API Gateway Integration - Lambda or HTTP proxy
resource "aws_api_gateway_integration" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.portfolio_platform.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method
  
  # Use HTTP_PROXY for direct integration with FastAPI backend
  # Change to AWS_PROXY if using Lambda
  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  uri                     = var.backend_endpoint_url
  
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# API Gateway Method - Root path
resource "aws_api_gateway_method" "root" {
  rest_api_id   = aws_api_gateway_rest_api.portfolio_platform.id
  resource_id   = aws_api_gateway_rest_api.portfolio_platform.root_resource_id
  http_method   = "ANY"
  authorization = "AWS_IAM"
}

# API Gateway Integration - Root path
resource "aws_api_gateway_integration" "root" {
  rest_api_id = aws_api_gateway_rest_api.portfolio_platform.id
  resource_id = aws_api_gateway_rest_api.portfolio_platform.root_resource_id
  http_method = aws_api_gateway_method.root.http_method
  
  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  uri                     = var.backend_endpoint_url
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "portfolio_platform" {
  rest_api_id = aws_api_gateway_rest_api.portfolio_platform.id
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.proxy.id,
      aws_api_gateway_integration.proxy.id,
      aws_api_gateway_method.root.id,
      aws_api_gateway_integration.root.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "portfolio_platform" {
  deployment_id = aws_api_gateway_deployment.portfolio_platform.id
  rest_api_id   = aws_api_gateway_rest_api.portfolio_platform.id
  stage_name    = var.stage_name
  
  # Enable CloudWatch Logs
  access_log_settings {
    destination_arn = var.cloudwatch_log_group_arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
  
  # Enable X-Ray tracing
  xray_tracing_enabled = true
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-${var.stage_name}"
    }
  )
}

# API Gateway Method Settings
resource "aws_api_gateway_method_settings" "portfolio_platform" {
  rest_api_id = aws_api_gateway_rest_api.portfolio_platform.id
  stage_name  = aws_api_gateway_stage.portfolio_platform.stage_name
  method_path = "*/*"
  
  settings {
    metrics_enabled        = true
    logging_level          = "INFO"
    data_trace_enabled     = true
    throttling_burst_limit = var.throttle_burst_limit
    throttling_rate_limit  = var.throttle_rate_limit
  }
}

# API Gateway Usage Plan
resource "aws_api_gateway_usage_plan" "portfolio_platform" {
  name        = "${var.environment}-portfolio-platform-usage-plan"
  description = "Usage plan for portfolio platform API"
  
  api_stages {
    api_id = aws_api_gateway_rest_api.portfolio_platform.id
    stage  = aws_api_gateway_stage.portfolio_platform.stage_name
  }
  
  quota_settings {
    limit  = 10000
    period = "DAY"
  }
  
  throttle_settings {
    burst_limit = var.throttle_burst_limit
    rate_limit  = var.throttle_rate_limit
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-usage-plan"
    }
  )
}

# API Gateway API Key
resource "aws_api_gateway_api_key" "portfolio_platform" {
  name    = "${var.environment}-portfolio-platform-api-key"
  enabled = true
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.environment}-api-key"
    }
  )
}

# API Gateway Usage Plan Key
resource "aws_api_gateway_usage_plan_key" "portfolio_platform" {
  key_id        = aws_api_gateway_api_key.portfolio_platform.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.portfolio_platform.id
}

# CORS Configuration (if needed)
resource "aws_api_gateway_gateway_response" "cors_4xx" {
  rest_api_id   = aws_api_gateway_rest_api.portfolio_platform.id
  response_type = "DEFAULT_4XX"
  
  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}

resource "aws_api_gateway_gateway_response" "cors_5xx" {
  rest_api_id   = aws_api_gateway_rest_api.portfolio_platform.id
  response_type = "DEFAULT_5XX"
  
  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin"  = "'*'"
    "gatewayresponse.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "gatewayresponse.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
  }
}
