"""
Schema Version Validation and Backward Compatibility

This module provides utilities for validating schema versions and ensuring
backward compatibility across schema changes.
"""

from typing import Optional, List, Tuple
from packaging import version
from pydantic import BaseModel, Field


class SchemaVersion(BaseModel):
    """Schema version information"""
    version: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Semantic version (major.minor.patch)")
    
    def parse(self) -> version.Version:
        """Parse version string into Version object"""
        return version.parse(self.version)
    
    def is_compatible_with(self, other: "SchemaVersion") -> bool:
        """
        Check if this version is backward compatible with another version.
        
        Compatibility rules:
        - Same major version = compatible
        - Different major version = incompatible (breaking change)
        """
        self_ver = self.parse()
        other_ver = other.parse()
        
        # Same major version means backward compatible
        return self_ver.major == other_ver.major
    
    def is_newer_than(self, other: "SchemaVersion") -> bool:
        """Check if this version is newer than another version"""
        return self.parse() > other.parse()
    
    def is_same_as(self, other: "SchemaVersion") -> bool:
        """Check if this version is the same as another version"""
        return self.parse() == other.parse()


class SchemaVersionValidator:
    """
    Validator for schema versions with backward compatibility checking.
    """
    
    # Supported schema versions (add new versions here as they are released)
    SUPPORTED_VERSIONS: List[str] = [
        "1.0.0",
    ]
    
    # Current production version
    CURRENT_VERSION: str = "1.0.0"
    
    @classmethod
    def validate_version(cls, version_str: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a schema version string.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            schema_ver = SchemaVersion(version=version_str)
        except Exception as e:
            return False, f"Invalid version format: {str(e)}"
        
        # Check if version is supported
        if version_str not in cls.SUPPORTED_VERSIONS:
            return False, f"Unsupported schema version: {version_str}. Supported versions: {', '.join(cls.SUPPORTED_VERSIONS)}"
        
        return True, None
    
    @classmethod
    def is_compatible(cls, client_version: str, server_version: str) -> Tuple[bool, Optional[str]]:
        """
        Check if client version is compatible with server version.
        
        Args:
            client_version: Version used by the client
            server_version: Version expected by the server
            
        Returns:
            Tuple of (is_compatible, error_message)
        """
        try:
            client_ver = SchemaVersion(version=client_version)
            server_ver = SchemaVersion(version=server_version)
        except Exception as e:
            return False, f"Invalid version format: {str(e)}"
        
        # Check if client version is supported
        if client_version not in cls.SUPPORTED_VERSIONS:
            return False, f"Unsupported client schema version: {client_version}"
        
        # Check if server version is supported
        if server_version not in cls.SUPPORTED_VERSIONS:
            return False, f"Unsupported server schema version: {server_version}"
        
        # Check backward compatibility
        if not client_ver.is_compatible_with(server_ver):
            return False, f"Incompatible schema versions: client={client_version}, server={server_version}. Major version mismatch indicates breaking changes."
        
        return True, None
    
    @classmethod
    def get_current_version(cls) -> str:
        """Get the current production schema version"""
        return cls.CURRENT_VERSION
    
    @classmethod
    def get_supported_versions(cls) -> List[str]:
        """Get list of all supported schema versions"""
        return cls.SUPPORTED_VERSIONS.copy()
    
    @classmethod
    def add_supported_version(cls, new_version: str) -> Tuple[bool, Optional[str]]:
        """
        Add a new supported version (for testing or migration).
        
        Args:
            new_version: New version to add
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            schema_ver = SchemaVersion(version=new_version)
        except Exception as e:
            return False, f"Invalid version format: {str(e)}"
        
        if new_version in cls.SUPPORTED_VERSIONS:
            return False, f"Version {new_version} is already supported"
        
        cls.SUPPORTED_VERSIONS.append(new_version)
        cls.SUPPORTED_VERSIONS.sort(key=lambda v: version.parse(v))
        
        return True, None


def validate_schema_version(version_str: str) -> None:
    """
    Validate a schema version string and raise ValueError if invalid.
    
    This is a convenience function for use in Pydantic validators.
    
    Args:
        version_str: Version string to validate
        
    Raises:
        ValueError: If version is invalid or unsupported
    """
    is_valid, error_msg = SchemaVersionValidator.validate_version(version_str)
    if not is_valid:
        raise ValueError(error_msg)


def check_compatibility(client_version: str, server_version: str) -> None:
    """
    Check schema version compatibility and raise ValueError if incompatible.
    
    This is a convenience function for use in request validation.
    
    Args:
        client_version: Version used by the client
        server_version: Version expected by the server
        
    Raises:
        ValueError: If versions are incompatible
    """
    is_compatible, error_msg = SchemaVersionValidator.is_compatible(client_version, server_version)
    if not is_compatible:
        raise ValueError(error_msg)
