"""
DynamoDB IAM Policies

This module defines IAM policies for DynamoDB table access with role-based permissions.
"""

import json
from typing import Dict, List, Any


def get_dynamodb_read_policy(table_names: List[str], region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for read-only access to DynamoDB tables.
    
    Permissions:
    - GetItem
    - Query
    - Scan (limited use)
    - DescribeTable
    
    Args:
        table_names: List of table names to grant access to
        region: AWS region
        account_id: AWS account ID (use "*" for any account)
    
    Returns:
        IAM policy document
    """
    table_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}" for table_name in table_names]
    index_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}/index/*" for table_name in table_names]
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBReadAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:DescribeTable",
                    "dynamodb:BatchGetItem"
                ],
                "Resource": table_arns + index_arns
            }
        ]
    }
    
    return policy


def get_dynamodb_write_policy(table_names: List[str], region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for write access to DynamoDB tables.
    
    Permissions:
    - PutItem
    - UpdateItem
    - DeleteItem
    - BatchWriteItem
    
    Args:
        table_names: List of table names to grant access to
        region: AWS region
        account_id: AWS account ID (use "*" for any account)
    
    Returns:
        IAM policy document
    """
    table_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}" for table_name in table_names]
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBWriteAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:BatchWriteItem"
                ],
                "Resource": table_arns
            }
        ]
    }
    
    return policy


def get_dynamodb_read_write_policy(table_names: List[str], region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for read and write access to DynamoDB tables.
    
    Combines read and write permissions.
    
    Args:
        table_names: List of table names to grant access to
        region: AWS region
        account_id: AWS account ID (use "*" for any account)
    
    Returns:
        IAM policy document
    """
    table_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}" for table_name in table_names]
    index_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}/index/*" for table_name in table_names]
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBReadWriteAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:DescribeTable",
                    "dynamodb:BatchGetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:BatchWriteItem"
                ],
                "Resource": table_arns + index_arns
            }
        ]
    }
    
    return policy


def get_dynamodb_admin_policy(table_names: List[str], region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for admin access to DynamoDB tables.
    
    Permissions:
    - All read/write operations
    - Table management (CreateTable, DeleteTable, UpdateTable)
    - TTL management
    - PITR management
    - Backup management
    
    Args:
        table_names: List of table names to grant access to
        region: AWS region
        account_id: AWS account ID (use "*" for any account)
    
    Returns:
        IAM policy document
    """
    table_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}" for table_name in table_names]
    index_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}/index/*" for table_name in table_names]
    backup_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}/backup/*" for table_name in table_names]
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBAdminAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:*"
                ],
                "Resource": table_arns + index_arns + backup_arns
            },
            {
                "Sid": "DynamoDBListTables",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:ListTables",
                    "dynamodb:DescribeLimits"
                ],
                "Resource": "*"
            }
        ]
    }
    
    return policy


def get_approval_artifacts_read_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for read-only access to Approval Artifacts table.
    
    Use case: Portfolio managers and compliance reviewers who need to view approval artifacts.
    """
    return get_dynamodb_read_policy(["ApprovalArtifacts"], region, account_id)


def get_approval_artifacts_write_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for write access to Approval Artifacts table.
    
    Use case: Backend services that create and update approval artifacts.
    """
    return get_dynamodb_read_write_policy(["ApprovalArtifacts"], region, account_id)


def get_audit_events_write_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for write access to Audit Events table.
    
    Use case: Backend services that log audit events.
    Note: Audit events are write-only for most services; reads are restricted to compliance reviewers.
    """
    return get_dynamodb_write_policy(["AuditEvents"], region, account_id)


def get_audit_events_read_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for read access to Audit Events table.
    
    Use case: Compliance reviewers and platform admins who need to query audit logs.
    """
    return get_dynamodb_read_policy(["AuditEvents"], region, account_id)


def get_session_state_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for read/write access to Session State table.
    
    Use case: Backend services that manage session state.
    """
    return get_dynamodb_read_write_policy(["SessionState"], region, account_id)


def get_memory_consolidation_queue_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for read/write access to Memory Consolidation Queue table.
    
    Use case: Backend services that process memory consolidation tasks.
    """
    return get_dynamodb_read_write_policy(["MemoryConsolidationQueue"], region, account_id)


def get_backend_service_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate comprehensive IAM policy for backend services.
    
    Permissions:
    - Read/write access to Approval Artifacts
    - Write access to Audit Events
    - Read/write access to Session State
    - Read/write access to Memory Consolidation Queue
    
    Use case: FastAPI backend service that orchestrates the portfolio platform.
    """
    all_tables = ["ApprovalArtifacts", "SessionState", "MemoryConsolidationQueue"]
    table_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}" for table_name in all_tables]
    index_arns = [f"arn:aws:dynamodb:{region}:{account_id}:table/{table_name}/index/*" for table_name in all_tables]
    
    audit_table_arn = f"arn:aws:dynamodb:{region}:{account_id}:table/AuditEvents"
    audit_index_arns = f"arn:aws:dynamodb:{region}:{account_id}:table/AuditEvents/index/*"
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DynamoDBReadWriteAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:DescribeTable",
                    "dynamodb:BatchGetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:BatchWriteItem"
                ],
                "Resource": table_arns + index_arns
            },
            {
                "Sid": "AuditEventsWriteAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:BatchWriteItem"
                ],
                "Resource": [audit_table_arn, audit_index_arns]
            }
        ]
    }
    
    return policy


def get_compliance_reviewer_policy(region: str = "us-east-1", account_id: str = "*") -> Dict[str, Any]:
    """
    Generate IAM policy for compliance reviewers.
    
    Permissions:
    - Read access to Approval Artifacts
    - Read access to Audit Events
    
    Use case: Compliance reviewers who need to audit the system.
    """
    table_arns = [
        f"arn:aws:dynamodb:{region}:{account_id}:table/ApprovalArtifacts",
        f"arn:aws:dynamodb:{region}:{account_id}:table/AuditEvents"
    ]
    index_arns = [
        f"arn:aws:dynamodb:{region}:{account_id}:table/ApprovalArtifacts/index/*",
        f"arn:aws:dynamodb:{region}:{account_id}:table/AuditEvents/index/*"
    ]
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ComplianceReviewerReadAccess",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:DescribeTable",
                    "dynamodb:BatchGetItem"
                ],
                "Resource": table_arns + index_arns
            }
        ]
    }
    
    return policy


def print_policy(policy_name: str, policy: Dict[str, Any]):
    """Print policy in formatted JSON"""
    print(f"\n{'='*60}")
    print(f"Policy: {policy_name}")
    print(f"{'='*60}\n")
    print(json.dumps(policy, indent=2))
    print()


def main():
    """Generate and print all IAM policies"""
    region = "us-east-1"
    account_id = "123456789012"  # Replace with your AWS account ID
    
    print("\n" + "="*60)
    print("DynamoDB IAM Policies for Portfolio Management Platform")
    print("="*60)
    
    # Backend service policy
    print_policy(
        "Backend Service Policy",
        get_backend_service_policy(region, account_id)
    )
    
    # Compliance reviewer policy
    print_policy(
        "Compliance Reviewer Policy",
        get_compliance_reviewer_policy(region, account_id)
    )
    
    # Individual table policies
    print_policy(
        "Approval Artifacts Read Policy",
        get_approval_artifacts_read_policy(region, account_id)
    )
    
    print_policy(
        "Approval Artifacts Write Policy",
        get_approval_artifacts_write_policy(region, account_id)
    )
    
    print_policy(
        "Audit Events Write Policy",
        get_audit_events_write_policy(region, account_id)
    )
    
    print_policy(
        "Audit Events Read Policy",
        get_audit_events_read_policy(region, account_id)
    )
    
    print_policy(
        "Session State Policy",
        get_session_state_policy(region, account_id)
    )
    
    print_policy(
        "Memory Consolidation Queue Policy",
        get_memory_consolidation_queue_policy(region, account_id)
    )
    
    # Admin policy
    all_tables = ["ApprovalArtifacts", "AuditEvents", "SessionState", "MemoryConsolidationQueue"]
    print_policy(
        "Admin Policy (All Tables)",
        get_dynamodb_admin_policy(all_tables, region, account_id)
    )
    
    print("\n" + "="*60)
    print("✅ All IAM policies generated successfully!")
    print("="*60 + "\n")
    print("Usage:")
    print("  1. Replace account_id with your AWS account ID")
    print("  2. Create IAM roles for each use case")
    print("  3. Attach the appropriate policy to each role")
    print("  4. Assign roles to users, services, or Lambda functions\n")


if __name__ == "__main__":
    main()
