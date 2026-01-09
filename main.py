"""
Radiocall Generator - Main Entry Point
Populates reference data and generates radiocall practice content
"""

import random
from config import DIRECTUS_URL, DIRECTUS_EMAIL, DIRECTUS_PASSWORD, NUM_RADIOCALLS_TO_GENERATE, DIFFICULTY_DISTRIBUTION
from directus_client import DirectusClient
from data import INSTRUCTION_TYPES, CALLSIGN_FORMATS, COMMON_ERRORS
from generator import RadiocallGenerator


def populate_instruction_types(client: DirectusClient):
    """Load instruction types into Directus"""
    print("\n📋 Populating instruction_type collection...")
    
    # Check if already populated
    existing = client.get_items("instruction_type", {"limit": 1})
    if existing:
        print(f"  Already has data ({len(client.get_items('instruction_type', {'limit': 100}))} types)")
        return client.get_items("instruction_type", {"limit": 100})
    
    # Insert all instruction types
    items = []
    for it in INSTRUCTION_TYPES:
        items.append({
            "code": it["code"],
            "display_name": it["display_name"],
            "category": it["category"],
            "requires_readback": it["requires_readback"],
            "is_critical": it["is_critical"],
            "grading_weight": it["grading_weight"],
            "description": it.get("description", ""),
            "example_phrase": it.get("example_phrase", "")
        })
    
    result = client.create_items("instruction_type", items)
    print(f"  ✓ Created {len(result)} instruction types")
    return result


def populate_callsign_formats(client: DirectusClient):
    """Load callsign formats into Directus"""
    print("\n📋 Populating callsign_format collection...")
    
    # Check if already populated
    existing = client.get_items("callsign_format", {"limit": 1})
    if existing:
        print(f"  Already has data ({len(client.get_items('callsign_format', {'limit': 100}))} formats)")
        return client.get_items("callsign_format", {"limit": 100})
    
    # Insert all callsign formats
    items = []
    for cf in CALLSIGN_FORMATS:
        items.append({
            "airline_code": cf.get("airline_code"),
            "airline_callsign": cf.get("airline_callsign"),
            "format_pattern": cf["format_pattern"],
            "region": cf["region"],
            "difficulty": cf["difficulty"],
            "is_registration_based": cf["is_registration_based"],
            "phonetic_template": cf["phonetic_template"]
        })
    
    result = client.create_items("callsign_format", items)
    print(f"  ✓ Created {len(result)} callsign formats")
    return result


def get_airports(client: DirectusClient):
    """Get all airports from existing collection"""
    print("\n📋 Fetching airports...")
    airports = client.get_items("airport", {"limit": 100})
    print(f"  Found {len(airports)} airports")
    return airports


def select_difficulty():
    """Select a difficulty based on configured distribution"""
    roll = random.randint(1, 100)
    cumulative = 0
    for difficulty, percentage in DIFFICULTY_DISTRIBUTION.items():
        cumulative += percentage
        if roll <= cumulative:
            return difficulty
    return "easy"  # fallback


def main():
    print("="*70)
    print("RADIOCALL GENERATOR")
    print("="*70)
    
    # Connect to Directus
    client = DirectusClient()
    client.login()
    
    # Populate reference data
    instruction_types = populate_instruction_types(client)
    callsign_formats = populate_callsign_formats(client)
    airports = get_airports(client)
    
    if not airports:
        print("\n❌ No airports found! Run ATIS generator first to populate airports.")
        return
    
    # Build lookup maps
    instruction_type_map = {it["code"]: it for it in instruction_types}
    
    # Initialize generator
    generator = RadiocallGenerator(
        airports=airports,
        instruction_types=instruction_types,
        callsign_formats=callsign_formats,
        instruction_type_map=instruction_type_map
    )
    
    # Generate radiocalls
    print(f"\n🎙️ Generating {NUM_RADIOCALLS_TO_GENERATE} radiocalls...")
    
    created_count = 0
    difficulty_counts = {"super_easy": 0, "easy": 0, "medium": 0, "hard": 0}
    category_counts = {}
    
    for i in range(NUM_RADIOCALLS_TO_GENERATE):
        difficulty = select_difficulty()
        
        # Generate a complete radiocall with all related data
        radiocall_data = generator.generate_radiocall(difficulty)
        
        if radiocall_data:
            # Create main radiocall record
            radiocall = client.create_item("radiocall", radiocall_data["radiocall"])
            radiocall_id = radiocall["id"]
            
            # Create instruction records
            for instr in radiocall_data["instructions"]:
                instr["radiocall"] = radiocall_id
                client.create_item("radiocall_instruction", instr)
            
            # Create acceptable variations
            for var in radiocall_data.get("variations", []):
                var["radiocall"] = radiocall_id
                client.create_item("acceptable_variation", var)
            
            # Create common errors
            for err in radiocall_data.get("errors", []):
                err["radiocall"] = radiocall_id
                client.create_item("common_error", err)
            
            created_count += 1
            difficulty_counts[difficulty] += 1
            cat = radiocall_data["radiocall"]["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{NUM_RADIOCALLS_TO_GENERATE}")
    
    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"Total radiocalls created: {created_count}")
    print("\nBy difficulty:")
    for diff, count in difficulty_counts.items():
        pct = (count / created_count * 100) if created_count > 0 else 0
        print(f"  {diff}: {count} ({pct:.1f}%)")
    print("\nBy category:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")
    print("="*70)


if __name__ == "__main__":
    main()
