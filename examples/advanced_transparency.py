"""
Advanced transparency features example.

Demonstrates encryption, data integrity verification, and
comprehensive audit trail management.
"""

from pathlib import Path
from personatwinfactory import PersonaTwin, TransparencyLogger


def main():
    """Demonstrate advanced transparency features."""
    print("=" * 60)
    print("PersonaTwinFactory - Advanced Transparency Example")
    print("=" * 60)

    # Generate encryption key for sensitive data
    encryption_key = TransparencyLogger.generate_encryption_key()
    print("\n1. Generated encryption key")
    print(f"   Key (first 32 chars): {encryption_key[:32]}...")

    # Initialize logger with encryption
    logger = TransparencyLogger(
        log_directory=Path("./audit_logs"),
        encryption_key=encryption_key,
    )
    print("\n2. Initialized TransparencyLogger with encryption")

    # Create persona with encrypted data capability
    persona = PersonaTwin(
        name="Bob Smith",
        transparency_logger=logger,
    )
    print(f"\n3. Created PersonaTwin: {persona}")

    # Add sensitive information with encryption
    sensitive_data = "SSN: 123-45-6789"
    encrypted_data = logger.encrypt_data(sensitive_data)
    print("\n4. Encrypted sensitive data")
    print(f"   Original: {sensitive_data}")
    print(f"   Encrypted: {encrypted_data[:50]}...")

    # Decrypt data
    decrypted_data = logger.decrypt_data(encrypted_data)
    print(f"   Decrypted: {decrypted_data}")
    print(f"   Match: {decrypted_data == sensitive_data}")

    # Record behavior with encrypted metadata
    persona.add_behavior(
        behavior_type="authentication",
        context={"method": "biometric", "device": "mobile"},
        response="success",
        metadata={"encrypted_id": encrypted_data.decode()},
    )
    print("\n5. Recorded behavior with encrypted metadata")

    # Demonstrate data hashing
    data_to_hash = {"user": "bob", "action": "data_access", "timestamp": "2024-01-15"}
    hash_value = logger.compute_hash(data_to_hash)
    print(f"\n6. Computed data hash")
    print(f"   Data: {data_to_hash}")
    print(f"   Hash: {hash_value}")

    # Verify integrity
    is_valid = logger.verify_data_integrity(data_to_hash, hash_value)
    print(f"   Integrity check: {is_valid}")

    # Test with tampered data
    tampered_data = data_to_hash.copy()
    tampered_data["action"] = "tampered"
    is_valid_tampered = logger.verify_data_integrity(tampered_data, hash_value)
    print(f"   Tampered data check: {is_valid_tampered}")

    # Create snapshot with integrity verification
    snapshot = persona.create_snapshot()
    print(f"\n7. Created snapshot with checksum: {snapshot.snapshot_id}")
    
    # Verify snapshot integrity
    snapshot_data = snapshot.model_dump(exclude={"checksum"})
    is_snapshot_valid = logger.verify_data_integrity(
        snapshot_data,
        snapshot.checksum,
    )
    print(f"   Snapshot integrity verified: {is_snapshot_valid}")

    # Demonstrate complete audit trail
    audit_trail = persona.get_audit_trail()
    print(f"\n8. Complete audit trail ({len(audit_trail)} entries):")
    for i, log in enumerate(audit_trail, 1):
        print(f"   {i}. {log['timestamp']}: {log['operation']} - {log['details'].get('action')}")
        print(f"      Data hash: {log['data_hash'][:32]}...")

    # Save with full transparency
    file_path = persona.save(user_id="admin")
    print(f"\n9. Saved persona with complete audit trail")
    print(f"   Location: {file_path}")

    # Load and verify
    loaded_persona = PersonaTwin.load(
        persona.persona_id,
        transparency_logger=logger,
    )
    print(f"\n10. Loaded persona: {loaded_persona}")
    print(f"    Behaviors preserved: {len(loaded_persona.behaviors)}")

    print("\n" + "=" * 60)
    print("Advanced transparency example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
