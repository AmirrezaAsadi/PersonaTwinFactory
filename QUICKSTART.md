# PersonaTwin Quick Start Guide

## Installation

```bash
cd PersonaTwinFactory
pip install -e .
```

## 5-Minute Quick Start

### 1. Basic Usage

```python
import personatwin as pt
from datetime import datetime

# Create a person with events
demographics = pt.Demographics(
    age=35,
    gender="Male",
    ethnicity="White",
    geography="Hamilton County, OH"
)

events = [
    pt.Event(
        event_id="E1",
        date=datetime(2023, 1, 15),
        event_type="arrest",
        outcome="charged"
    ),
    pt.Event(
        event_id="E2",
        date=datetime(2023, 3, 20),
        event_type="trial",
        outcome="guilty"
    )
]

person = pt.Person(
    person_id="P001",
    demographics=demographics,
    events=events
)

# Generate safe personas
result = pt.create_safe_personas(
    data=[person],  # Add more people for realistic use
    privacy_level="high",
    domain="criminal_justice",
    target_risk=0.05
)

print(f"Risk: {result.risk_metrics.population_average_risk:.3%}")
print(f"Safe: {result.is_safe_for_research()}")
```

### 2. With CSV Data

```python
import personatwin as pt
import pandas as pd

# Load your CSV
df = pd.read_csv("your_data.csv")

# Generate personas
result = pt.create_safe_personas(
    data=df,
    privacy_level="high",
    domain="criminal_justice"
)

# Export results
pt.export_personas(result.personas, "safe_personas.csv")
pt.export_privacy_report(result, "privacy_report.html")
```

### 3. Custom Domain

```python
import personatwin as pt

# Define your domain
config = pt.create_custom_config(
    event_types=["login", "purchase", "logout"],
    outcomes=["successful", "failed"],
    sensitive_fields={"user_id", "email"},
    preserve_fields={"action_type", "timestamp"},
    temporal_precision="week",
    geographic_precision="state"
)

# Use it
result = pt.create_safe_personas(
    data=your_data,
    domain="custom",
    domain_config=config
)
```

## Running Examples

```bash
# Criminal justice example
python examples/criminal_justice_example.py

# Healthcare example
python examples/healthcare_example.py

# Custom domain example
python examples/custom_domain_example.py
```

## Privacy Levels

- **low**: Minimal protection, higher data utility
- **medium**: Balanced (recommended for most cases)
- **high**: Strong protection (recommended for public release)
- **maximum**: Maximum privacy, minimal utility

## Risk Targets

- **0.01** (1%): Safe for public release
- **0.05** (5%): Safe for research use
- **0.15** (15%): Internal use only

## Common Use Cases

### Use Case 1: Public Dataset Release
```python
result = pt.create_safe_personas(
    data=sensitive_data,
    privacy_level="high",
    target_risk=0.01  # 1% risk
)
```

### Use Case 2: Research Collaboration
```python
result = pt.create_safe_personas(
    data=sensitive_data,
    privacy_level="medium",
    target_risk=0.05  # 5% risk
)
```

### Use Case 3: Internal Analytics
```python
result = pt.create_safe_personas(
    data=sensitive_data,
    privacy_level="low",
    target_risk=0.15  # 15% risk
)
```

## Data Format Requirements

### Option 1: Event-level CSV
```csv
person_id,age,gender,ethnicity,geography,event_id,date,event_type,outcome
P001,35,Male,White,Hamilton County,E1,2023-01-15,arrest,charged
P001,35,Male,White,Hamilton County,E2,2023-03-20,trial,guilty
P002,28,Female,Black,Franklin County,E3,2023-02-10,arrest,dismissed
```

### Option 2: Person objects
```python
people = [
    pt.Person(
        person_id="P001",
        demographics=pt.Demographics(...),
        events=[pt.Event(...), ...]
    ),
    ...
]
```

## Troubleshooting

### Issue: "Population risk too high"
**Solution**: Increase privacy level or reduce target risk

```python
result = pt.create_safe_personas(
    data=data,
    privacy_level="maximum",  # Increase this
    target_risk=0.10  # Or increase this
)
```

### Issue: "Not enough data"
**Solution**: PersonaTwin works best with 50+ people

```python
# Need at least 50 people for good results
assert len(your_data) >= 50
```

### Issue: "K-anonymity too low"
**Solution**: Merge more people together

```python
config = pt.ProcessingConfig(
    min_k_anonymity=10  # Increase this
)
```

## Next Steps

1. **Read the full README**: [README.md](README.md)
2. **Explore examples**: [examples/](examples/)
3. **Check the requirements doc**: [PersonaTwin_Requirements.md](PersonaTwin_Requirements.md)
4. **Run tests**: `pytest tests/`

## Getting Help

- **GitHub Issues**: https://github.com/AmirrezaAsadi/PersonaTwinFactory/issues
- **Documentation**: Coming soon
- **Examples**: See `examples/` directory

## Quick Reference

```python
import personatwin as pt

# Core classes
pt.Person, pt.Event, pt.Persona, pt.Demographics

# Privacy levels
pt.PrivacyLevel.LOW, .MEDIUM, .HIGH, .MAXIMUM

# Domains
pt.Domain.CRIMINAL_JUSTICE, .HEALTHCARE, .EDUCATION, 
.SOCIAL_SERVICES, .EMPLOYMENT, .CUSTOM

# Main function
result = pt.create_safe_personas(data, privacy_level, domain)

# Export functions
pt.export_personas(personas, "file.csv")
pt.export_privacy_report(result, "report.html")
pt.personas_to_dataframe(personas)
```
