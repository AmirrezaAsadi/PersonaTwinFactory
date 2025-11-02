"""Core PersonaTwin class for creating and managing digital persona twins."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .data_models import PersonaAttributes, PersonaBehavior, DataSnapshot
from .transparency import TransparencyLogger


class PersonaTwin:
    """
    Digital Persona Twin with data transparency features.
    
    Represents a digital twin of a person's persona, including attributes,
    behaviors, and complete audit trail for data transparency.
    """

    def __init__(
        self,
        persona_id: Optional[str] = None,
        name: str = "Anonymous",
        transparency_logger: Optional[TransparencyLogger] = None,
        storage_path: Optional[Path] = None,
    ):
        """
        Initialize a new PersonaTwin.

        Args:
            persona_id: Unique identifier (generated if not provided)
            name: Name of the persona
            transparency_logger: Logger for transparency and audit trails
            storage_path: Path to store persona data
        """
        self.persona_id = persona_id or str(uuid.uuid4())
        self.transparency_logger = transparency_logger or TransparencyLogger()
        self.storage_path = storage_path or Path("./persona_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize persona attributes
        self.attributes = PersonaAttributes(
            persona_id=self.persona_id,
            name=name,
        )

        # Initialize behaviors list
        self.behaviors: List[PersonaBehavior] = []

        # Log creation
        self.transparency_logger.log_operation(
            operation="create",
            persona_id=self.persona_id,
            data=self.attributes.model_dump(),
            details={"action": "persona_twin_created"},
        )

    def update_attributes(
        self, user_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        """
        Update persona attributes with transparency logging.

        Args:
            user_id: User performing the update
            **kwargs: Attributes to update
        """
        old_data = self.attributes.model_dump()

        # Update attributes
        for key, value in kwargs.items():
            if hasattr(self.attributes, key):
                setattr(self.attributes, key, value)

        self.attributes.updated_at = datetime.now(timezone.utc)

        # Log the update
        self.transparency_logger.log_operation(
            operation="update",
            persona_id=self.persona_id,
            data=self.attributes.model_dump(),
            user_id=user_id,
            details={"updated_fields": list(kwargs.keys()), "old_data": old_data},
        )

    def add_behavior(
        self,
        behavior_type: str,
        context: Optional[Dict[str, Any]] = None,
        response: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> PersonaBehavior:
        """
        Record a behavior with transparency logging.

        Args:
            behavior_type: Type of behavior
            context: Context in which the behavior occurred
            response: Response or action taken
            metadata: Additional metadata
            user_id: User recording the behavior

        Returns:
            The created PersonaBehavior object
        """
        behavior = PersonaBehavior(
            persona_id=self.persona_id,
            behavior_type=behavior_type,
            context=context or {},
            response=response,
            metadata=metadata or {},
        )

        self.behaviors.append(behavior)

        # Log the behavior addition
        self.transparency_logger.log_operation(
            operation="create",
            persona_id=self.persona_id,
            data=behavior.model_dump(),
            user_id=user_id,
            details={"action": "behavior_added", "behavior_type": behavior_type},
        )

        return behavior

    def get_behaviors(
        self, behavior_type: Optional[str] = None, limit: Optional[int] = None
    ) -> List[PersonaBehavior]:
        """
        Retrieve behaviors, optionally filtered by type.

        Args:
            behavior_type: Optional filter by behavior type
            limit: Maximum number of behaviors to return

        Returns:
            List of PersonaBehavior objects
        """
        behaviors = self.behaviors

        if behavior_type:
            behaviors = [b for b in behaviors if b.behavior_type == behavior_type]

        # Sort by timestamp (most recent first)
        behaviors = sorted(behaviors, key=lambda b: b.timestamp, reverse=True)

        if limit:
            behaviors = behaviors[:limit]

        # Log the read operation
        self.transparency_logger.log_operation(
            operation="read",
            persona_id=self.persona_id,
            data={"behavior_count": len(behaviors), "behavior_type": behavior_type},
            details={"action": "behaviors_retrieved"},
        )

        return behaviors

    def create_snapshot(self) -> DataSnapshot:
        """
        Create a snapshot of the current persona state.

        Returns:
            DataSnapshot object with current state
        """
        snapshot_id = f"{self.persona_id}_snapshot_{datetime.now(timezone.utc).timestamp()}"

        snapshot = DataSnapshot(
            snapshot_id=snapshot_id,
            persona_id=self.persona_id,
            attributes=self.attributes,
            behaviors=self.behaviors[-10:],  # Last 10 behaviors
        )

        # Compute checksum for integrity
        snapshot.checksum = self.transparency_logger.compute_hash(
            snapshot.model_dump(exclude={"checksum"})
        )

        # Log snapshot creation
        self.transparency_logger.log_operation(
            operation="create",
            persona_id=self.persona_id,
            data=snapshot.model_dump(),
            details={"action": "snapshot_created", "snapshot_id": snapshot_id},
        )

        return snapshot

    def save(self, user_id: Optional[str] = None) -> Path:
        """
        Save persona data to storage.

        Args:
            user_id: User performing the save operation

        Returns:
            Path to saved file
        """
        file_path = self.storage_path / f"{self.persona_id}.json"

        data = {
            "attributes": self.attributes.model_dump(),
            "behaviors": [b.model_dump() for b in self.behaviors],
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        # Log save operation
        self.transparency_logger.log_operation(
            operation="create",
            persona_id=self.persona_id,
            data={"file_path": str(file_path)},
            user_id=user_id,
            details={"action": "persona_saved"},
        )

        return file_path

    @classmethod
    def load(
        cls,
        persona_id: str,
        transparency_logger: Optional[TransparencyLogger] = None,
        storage_path: Optional[Path] = None,
    ) -> "PersonaTwin":
        """
        Load a persona from storage.

        Args:
            persona_id: ID of the persona to load
            transparency_logger: Logger for transparency
            storage_path: Path where persona data is stored

        Returns:
            Loaded PersonaTwin object

        Raises:
            FileNotFoundError: If persona file doesn't exist
        """
        storage_path = storage_path or Path("./persona_data")
        file_path = storage_path / f"{persona_id}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Persona {persona_id} not found at {file_path}")

        with open(file_path, "r") as f:
            data = json.load(f)

        # Create persona twin
        persona = cls(
            persona_id=persona_id,
            name=data["attributes"]["name"],
            transparency_logger=transparency_logger,
            storage_path=storage_path,
        )

        # Restore attributes
        persona.attributes = PersonaAttributes(**data["attributes"])

        # Restore behaviors
        persona.behaviors = [PersonaBehavior(**b) for b in data["behaviors"]]

        # Log load operation
        persona.transparency_logger.log_operation(
            operation="read",
            persona_id=persona_id,
            data={"file_path": str(file_path)},
            details={"action": "persona_loaded"},
        )

        return persona

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Get the complete audit trail for this persona.

        Returns:
            List of audit log entries
        """
        logs = self.transparency_logger.get_audit_trail(persona_id=self.persona_id)
        return [log.model_dump() for log in logs]

    def __repr__(self) -> str:
        """String representation of the PersonaTwin."""
        return (
            f"PersonaTwin(id={self.persona_id}, name={self.attributes.name}, "
            f"behaviors={len(self.behaviors)})"
        )
