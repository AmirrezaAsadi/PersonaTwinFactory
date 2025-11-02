"""Transparency and audit logging mechanisms for data operations."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field


class AuditLog(BaseModel):
    """Individual audit log entry for data transparency."""

    log_id: str = Field(..., description="Unique identifier for this log entry")
    operation: str = Field(..., description="Type of operation (create, read, update, delete)")
    persona_id: str = Field(..., description="ID of the persona affected")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When the operation occurred"
    )
    user_id: Optional[str] = Field(None, description="User who performed the operation")
    data_hash: str = Field(..., description="Hash of the data for integrity verification")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional operation details"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class TransparencyLogger:
    """
    Manages transparency logging and data integrity verification.
    
    Provides audit logging, data hashing, and optional encryption for
    ensuring data transparency and integrity in persona twin operations.
    """

    def __init__(self, log_directory: Optional[Path] = None, encryption_key: Optional[bytes] = None):
        """
        Initialize the transparency logger.

        Args:
            log_directory: Directory to store audit logs (default: ./audit_logs)
            encryption_key: Optional encryption key for sensitive data
        """
        self.log_directory = log_directory or Path("./audit_logs")
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.encryption_key = encryption_key
        self.cipher = Fernet(encryption_key) if encryption_key else None
        self.logs: List[AuditLog] = []

    @staticmethod
    def generate_encryption_key() -> bytes:
        """Generate a new encryption key for data protection."""
        return Fernet.generate_key()

    @staticmethod
    def compute_hash(data: Any) -> str:
        """
        Compute SHA-256 hash of data for integrity verification.

        Args:
            data: Data to hash (will be JSON serialized)

        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def log_operation(
        self,
        operation: str,
        persona_id: str,
        data: Any,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Log an operation for audit and transparency.

        Args:
            operation: Type of operation (create, read, update, delete)
            persona_id: ID of the persona affected
            data: The data involved in the operation
            user_id: User who performed the operation
            details: Additional operation details

        Returns:
            The created audit log entry
        """
        log_id = f"{persona_id}_{operation}_{datetime.utcnow().timestamp()}"
        data_hash = self.compute_hash(data)

        audit_log = AuditLog(
            log_id=log_id,
            operation=operation,
            persona_id=persona_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            data_hash=data_hash,
            details=details or {},
        )

        self.logs.append(audit_log)
        self._persist_log(audit_log)
        return audit_log

    def _persist_log(self, audit_log: AuditLog) -> None:
        """Persist audit log to disk."""
        log_file = self.log_directory / f"{audit_log.log_id}.json"
        with open(log_file, "w") as f:
            json.dump(audit_log.model_dump(), f, indent=2, default=str)

    def verify_data_integrity(self, data: Any, expected_hash: str) -> bool:
        """
        Verify data integrity by comparing hashes.

        Args:
            data: The data to verify
            expected_hash: The expected hash value

        Returns:
            True if data integrity is verified, False otherwise
        """
        computed_hash = self.compute_hash(data)
        return computed_hash == expected_hash

    def encrypt_data(self, data: str) -> bytes:
        """
        Encrypt sensitive data.

        Args:
            data: String data to encrypt

        Returns:
            Encrypted bytes

        Raises:
            ValueError: If encryption is not configured
        """
        if not self.cipher:
            raise ValueError("Encryption not configured. Provide encryption_key during initialization.")
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Decrypt sensitive data.

        Args:
            encrypted_data: Encrypted bytes to decrypt

        Returns:
            Decrypted string

        Raises:
            ValueError: If encryption is not configured
        """
        if not self.cipher:
            raise ValueError("Encryption not configured. Provide encryption_key during initialization.")
        return self.cipher.decrypt(encrypted_data).decode()

    def get_audit_trail(self, persona_id: Optional[str] = None) -> List[AuditLog]:
        """
        Retrieve audit trail, optionally filtered by persona ID.

        Args:
            persona_id: Optional persona ID to filter by

        Returns:
            List of audit log entries
        """
        if persona_id:
            return [log for log in self.logs if log.persona_id == persona_id]
        return self.logs

    def export_audit_logs(self, output_file: Path) -> None:
        """
        Export all audit logs to a single file.

        Args:
            output_file: Path to output file
        """
        with open(output_file, "w") as f:
            logs_data = [log.model_dump() for log in self.logs]
            json.dump(logs_data, f, indent=2, default=str)
