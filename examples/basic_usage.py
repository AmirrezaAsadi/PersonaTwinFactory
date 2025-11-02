"""
Basic usage example of PersonaTwinFactory.

This example demonstrates creating a digital persona twin,
updating attributes, recording behaviors, and ensuring data transparency.
"""

from personatwinfactory import PersonaTwin, TransparencyLogger


def main():
    """Demonstrate basic PersonaTwin usage."""
    print("=" * 60)
    print("PersonaTwinFactory - Basic Usage Example")
    print("=" * 60)

    # Initialize transparency logger
    logger = TransparencyLogger()
    print("\n1. Initialized TransparencyLogger")

    # Create a new persona twin
    persona = PersonaTwin(
        name="Alice Johnson",
        transparency_logger=logger,
    )
    print(f"\n2. Created PersonaTwin: {persona}")
    print(f"   Persona ID: {persona.persona_id}")

    # Update persona attributes
    persona.update_attributes(
        age=28,
        gender="Female",
        occupation="Software Engineer",
        interests=["AI", "Machine Learning", "Data Privacy"],
        traits={
            "openness": 0.8,
            "conscientiousness": 0.9,
            "extroversion": 0.6,
        },
        user_id="admin",
    )
    print("\n3. Updated persona attributes")
    print(f"   Age: {persona.attributes.age}")
    print(f"   Occupation: {persona.attributes.occupation}")
    print(f"   Interests: {', '.join(persona.attributes.interests)}")

    # Record behaviors
    persona.add_behavior(
        behavior_type="interaction",
        context={"platform": "web", "action": "login"},
        response="successful_login",
        metadata={"ip_address": "192.168.1.1"},
        user_id="system",
    )
    print("\n4. Recorded behavior: interaction/login")

    persona.add_behavior(
        behavior_type="preference",
        context={"category": "privacy", "setting": "data_sharing"},
        response="opted_out",
        metadata={"timestamp": "2024-01-15T10:30:00"},
        user_id="alice_johnson",
    )
    print("5. Recorded behavior: preference/privacy")

    # Retrieve behaviors
    all_behaviors = persona.get_behaviors()
    print(f"\n6. Retrieved {len(all_behaviors)} behaviors")

    # Create a data snapshot
    snapshot = persona.create_snapshot()
    print(f"\n7. Created data snapshot: {snapshot.snapshot_id}")
    print(f"   Checksum: {snapshot.checksum[:32]}...")

    # Verify data integrity
    is_valid = logger.verify_data_integrity(
        snapshot.model_dump(exclude={"checksum"}),
        snapshot.checksum,
    )
    print(f"   Data integrity verified: {is_valid}")

    # Save persona to disk
    file_path = persona.save(user_id="admin")
    print(f"\n8. Saved persona to: {file_path}")

    # Get audit trail
    audit_trail = persona.get_audit_trail()
    print(f"\n9. Audit trail has {len(audit_trail)} entries")
    print("   Recent operations:")
    for log in audit_trail[-3:]:
        print(f"   - {log['operation']}: {log['details'].get('action', 'N/A')}")

    # Export all audit logs
    logger.export_audit_logs(file_path.parent / "audit_export.json")
    print("\n10. Exported audit logs to audit_export.json")

    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
