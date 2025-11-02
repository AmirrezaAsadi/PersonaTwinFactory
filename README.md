# PersonaTwinFactory

A Python framework for Digital Persona Twin development and data transparency.

## Overview

PersonaTwinFactory is a comprehensive Python library designed for creating, managing, and maintaining digital persona twins with a strong focus on data transparency, integrity, and audit trails. The framework provides tools for modeling persona attributes, recording behaviors, and ensuring complete transparency of all data operations through cryptographic hashing and optional encryption.

## Key Features

- **Digital Persona Twin Management**: Create and manage digital representations of personas with rich attributes and behavioral patterns
- **Data Transparency**: Complete audit logging of all operations with cryptographic hashing for data integrity
- **Encryption Support**: Optional encryption for sensitive persona data
- **Behavioral Tracking**: Record and analyze persona behaviors with contextual information
- **Data Snapshots**: Create point-in-time snapshots of persona state with integrity verification
- **Audit Trails**: Comprehensive logging of all create, read, update, and delete operations
- **Data Integrity**: Built-in hash-based verification to detect data tampering
- **Persistence**: Save and load persona data with full audit trail preservation

## Installation

### From Source

```bash
git clone https://github.com/AmirrezaAsadi/PersonaTwinFactory.git
cd PersonaTwinFactory
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

For development:

```bash
pip install -r requirements-dev.txt
```

## Quick Start

### Basic Usage

```python
from personatwinfactory import PersonaTwin, TransparencyLogger

# Initialize transparency logger
logger = TransparencyLogger()

# Create a new persona twin
persona = PersonaTwin(
    name="Alice Johnson",
    transparency_logger=logger,
)

# Update persona attributes
persona.update_attributes(
    age=28,
    occupation="Software Engineer",
    interests=["AI", "Data Privacy", "Machine Learning"],
    user_id="admin",
)

# Record behaviors
persona.add_behavior(
    behavior_type="interaction",
    context={"platform": "web", "action": "login"},
    response="successful_login",
)

# Create a data snapshot
snapshot = persona.create_snapshot()
print(f"Snapshot created with checksum: {snapshot.checksum}")

# Save persona to disk
file_path = persona.save()
print(f"Persona saved to: {file_path}")

# Get audit trail
audit_trail = persona.get_audit_trail()
print(f"Total operations logged: {len(audit_trail)}")
```

### Advanced Transparency Features

```python
from personatwinfactory import TransparencyLogger

# Generate encryption key
encryption_key = TransparencyLogger.generate_encryption_key()

# Initialize logger with encryption
logger = TransparencyLogger(encryption_key=encryption_key)

# Encrypt sensitive data
sensitive_data = "SSN: 123-45-6789"
encrypted = logger.encrypt_data(sensitive_data)

# Decrypt when needed
decrypted = logger.decrypt_data(encrypted)

# Verify data integrity
data = {"user": "alice", "action": "login"}
hash_value = logger.compute_hash(data)
is_valid = logger.verify_data_integrity(data, hash_value)
```

## Architecture

### Core Components

1. **PersonaTwin**: Main class for managing digital persona twins
2. **PersonaAttributes**: Data model for persona characteristics
3. **PersonaBehavior**: Data model for behavioral records
4. **TransparencyLogger**: Audit logging and data integrity verification
5. **AuditLog**: Individual audit log entry model
6. **DataSnapshot**: Point-in-time snapshot with integrity verification

### Data Models

#### PersonaAttributes
- `persona_id`: Unique identifier
- `name`: Persona name
- `age`, `gender`, `occupation`: Demographic attributes
- `interests`: List of interests
- `traits`: Dictionary of personality traits
- `created_at`, `updated_at`: Timestamps

#### PersonaBehavior
- `persona_id`: Reference to persona
- `behavior_type`: Category of behavior
- `context`: Situational context
- `response`: Action or response taken
- `timestamp`: When behavior occurred
- `metadata`: Additional information

## Data Transparency

PersonaTwinFactory ensures complete transparency through:

1. **Audit Logging**: Every operation (create, read, update, delete) is logged
2. **Data Hashing**: SHA-256 hashes verify data integrity
3. **Encryption**: Optional encryption for sensitive information
4. **Immutable Logs**: Audit logs are persisted to disk
5. **Timestamp Tracking**: All operations are timestamped
6. **User Attribution**: Operations can be attributed to specific users

## Examples

See the `examples/` directory for complete examples:

- `basic_usage.py`: Basic persona creation and management
- `advanced_transparency.py`: Advanced encryption and integrity features

Run examples:

```bash
python examples/basic_usage.py
python examples/advanced_transparency.py
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=personatwinfactory tests/
```

## Development

### Project Structure

```
PersonaTwinFactory/
├── personatwinfactory/      # Main package
│   ├── __init__.py
│   ├── persona_twin.py      # Core PersonaTwin class
│   ├── data_models.py       # Pydantic data models
│   └── transparency.py      # Transparency and audit logging
├── tests/                   # Test suite
│   ├── test_persona_twin.py
│   ├── test_data_models.py
│   └── test_transparency.py
├── examples/                # Usage examples
│   ├── basic_usage.py
│   └── advanced_transparency.py
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Code Quality

Format code:

```bash
black personatwinfactory/ tests/ examples/
```

Lint code:

```bash
flake8 personatwinfactory/ tests/
```

Type checking:

```bash
mypy personatwinfactory/
```

## Use Cases

- **Privacy-Preserving AI**: Train AI models on persona twins instead of real user data
- **User Modeling**: Create digital twins for personalization research
- **Data Governance**: Maintain transparent records of data usage
- **Compliance**: Demonstrate data handling practices for regulatory compliance
- **Research**: Study persona behaviors and patterns with full transparency
- **Testing**: Generate synthetic personas for testing user-facing systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Contact

For questions or issues, please open an issue on GitHub.

## Roadmap

- [ ] GraphQL API for persona management
- [ ] Blockchain integration for immutable audit trails
- [ ] Machine learning models for behavior prediction
- [ ] Web dashboard for persona visualization
- [ ] Export to standard data formats (JSON-LD, RDF)
- [ ] Integration with identity management systems