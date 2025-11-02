# PersonaTwin: Privacy-Preserving Persona Generation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Transform sensitive people-events datasets into shareable personas while preserving statistical utility and ensuring privacy.**

## 🎯 What is PersonaTwin?

PersonaTwin is a Python package that solves a critical problem: **How to safely share and analyze sensitive user data while protecting individual privacy**.

It's domain-agnostic and works with any people-events data:
- 🏛️ **Criminal Justice**: court records, arrests, sentencing
- 🏥 **Healthcare**: patient visits, diagnoses, treatments
- 🎓 **Education**: student records, assessments, outcomes
- 🤝 **Social Services**: benefits, case management, interventions
- 💼 **Employment**: HR records, performance, career progression
- 🔧 **Custom Domains**: Define your own event types and outcomes

## ✨ Key Features

### 🔒 Strong Privacy Protection
- **K-Anonymity**: Ensures minimum group sizes
- **Differential Privacy**: Mathematical privacy guarantees
- **Population-Level Traceability**: Measures re-identification risk
- **Census-Enhanced Privacy**: Uses public demographic data for accurate risk assessment
- **Automatic Risk Mitigation**: Adjusts protection until safe

### 📊 Preserves Statistical Utility
- Maintains demographic distributions for bias analysis
- Preserves outcome patterns and correlations
- Enables meaningful research on protected data
- Configurable privacy-utility trade-offs

### 🚀 Easy to Use
```python
import personatwin as pt

# Load your sensitive data
people = pt.load_criminal_justice_data("court_records.csv")

# Generate safe personas
result = pt.create_safe_personas(
    data=people,
    privacy_level="high",
    domain="criminal_justice",
    target_risk=0.01  # 1% re-identification risk
)

# Check safety
print(f"Risk level: {result.risk_metrics.get_risk_level()}")
print(f"Safe for public: {result.is_safe_for_public()}")

# Export
pt.export_personas(result.personas, "safe_personas.csv")
pt.export_privacy_report(result, "privacy_report.html")
```

## 📦 Installation

```bash
# Install from source
git clone https://github.com/AmirrezaAsadi/PersonaTwinFactory.git
cd PersonaTwinFactory
pip install -e .

# Or install from PyPI (when published)
pip install personatwin
```

### Requirements
- Python 3.8+
- pandas, numpy, scipy
- scikit-learn
- Optional: openai, anthropic (for LLM-enhanced privacy decisions)

## 🚀 Quick Start

### Example 1: Criminal Justice Data

```python
import personatwin as pt
import pandas as pd

# Load court records
df = pd.read_csv("court_records.csv")

# Generate personas with high privacy
result = pt.create_safe_personas(
    data=df,
    privacy_level="high",
    domain="criminal_justice",
    target_risk=0.01
)

# Analyze results
print(f"Generated {len(result.personas)} personas")
print(f"Population risk: {result.risk_metrics.population_average_risk:.3%}")
print(f"K-anonymity: {result.risk_metrics.k_anonymity}")

# Export for sharing
personas_df = pt.personas_to_dataframe(result.personas)
personas_df.to_csv("safe_court_data.csv", index=False)
```

### Example 2: Healthcare Data

```python
import personatwin as pt

# Load patient records
patients = pt.load_healthcare_data("patient_visits.csv")

# Generate personas for research
result = pt.create_safe_personas(
    data=patients,
    privacy_level="medium",
    domain="healthcare",
    target_risk=0.05  # 5% risk for research use
)

# Event-level export
events_df = pt.personas_to_event_dataframe(result.personas)
events_df.to_csv("safe_patient_events.csv", index=False)
```

### Example 3: Custom Domain

```python
import personatwin as pt

# Define your own domain
custom_config = pt.create_custom_config(
    event_types=["application", "interview", "hire", "promotion", "exit"],
    outcomes=["successful", "unsuccessful", "pending"],
    sensitive_fields={"employee_id", "ssn", "salary"},
    preserve_fields={"job_level", "department", "performance_rating"},
    temporal_precision="month",
    geographic_precision="state"
)

# Generate personas
result = pt.create_safe_personas(
    data=your_data,
    privacy_level="high",
    domain="custom",
    domain_config=custom_config
)
```

## 🏗️ Architecture

### Core Components

1. **Data Models** (`models.py`)
   - `Person`: Original individual with demographics and events
   - `Event`: Domain-agnostic event structure
   - `Persona`: Privacy-protected merged entity

2. **Privacy Protection** (`privacy.py`)
   - `PopulationTraceability`: Risk calculation
   - `RiskMetrics`: Comprehensive risk assessment
   - `AutoPrivacyAdjustment`: Automatic risk mitigation

3. **Processing** (`merging.py`, `noise.py`)
   - `PeopleMerging`: K-anonymity through merging
   - `EventNoiseGeneration`: Temporal and outcome noise

4. **Domain Configurations** (`domains.py`)
   - Pre-configured domains (criminal justice, healthcare, education, etc.)
   - Custom domain support

5. **Pipeline** (`pipeline.py`)
   - End-to-end processing
   - Iterative privacy adjustment
   - Validation and reporting

6. **LLM Integration** (`llm_integration.py`) - Optional
   - AI-driven privacy decisions
   - Synthetic event generation

## 🔧 Configuration Options

### Privacy Levels

```python
privacy_level = "low"      # Minimal protection, higher utility
privacy_level = "medium"   # Balanced (default)
privacy_level = "high"     # Strong protection
privacy_level = "maximum"  # Maximum privacy, minimal utility
```

### Risk Thresholds

```python
target_risk = 0.01  # 1% - Safe for public release
target_risk = 0.05  # 5% - Safe for research
target_risk = 0.15  # 15% - Internal use only
```

### Domain Selection

```python
from personatwin import Domain

domain = Domain.CRIMINAL_JUSTICE
domain = Domain.HEALTHCARE
domain = Domain.EDUCATION
domain = Domain.SOCIAL_SERVICES
domain = Domain.EMPLOYMENT
domain = Domain.CUSTOM  # Define your own
```

## 📊 Supported Domains

### Criminal Justice
Events: arrest, charge, trial, sentencing, probation, appeal, etc.
Outcomes: guilty, not_guilty, dismissed, plea_bargain, etc.

### Healthcare
Events: admission, discharge, diagnosis, treatment, surgery, etc.
Outcomes: recovered, improved, stable, declined, etc.

### Education
Events: enrollment, assessment, grade, graduation, suspension, etc.
Outcomes: passed, failed, graduated, promoted, etc.

### Social Services
Events: application, benefit_received, case_opened, service_provided, etc.
Outcomes: approved, denied, completed, compliant, etc.

### Employment
Events: hire, promotion, performance_review, training, termination, etc.
Outcomes: successful, promoted, completed, terminated, etc.

## 📈 Census-Enhanced Privacy Assessment

PersonaTwin automatically uses **public demographic data** to improve privacy assessment - no manual data collection required!

### How It Works

1. **Automatic Census Data Fetching**
   - Connects to US Census Bureau API (free, no auth required)
   - Downloads real demographic distributions for geographic areas
   - Caches data locally in `~/.personatwin/census_cache`

2. **Enhanced Risk Calculation**
   - Detects rare demographic combinations using real population data
   - Calculates realistic external linkage risk
   - Identifies vulnerable populations automatically

3. **Fallback System**
   - Works offline with bundled synthetic census data
   - Uses US national averages when API unavailable
   - Conservative estimates ensure safety

### Usage

```python
import personatwin as pt

# Census enhancement enabled by default
result = pt.create_safe_personas(
    data=your_data,
    privacy_level="high",
    use_census_data=True  # Enabled by default
)

# Check for census insights in the report
if "CENSUS:" in result.risk_metrics.recommendation:
    print("Census-enhanced privacy assessment detected rare demographics")
```

### Data Sources

- **Primary**: [US Census Bureau API](https://www.census.gov/data/developers/data-sets.html)
- **Cache**: `~/.personatwin/census_cache/` (automatically created)
- **Fallback**: Bundled US national demographic averages

**No API keys or manual downloads required!** The system handles everything automatically.

See `examples/census_enhanced_example.py` for a complete demonstration.

## 🤖 LLM Integration (Optional)

Enable AI-driven privacy decisions with OpenAI or Anthropic:

```python
import personatwin as pt

result = pt.create_safe_personas(
    data=your_data,
    privacy_level="high",
    domain="healthcare",
    enable_llm=True,
    llm_api_key="your-openai-api-key"
)
```

Benefits:
- Intelligent privacy-utility trade-offs
- Context-aware synthetic event generation
- Adaptive risk mitigation strategies

## 📈 How It Works

1. **Merge Similar People**: Groups people by demographics to create k-anonymity
2. **Add Noise**: Blurs dates, generalizes locations, adds outcome uncertainty
3. **Calculate Risk**: Measures population-level re-identification risk
4. **Iterate**: Automatically adjusts protection until target risk achieved
5. **Validate**: Ensures statistical utility preserved

### Privacy Protection Strategies

- **Merging**: Combines similar people (improves k-anonymity)
- **Temporal Noise**: Blurs exact dates to time periods
- **Geographic Generalization**: address → city → county → state
- **Outcome Noise**: Adds realistic uncertainty
- **Synthetic Events**: LLM-generated fake events (optional)

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=personatwin --cov-report=html
```

## 📝 Data Format

### Input Format (CSV)

**Person-level:**
```csv
person_id,age,gender,ethnicity,geography
001,35,Male,White,Hamilton County OH
002,28,Female,Black,Hamilton County OH
```

**Event-level:**
```csv
person_id,age,gender,ethnicity,geography,event_id,date,event_type,outcome
001,35,Male,White,Hamilton County,E1,2023-01-15,arrest,charged
001,35,Male,White,Hamilton County,E2,2023-03-20,trial,guilty
```

### Output Format

PersonaTwin generates:
1. **Persona-level CSV**: One row per persona with aggregated statistics
2. **Event-level CSV**: All events with persona linkage
3. **Privacy Report HTML**: Detailed risk assessment

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Additional domain configurations
- Enhanced privacy metrics
- Performance optimizations
- Documentation improvements

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 📚 Citation

If you use PersonaTwin in research, please cite:

```bibtex
@software{personatwin2025,
  author = {Asadi, Amirreza},
  title = {PersonaTwin: Privacy-Preserving Persona Generation},
  year = {2025},
  url = {https://github.com/AmirrezaAsadi/PersonaTwinFactory}
}
```

## 🔗 Links

- **GitHub**: https://github.com/AmirrezaAsadi/PersonaTwinFactory
- **Issues**: https://github.com/AmirrezaAsadi/PersonaTwinFactory/issues
- **Documentation**: Coming soon

## 💡 Use Cases

- **Government Transparency**: Share public sector data safely
- **Research Collaboration**: Enable multi-institution studies
- **Bias Analysis**: Study disparities without privacy risks
- **ML Training**: Generate diverse test datasets
- **Regulatory Compliance**: Meet GDPR, CCPA requirements

## ⚠️ Important Notes

- PersonaTwin provides **statistical privacy**, not absolute guarantees
- Always review risk reports before public release
- Test with your specific data before production use
- Consider legal and ethical implications in your domain
- LLM features require API keys and may incur costs

## 📞 Contact

- **Author**: Amirreza Asadi
- **Email**: your.email@example.com
- **Issues**: Use GitHub Issues for bugs and feature requests

---

**PersonaTwin** - Making sensitive data safe to share, one persona at a time. 🔒✨