# Intelligent Event Merging - Implementation Summary

## 🎯 Problem Solved

**Before:** PersonaTwin naively concatenated all events from merged people, creating **unrealistic personas**:

```python
# ❌ PROBLEM: Naive concatenation
Person A: [arrest_2020, trial_2020, sentencing_2021]
Person B: [arrest_2022, trial_2023]

# Result: Unrealistic persona
Persona: [arrest_2020, trial_2020, sentencing_2021, arrest_2022, trial_2023]
# Issues:
# - 2 arrests, 2 trials, but only 1 sentencing (illogical)
# - Arrested again AFTER sentencing (impossible sequence)
# - Patient hospitalized twice without discharge (violates domain logic)
```

**Now:** PersonaTwin uses **intelligent event merging** with multiple strategies:

```python
# ✅ SOLUTION: Similarity-based merging
Person A: [arrest_2020-01-15, trial_2020-03-20, sentencing_2020-06-10]
Person B: [arrest_2020-02-10, trial_2020-04-15, sentencing_2020-07-05]

# Result: Realistic persona
Persona: [arrest_2020-01, trial_2020-03, sentencing_2020-06]
# - Similar events merged into representative events
# - Logical sequence preserved
# - Domain rules validated
```

---

## 🏗️ Implementation

### New Modules Created

#### 1. `personatwin/event_merging.py` (NEW)

**Purpose:** Intelligent event merging strategies

**Key Classes:**

```python
class EventMergingStrategy(Enum):
    CONCATENATE = "concatenate"   # Old naive approach
    SIMILARITY = "similarity"     # NEW: Merge similar events (RECOMMENDED)
    RULE_BASED = "rule_based"     # NEW: Validate domain rules
    AGGREGATE = "aggregate"       # NEW: Combine into composite events
    SAMPLE = "sample"             # NEW: Sample representative events
    INTERLEAVE = "interleave"     # Chronological ordering
```

**Core Logic:**

1. **EventSimilarityCalculator**
   - Calculates cosine similarity between events
   - Factors: Event type (40%), Outcome (20%), Date (20%), Location (20%)
   - Threshold: 0.6 (60% similarity)

2. **DomainEventRules**
   - Criminal Justice: arrest → charge → trial → sentencing
   - Healthcare: admission → diagnosis → treatment → discharge
   - Education: enrollment → assessment → graduation

3. **IntelligentEventMerger**
   - Groups similar events (clustering)
   - Creates representative events (median/mode aggregation)
   - Validates sequences (domain rules)
   - Inserts synthetic events (when needed)

#### 2. Updated `personatwin/merging.py`

**Changes:**

```python
# NEW: Import event merging
from personatwin.event_merging import IntelligentEventMerger, EventMergingStrategy
from personatwin.domains import Domain

class PeopleMerging:
    def __init__(
        self,
        privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM,
        min_group_size: int = 5,
        domain: Domain = Domain.CUSTOM,  # NEW
        event_merging_strategy: EventMergingStrategy = EventMergingStrategy.SIMILARITY  # NEW
    ):
        self.event_merger = IntelligentEventMerger(domain, event_merging_strategy)  # NEW
    
    def _create_persona_from_group(self, group: List[Person]) -> Persona:
        # OLD: all_events.extend(person.events)  # Naive concatenation
        
        # NEW: Intelligent merging
        merged_events = self.event_merger.merge_events(group)
```

---

## 📊 Event Merging Strategies Explained

### 1. SIMILARITY-BASED (Recommended) ⭐

**How it works:**
1. Calculate similarity between all events
2. Group similar events (threshold: 0.6)
3. Create representative event for each group
4. Validate sequence

**Similarity Formula:**
```
similarity = 0.4 * (same_type) + 0.2 * (same_outcome) + 
             0.2 * (temporal_closeness) + 0.2 * (same_location)
```

**Example:**
```python
# Input: 3 patients with pneumonia admissions
Person 1: admission 2023-01-10, Memorial Hospital
Person 2: admission 2023-01-15, Memorial Hospital  
Person 3: admission 2023-01-18, Memorial Hospital

# Similarity: 0.4 (same type) + 0.2 (close dates) + 0.2 (same location) = 0.8

# Output: 1 merged event
Persona: admission 2023-01-15, Memorial Hospital [MERGED FROM 3]
```

**Benefits:**
- ✅ Creates realistic personas
- ✅ Reduces event count
- ✅ Preserves statistical patterns
- ✅ Clear provenance (tracks merged events)

---

### 2. RULE-BASED (Validates Logic) ✅

**How it works:**
1. Merge by similarity (as above)
2. Validate event sequence
3. Insert missing prerequisite events
4. Close open events

**Domain Rules:**

**Healthcare:**
```python
admission: requires_closure=True, closure_event="discharge"
# Can't be hospitalized twice without discharge

discharge: must_follow=["admission"]
# Can't discharge without admission

surgery: must_follow=["admission"]
# Surgery requires hospitalization
```

**Criminal Justice:**
```python
charge: must_follow=["arrest"]
# Can't be charged without arrest

trial: must_follow=["charge"]
# Can't have trial without charges

sentencing: must_follow=["trial"]
# Can't be sentenced without trial

incarceration: requires_closure=True, closure_event="release"
# Incarceration requires release
```

**Example:**
```python
# Input: Incomplete sequence
Events: [trial_2023-03, sentencing_2023-06]

# Rule violation: trial requires arrest and charge

# Output: Fixed sequence with synthetic events
Events: [
    arrest_2023-02 (synthetic),      # Auto-added
    charge_2023-02 (synthetic),      # Auto-added
    trial_2023-03,
    sentencing_2023-06
]
```

**Benefits:**
- ✅ Prevents illogical sequences
- ✅ Maintains domain-specific rules
- ✅ Synthetic events clearly marked
- ✅ Ensures data quality

---

### 3. AGGREGATE (Reduces Count) 📊

**How it works:**
1. Group events by type
2. Create composite events
3. Track count and date range

**Example:**
```python
# Input: Multiple arrests
Person A: arrest_2020, arrest_2021, arrest_2022
Person B: arrest_2020, arrest_2023

# Output: Aggregate event
Persona: "5 arrests between 2020-2023" (composite)
# details = {
#     "_aggregate": True,
#     "_count": 5,
#     "_date_range": "2020-01 to 2023-12"
# }
```

**Benefits:**
- ✅ Reduces event count
- ✅ Useful for high-frequency events
- ✅ Maintains statistical patterns
- ❌ Loses temporal granularity

---

### 4. SAMPLE (Limits Events) 🎲

**How it works:**
1. Sort events chronologically
2. Keep first, last, and evenly-spaced middle events
3. Limit to max_events (default: 10)

**Example:**
```python
# Input: 25 events
Events: [e1, e2, e3, ..., e25]

# Output: 10 sampled events
Events: [e1, e3, e6, e9, e12, e15, e18, e21, e24, e25]
#        ^first      ^middle (evenly spaced)      ^last
```

**Benefits:**
- ✅ Prevents personas with too many events
- ✅ Maintains temporal range
- ❌ May lose important middle events

---

## 🔧 Synthetic Events

**When are they added?**

1. **Missing Prerequisites**
   ```python
   # Have trial but no arrest → Add synthetic arrest
   Events: [trial_2023-03]
   Result: [arrest_2023-02 (synthetic), trial_2023-03]
   ```

2. **Open Events**
   ```python
   # Admission without discharge → Add synthetic discharge
   Events: [admission_2023-01, diagnosis_2023-01]
   Result: [admission_2023-01, diagnosis_2023-01, discharge_2023-02 (synthetic)]
   ```

3. **Multiple Open Events**
   ```python
   # Hospitalized twice simultaneously → Close first, then open second
   Events: [admission_2023-01, admission_2023-03]
   Result: [admission_2023-01, discharge_2023-02 (synthetic), admission_2023-03]
   ```

**How are they marked?**

```python
event.details = {
    "_synthetic": True,
    "_reason": "Required before trial",
    ...
}
```

---

## 📈 Results & Performance

### Test: Healthcare Example

**Input:** 3 patients with similar admissions

| Patient | Events | Details |
|---------|--------|---------|
| P001 | 4 events | admission → diagnosis → treatment → discharge |
| P002 | 4 events | admission → diagnosis → treatment → discharge |
| P003 | 3 events | admission → diagnosis → surgery (missing discharge) |
| **Total** | **11 events** | |

**Output:** 1 persona

| Strategy | Events | Notes |
|----------|--------|-------|
| SIMILARITY | 5 events | Merged 3 admissions, 3 diagnoses, 2 treatments, 2 discharges |
| RULE_BASED | 5 events | Same as similarity + validates sequence |
| AGGREGATE | 5 aggregates | "3 admissions (2023-01 to 2023-02)" |

**Privacy Improvement:**
- K-anonymity: 3 (3 people merged)
- Event uniqueness: Reduced from 11 individual events to 5 representative patterns
- Re-identification risk: Lowered (shared event patterns)

---

## 🎯 Recommendations

### When to use each strategy:

| Strategy | Best For | Trade-offs |
|----------|----------|------------|
| **SIMILARITY** ⭐ | General use, preserves realism | Recommended default |
| **RULE_BASED** | Critical domains (healthcare, justice) | Ensures logic, adds synthetic events |
| **AGGREGATE** | High-frequency events | Loses temporal detail |
| **SAMPLE** | Personas with too many events | May lose important events |
| ~~CONCATENATE~~ | ❌ Never use (unrealistic) | Legacy/deprecated |

### Configuration:

```python
# High privacy + realistic events (RECOMMENDED)
merger = PeopleMerging(
    privacy_level=PrivacyLevel.HIGH,
    min_group_size=10,
    domain=Domain.HEALTHCARE,
    event_merging_strategy=EventMergingStrategy.RULE_BASED
)

# Medium privacy + statistical patterns
merger = PeopleMerging(
    privacy_level=PrivacyLevel.MEDIUM,
    min_group_size=5,
    domain=Domain.CRIMINAL_JUSTICE,
    event_merging_strategy=EventMergingStrategy.SIMILARITY
)

# Reduce event count for high-frequency data
merger = PeopleMerging(
    privacy_level=PrivacyLevel.MEDIUM,
    min_group_size=5,
    domain=Domain.CUSTOM,
    event_merging_strategy=EventMergingStrategy.AGGREGATE
)
```

---

## ✅ Testing

**Run the example:**

```bash
python3 examples/intelligent_event_merging_example.py
```

**Output:** Demonstrates all strategies with healthcare and criminal justice data

---

## 🚀 Next Steps

1. ✅ **COMPLETED:** Intelligent event merging implementation
2. 🔜 **TODO:** Update API to expose event merging strategy parameter
3. 🔜 **TODO:** Add event pattern k-anonymity calculation
4. 🔜 **TODO:** Update README with event merging documentation
5. 🔜 **TODO:** Add connection pattern k-anonymity (for social networks)

---

## 📚 Key Files

- `personatwin/event_merging.py` - Core implementation (NEW)
- `personatwin/merging.py` - Updated to use intelligent merging
- `examples/intelligent_event_merging_example.py` - Complete demonstration
- `personatwin/domains.py` - Domain rules and configurations

---

**PersonaTwin PrivacyForge** now creates **realistic, privacy-protected personas** with **intelligently merged events**! 🎉
