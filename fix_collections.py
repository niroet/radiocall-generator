"""
Fix the radiocall collections - recreate with proper database schema
"""
import requests
from config import DIRECTUS_URL, DIRECTUS_EMAIL, DIRECTUS_PASSWORD

resp = requests.post(f'{DIRECTUS_URL}/auth/login', json={'email': DIRECTUS_EMAIL, 'password': DIRECTUS_PASSWORD})
token = resp.json()['data']['access_token']
headers = {'Authorization': f'Bearer {token}'}

collections_to_fix = [
    'radiocall_set_items',  # Delete children first (foreign keys)
    'common_error',
    'acceptable_variation', 
    'radiocall_instruction',
    'radiocall',
    'radiocall_set',
    'callsign_format',
    'instruction_type'
]

print("STEP 1: Deleting broken collections...")
print("="*50)

for coll in collections_to_fix:
    resp = requests.delete(f'{DIRECTUS_URL}/collections/{coll}', headers=headers)
    print(f'  Delete {coll}: {resp.status_code}')

print("\nSTEP 2: Recreating collections with proper schema...")
print("="*50)

# Now recreate with proper schema - using schema dict instead of just meta
# The key is to include a proper 'schema' object

def create_collection_with_schema(name, fields, meta_note):
    """Create a collection with actual database schema"""
    payload = {
        "collection": name,
        "schema": {},  # This tells Directus to create an actual table!
        "meta": {
            "collection": name,
            "icon": "radio",
            "note": meta_note,
            "group": "Radiocall"
        },
        "fields": fields
    }
    
    resp = requests.post(
        f'{DIRECTUS_URL}/collections',
        headers=headers,
        json=payload
    )
    return resp

# 1. instruction_type
print("\nCreating instruction_type...")
resp = create_collection_with_schema("instruction_type", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "code", "type": "string", "schema": {"is_nullable": False, "is_unique": True}, "meta": {"required": True}},
    {"field": "display_name", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "category", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "requires_readback", "type": "boolean", "schema": {"is_nullable": False, "default_value": True}, "meta": {"required": True}},
    {"field": "is_critical", "type": "boolean", "schema": {"is_nullable": False, "default_value": False}, "meta": {"required": True}},
    {"field": "grading_weight", "type": "float", "schema": {"is_nullable": False, "default_value": 0.5}, "meta": {"required": True}},
    {"field": "description", "type": "text", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "example_phrase", "type": "string", "schema": {"is_nullable": True}, "meta": {}}
], "Master list of ATC instruction types")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 2. callsign_format
print("\nCreating callsign_format...")
resp = create_collection_with_schema("callsign_format", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "airline_code", "type": "string", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "airline_callsign", "type": "string", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "format_pattern", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "region", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "difficulty", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "is_registration_based", "type": "boolean", "schema": {"is_nullable": False, "default_value": False}, "meta": {"required": True}},
    {"field": "phonetic_template", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}}
], "Callsign templates for generation")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 3. radiocall_set (before radiocall, no FKs to radiocall)
print("\nCreating radiocall_set...")
resp = create_collection_with_schema("radiocall_set", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "name", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "description", "type": "text", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "difficulty", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "category", "type": "string", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "is_scenario", "type": "boolean", "schema": {"is_nullable": False, "default_value": False}, "meta": {}},
    {"field": "estimated_duration", "type": "integer", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "sort_order", "type": "integer", "schema": {"is_nullable": True}, "meta": {}}
], "Practice sets for structured learning")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 4. radiocall (main collection)
print("\nCreating radiocall...")
resp = create_collection_with_schema("radiocall", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "category", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "subcategory", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "difficulty", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "flight_phase", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "controller_position", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "aircraft_callsign", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "callsign_phonetic", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "full_transmission", "type": "text", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "expected_readback", "type": "text", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "critical_elements", "type": "json", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "instruction_count", "type": "integer", "schema": {"is_nullable": False, "default_value": 1}, "meta": {"required": True}},
    {"field": "has_conditional", "type": "boolean", "schema": {"is_nullable": False, "default_value": False}, "meta": {}},
    {"field": "is_amendment", "type": "boolean", "schema": {"is_nullable": False, "default_value": False}, "meta": {}},
    {"field": "notes", "type": "text", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "date_created", "type": "timestamp", "schema": {"is_nullable": True}, "meta": {"special": ["date-created"], "readonly": True}}
], "ATC transmissions for readback practice")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 5. radiocall_instruction
print("\nCreating radiocall_instruction...")
resp = create_collection_with_schema("radiocall_instruction", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "sequence", "type": "integer", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "raw_value", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "display_text", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "phonetic_text", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "readback_text", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "unit", "type": "string", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "is_conditional", "type": "boolean", "schema": {"is_nullable": False, "default_value": False}, "meta": {}},
    {"field": "condition_text", "type": "string", "schema": {"is_nullable": True}, "meta": {}}
], "Individual instructions for granular grading")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 6. acceptable_variation
print("\nCreating acceptable_variation...")
resp = create_collection_with_schema("acceptable_variation", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "variation_text", "type": "text", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "notes", "type": "string", "schema": {"is_nullable": True}, "meta": {}}
], "Alternative correct readbacks")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 7. common_error
print("\nCreating common_error...")
resp = create_collection_with_schema("common_error", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "error_code", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "description", "type": "text", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "example", "type": "string", "schema": {"is_nullable": True}, "meta": {}},
    {"field": "severity", "type": "string", "schema": {"is_nullable": False}, "meta": {"required": True}},
    {"field": "feedback_text", "type": "text", "schema": {"is_nullable": True}, "meta": {}}
], "Common errors with severity ratings")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

# 8. radiocall_set_items
print("\nCreating radiocall_set_items...")
resp = create_collection_with_schema("radiocall_set_items", [
    {"field": "id", "type": "uuid", "schema": {"is_primary_key": True, "is_nullable": False}, "meta": {"special": ["uuid"], "hidden": True}},
    {"field": "sequence", "type": "integer", "schema": {"is_nullable": False}, "meta": {"required": True}}
], "Junction table for sets")
print(f"  Status: {resp.status_code}")
if resp.status_code >= 400:
    print(f"  Error: {resp.text[:200]}")

print("\nSTEP 3: Adding relations...")
print("="*50)

# Add foreign key fields and relations
def add_relation(collection, field_name, related_collection):
    # First add the field
    field_resp = requests.post(
        f'{DIRECTUS_URL}/fields/{collection}',
        headers=headers,
        json={
            "field": field_name,
            "type": "uuid",
            "schema": {"is_nullable": True},
            "meta": {"interface": "select-dropdown-m2o", "special": ["m2o"]}
        }
    )
    print(f"  Field {collection}.{field_name}: {field_resp.status_code}")
    
    # Then create the relation
    rel_resp = requests.post(
        f'{DIRECTUS_URL}/relations',
        headers=headers,
        json={
            "collection": collection,
            "field": field_name,
            "related_collection": related_collection
        }
    )
    print(f"  Relation {collection}.{field_name} -> {related_collection}: {rel_resp.status_code}")

add_relation("radiocall", "airport", "airport")
add_relation("radiocall_instruction", "radiocall", "radiocall")
add_relation("radiocall_instruction", "instruction_type", "instruction_type")
add_relation("acceptable_variation", "radiocall", "radiocall")
add_relation("common_error", "radiocall", "radiocall")
add_relation("radiocall_set", "airport", "airport")
add_relation("radiocall_set_items", "set", "radiocall_set")
add_relation("radiocall_set_items", "radiocall", "radiocall")

print("\n" + "="*50)
print("DONE! Testing access...")
print("="*50)

# Test
resp = requests.get(f'{DIRECTUS_URL}/items/instruction_type?limit=1', headers=headers)
print(f'instruction_type access: {resp.status_code}')

resp = requests.get(f'{DIRECTUS_URL}/items/radiocall?limit=1', headers=headers)
print(f'radiocall access: {resp.status_code}')

if resp.status_code == 200:
    print("\n✓ SUCCESS! Collections are now accessible.")
else:
    print(f"\n✗ Still having issues: {resp.text[:200]}")
