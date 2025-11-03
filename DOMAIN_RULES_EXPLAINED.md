# Domain-Specific Rules & Patient Impact - Explained

## 🏥 How Patients Are Impacted

### Before: The Problem

When PersonaTwin merges multiple patients into one persona, **naive concatenation creates medical impossibilities**:

```python
# Real scenario example:
Patient A: [admission_2023-01-10, discharge_2023-01-20]
Patient B: [admission_2023-02-05, discharge_2023-02-15]  
Patient C: [admission_2023-03-01]  # Still hospitalized (no discharge)

# ❌ NAIVE MERGE (OLD):
Persona: [
    admission_2023-01-10,
    discharge_2023-01-20,
    admission_2023-02-05,    # ❌ Re-admitted after discharge (OK)
    discharge_2023-02-15,
    admission_2023-03-01     # ❌ Still "hospitalized" forever (BAD!)
]
```

**Medical Problem:** The persona appears to be hospitalized indefinitely (since March 2023) with no discharge. This is:
- 🚨 **Medically unrealistic** (long-term hospitalizations should close)
- 🚨 **Data quality issue** (incomplete record)
- 🚨 **Privacy risk** (unique pattern: "person hospitalized for 9+ months")

### After: The Solution

With **domain-specific rules**, PersonaTwin ensures medical logic:

```python
# ✅ RULE-BASED MERGE (NEW):
Persona: [
    admission_2023-01-10,
    discharge_2023-01-20,
    admission_2023-02-05,
    discharge_2023-02-15,
    admission_2023-03-01,
    discharge_2023-03-31  # ✨ AUTO-ADDED (synthetic event)
]
```

**Impact on Patient Privacy:**
- ✅ **More realistic personas** → harder to identify
- ✅ **Complete medical records** → better for research
- ✅ **Reduced uniqueness** → similar patterns across personas
- ✅ **Preserved medical logic** → usable for healthcare analysis

---

## 🔍 Detailed Patient Impact Examples

### Example 1: Patient with Incomplete Records

**Scenario:** Patient admitted but no discharge recorded (transferred, data entry error, etc.)

```python
# Original Patient Record:
Patient X:
  - admission: 2023-01-15, Memorial Hospital
  - diagnosis: pneumonia
  - treatment: antibiotics
  # Missing discharge!

# What happens during merging:
```

#### Without Rules ❌:
```python
# Merged with 2 other patients:
Persona:
  - admission: 2023-01-15  # From Patient X
  - diagnosis: pneumonia
  - treatment: antibiotics
  - admission: 2023-02-10  # From Patient Y
  # ❌ PROBLEM: Admitted twice without discharge!
  # This violates medical logic
```

**Patient Impact:**
- ❌ Unrealistic medical history
- ❌ Could be re-identified by this unique pattern
- ❌ Data unusable for medical research (invalid sequence)

#### With Rules ✅:
```python
# Rule: admission requires_closure=True
Persona:
  - admission: 2023-01-15  # From Patient X
  - diagnosis: pneumonia
  - treatment: antibiotics
  - discharge: 2023-02-05  # ✨ AUTO-ADDED (synthetic)
  - admission: 2023-02-10  # From Patient Y
  # ✅ FIXED: Logical sequence maintained
```

**Patient Impact:**
- ✅ Realistic medical history
- ✅ Cannot be re-identified (common pattern)
- ✅ Data usable for research
- ✅ **Original patient still protected** (synthetic discharge is noise)

---

### Example 2: Surgery Without Admission

**Scenario:** Patient has surgery record but no admission (data import error)

```python
# Original Patient Record:
Patient Y:
  # Missing admission!
  - surgery: 2023-03-20, knee_replacement
  - discharge: 2023-03-25
```

#### Without Rules ❌:
```python
Persona:
  - surgery: 2023-03-20  # ❌ Surgery without admission!
  - discharge: 2023-03-25
```

**Medical Problem:** You cannot have surgery without being admitted to a hospital. This is **medically impossible**.

#### With Rules ✅:
```python
# Rule: surgery must_follow=["admission"]
Persona:
  - admission: 2023-03-19  # ✨ AUTO-ADDED (1 day before surgery)
  - surgery: 2023-03-20
  - discharge: 2023-03-25
```

**Patient Impact:**
- ✅ Medically valid sequence
- ✅ Protects patient (synthetic admission adds noise)
- ✅ Research-ready data

---

### Example 3: Multiple Hospitalizations

**Scenario:** Merging 3 patients who all had hospital admissions

```python
# Original Patients:
Patient A: [admission_2023-01-10, diagnosis_flu, discharge_2023-01-15]
Patient B: [admission_2023-01-12, diagnosis_pneumonia, discharge_2023-01-18]
Patient C: [admission_2023-01-14, diagnosis_flu, discharge_2023-01-20]
```

#### Similarity-Based Merging:
```python
# Similar events merged:
Persona:
  - admission: 2023-01-12      # Merged from 3 (median date)
    details: { "_merged_count": 3 }
  - diagnosis: flu              # Merged from 2 (most common)
    details: { "_merged_count": 2 }
  - discharge: 2023-01-18       # Merged from 3 (median date)
    details: { "_merged_count": 3 }
```

**Patient Impact:**
- ✅ **K-anonymity improved:** 3 patients share this pattern
- ✅ **Event count reduced:** 9 events → 3 representative events
- ✅ **Privacy enhanced:** Individual timelines obscured
- ✅ **Statistical patterns preserved:** Still shows flu admission in January

---

## ⚙️ How Domain-Specific Rules Work

### 1. Event Sequence Rules

Rules are defined per event type:

```python
@dataclass
class EventSequenceRule:
    event_type: str                          # e.g., "admission"
    must_follow: Optional[List[str]]         # Must come AFTER these events
    cannot_follow: Optional[List[str]]       # Cannot come AFTER these events
    max_occurrences: Optional[int]           # Maximum times allowed
    requires_closure: bool                   # Needs a closing event?
    closure_event_type: Optional[str]        # What event closes this?
```

### 2. Healthcare Rules (Built-in)

```python
# ADMISSION
EventSequenceRule(
    event_type="admission",
    requires_closure=True,           # Must be closed
    closure_event_type="discharge"   # Closed by discharge
)
# Impact: Prevents "stuck in hospital" personas

# DISCHARGE
EventSequenceRule(
    event_type="discharge",
    must_follow=["admission"]        # Can't discharge without admission
)
# Impact: Ensures logical sequence

# SURGERY
EventSequenceRule(
    event_type="surgery",
    must_follow=["admission"]        # Surgery requires hospitalization
)
# Impact: Adds missing admission if needed

# TREATMENT
EventSequenceRule(
    event_type="treatment",
    must_follow=["diagnosis"]        # Can't treat without diagnosis
)
# Impact: Ensures medical logic

# FOLLOW_UP
EventSequenceRule(
    event_type="follow_up",
    must_follow=["discharge"]        # Follow-up after discharge
)
# Impact: Maintains care continuum
```

### 3. Criminal Justice Rules (Built-in)

```python
# CHARGE
EventSequenceRule(
    event_type="charge",
    must_follow=["arrest"]           # Must be arrested first
)

# TRIAL
EventSequenceRule(
    event_type="trial",
    must_follow=["charge"]           # Trial follows charges
)

# SENTENCING
EventSequenceRule(
    event_type="sentencing",
    must_follow=["trial"]            # Sentencing follows trial
)

# INCARCERATION
EventSequenceRule(
    event_type="incarceration",
    must_follow=["sentencing"],
    requires_closure=True,
    closure_event_type="release"     # Must eventually be released
)
```

### 4. Education Rules (Built-in)

```python
# ASSESSMENT
EventSequenceRule(
    event_type="assessment",
    must_follow=["enrollment"]       # Must be enrolled to be assessed
)

# GRADUATION
EventSequenceRule(
    event_type="graduation",
    must_follow=["enrollment"]       # Must be enrolled to graduate
)
```

---

## 🛠️ Can Users Define Custom Rules?

### ✅ YES! Three Ways:

### Option 1: Custom Domain with Rules

```python
from personatwin.event_merging import EventSequenceRule, DomainEventRules
from personatwin.domains import Domain

# Extend DomainEventRules class
class CustomDomainRules(DomainEventRules):
    @staticmethod
    def get_rules(domain: Domain) -> Dict[str, EventSequenceRule]:
        if domain == Domain.CUSTOM:
            return {
                # Your custom rules
                "loan_application": EventSequenceRule("loan_application"),
                "credit_check": EventSequenceRule(
                    "credit_check",
                    must_follow=["loan_application"]
                ),
                "loan_approval": EventSequenceRule(
                    "loan_approval",
                    must_follow=["credit_check"]
                ),
                "loan_disbursement": EventSequenceRule(
                    "loan_disbursement",
                    must_follow=["loan_approval"],
                    requires_closure=True,
                    closure_event_type="loan_repayment"
                ),
                "loan_repayment": EventSequenceRule(
                    "loan_repayment",
                    must_follow=["loan_disbursement"]
                ),
            }
        else:
            # Use built-in rules for other domains
            return DomainEventRules.get_rules(domain)

# Use custom rules
from personatwin.event_merging import IntelligentEventMerger

merger = IntelligentEventMerger(
    domain=Domain.CUSTOM,
    strategy=EventMergingStrategy.RULE_BASED
)

# Inject custom rules
merger.rules = CustomDomainRules.get_rules(Domain.CUSTOM)
```

### Option 2: Direct Rule Dictionary

```python
from personatwin.event_merging import IntelligentEventMerger, EventSequenceRule

# Define rules directly
custom_rules = {
    "order_placed": EventSequenceRule("order_placed"),
    "payment_received": EventSequenceRule(
        "payment_received",
        must_follow=["order_placed"]
    ),
    "item_shipped": EventSequenceRule(
        "item_shipped",
        must_follow=["payment_received"]
    ),
    "item_delivered": EventSequenceRule(
        "item_delivered",
        must_follow=["item_shipped"]
    ),
}

# Create merger and inject rules
merger = IntelligentEventMerger(Domain.CUSTOM, EventMergingStrategy.RULE_BASED)
merger.rules = custom_rules
```

### Option 3: Modify Existing Rules

```python
from personatwin.event_merging import IntelligentEventMerger, DomainEventRules
from personatwin.domains import Domain

# Get healthcare rules
healthcare_rules = DomainEventRules.get_rules(Domain.HEALTHCARE)

# Add custom healthcare events
healthcare_rules["mri_scan"] = EventSequenceRule(
    "mri_scan",
    must_follow=["admission"],           # MRI requires hospitalization
    cannot_follow=["discharge"]          # Can't do MRI after discharge
)

healthcare_rules["physical_therapy"] = EventSequenceRule(
    "physical_therapy",
    must_follow=["discharge"],           # PT after discharge
    max_occurrences=None                 # Can have multiple PT sessions
)

# Use modified rules
merger = IntelligentEventMerger(Domain.HEALTHCARE, EventMergingStrategy.RULE_BASED)
merger.rules = healthcare_rules
```

---

## 📋 Complete Custom Domain Example

### Scenario: Employee HR Records

```python
from personatwin.models import Person, Event, Demographics
from personatwin.event_merging import (
    IntelligentEventMerger, 
    EventSequenceRule, 
    EventMergingStrategy
)
from personatwin.domains import Domain
from datetime import datetime

# Define HR event rules
hr_rules = {
    "application": EventSequenceRule("application"),
    
    "interview": EventSequenceRule(
        "interview",
        must_follow=["application"]
    ),
    
    "job_offer": EventSequenceRule(
        "job_offer",
        must_follow=["interview"]
    ),
    
    "hire": EventSequenceRule(
        "hire",
        must_follow=["job_offer"],
        requires_closure=True,
        closure_event_type="termination"
    ),
    
    "promotion": EventSequenceRule(
        "promotion",
        must_follow=["hire"]
    ),
    
    "termination": EventSequenceRule(
        "termination",
        must_follow=["hire"]
    ),
    
    "rehire": EventSequenceRule(
        "rehire",
        must_follow=["termination"]
    ),
}

# Create sample employees
employees = [
    Person(
        person_id="E001",
        demographics=Demographics(age=28, gender="Male"),
        events=[
            Event("EV1", datetime(2022, 1, 15), "application", "submitted"),
            Event("EV2", datetime(2022, 2, 1), "interview", "passed"),
            Event("EV3", datetime(2022, 2, 10), "job_offer", "accepted"),
            Event("EV4", datetime(2022, 3, 1), "hire", "hired"),
            # Missing termination!
        ]
    ),
    Person(
        person_id="E002",
        demographics=Demographics(age=30, gender="Male"),
        events=[
            Event("EV5", datetime(2022, 1, 20), "application", "submitted"),
            Event("EV6", datetime(2022, 2, 5), "interview", "passed"),
            Event("EV7", datetime(2022, 2, 15), "hire", "hired"),  # Missing job_offer!
            Event("EV8", datetime(2023, 6, 30), "termination", "resigned"),
        ]
    ),
]

# Create merger with custom rules
merger = IntelligentEventMerger(Domain.CUSTOM, EventMergingStrategy.RULE_BASED)
merger.rules = hr_rules

# Merge events
merged_events = merger.merge_events(employees)

# Print results
print("Merged Employee Persona:")
for event in merged_events:
    marker = " ✨ [SYNTHETIC]" if event.details.get("_synthetic") else ""
    print(f"  {event.date.strftime('%Y-%m-%d')}: {event.event_type}{marker}")
    if event.details.get("_reason"):
        print(f"    Reason: {event.details['_reason']}")
```

**Expected Output:**
```
Merged Employee Persona:
  2022-01-20: application
  2022-02-05: interview
  2022-02-10: job_offer ✨ [SYNTHETIC]
    Reason: Required before hire
  2022-02-15: hire
  2023-06-30: termination
```

---

## 🎯 Benefits for Patients/Individuals

### 1. **Enhanced Privacy** 🔒
- Synthetic events add noise → harder to re-identify
- Complete sequences → reduces uniqueness
- Shared patterns → increased k-anonymity

### 2. **Data Quality** ✅
- Medically valid sequences → usable for research
- Complete records → better statistical analysis
- Logical flow → maintains domain integrity

### 3. **Realistic Personas** 👤
- Natural event sequences → harder to spot synthetic data
- Domain-compliant → passes expert review
- Statistical accuracy → preserves research value

### 4. **Transparency** 📊
- Synthetic events clearly marked
- Provenance tracked (merged from N events)
- Reasons documented

---

## 🔑 Key Takeaways

1. **Domain rules protect patients** by creating realistic, complete medical records
2. **Synthetic events are privacy-enhancing noise**, not falsification
3. **Users CAN define custom rules** for any domain
4. **Built-in rules** cover Healthcare, Criminal Justice, and Education
5. **Rules are optional** - can use similarity-based merging without validation

---

## 📚 Configuration Reference

```python
# Use built-in healthcare rules (RECOMMENDED)
from personatwin.event_merging import IntelligentEventMerger, EventMergingStrategy
from personatwin.domains import Domain

merger = IntelligentEventMerger(
    domain=Domain.HEALTHCARE,
    strategy=EventMergingStrategy.RULE_BASED
)

# Use custom rules
custom_rules = { ... }
merger = IntelligentEventMerger(Domain.CUSTOM, EventMergingStrategy.RULE_BASED)
merger.rules = custom_rules

# No rules (just similarity merging)
merger = IntelligentEventMerger(Domain.CUSTOM, EventMergingStrategy.SIMILARITY)
# Rules not used in SIMILARITY mode
```

---

**PersonaTwin PrivacyForge** gives users **full control** over domain rules while providing **smart defaults** for common domains! 🎉
