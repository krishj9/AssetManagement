"""
DynamoDB Table Setup Script

This script creates all DynamoDB tables required for the portfolio platform.
"""

import boto3
from typing import Dict, Any, List
import sys


def create_approval_artifacts_table(dynamodb_client, table_name: str = "ApprovalArtifacts") -> Dict[str, Any]:
    """
    Create DynamoDB table for approval artifacts.
    
    Primary Key: approval_id (String)
    GSI: request_id (String)
    TTL: 90 days
    """
    try:
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'approval_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'approval_id',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'request_id',
                    'AttributeType': 'S'  # String
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'RequestIdIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'request_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand billing
            StreamSpecification={
                'StreamEnabled': False
            },
            SSESpecification={
                'Enabled': True,
                'SSEType': 'KMS'  # AWS-managed encryption
            },
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'PortfolioManagementPlatform'
                },
                {
                    'Key': 'Environment',
                    'Value': 'dev'
                }
            ]
        )
        
        print(f"✅ Created table: {table_name}")
        return response
        
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return {"TableName": table_name, "Status": "ALREADY_EXISTS"}
    except Exception as e:
        print(f"❌ Failed to create table {table_name}: {str(e)}")
        raise


def enable_ttl(dynamodb_client, table_name: str, ttl_attribute: str = "ttl") -> Dict[str, Any]:
    """Enable TTL on a DynamoDB table"""
    try:
        response = dynamodb_client.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': ttl_attribute
            }
        )
        print(f"✅ Enabled TTL on {table_name} (attribute: {ttl_attribute})")
        return response
    except Exception as e:
        print(f"❌ Failed to enable TTL on {table_name}: {str(e)}")
        raise


def enable_point_in_time_recovery(dynamodb_client, table_name: str) -> Dict[str, Any]:
    """Enable point-in-time recovery (PITR) on a DynamoDB table"""
    try:
        response = dynamodb_client.update_continuous_backups(
            TableName=table_name,
            PointInTimeRecoverySpecification={
                'PointInTimeRecoveryEnabled': True
            }
        )
        print(f"✅ Enabled PITR on {table_name}")
        return response
    except Exception as e:
        print(f"❌ Failed to enable PITR on {table_name}: {str(e)}")
        raise


def wait_for_table_active(dynamodb_client, table_name: str, max_attempts: int = 30):
    """Wait for table to become active"""
    waiter = dynamodb_client.get_waiter('table_exists')
    try:
        print(f"⏳ Waiting for {table_name} to become active...")
        waiter.wait(
            TableName=table_name,
            WaiterConfig={
                'Delay': 2,
                'MaxAttempts': max_attempts
            }
        )
        print(f"✅ Table {table_name} is active")
    except Exception as e:
        print(f"❌ Table {table_name} did not become active: {str(e)}")
        raise


def setup_approval_artifacts_table(
    dynamodb_client,
    table_name: str = "ApprovalArtifacts",
    enable_pitr: bool = True,
    enable_ttl_flag: bool = True
):
    """
    Complete setup for Approval Artifacts table.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the table
        enable_pitr: Whether to enable point-in-time recovery
        enable_ttl_flag: Whether to enable TTL
    """
    print(f"\n{'='*60}")
    print(f"Setting up Approval Artifacts Table: {table_name}")
    print(f"{'='*60}\n")
    
    # Create table
    create_approval_artifacts_table(dynamodb_client, table_name)
    
    # Wait for table to be active
    wait_for_table_active(dynamodb_client, table_name)
    
    # Enable TTL (90 days retention)
    if enable_ttl_flag:
        enable_ttl(dynamodb_client, table_name, ttl_attribute="ttl")
    
    # Enable PITR
    if enable_pitr:
        enable_point_in_time_recovery(dynamodb_client, table_name)
    
    print(f"\n✅ Approval Artifacts table setup complete!\n")


def create_audit_events_table(dynamodb_client, table_name: str = "AuditEvents") -> Dict[str, Any]:
    """
    Create DynamoDB table for audit events.
    
    Primary Key: event_id (String)
    GSI1: request_id (PK) + timestamp (SK)
    GSI2: trace_id (PK) + timestamp (SK)
    GSI3: timestamp (PK) + event_type (SK)
    TTL: 7 years (2557 days)
    """
    try:
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'event_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'event_id',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'request_id',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'trace_id',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'  # String (ISO 8601)
                },
                {
                    'AttributeName': 'event_type',
                    'AttributeType': 'S'  # String
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'RequestIdTimestampIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'request_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'TraceIdTimestampIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'trace_id',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'TimestampEventTypeIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'event_type',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand billing
            StreamSpecification={
                'StreamEnabled': False
            },
            SSESpecification={
                'Enabled': True,
                'SSEType': 'KMS'  # AWS-managed encryption
            },
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'PortfolioManagementPlatform'
                },
                {
                    'Key': 'Environment',
                    'Value': 'dev'
                }
            ]
        )
        
        print(f"✅ Created table: {table_name}")
        return response
        
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return {"TableName": table_name, "Status": "ALREADY_EXISTS"}
    except Exception as e:
        print(f"❌ Failed to create table {table_name}: {str(e)}")
        raise


def create_session_state_table(dynamodb_client, table_name: str = "SessionState") -> Dict[str, Any]:
    """
    Create DynamoDB table for session state.
    
    Primary Key: session_id (String)
    TTL: 24 hours after last_activity_at
    """
    try:
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'session_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'session_id',
                    'AttributeType': 'S'  # String
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand billing
            StreamSpecification={
                'StreamEnabled': False
            },
            SSESpecification={
                'Enabled': True,
                'SSEType': 'KMS'  # AWS-managed encryption
            },
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'PortfolioManagementPlatform'
                },
                {
                    'Key': 'Environment',
                    'Value': 'dev'
                }
            ]
        )
        
        print(f"✅ Created table: {table_name}")
        return response
        
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return {"TableName": table_name, "Status": "ALREADY_EXISTS"}
    except Exception as e:
        print(f"❌ Failed to create table {table_name}: {str(e)}")
        raise


def create_memory_consolidation_queue_table(dynamodb_client, table_name: str = "MemoryConsolidationQueue") -> Dict[str, Any]:
    """
    Create DynamoDB table for memory consolidation queue.
    
    Primary Key: consolidation_id (String)
    GSI: consolidation_status (PK) + created_at (SK)
    TTL: 30 days
    """
    try:
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'consolidation_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'consolidation_id',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'consolidation_status',
                    'AttributeType': 'S'  # String
                },
                {
                    'AttributeName': 'created_at',
                    'AttributeType': 'S'  # String (ISO 8601)
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'StatusCreatedAtIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'consolidation_status',
                            'KeyType': 'HASH'
                        },
                        {
                            'AttributeName': 'created_at',
                            'KeyType': 'RANGE'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand billing
            StreamSpecification={
                'StreamEnabled': False
            },
            SSESpecification={
                'Enabled': True,
                'SSEType': 'KMS'  # AWS-managed encryption
            },
            Tags=[
                {
                    'Key': 'Project',
                    'Value': 'PortfolioManagementPlatform'
                },
                {
                    'Key': 'Environment',
                    'Value': 'dev'
                }
            ]
        )
        
        print(f"✅ Created table: {table_name}")
        return response
        
    except dynamodb_client.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return {"TableName": table_name, "Status": "ALREADY_EXISTS"}
    except Exception as e:
        print(f"❌ Failed to create table {table_name}: {str(e)}")
        raise


def setup_audit_events_table(
    dynamodb_client,
    table_name: str = "AuditEvents",
    enable_pitr: bool = True,
    enable_ttl_flag: bool = True
):
    """
    Complete setup for Audit Events table.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the table
        enable_pitr: Whether to enable point-in-time recovery
        enable_ttl_flag: Whether to enable TTL
    """
    print(f"\n{'='*60}")
    print(f"Setting up Audit Events Table: {table_name}")
    print(f"{'='*60}\n")
    
    # Create table
    create_audit_events_table(dynamodb_client, table_name)
    
    # Wait for table to be active
    wait_for_table_active(dynamodb_client, table_name)
    
    # Enable TTL (7 years retention = 2557 days)
    if enable_ttl_flag:
        enable_ttl(dynamodb_client, table_name, ttl_attribute="ttl")
    
    # Enable PITR
    if enable_pitr:
        enable_point_in_time_recovery(dynamodb_client, table_name)
    
    print(f"\n✅ Audit Events table setup complete!\n")


def setup_session_state_table(
    dynamodb_client,
    table_name: str = "SessionState",
    enable_pitr: bool = True,
    enable_ttl_flag: bool = True
):
    """
    Complete setup for Session State table.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the table
        enable_pitr: Whether to enable point-in-time recovery
        enable_ttl_flag: Whether to enable TTL
    """
    print(f"\n{'='*60}")
    print(f"Setting up Session State Table: {table_name}")
    print(f"{'='*60}\n")
    
    # Create table
    create_session_state_table(dynamodb_client, table_name)
    
    # Wait for table to be active
    wait_for_table_active(dynamodb_client, table_name)
    
    # Enable TTL (24 hours after last_activity_at)
    if enable_ttl_flag:
        enable_ttl(dynamodb_client, table_name, ttl_attribute="ttl")
    
    # Enable PITR
    if enable_pitr:
        enable_point_in_time_recovery(dynamodb_client, table_name)
    
    print(f"\n✅ Session State table setup complete!\n")


def setup_memory_consolidation_queue_table(
    dynamodb_client,
    table_name: str = "MemoryConsolidationQueue",
    enable_pitr: bool = True,
    enable_ttl_flag: bool = True
):
    """
    Complete setup for Memory Consolidation Queue table.
    
    Args:
        dynamodb_client: Boto3 DynamoDB client
        table_name: Name of the table
        enable_pitr: Whether to enable point-in-time recovery
        enable_ttl_flag: Whether to enable TTL
    """
    print(f"\n{'='*60}")
    print(f"Setting up Memory Consolidation Queue Table: {table_name}")
    print(f"{'='*60}\n")
    
    # Create table
    create_memory_consolidation_queue_table(dynamodb_client, table_name)
    
    # Wait for table to be active
    wait_for_table_active(dynamodb_client, table_name)
    
    # Enable TTL (30 days retention)
    if enable_ttl_flag:
        enable_ttl(dynamodb_client, table_name, ttl_attribute="ttl")
    
    # Enable PITR
    if enable_pitr:
        enable_point_in_time_recovery(dynamodb_client, table_name)
    
    print(f"\n✅ Memory Consolidation Queue table setup complete!\n")


def main():
    """Main setup function"""
    # Initialize DynamoDB client
    # For local development, you might use localstack or DynamoDB Local
    # dynamodb_client = boto3.client('dynamodb', endpoint_url='http://localhost:8000')
    
    # For AWS
    dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
    
    try:
        # Setup all 4 DynamoDB tables
        setup_approval_artifacts_table(
            dynamodb_client,
            table_name="ApprovalArtifacts",
            enable_pitr=True,
            enable_ttl_flag=True
        )
        
        setup_audit_events_table(
            dynamodb_client,
            table_name="AuditEvents",
            enable_pitr=True,
            enable_ttl_flag=True
        )
        
        setup_session_state_table(
            dynamodb_client,
            table_name="SessionState",
            enable_pitr=True,
            enable_ttl_flag=True
        )
        
        setup_memory_consolidation_queue_table(
            dynamodb_client,
            table_name="MemoryConsolidationQueue",
            enable_pitr=True,
            enable_ttl_flag=True
        )
        
        print("\n" + "="*60)
        print("✅ All DynamoDB tables created successfully!")
        print("="*60 + "\n")
        
        print("Tables created:")
        print("  1. ApprovalArtifacts (TTL: 90 days)")
        print("  2. AuditEvents (TTL: 7 years)")
        print("  3. SessionState (TTL: 24 hours)")
        print("  4. MemoryConsolidationQueue (TTL: 30 days)")
        print("\nAll tables have:")
        print("  - Point-in-time recovery (PITR) enabled")
        print("  - Encryption at rest with AWS-managed keys")
        print("  - On-demand billing mode")
        print("  - Appropriate GSIs for query patterns\n")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
