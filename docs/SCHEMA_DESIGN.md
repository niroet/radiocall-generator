# Directus Schema Design - Radiocall Readback Tool

## Design Philosophy

This schema is designed with several key principles in mind:

1. **Grading Precision**: Every piece of data needed to grade a user's readback is stored explicitly
2. **Flexibility**: Support for various instruction types, difficulties, and regional variations
3. **Relational Integrity**: Proper normalization to avoid data duplication
4. **Query Efficiency**: Structure optimized for common access patterns
5. **Extensibility**: Easy to add new instruction types, categories, or difficulty levels

---

## Collection Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SCHEMA DIAGRAM                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐  │
│  │   airport    │────▶│   radiocall      │◀────│ instruction_    │  │
│  │  (existing)  │     │                  │     │ type            │  │
│  └──────────────┘     └────────┬─────────┘     └─────────────────┘  │
│                                │                                     │
│                                │ 1:N                                 │
│                                ▼                                     │
│                       ┌──────────────────┐                          │
│                       │  radiocall_      │                          │
│                       │  instruction     │                          │
│                       └────────┬─────────┘                          │
│                                │                                     │
│                                │ 1:N                                 │
│                                ▼                                     │
│                       ┌──────────────────┐                          │
│                       │  common_error    │                          │
│                       └──────────────────┘                          │
│                                                                      │
│  ┌──────────────────┐     ┌──────────────────┐                      │
│  │ callsign_format  │     │ acceptable_      │                      │
│  │                  │     │ variation        │                      │
│  └──────────────────┘     └──────────────────┘                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Collection: `instruction_type`

### Purpose
Master reference table for all types of ATC instructions. This normalization allows:
- Consistent instruction categorization across all radiocalls
- Easy addition of new instruction types
- Standardized grading rules per instruction type

### Why This Design?
Instead of hardcoding instruction types as strings in radiocalls, we use a reference table because:
1. **Consistency**: Ensures same instruction type is always spelled/formatted identically
2. **Grading Logic**: Each type has fixed rules (requires_readback, is_critical)
3. **Analytics**: Easy to query which instruction types cause most errors
4. **Extensibility**: Add new types without code changes

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `code` | string | Yes | Unique identifier (e.g., "runway_assignment") |
| `display_name` | string | Yes | Human-readable name |
| `category` | string | Yes | Grouping (ground, departure, enroute, arrival, landing) |
| `requires_readback` | boolean | Yes | Must pilot read this back? |
| `is_critical` | boolean | Yes | Is error safety-critical? |
| `description` | text | No | Detailed explanation |
| `example_phrase` | string | No | Example of this instruction |
| `grading_weight` | float | Yes | Weight in scoring (0.0-1.0) |

### Example Data
```json
{
  "code": "altitude_assignment",
  "display_name": "Altitude Assignment",
  "category": "enroute",
  "requires_readback": true,
  "is_critical": true,
  "description": "Any instruction assigning a new altitude or flight level",
  "example_phrase": "climb and maintain flight level 350",
  "grading_weight": 0.9
}
```

---

## Collection: `callsign_format`

### Purpose
Templates for generating realistic aircraft callsigns with phonetic pronunciations.

### Why This Design?
Callsigns are complex with multiple formats:
- Airline callsigns: "Lufthansa 450" (spoken "Lufthansa four five zero")
- Registration: "D-AIBC" (spoken "Delta Alpha India Bravo Charlie")
- Mixed: "Speedbird 1-2-Alpha" (spoken "Speedbird one two Alpha")

Storing templates allows:
1. **Realistic Generation**: Create authentic callsigns for each region
2. **Phonetic Mapping**: Know exactly how each callsign should be spoken
3. **Confusion Training**: Generate similar-sounding callsigns deliberately

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `airline_code` | string | No | ICAO airline code (DLH, BAW, etc.) |
| `airline_callsign` | string | No | Radio callsign (Lufthansa, Speedbird) |
| `format_pattern` | string | Yes | Pattern like "{airline} {number}" |
| `region` | string | Yes | DACH, UK, US, etc. |
| `difficulty` | string | Yes | Which difficulty uses this format |
| `is_registration_based` | boolean | Yes | True for N123AB style |
| `phonetic_template` | string | Yes | How to speak: "{airline} {number_phonetic}" |

### Example Data
```json
{
  "airline_code": "DLH",
  "airline_callsign": "Lufthansa",
  "format_pattern": "{airline} {flight_number}",
  "region": "DACH",
  "difficulty": "easy",
  "is_registration_based": false,
  "phonetic_template": "{airline} {number_individual}"
}
```

---

## Collection: `radiocall`

### Purpose
The main collection storing complete ATC transmissions. This is the parent record that groups all instructions in a single radio call.

### Why This Design?
Each radiocall represents one complete controller transmission. We separate this from individual instructions because:
1. **Context Preservation**: The full transmission text matters for realism
2. **Difficulty Scoping**: Difficulty applies to the call, not individual instructions
3. **Expected Readback**: The complete expected response is call-level
4. **Airport Context**: Each call is associated with a specific airport's procedures

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `airport` | M2O→airport | Yes | Reference to airport collection |
| `category` | string | Yes | ground/departure/enroute/arrival/landing |
| `subcategory` | string | Yes | Specific type (taxi, takeoff_clearance, etc.) |
| `difficulty` | string | Yes | super_easy/easy/medium/hard |
| `flight_phase` | string | Yes | Current phase of flight |
| `controller_position` | string | Yes | ground/tower/departure/approach/center |
| `aircraft_callsign` | string | Yes | The callsign used in this call |
| `callsign_phonetic` | string | Yes | How callsign should be spoken |
| `full_transmission` | text | Yes | Complete controller transmission text |
| `expected_readback` | text | Yes | The correct pilot readback |
| `critical_elements` | json | Yes | Array of critical instruction codes |
| `instruction_count` | integer | Yes | Number of instructions (for filtering) |
| `has_conditional` | boolean | Yes | Contains conditional instruction? |
| `is_amendment` | boolean | No | Is this an amended clearance? |
| `weather_context` | json | No | Weather conditions affecting this call |
| `notes` | text | No | Additional context or teaching notes |
| `date_created` | datetime | Auto | Creation timestamp |

### Why These Specific Fields?

**`category` + `subcategory`**: Two-level categorization allows filtering by broad category (all departure calls) or specific type (just takeoff clearances).

**`flight_phase`**: Separate from category because the same instruction type can occur in different phases (altitude changes happen during climb, cruise, and descent).

**`critical_elements` (JSON array)**: Stored as JSON because:
- Variable number of critical elements per call
- Need quick access without joining
- Used directly by grading algorithm

**`has_conditional` + `is_amendment`**: Boolean flags for quick filtering of complex scenarios - these are harder and should be reserved for medium/hard difficulties.

**`instruction_count`**: Denormalized count for efficient filtering without counting relations.

### Example Data
```json
{
  "airport": "uuid-of-EDDF",
  "category": "departure",
  "subcategory": "takeoff_clearance",
  "difficulty": "medium",
  "flight_phase": "departure",
  "controller_position": "tower",
  "aircraft_callsign": "Lufthansa 450",
  "callsign_phonetic": "Lufthansa four five zero",
  "full_transmission": "Lufthansa 450, wind 270 degrees 8 knots, runway 25L, cleared for takeoff",
  "expected_readback": "Cleared for takeoff runway 25L, Lufthansa 450",
  "critical_elements": ["runway_assignment", "takeoff_clearance"],
  "instruction_count": 3,
  "has_conditional": false,
  "is_amendment": false
}
```

---

## Collection: `radiocall_instruction`

### Purpose
Individual instructions within a radiocall. This is the heart of the grading system.

### Why This Design?
Breaking calls into individual instructions enables:
1. **Granular Grading**: Score each instruction independently
2. **Error Attribution**: Know exactly which instruction was missed/wrong
3. **Analytics**: Track which instruction types are most problematic
4. **Flexible Ordering**: `sequence` field preserves instruction order

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `radiocall` | M2O→radiocall | Yes | Parent radiocall |
| `instruction_type` | M2O→instruction_type | Yes | Type reference |
| `sequence` | integer | Yes | Order in the transmission (1, 2, 3...) |
| `raw_value` | string | Yes | The actual value (e.g., "25L", "FL350") |
| `display_text` | string | Yes | How it appears in transmission |
| `phonetic_text` | string | Yes | How it should be spoken |
| `readback_text` | string | Yes | Expected text in readback |
| `unit` | string | No | Unit if applicable (feet, FL, degrees) |
| `is_conditional` | boolean | No | "After landing traffic..." type |
| `condition_text` | string | No | The condition if conditional |

### Why These Specific Fields?

**`raw_value` vs `display_text` vs `phonetic_text` vs `readback_text`**: Four representations because:
- `raw_value`: Machine-readable ("25L", "35000", "090")
- `display_text`: As in transmission ("runway 25L", "flight level 350")
- `phonetic_text`: Spoken form ("runway two five left", "flight level three five zero")
- `readback_text`: What appears in readback ("runway 25L" - pilot might say differently)

**`sequence`**: Critical for reconstructing call order and identifying if pilot read back in wrong order.

**`is_conditional` + `condition_text`**: Conditional clearances are complex - "After the landing 737, line up runway 25L" - the condition must be understood but not read back.

### Example Data
```json
{
  "radiocall": "uuid-of-parent-call",
  "instruction_type": "uuid-of-altitude_assignment",
  "sequence": 2,
  "raw_value": "12000",
  "display_text": "descend flight level 120",
  "phonetic_text": "descend flight level one two zero",
  "readback_text": "descend FL120",
  "unit": "FL",
  "is_conditional": false
}
```

---

## Collection: `acceptable_variation`

### Purpose
Store alternative correct readbacks. Pilots may phrase things differently while still being correct.

### Why This Design?
There's no single "correct" readback. Acceptable variations include:
- Word order differences: "Runway 25L, cleared takeoff" vs "Cleared takeoff, 25L"
- Abbreviations: "Flight level" vs "FL"
- Omissions: Some non-critical words can be omitted

Storing these enables:
1. **Flexible Grading**: Accept multiple correct answers
2. **Learning**: Show users acceptable alternatives
3. **Pattern Recognition**: Build grading algorithm from examples

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `radiocall` | M2O→radiocall | Yes | Parent radiocall |
| `variation_text` | text | Yes | Alternative correct readback |
| `notes` | string | No | Why this variation is acceptable |

---

## Collection: `common_error`

### Purpose
Catalog of typical mistakes for each radiocall, with severity ratings.

### Why This Design?
Knowing common errors enables:
1. **Targeted Feedback**: Tell user exactly what they did wrong
2. **Severity Grading**: Distinguish critical from minor errors
3. **Pattern Detection**: Recognize error patterns in user's readback
4. **Training Focus**: Warn about common mistakes before practice

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `radiocall` | M2O→radiocall | Yes | Parent radiocall |
| `error_code` | string | Yes | Unique error identifier |
| `description` | text | Yes | What the error is |
| `example` | string | No | Example of this error |
| `severity` | string | Yes | critical/major/minor/style |
| `instruction_affected` | M2O→radiocall_instruction | No | Which instruction this error relates to |
| `feedback_text` | text | No | Feedback to show user |

### Severity Definitions

| Severity | Description | Score Impact |
|----------|-------------|--------------|
| `critical` | Safety-of-flight issue | -40% to -60% |
| `major` | Missing required readback | -20% to -30% |
| `minor` | Incorrect phraseology | -5% to -10% |
| `style` | Non-standard but acceptable | -0% to -2% |

---

## Collection: `radiocall_set`

### Purpose
Group radiocalls into curated practice sets for structured learning.

### Why This Design?
Random practice isn't optimal for learning. Curated sets allow:
1. **Progressive Difficulty**: Start easy, build up
2. **Focused Practice**: "All approach clearances" or "All hold short"
3. **Scenario Training**: Complete flight from startup to shutdown
4. **Exam Prep**: Sets matching checkride requirements

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `name` | string | Yes | Set name |
| `description` | text | No | What this set covers |
| `difficulty` | string | Yes | Overall difficulty level |
| `category` | string | No | Focus category if any |
| `airport` | M2O→airport | No | Airport focus if any |
| `is_scenario` | boolean | Yes | Is this a complete flight scenario? |
| `estimated_duration` | integer | No | Minutes to complete |
| `sort_order` | integer | No | For ordering in UI |

### Junction: `radiocall_set_items`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | uuid | Auto | Primary key |
| `set` | M2O→radiocall_set | Yes | Parent set |
| `radiocall` | M2O→radiocall | Yes | Included radiocall |
| `sequence` | integer | Yes | Order in set |

---

## Indexes & Performance Considerations

### Recommended Indexes

```sql
-- Fast filtering by difficulty and category
CREATE INDEX idx_radiocall_difficulty ON radiocall(difficulty);
CREATE INDEX idx_radiocall_category ON radiocall(category);
CREATE INDEX idx_radiocall_airport ON radiocall(airport);

-- Compound index for common query pattern
CREATE INDEX idx_radiocall_diff_cat ON radiocall(difficulty, category);

-- Instruction lookups
CREATE INDEX idx_instruction_radiocall ON radiocall_instruction(radiocall);
CREATE INDEX idx_instruction_type ON radiocall_instruction(instruction_type);
```

### Query Patterns Optimized For

1. **Get random call by difficulty**: Filter radiocall by difficulty, random select
2. **Get all calls for airport**: Filter radiocall by airport FK
3. **Get call with all instructions**: Join radiocall → radiocall_instruction
4. **Get calls by category**: Filter radiocall by category
5. **Get practice set contents**: Join radiocall_set → radiocall_set_items → radiocall

---

## Relationship Summary

```
airport (existing)
    │
    └──< radiocall (M2O: many radiocalls per airport)
              │
              ├──< radiocall_instruction (M2O: many instructions per call)
              │         │
              │         └──> instruction_type (M2O: each instruction has a type)
              │
              ├──< acceptable_variation (M2O: many variations per call)
              │
              ├──< common_error (M2O: many errors per call)
              │
              └──< radiocall_set_items (M2M junction to radiocall_set)

callsign_format (standalone reference table)

radiocall_set
    │
    └──< radiocall_set_items (junction table)
              │
              └──> radiocall
```

---

## Migration Path from ATIS Tool

The radiocall schema integrates with existing ATIS infrastructure:

1. **Shared `airport` collection**: Same 37 DACH airports
2. **Matching difficulty levels**: super_easy, easy, medium, hard
3. **Similar generation approach**: Python generator creating bulk data
4. **Consistent API patterns**: Same Directus client code

---

## Future Extensibility

This schema supports planned future features:

1. **Audio Generation**: Add `audio_file` field to radiocall
2. **User Progress**: New `user_attempt` collection linking users to radiocalls
3. **Spaced Repetition**: Add `next_review` and `interval` fields
4. **Multi-language**: Add `language` field for localization
5. **Voice Recognition**: Add `speech_patterns` JSON for recognition training

---

*Schema Version: 1.0*
*Created: 2026-01-09*
*Compatible with: Directus 10.x*
