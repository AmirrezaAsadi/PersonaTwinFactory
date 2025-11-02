"""Tests for transparency and audit logging."""

import pytest
import tempfile
from pathlib import Path
from personatwinfactory.transparency import TransparencyLogger, AuditLog


class TestTransparencyLogger:
    """Test TransparencyLogger functionality."""

    def test_initialization(self):
        """Test logger initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            assert logger.log_directory.exists()
            assert len(logger.logs) == 0

    def test_compute_hash(self):
        """Test hash computation."""
        data = {"key": "value", "number": 42}
        hash1 = TransparencyLogger.compute_hash(data)
        hash2 = TransparencyLogger.compute_hash(data)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex length

    def test_hash_consistency(self):
        """Test that same data produces same hash."""
        data = {"b": 2, "a": 1}  # Different order
        sorted_data = {"a": 1, "b": 2}
        hash1 = TransparencyLogger.compute_hash(data)
        hash2 = TransparencyLogger.compute_hash(sorted_data)
        assert hash1 == hash2  # Should be same due to sort_keys

    def test_log_operation(self):
        """Test logging an operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            log = logger.log_operation(
                operation="create",
                persona_id="test-123",
                data={"name": "Test"},
                user_id="admin",
            )
            assert log.operation == "create"
            assert log.persona_id == "test-123"
            assert log.user_id == "admin"
            assert len(logger.logs) == 1

    def test_verify_data_integrity(self):
        """Test data integrity verification."""
        logger = TransparencyLogger()
        data = {"test": "data"}
        hash_value = logger.compute_hash(data)
        
        # Valid data
        assert logger.verify_data_integrity(data, hash_value) is True
        
        # Tampered data
        tampered = {"test": "tampered"}
        assert logger.verify_data_integrity(tampered, hash_value) is False

    def test_encryption_key_generation(self):
        """Test encryption key generation."""
        key = TransparencyLogger.generate_encryption_key()
        assert isinstance(key, bytes)
        assert len(key) > 0

    def test_encrypt_decrypt(self):
        """Test encryption and decryption."""
        key = TransparencyLogger.generate_encryption_key()
        logger = TransparencyLogger(encryption_key=key)
        
        original = "sensitive data"
        encrypted = logger.encrypt_data(original)
        decrypted = logger.decrypt_data(encrypted)
        
        assert encrypted != original.encode()
        assert decrypted == original

    def test_encryption_without_key(self):
        """Test that encryption fails without key."""
        logger = TransparencyLogger()
        with pytest.raises(ValueError):
            logger.encrypt_data("test")
        with pytest.raises(ValueError):
            logger.decrypt_data(b"test")

    def test_get_audit_trail(self):
        """Test retrieving audit trail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            
            logger.log_operation("create", "persona-1", {"data": 1})
            logger.log_operation("update", "persona-1", {"data": 2})
            logger.log_operation("create", "persona-2", {"data": 3})
            
            # All logs
            all_logs = logger.get_audit_trail()
            assert len(all_logs) == 3
            
            # Filtered by persona
            persona1_logs = logger.get_audit_trail(persona_id="persona-1")
            assert len(persona1_logs) == 2
            assert all(log.persona_id == "persona-1" for log in persona1_logs)

    def test_export_audit_logs(self):
        """Test exporting audit logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = TransparencyLogger(log_directory=Path(tmpdir))
            logger.log_operation("create", "test-123", {"data": "value"})
            
            output_file = Path(tmpdir) / "export.json"
            logger.export_audit_logs(output_file)
            
            assert output_file.exists()
            assert output_file.stat().st_size > 0


class TestAuditLog:
    """Test AuditLog model."""

    def test_create_audit_log(self):
        """Test creating an audit log entry."""
        log = AuditLog(
            log_id="log-001",
            operation="create",
            persona_id="test-123",
            data_hash="abc123",
        )
        assert log.log_id == "log-001"
        assert log.operation == "create"
        assert log.data_hash == "abc123"
