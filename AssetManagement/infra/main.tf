# Bedrock Multi-Agent Portfolio Platform - Main Terraform Configuration

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # Configure S3 backend for state management
    # bucket         = "your-terraform-state-bucket"
    # key            = "portfolio-platform/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "terraform-state-lock"
    # encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "BedrockMultiAgentPortfolio"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local variables
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  
  common_tags = {
    Project     = "BedrockMultiAgentPortfolio"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Modules
module "dynamodb" {
  source = "./modules/dynamodb"
  
  environment              = var.environment
  common_tags              = local.common_tags
  billing_mode             = var.dynamodb_billing_mode
  point_in_time_recovery   = var.dynamodb_point_in_time_recovery
}

module "iam" {
  source = "./modules/iam"
  
  environment         = var.environment
  common_tags         = local.common_tags
  account_id          = local.account_id
  dynamodb_table_arns = values(module.dynamodb.table_arns)
  kms_key_arns        = [module.dynamodb.kms_key_arn]
}

module "bedrock_agents" {
  source = "./modules/bedrock"
  
  environment                      = var.environment
  common_tags                      = local.common_tags
  bedrock_model_id                 = var.bedrock_model_id
  bedrock_agent_execution_role_arn = module.iam.bedrock_agent_execution_role_arn
  
  depends_on = [module.iam]
}

module "cloudwatch" {
  source = "./modules/cloudwatch"
  
  environment        = var.environment
  common_tags        = local.common_tags
  log_retention_days = var.cloudwatch_log_retention_days
  alarm_email        = var.cloudwatch_alarm_email
}

module "api_gateway" {
  source = "./modules/api_gateway"
  
  environment              = var.environment
  common_tags              = local.common_tags
  stage_name               = var.api_gateway_stage_name
  throttle_burst_limit     = var.api_gateway_throttle_burst_limit
  throttle_rate_limit      = var.api_gateway_throttle_rate_limit
  backend_endpoint_url     = "http://localhost:8000"  # Update with actual backend URL
  cloudwatch_log_group_arn = module.cloudwatch.backend_log_group_arn
}

# Outputs are defined in outputs.tf
