# Radiocall Readback Practice Tool

A generator for realistic ATC (Air Traffic Control) radio calls for pilot readback practice. Creates structured data with grading information for use in aviation training applications.

## Features

- **Realistic ATC Transmissions**: Based on FAA AIM and ICAO standards
- **4-Tier Difficulty System**: Progressive learning from beginner to advanced
- **Granular Grading Data**: Each instruction tagged for precise scoring
- **DACH Region Focus**: German, Austrian, and Swiss airports/procedures
- **Directus CMS Backend**: All data stored in a flexible headless CMS

## Difficulty Tiers

| Tier | Target Audience | Instructions/Call | Features |
|------|-----------------|-------------------|----------|
| Super Easy | Complete beginners | 1 | Simple callsigns, basic clearances |
| Easy | Student pilots | 1-2 | Standard procedures, common scenarios |
| Medium | PPL/IR students | 2-3 | Registration callsigns, conditionals |
| Hard | CPL/ATPL prep | 3-4 | Complex scenarios, amendments, fast pace |

## Project Structure

```
radiocall_generator/
├── docs/
│   ├── CONCEPT.md          # Full concept design document
│   └── SCHEMA_DESIGN.md    # Directus schema with explanations
├── config.py               # Directus connection settings
├── data.py                 # Reference data (instructions, callsigns)
├── directus_client.py      # API client with schema setup
├── generator.py            # Radiocall generation logic (TBD)
├── main.py                 # Main entry point (TBD)
└── README.md              # This file
```

## Schema Overview

### Collections

1. **instruction_type** - Master list of ATC instruction types with grading rules
2. **callsign_format** - Templates for generating realistic callsigns
3. **radiocall** - Main entity: complete ATC transmissions
4. **radiocall_instruction** - Individual instructions within a call
5. **acceptable_variation** - Alternative correct readbacks
6. **common_error** - Typical mistakes with severity ratings
7. **radiocall_set** - Curated practice sets
8. **radiocall_set_items** - Junction table for sets

See [SCHEMA_DESIGN.md](docs/SCHEMA_DESIGN.md) for detailed explanations.

## Setup

1. **Install dependencies**:
   ```bash
   pip install requests
   ```

2. **Configure Directus connection** in `config.py`:
   ```python
   DIRECTUS_URL = "https://your-directus-instance.com"
   DIRECTUS_EMAIL = "your-email@example.com"
   DIRECTUS_PASSWORD = "your-password"
   ```

3. **Create schema in Directus**:
   ```bash
   python directus_client.py
   ```

4. **Generate radiocalls** (once generator is built):
   ```bash
   python main.py
   ```

## Grading System

Each radiocall includes:
- **critical_elements**: Must be read back correctly (runway, altitude, heading)
- **requires_readback**: Items that should be included
- **acceptable_variations**: Alternative correct phrasings
- **common_errors**: Known mistakes with severity levels

### Error Severity

| Severity | Description | Score Impact |
|----------|-------------|--------------|
| Critical | Safety-of-flight issue | -40% to -60% |
| Major | Missing required readback | -20% to -30% |
| Minor | Incorrect phraseology | -5% to -10% |
| Style | Non-standard but acceptable | -0% to -2% |

## Related Projects

- **ATIS Generator**: [github.com/niroet/atis-generator](https://github.com/niroet/atis-generator)
  - Same airport database
  - Matching difficulty tiers
  - Complementary training tool

## License

MIT License

## Author

Created for Aevoli aviation training platform.
