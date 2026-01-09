"""
Directus Client for Radiocall Generator
Handles API communication and schema setup
"""

import requests
from config import DIRECTUS_URL, DIRECTUS_EMAIL, DIRECTUS_PASSWORD


class DirectusClient:
    def __init__(self):
        self.base_url = DIRECTUS_URL
        self.token = None
        
    def login(self):
        """Authenticate with Directus"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": DIRECTUS_EMAIL,
                "password": DIRECTUS_PASSWORD
            }
        )
        response.raise_for_status()
        self.token = response.json()["data"]["access_token"]
        print("✓ Authenticated with Directus")
        return self
    
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_collections(self):
        """Get all collections"""
        response = requests.get(
            f"{self.base_url}/collections",
            headers=self._headers()
        )
        response.raise_for_status()
        return [c["collection"] for c in response.json()["data"]]
    
    def create_collection(self, collection_name, fields, meta=None):
        """Create a new collection with fields"""
        payload = {
            "collection": collection_name,
            "fields": fields,
            "meta": meta or {}
        }
        response = requests.post(
            f"{self.base_url}/collections",
            headers=self._headers(),
            json=payload
        )
        if response.status_code == 400 and "already exists" in response.text:
            print(f"  Collection '{collection_name}' already exists")
            return None
        response.raise_for_status()
        print(f"✓ Created collection: {collection_name}")
        return response.json()
    
    def create_field(self, collection, field_name, field_type, meta=None, schema=None):
        """Add a field to an existing collection"""
        payload = {
            "field": field_name,
            "type": field_type,
            "meta": meta or {},
            "schema": schema or {}
        }
        response = requests.post(
            f"{self.base_url}/fields/{collection}",
            headers=self._headers(),
            json=payload
        )
        if response.status_code == 400 and "already exists" in response.text.lower():
            return None
        response.raise_for_status()
        return response.json()
    
    def create_relation(self, many_collection, many_field, one_collection, one_field=None):
        """Create a M2O relation"""
        payload = {
            "collection": many_collection,
            "field": many_field,
            "related_collection": one_collection,
        }
        if one_field:
            payload["meta"] = {
                "one_field": one_field
            }
        response = requests.post(
            f"{self.base_url}/relations",
            headers=self._headers(),
            json=payload
        )
        if response.status_code == 400 and "already exists" in response.text.lower():
            return None
        response.raise_for_status()
        return response.json()
    
    def create_item(self, collection, data):
        """Create a single item"""
        response = requests.post(
            f"{self.base_url}/items/{collection}",
            headers=self._headers(),
            json=data
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def create_items(self, collection, items):
        """Create multiple items at once"""
        response = requests.post(
            f"{self.base_url}/items/{collection}",
            headers=self._headers(),
            json=items
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def get_items(self, collection, params=None):
        """Get items from a collection"""
        response = requests.get(
            f"{self.base_url}/items/{collection}",
            headers=self._headers(),
            params=params or {}
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def get_item(self, collection, item_id):
        """Get a single item by ID"""
        response = requests.get(
            f"{self.base_url}/items/{collection}/{item_id}",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def delete_items(self, collection, ids):
        """Delete multiple items"""
        response = requests.delete(
            f"{self.base_url}/items/{collection}",
            headers=self._headers(),
            json=ids
        )
        response.raise_for_status()
        return True


def setup_instruction_type_collection(client: DirectusClient):
    """
    Create the instruction_type reference collection.
    
    Purpose: Master table of all ATC instruction types with grading rules.
    
    Why: Normalizing instruction types ensures consistent grading logic,
    prevents typos in type names, and allows easy addition of new types.
    """
    print("\n📋 Setting up instruction_type collection...")
    
    # Check if already exists
    if "instruction_type" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True, "has_auto_increment": False}
        },
        {
            "field": "code",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Unique identifier (e.g., 'runway_assignment', 'altitude_assignment')"
            },
            "schema": {"is_unique": True, "is_nullable": False}
        },
        {
            "field": "display_name",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Human-readable name for display"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "category",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "options": {
                    "choices": [
                        {"text": "Ground", "value": "ground"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "En Route", "value": "enroute"},
                        {"text": "Arrival", "value": "arrival"},
                        {"text": "Landing", "value": "landing"}
                    ]
                },
                "note": "Flight phase category for this instruction type"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "requires_readback",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "required": True,
                "note": "Must the pilot read this back? (FAA AIM 4-4-7)"
            },
            "schema": {"default_value": True, "is_nullable": False}
        },
        {
            "field": "is_critical",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "required": True,
                "note": "Is an error safety-critical? (runway, altitude, heading)"
            },
            "schema": {"default_value": False, "is_nullable": False}
        },
        {
            "field": "description",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "note": "Detailed explanation of this instruction type"
            }
        },
        {
            "field": "example_phrase",
            "type": "string",
            "meta": {
                "interface": "input",
                "note": "Example of this instruction in a transmission"
            }
        },
        {
            "field": "grading_weight",
            "type": "float",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Weight in scoring algorithm (0.0 - 1.0)"
            },
            "schema": {"default_value": 0.5, "is_nullable": False}
        }
    ]
    
    client.create_collection(
        "instruction_type",
        fields,
        meta={
            "icon": "category",
            "note": "Master reference table for ATC instruction types with grading rules",
            "singleton": False
        }
    )


def setup_callsign_format_collection(client: DirectusClient):
    """
    Create the callsign_format collection.
    
    Purpose: Templates for generating realistic aircraft callsigns.
    
    Why: Callsigns vary by region and type (airline vs registration).
    Storing templates enables realistic generation and proper phonetic rendering.
    """
    print("\n📋 Setting up callsign_format collection...")
    
    if "callsign_format" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "airline_code",
            "type": "string",
            "meta": {
                "interface": "input",
                "note": "ICAO airline code (DLH, BAW, AUA, SWR)"
            }
        },
        {
            "field": "airline_callsign",
            "type": "string",
            "meta": {
                "interface": "input",
                "note": "Radio callsign (Lufthansa, Speedbird, Austrian, Swiss)"
            }
        },
        {
            "field": "format_pattern",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Pattern: {airline} {number} or {registration}"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "region",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "options": {
                    "choices": [
                        {"text": "DACH", "value": "DACH"},
                        {"text": "Europe", "value": "EU"},
                        {"text": "UK", "value": "UK"},
                        {"text": "US", "value": "US"}
                    ]
                }
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "difficulty",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "options": {
                    "choices": [
                        {"text": "Super Easy", "value": "super_easy"},
                        {"text": "Easy", "value": "easy"},
                        {"text": "Medium", "value": "medium"},
                        {"text": "Hard", "value": "hard"}
                    ]
                },
                "note": "Minimum difficulty level using this format"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "is_registration_based",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "note": "True for D-AIBC style, False for Lufthansa 450 style"
            },
            "schema": {"default_value": False}
        },
        {
            "field": "phonetic_template",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "How to speak: {airline} {number_individual}"
            },
            "schema": {"is_nullable": False}
        }
    ]
    
    client.create_collection(
        "callsign_format",
        fields,
        meta={
            "icon": "flight",
            "note": "Templates for generating realistic aircraft callsigns with phonetics",
            "singleton": False
        }
    )


def setup_radiocall_collection(client: DirectusClient):
    """
    Create the main radiocall collection.
    
    Purpose: Complete ATC transmissions that pilots must read back.
    
    Why: This is the central entity - each record represents one complete
    controller transmission. It links to airport, contains the full text,
    and specifies the expected readback for grading.
    """
    print("\n📋 Setting up radiocall collection...")
    
    if "radiocall" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "category",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Ground", "value": "ground"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "En Route", "value": "enroute"},
                        {"text": "Arrival", "value": "arrival"},
                        {"text": "Landing", "value": "landing"}
                    ]
                },
                "note": "Broad category of this radio call"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "subcategory",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Startup/Pushback", "value": "startup"},
                        {"text": "Taxi", "value": "taxi"},
                        {"text": "Hold Short", "value": "hold_short"},
                        {"text": "Line Up", "value": "line_up"},
                        {"text": "Takeoff Clearance", "value": "takeoff_clearance"},
                        {"text": "Initial Climb", "value": "initial_climb"},
                        {"text": "Frequency Change", "value": "frequency_change"},
                        {"text": "Altitude Change", "value": "altitude_change"},
                        {"text": "Speed Control", "value": "speed_control"},
                        {"text": "Heading Assignment", "value": "heading_assignment"},
                        {"text": "Direct Routing", "value": "direct_routing"},
                        {"text": "Approach Clearance", "value": "approach_clearance"},
                        {"text": "Landing Clearance", "value": "landing_clearance"},
                        {"text": "Go Around", "value": "go_around"},
                        {"text": "Vacate Runway", "value": "vacate"},
                        {"text": "Taxi to Gate", "value": "taxi_in"}
                    ]
                },
                "note": "Specific type of radio call"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "difficulty",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Super Easy", "value": "super_easy"},
                        {"text": "Easy", "value": "easy"},
                        {"text": "Medium", "value": "medium"},
                        {"text": "Hard", "value": "hard"}
                    ]
                },
                "note": "Difficulty tier for progressive learning"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "flight_phase",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Pre-flight", "value": "preflight"},
                        {"text": "Taxi Out", "value": "taxi_out"},
                        {"text": "Takeoff", "value": "takeoff"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "Climb", "value": "climb"},
                        {"text": "Cruise", "value": "cruise"},
                        {"text": "Descent", "value": "descent"},
                        {"text": "Approach", "value": "approach"},
                        {"text": "Landing", "value": "landing"},
                        {"text": "Taxi In", "value": "taxi_in"}
                    ]
                },
                "note": "Current phase of flight for context"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "controller_position",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Clearance Delivery", "value": "clearance"},
                        {"text": "Ground", "value": "ground"},
                        {"text": "Tower", "value": "tower"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "Approach", "value": "approach"},
                        {"text": "Center/Radar", "value": "center"}
                    ]
                },
                "note": "Which controller position is transmitting"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "aircraft_callsign",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "width": "half",
                "note": "Aircraft callsign as written (e.g., 'Lufthansa 450')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "callsign_phonetic",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "width": "half",
                "note": "How callsign is spoken (e.g., 'Lufthansa four five zero')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "full_transmission",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "required": True,
                "note": "Complete controller transmission as text"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "expected_readback",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "required": True,
                "note": "The correct pilot readback (primary answer for grading)"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "critical_elements",
            "type": "json",
            "meta": {
                "interface": "input-code",
                "required": True,
                "options": {"language": "json"},
                "note": "Array of critical instruction type codes that MUST be read back correctly"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "instruction_count",
            "type": "integer",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Number of instructions in this call (denormalized for filtering)"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "has_conditional",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "note": "Contains conditional instruction? ('After the landing traffic...')"
            },
            "schema": {"default_value": False}
        },
        {
            "field": "is_amendment",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "note": "Is this an amended/corrected clearance?"
            },
            "schema": {"default_value": False}
        },
        {
            "field": "weather_context",
            "type": "json",
            "meta": {
                "interface": "input-code",
                "options": {"language": "json"},
                "note": "Weather conditions affecting this call (wind, visibility)"
            }
        },
        {
            "field": "notes",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "note": "Teaching notes or additional context"
            }
        }
    ]
    
    client.create_collection(
        "radiocall",
        fields,
        meta={
            "icon": "radio",
            "note": "ATC transmissions for readback practice - the main entity",
            "singleton": False
        }
    )
    
    # Add relation to airport collection
    print("  Adding relation to airport...")
    client.create_field(
        "radiocall",
        "airport",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True,
            "note": "Airport where this call takes place"
        }
    )
    client.create_relation("radiocall", "airport", "airport")


def setup_radiocall_instruction_collection(client: DirectusClient):
    """
    Create the radiocall_instruction collection.
    
    Purpose: Individual instructions within a radiocall.
    
    Why: Breaking calls into instructions enables granular grading.
    We can score each instruction independently and track exactly
    which parts the user got right or wrong.
    """
    print("\n📋 Setting up radiocall_instruction collection...")
    
    if "radiocall_instruction" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "sequence",
            "type": "integer",
            "meta": {
                "interface": "input",
                "required": True,
                "width": "half",
                "note": "Order in the transmission (1, 2, 3...)"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "raw_value",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Machine-readable value (e.g., '25L', '35000', '090')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "display_text",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "As in transmission (e.g., 'runway 25L', 'flight level 350')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "phonetic_text",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Spoken form (e.g., 'runway two five left')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "readback_text",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Expected text in pilot's readback"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "unit",
            "type": "string",
            "meta": {
                "interface": "input",
                "width": "half",
                "note": "Unit if applicable (feet, FL, degrees, knots)"
            }
        },
        {
            "field": "is_conditional",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "width": "half",
                "note": "Is this a conditional instruction?"
            },
            "schema": {"default_value": False}
        },
        {
            "field": "condition_text",
            "type": "string",
            "meta": {
                "interface": "input",
                "note": "The condition if conditional (e.g., 'after landing traffic')"
            }
        }
    ]
    
    client.create_collection(
        "radiocall_instruction",
        fields,
        meta={
            "icon": "format_list_numbered",
            "note": "Individual instructions within a radiocall - enables granular grading",
            "singleton": False
        }
    )
    
    # Add relation to radiocall
    print("  Adding relation to radiocall...")
    client.create_field(
        "radiocall_instruction",
        "radiocall",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True,
            "note": "Parent radiocall"
        }
    )
    client.create_relation("radiocall_instruction", "radiocall", "radiocall", "instructions")
    
    # Add relation to instruction_type
    print("  Adding relation to instruction_type...")
    client.create_field(
        "radiocall_instruction",
        "instruction_type",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True,
            "note": "Type of this instruction"
        }
    )
    client.create_relation("radiocall_instruction", "instruction_type", "instruction_type")


def setup_acceptable_variation_collection(client: DirectusClient):
    """
    Create the acceptable_variation collection.
    
    Purpose: Alternative correct readbacks for flexible grading.
    
    Why: There's no single "correct" readback. Pilots may phrase things
    differently (different word order, abbreviations) while still being
    correct. This enables flexible grading without penalizing valid variations.
    """
    print("\n📋 Setting up acceptable_variation collection...")
    
    if "acceptable_variation" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "variation_text",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "required": True,
                "note": "Alternative correct readback"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "notes",
            "type": "string",
            "meta": {
                "interface": "input",
                "note": "Why this variation is acceptable"
            }
        }
    ]
    
    client.create_collection(
        "acceptable_variation",
        fields,
        meta={
            "icon": "swap_horiz",
            "note": "Alternative correct readbacks - enables flexible grading",
            "singleton": False
        }
    )
    
    # Add relation to radiocall
    print("  Adding relation to radiocall...")
    client.create_field(
        "acceptable_variation",
        "radiocall",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True,
            "note": "Parent radiocall"
        }
    )
    client.create_relation("acceptable_variation", "radiocall", "radiocall", "variations")


def setup_common_error_collection(client: DirectusClient):
    """
    Create the common_error collection.
    
    Purpose: Catalog of typical mistakes with severity ratings.
    
    Why: Knowing common errors enables targeted feedback. Instead of
    just "wrong", we can tell the user exactly what they did wrong
    and how serious the error is.
    """
    print("\n📋 Setting up common_error collection...")
    
    if "common_error" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "error_code",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "width": "half",
                "note": "Unique error identifier (e.g., 'omit_runway')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "severity",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Critical", "value": "critical"},
                        {"text": "Major", "value": "major"},
                        {"text": "Minor", "value": "minor"},
                        {"text": "Style", "value": "style"}
                    ]
                },
                "note": "Error severity for scoring"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "description",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "required": True,
                "note": "What this error is"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "example",
            "type": "string",
            "meta": {
                "interface": "input",
                "note": "Example of this error in a readback"
            }
        },
        {
            "field": "feedback_text",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "note": "Feedback to show user when this error is detected"
            }
        }
    ]
    
    client.create_collection(
        "common_error",
        fields,
        meta={
            "icon": "error",
            "note": "Catalog of typical readback mistakes with severity ratings",
            "singleton": False
        }
    )
    
    # Add relation to radiocall
    print("  Adding relation to radiocall...")
    client.create_field(
        "common_error",
        "radiocall",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True,
            "note": "Parent radiocall"
        }
    )
    client.create_relation("common_error", "radiocall", "radiocall", "common_errors")
    
    # Add optional relation to specific instruction
    print("  Adding relation to instruction (optional)...")
    client.create_field(
        "common_error",
        "instruction_affected",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "note": "Specific instruction this error relates to (optional)"
        }
    )
    client.create_relation("common_error", "instruction_affected", "radiocall_instruction")


def setup_radiocall_set_collection(client: DirectusClient):
    """
    Create the radiocall_set collection for curated practice sets.
    
    Purpose: Group radiocalls into curated sets for structured learning.
    
    Why: Random practice isn't optimal. Curated sets allow progressive
    difficulty, focused practice on specific topics, and complete
    flight scenarios from startup to shutdown.
    """
    print("\n📋 Setting up radiocall_set collection...")
    
    if "radiocall_set" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "name",
            "type": "string",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Set name (e.g., 'Departure Procedures - Easy')"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "description",
            "type": "text",
            "meta": {
                "interface": "input-multiline",
                "note": "What this set covers"
            }
        },
        {
            "field": "difficulty",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "required": True,
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Super Easy", "value": "super_easy"},
                        {"text": "Easy", "value": "easy"},
                        {"text": "Medium", "value": "medium"},
                        {"text": "Hard", "value": "hard"},
                        {"text": "Mixed", "value": "mixed"}
                    ]
                },
                "note": "Overall difficulty level"
            },
            "schema": {"is_nullable": False}
        },
        {
            "field": "category",
            "type": "string",
            "meta": {
                "interface": "select-dropdown",
                "width": "half",
                "options": {
                    "choices": [
                        {"text": "Ground", "value": "ground"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "En Route", "value": "enroute"},
                        {"text": "Arrival", "value": "arrival"},
                        {"text": "Landing", "value": "landing"},
                        {"text": "Full Flight", "value": "full_flight"}
                    ]
                },
                "note": "Focus category (optional)"
            }
        },
        {
            "field": "is_scenario",
            "type": "boolean",
            "meta": {
                "interface": "boolean",
                "note": "Is this a complete flight scenario (startup to shutdown)?"
            },
            "schema": {"default_value": False}
        },
        {
            "field": "estimated_duration",
            "type": "integer",
            "meta": {
                "interface": "input",
                "note": "Estimated minutes to complete"
            }
        },
        {
            "field": "sort_order",
            "type": "integer",
            "meta": {
                "interface": "input",
                "note": "For ordering in UI"
            }
        }
    ]
    
    client.create_collection(
        "radiocall_set",
        fields,
        meta={
            "icon": "playlist_play",
            "note": "Curated practice sets for structured learning",
            "singleton": False
        }
    )
    
    # Add optional relation to airport
    print("  Adding relation to airport (optional)...")
    client.create_field(
        "radiocall_set",
        "airport",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "note": "Airport focus if this set is airport-specific"
        }
    )
    client.create_relation("radiocall_set", "airport", "airport")


def setup_radiocall_set_items_collection(client: DirectusClient):
    """
    Create the junction table for radiocall sets.
    
    Purpose: Many-to-many relationship between sets and radiocalls.
    
    Why: A radiocall can belong to multiple sets, and a set contains
    multiple radiocalls. The sequence field preserves the order within
    a set.
    """
    print("\n📋 Setting up radiocall_set_items collection...")
    
    if "radiocall_set_items" in client.get_collections():
        print("  Collection already exists, skipping creation")
        return
    
    fields = [
        {
            "field": "id",
            "type": "uuid",
            "meta": {"hidden": True, "interface": "input", "readonly": True},
            "schema": {"is_primary_key": True}
        },
        {
            "field": "sequence",
            "type": "integer",
            "meta": {
                "interface": "input",
                "required": True,
                "note": "Order within the set (1, 2, 3...)"
            },
            "schema": {"is_nullable": False}
        }
    ]
    
    client.create_collection(
        "radiocall_set_items",
        fields,
        meta={
            "icon": "link",
            "note": "Junction table linking sets to radiocalls with ordering",
            "singleton": False,
            "hidden": True  # Hide from main menu, accessed via relations
        }
    )
    
    # Add relation to set
    print("  Adding relation to radiocall_set...")
    client.create_field(
        "radiocall_set_items",
        "set",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True
        }
    )
    client.create_relation("radiocall_set_items", "set", "radiocall_set", "items")
    
    # Add relation to radiocall
    print("  Adding relation to radiocall...")
    client.create_field(
        "radiocall_set_items",
        "radiocall",
        "uuid",
        meta={
            "interface": "select-dropdown-m2o",
            "required": True
        }
    )
    client.create_relation("radiocall_set_items", "radiocall", "radiocall", "in_sets")


def setup_full_schema(client: DirectusClient):
    """
    Create the complete radiocall schema in the correct order.
    
    Order matters because of foreign key dependencies:
    1. instruction_type (no dependencies)
    2. callsign_format (no dependencies)
    3. radiocall (depends on airport - already exists)
    4. radiocall_instruction (depends on radiocall, instruction_type)
    5. acceptable_variation (depends on radiocall)
    6. common_error (depends on radiocall, radiocall_instruction)
    7. radiocall_set (depends on airport)
    8. radiocall_set_items (depends on radiocall_set, radiocall)
    """
    print("\n" + "="*60)
    print("RADIOCALL SCHEMA SETUP")
    print("="*60)
    
    # Independent collections first
    setup_instruction_type_collection(client)
    setup_callsign_format_collection(client)
    
    # Main entity
    setup_radiocall_collection(client)
    
    # Dependent collections
    setup_radiocall_instruction_collection(client)
    setup_acceptable_variation_collection(client)
    setup_common_error_collection(client)
    
    # Set management
    setup_radiocall_set_collection(client)
    setup_radiocall_set_items_collection(client)
    
    print("\n" + "="*60)
    print("✓ Schema setup complete!")
    print("="*60)


if __name__ == "__main__":
    client = DirectusClient()
    client.login()
    setup_full_schema(client)
