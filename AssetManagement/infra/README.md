# Bedrock Multi-Agent Portfolio Platform - Infrastructure

This directory contains Terraform Infrastructure as Code (IaC) for deploying the Bedrock Multi-Agent Portfolio Platform to AWS.

## Architecture Overview

The infrastructure deploys the following AWS resources:

### Core Components

1. **DynamoDB Tables** (4 tables)
   - Approval Artifacts (90-day retention)
   - Audit Events (7-year retention)
   - Session State (24-hour retention)
   - Memory Consolidation Queue (30-day retention)

2. **Bedrock Agents** (5 agents)
   - Supervisor Agent (orchestrator)
   - Research Agent (market data)
   - Memory & Personalization Agent
   - Risk & Compliance Agent
   - Execution Agent (trade proposals)

3. **Bedrock Guardrail**
   - Content filtering (hate, violence, sexual, misconduct)
   - PII detection and blocking
   - Topic policy (denied topics)
   - Word policy (blocked terms)

4. **IAM Roles and Policies**
   - Bedrock Agent execution role
   - Backend application role
   - DynamoDB access policies
   - CloudWatch logging policies

5. **CloudWatch**
   - Log groups (backend, agents, audit)
   - Dashboards (executive workflow, agent performance)
   - Alarms (error rate, latency, blocked state, memory failures, guardrail violations)
   - SNS topic for alarm notifications

6. **API Gateway**
   - REST API for FastAPI backend
   - Usage plans and API keys
   - Throttling and rate limiting
   - CORS configuration

## Prerequisites

- **Terraform** >= 1.5.0
- **AWS CLI** configured with appropriate credentials
- **AWS Account** with permissions to create:
  - DynamoDB tables
  - Bedrock agents and guardrails
  - IAM roles and policies
  - CloudWatch resources
  - API Gateway
  - KMS keys

## Directory Structure

```
infra/
├── main.tf                    # Main Terraform configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example variable values
├── README.md                  # This file
└── modules/
    ├── dynamodb/              # DynamoDB tables module
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── iam/                   # IAM roles and policies module
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── bedrock/               # Bedrock agents and guardrail module
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── instructions/      # Agent instruction files
    │       ├── supervisor_instructions.txt
    │       ├── research_instructions.txt
    │       ├── memory_instructions.txt
    │       ├── compliance_instructions.txt
    │       └── execution_instructions.txt
    ├── cloudwatch/            # CloudWatch logs, metrics, dashboards module
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── api_gateway/           # API Gateway module
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Deployment Instructions

### 1. Configure Variables

Copy the example variables file and update with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set:
- `aws_region`: AWS region for deployment (default: us-east-1)
- `environment`: Environment name (dev, test, pre-prod, prod)
- `cloudwatch_alarm_email`: Email for alarm notifications (optional)
- Other configuration values as needed

### 2. Configure S3 Backend (Optional but Recommended)

For production deployments, configure S3 backend for state management. Uncomment and update the backend configuration in `main.tf`:

```hcl
backend "s3" {
  bucket         = "your-terraform-state-bucket"
  key            = "portfolio-platform/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "terraform-state-lock"
  encrypt        = true
}
```

Create the S3 bucket and DynamoDB table first:

```bash
# Create S3 bucket for state
aws s3 mb s3://your-terraform-state-bucket --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket your-terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 3. Initialize Terraform

```bash
cd infra
terraform init
```

### 4. Review the Plan

```bash
terraform plan
```

Review the resources that will be created. Ensure everything looks correct before applying.

### 5. Apply the Configuration

```bash
terraform apply
```

Type `yes` when prompted to confirm the deployment.

### 6. Retrieve Outputs

After successful deployment, retrieve important outputs:

```bash
# Get all outputs
terraform output

# Get specific outputs
terraform output api_gateway_url
terraform output supervisor_agent_id
terraform output dynamodb_table_names

# Get sensitive outputs
terraform output -json api_key_value
terraform output -json bedrock_agent_ids
```

## Post-Deployment Configuration

### 1. Update Backend Application

Update the FastAPI backend configuration with the deployed resource IDs:

- DynamoDB table names
- Bedrock agent IDs and alias IDs
- API Gateway URL
- CloudWatch log group names

### 2. Configure Agent Instructions

The agent instruction files are located in `modules/bedrock/instructions/`. You can update these files and re-apply Terraform to update agent configurations.

### 3. Set Up Alarm Notifications

If you provided an email address for `cloudwatch_alarm_email`, confirm the SNS subscription:

1. Check your email for a subscription confirmation from AWS SNS
2. Click the confirmation link

### 4. Test the Deployment

Test the deployed infrastructure:

```bash
# Test API Gateway endpoint
curl -X GET "$(terraform output -raw api_gateway_url)/health"

# Test DynamoDB tables
aws dynamodb list-tables --region us-east-1

# Test Bedrock agents
aws bedrock-agent list-agents --region us-east-1
```

## Environment Management

### Multiple Environments

Deploy separate environments by using different `terraform.tfvars` files:

```bash
# Development
terraform apply -var-file="terraform.dev.tfvars"

# Test
terraform apply -var-file="terraform.test.tfvars"

# Production
terraform apply -var-file="terraform.prod.tfvars"
```

Or use Terraform workspaces:

```bash
# Create workspaces
terraform workspace new dev
terraform workspace new test
terraform workspace new prod

# Switch workspace
terraform workspace select dev

# Apply
terraform apply
```

### Environment Promotion

To promote changes from dev → test → pre-prod → prod:

1. Test changes in dev environment
2. Run regression tests and validation
3. Apply to test environment
4. Run full test suite
5. Apply to pre-prod environment
6. Monitor for 7 days minimum
7. Apply to prod environment with approval

## Resource Costs

Estimated monthly costs (us-east-1, dev environment):

- **DynamoDB**: $5-50 (PAY_PER_REQUEST, depends on usage)
- **Bedrock Agents**: $0 (pay per invocation)
- **Bedrock Model Invocations**: Variable (depends on usage)
- **CloudWatch Logs**: $5-20 (depends on log volume)
- **API Gateway**: $3.50 per million requests
- **KMS Keys**: $1 per key per month

**Total estimated**: $15-100/month for dev environment

Production costs will be higher based on traffic volume.

## Monitoring and Observability

### CloudWatch Dashboards

Access dashboards in AWS Console:

1. **Executive Workflow Dashboard**: Request volume, latency, error rates
2. **Agent Performance Dashboard**: Per-agent latency and error rates

### CloudWatch Alarms

Configured alarms:

- High error rate (>5%)
- High blocked state rate (>10%)
- High latency (>30 seconds)
- Memory agent failures
- Guardrail violation spikes

### Logs

Log groups:

- `/aws/portfolio-platform/{environment}/backend` - Backend application logs
- `/aws/portfolio-platform/{environment}/agents` - Bedrock agent logs
- `/aws/portfolio-platform/{environment}/audit` - Audit event logs (7-year retention)

## Troubleshooting

### Common Issues

**Issue**: Terraform fails with "AccessDenied" error

**Solution**: Ensure your AWS credentials have sufficient permissions. Required permissions:
- DynamoDB: CreateTable, DescribeTable, UpdateTable
- Bedrock: CreateAgent, CreateGuardrail, CreateAgentAlias
- IAM: CreateRole, CreatePolicy, AttachRolePolicy
- CloudWatch: CreateLogGroup, PutMetricAlarm, PutDashboard
- API Gateway: CreateRestApi, CreateDeployment, CreateStage

**Issue**: Bedrock agent creation fails

**Solution**: Ensure Bedrock is available in your region and you have access to the specified model ID. Check AWS Service Quotas for Bedrock.

**Issue**: DynamoDB table already exists

**Solution**: Either import the existing table or destroy it first:
```bash
terraform import module.dynamodb.aws_dynamodb_table.approval_artifacts dev-approval-artifacts
```

### State Management

**Backup state file**:
```bash
cp terraform.tfstate terraform.tfstate.backup
```

**Recover from state issues**:
```bash
terraform refresh
terraform state list
terraform state show <resource>
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete all resources including DynamoDB tables and their data. Ensure you have backups if needed.

## Security Considerations

1. **State File**: Contains sensitive information. Use S3 backend with encryption and access controls.
2. **API Keys**: Stored in Terraform state. Rotate regularly.
3. **IAM Roles**: Follow principle of least privilege. Review policies regularly.
4. **KMS Keys**: Enable key rotation. Monitor key usage.
5. **DynamoDB**: Enable point-in-time recovery for production.
6. **CloudWatch Logs**: Enable encryption at rest.

## Compliance

- **Audit Logs**: 7-year retention for compliance requirements
- **Encryption**: All data encrypted at rest (DynamoDB, CloudWatch Logs)
- **Access Control**: IAM roles with least privilege
- **Monitoring**: CloudWatch alarms for security events

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Terraform logs: `terraform apply -debug`
3. Check AWS CloudWatch logs for runtime errors
4. Review the design document: `../docs/design.md`

## References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
