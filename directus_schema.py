"""
Directus Schema Setup for Radiocall Readback Tool

This module defines and creates all collections needed for the radiocall system.
Run with DRY_RUN=True in config.py to preview without making changes.
"""

import requests
import json
from config import DIRECTUS_URL, DIRECTUS_EMAIL, DIRECTUS_PASSWORD, DRY_RUN


class DirectusSchemaManager:
    def __init__(self, dry_run=False):
        self.base_url = DIRECTUS_URL
        self.token = None
        self.dry_run = dry_run
        self.planned_actions = []
        
    def log_action(self, action_type, description, details=None):
        """Log a planned or executed action"""
        action = {
            "type": action_type,
            "description": description,
            "details": details or {}
        }
        self.planned_actions.append(action)
        
        prefix = "[DRY RUN] " if self.dry_run else "[EXECUTE] "
        print(f"{prefix}{action_type}: {description}")
        
    def login(self):
        """Authenticate with Directus"""
        if self.dry_run:
            self.log_action("AUTH", "Would authenticate with Directus API")
            self.token = "dry-run-token"
            return True
            
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": DIRECTUS_EMAIL, "password": DIRECTUS_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json()["data"]["access_token"]
            self.log_action("AUTH", "Successfully authenticated with Directus")
            return True
        else:
            print(f"Login failed: {response.text}")
            return False
    
    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def collection_exists(self, collection_name):
        """Check if a collection already exists"""
        if self.dry_run:
            return False  # Assume it doesn't exist for dry run
            
        response = requests.get(
            f"{self.base_url}/collections/{collection_name}",
            headers=self._headers()
        )
        return response.status_code == 200
    
    def create_collection(self, collection_name, fields, meta=None):
        """Create a collection with specified fields"""
        
        if not self.dry_run and self.collection_exists(collection_name):
            self.log_action("SKIP", f"Collection '{collection_name}' already exists")
            return True
        
        # Build field details for logging
        field_summary = []
        for field in fields:
            field_info = f"  - {field['field']}: {field['type']}"
            if field.get('schema', {}).get('is_nullable') == False:
                field_info += " (required)"
            if field.get('meta', {}).get('note'):
                field_info += f" -- {field['meta']['note']}"
            field_summary.append(field_info)
        
        details = {
            "collection": collection_name,
            "field_count": len(fields),
            "fields": field_summary
        }
        
        self.log_action("CREATE_COLLECTION", f"Create collection '{collection_name}' with {len(fields)} fields", details)
        
        if self.dry_run:
            print(f"\n    Fields for '{collection_name}':")
            for f in field_summary:
                print(f"    {f}")
            print()
            return True
        
        # Actually create the collection
        payload = {
            "collection": collection_name,
            "fields": fields,
            "meta": meta or {
                "collection": collection_name,
                "icon": "radio",
                "note": f"Radiocall system: {collection_name}"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/collections",
            headers=self._headers(),
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print(f"    ✓ Created successfully")
            return True
        else:
            print(f"    ✗ Failed: {response.text}")
            return False
    
    def create_relation(self, many_collection, many_field, one_collection):
        """Create a M2O relation"""
        
        details = {
            "many_collection": many_collection,
            "many_field": many_field,
            "one_collection": one_collection
        }
        
        self.log_action(
            "CREATE_RELATION", 
            f"Relation: {many_collection}.{many_field} → {one_collection}",
            details
        )
        
        if self.dry_run:
            return True
        
        payload = {
            "collection": many_collection,
            "field": many_field,
            "related_collection": one_collection,
            "meta": {
                "many_collection": many_collection,
                "many_field": many_field,
                "one_collection": one_collection
            },
            "schema": {
                "on_delete": "SET NULL"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/relations",
            headers=self._headers(),
            json=payload
        )
        
        return response.status_code in [200, 201]
    
    def setup_all_collections(self):
        """Set up all collections for the radiocall system"""
        
        print("\n" + "="*70)
        print("RADIOCALL READBACK TOOL - DIRECTUS SCHEMA SETUP")
        print("="*70)
        if self.dry_run:
            print("MODE: DRY RUN (no changes will be made)")
        else:
            print("MODE: LIVE (changes will be applied to Directus)")
        print("="*70 + "\n")
        
        # 1. INSTRUCTION_TYPE - Master reference for instruction types
        print("\n--- 1. INSTRUCTION TYPE (Reference Table) ---")
        print("Purpose: Master list of all ATC instruction types with grading rules")
        self.create_collection("instruction_type", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True, "has_auto_increment": False}
            },
            {
                "field": "code",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Unique identifier (e.g., 'runway_assignment')"},
                "schema": {"is_nullable": False, "is_unique": True}
            },
            {
                "field": "display_name",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Human-readable name"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "category",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "note": "Instruction category",
                    "options": {"choices": [
                        {"text": "Ground", "value": "ground"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "En Route", "value": "enroute"},
                        {"text": "Arrival", "value": "arrival"},
                        {"text": "Landing", "value": "landing"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "requires_readback",
                "type": "boolean",
                "meta": {"interface": "boolean", "required": True, "note": "Must pilot read this back?"},
                "schema": {"is_nullable": False, "default_value": True}
            },
            {
                "field": "is_critical",
                "type": "boolean",
                "meta": {"interface": "boolean", "required": True, "note": "Is error safety-critical?"},
                "schema": {"is_nullable": False, "default_value": False}
            },
            {
                "field": "grading_weight",
                "type": "float",
                "meta": {"interface": "input", "required": True, "note": "Weight in scoring (0.0-1.0)"},
                "schema": {"is_nullable": False, "default_value": 0.5}
            },
            {
                "field": "description",
                "type": "text",
                "meta": {"interface": "input-multiline", "note": "Detailed explanation"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "example_phrase",
                "type": "string",
                "meta": {"interface": "input", "note": "Example of this instruction"},
                "schema": {"is_nullable": True}
            }
        ])
        
        # 2. CALLSIGN_FORMAT - Templates for generating callsigns
        print("\n--- 2. CALLSIGN FORMAT (Reference Table) ---")
        print("Purpose: Templates for generating realistic aircraft callsigns")
        self.create_collection("callsign_format", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "airline_code",
                "type": "string",
                "meta": {"interface": "input", "note": "ICAO airline code (DLH, BAW, etc.)"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "airline_callsign",
                "type": "string",
                "meta": {"interface": "input", "note": "Radio callsign (Lufthansa, Speedbird)"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "format_pattern",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Pattern: {airline} {number}"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "region",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "DACH", "value": "DACH"},
                        {"text": "Europe", "value": "EU"},
                        {"text": "USA", "value": "US"},
                        {"text": "UK", "value": "UK"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "difficulty",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "Super Easy", "value": "super_easy"},
                        {"text": "Easy", "value": "easy"},
                        {"text": "Medium", "value": "medium"},
                        {"text": "Hard", "value": "hard"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "is_registration_based",
                "type": "boolean",
                "meta": {"interface": "boolean", "required": True, "note": "True for N123AB style"},
                "schema": {"is_nullable": False, "default_value": False}
            },
            {
                "field": "phonetic_template",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "How to speak the callsign"},
                "schema": {"is_nullable": False}
            }
        ])
        
        # 3. RADIOCALL - Main collection for ATC transmissions
        print("\n--- 3. RADIOCALL (Main Collection) ---")
        print("Purpose: Complete ATC transmissions with expected readbacks")
        self.create_collection("radiocall", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "airport",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Associated airport"},
                "schema": {"is_nullable": False, "foreign_key_table": "airport"}
            },
            {
                "field": "category",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "note": "Transmission category",
                    "options": {"choices": [
                        {"text": "Ground", "value": "ground"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "En Route", "value": "enroute"},
                        {"text": "Arrival", "value": "arrival"},
                        {"text": "Landing", "value": "landing"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "subcategory",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "note": "Specific instruction type",
                    "options": {"choices": [
                        {"text": "Startup", "value": "startup"},
                        {"text": "Pushback", "value": "pushback"},
                        {"text": "Taxi", "value": "taxi"},
                        {"text": "Hold Short", "value": "hold_short"},
                        {"text": "Line Up", "value": "line_up"},
                        {"text": "Takeoff Clearance", "value": "takeoff_clearance"},
                        {"text": "Initial Climb", "value": "initial_climb"},
                        {"text": "Frequency Change", "value": "frequency_change"},
                        {"text": "Altitude Change", "value": "altitude_change"},
                        {"text": "Heading Assignment", "value": "heading_assignment"},
                        {"text": "Speed Control", "value": "speed_control"},
                        {"text": "Direct Routing", "value": "direct_routing"},
                        {"text": "Approach Clearance", "value": "approach_clearance"},
                        {"text": "Landing Clearance", "value": "landing_clearance"},
                        {"text": "Go Around", "value": "go_around"},
                        {"text": "Vacate Runway", "value": "vacate_runway"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "difficulty",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "Super Easy", "value": "super_easy"},
                        {"text": "Easy", "value": "easy"},
                        {"text": "Medium", "value": "medium"},
                        {"text": "Hard", "value": "hard"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "flight_phase",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "Pre-flight", "value": "preflight"},
                        {"text": "Taxi Out", "value": "taxi_out"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "Climb", "value": "climb"},
                        {"text": "Cruise", "value": "cruise"},
                        {"text": "Descent", "value": "descent"},
                        {"text": "Approach", "value": "approach"},
                        {"text": "Landing", "value": "landing"},
                        {"text": "Taxi In", "value": "taxi_in"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "controller_position",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "Clearance Delivery", "value": "clearance"},
                        {"text": "Ground", "value": "ground"},
                        {"text": "Tower", "value": "tower"},
                        {"text": "Departure", "value": "departure"},
                        {"text": "Approach", "value": "approach"},
                        {"text": "Center", "value": "center"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "aircraft_callsign",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Callsign used in transmission"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "callsign_phonetic",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "How callsign is spoken"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "full_transmission",
                "type": "text",
                "meta": {"interface": "input-multiline", "required": True, "note": "Complete controller transmission"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "expected_readback",
                "type": "text",
                "meta": {"interface": "input-multiline", "required": True, "note": "Correct pilot readback"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "critical_elements",
                "type": "json",
                "meta": {"interface": "input-code", "required": True, "note": "Array of critical instruction codes", "options": {"language": "json"}},
                "schema": {"is_nullable": False}
            },
            {
                "field": "instruction_count",
                "type": "integer",
                "meta": {"interface": "input", "required": True, "note": "Number of instructions"},
                "schema": {"is_nullable": False, "default_value": 1}
            },
            {
                "field": "has_conditional",
                "type": "boolean",
                "meta": {"interface": "boolean", "note": "Contains conditional instruction?"},
                "schema": {"is_nullable": False, "default_value": False}
            },
            {
                "field": "is_amendment",
                "type": "boolean",
                "meta": {"interface": "boolean", "note": "Is this an amended clearance?"},
                "schema": {"is_nullable": False, "default_value": False}
            },
            {
                "field": "notes",
                "type": "text",
                "meta": {"interface": "input-multiline", "note": "Teaching notes or context"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "date_created",
                "type": "timestamp",
                "meta": {"interface": "datetime", "readonly": True, "special": ["date-created"]},
                "schema": {"is_nullable": True}
            }
        ])
        
        # 4. RADIOCALL_INSTRUCTION - Individual instructions within a call
        print("\n--- 4. RADIOCALL INSTRUCTION (Detail Table) ---")
        print("Purpose: Individual instructions for granular grading")
        self.create_collection("radiocall_instruction", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "radiocall",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Parent radiocall"},
                "schema": {"is_nullable": False, "foreign_key_table": "radiocall"}
            },
            {
                "field": "instruction_type",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Instruction type reference"},
                "schema": {"is_nullable": False, "foreign_key_table": "instruction_type"}
            },
            {
                "field": "sequence",
                "type": "integer",
                "meta": {"interface": "input", "required": True, "note": "Order in transmission (1, 2, 3...)"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "raw_value",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Machine value (25L, FL350, 090)"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "display_text",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "As in transmission"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "phonetic_text",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Spoken form"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "readback_text",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Expected in readback"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "unit",
                "type": "string",
                "meta": {"interface": "input", "note": "Unit (feet, FL, degrees)"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "is_conditional",
                "type": "boolean",
                "meta": {"interface": "boolean", "note": "Is this a conditional instruction?"},
                "schema": {"is_nullable": False, "default_value": False}
            },
            {
                "field": "condition_text",
                "type": "string",
                "meta": {"interface": "input", "note": "The condition if conditional"},
                "schema": {"is_nullable": True}
            }
        ])
        
        # 5. ACCEPTABLE_VARIATION - Alternative correct readbacks
        print("\n--- 5. ACCEPTABLE VARIATION ---")
        print("Purpose: Alternative correct readbacks for flexible grading")
        self.create_collection("acceptable_variation", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "radiocall",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Parent radiocall"},
                "schema": {"is_nullable": False, "foreign_key_table": "radiocall"}
            },
            {
                "field": "variation_text",
                "type": "text",
                "meta": {"interface": "input-multiline", "required": True, "note": "Alternative correct readback"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "notes",
                "type": "string",
                "meta": {"interface": "input", "note": "Why this variation is acceptable"},
                "schema": {"is_nullable": True}
            }
        ])
        
        # 6. COMMON_ERROR - Typical mistakes for each radiocall
        print("\n--- 6. COMMON ERROR ---")
        print("Purpose: Catalog of typical mistakes with severity ratings")
        self.create_collection("common_error", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "radiocall",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Parent radiocall"},
                "schema": {"is_nullable": False, "foreign_key_table": "radiocall"}
            },
            {
                "field": "error_code",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Unique error identifier"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "description",
                "type": "text",
                "meta": {"interface": "input-multiline", "required": True, "note": "What the error is"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "example",
                "type": "string",
                "meta": {"interface": "input", "note": "Example of this error"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "severity",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "Critical", "value": "critical"},
                        {"text": "Major", "value": "major"},
                        {"text": "Minor", "value": "minor"},
                        {"text": "Style", "value": "style"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "instruction_affected",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "note": "Which instruction this error relates to"},
                "schema": {"is_nullable": True, "foreign_key_table": "radiocall_instruction"}
            },
            {
                "field": "feedback_text",
                "type": "text",
                "meta": {"interface": "input-multiline", "note": "Feedback to show user"},
                "schema": {"is_nullable": True}
            }
        ])
        
        # 7. RADIOCALL_SET - Curated practice sets
        print("\n--- 7. RADIOCALL SET ---")
        print("Purpose: Group radiocalls into curated practice sets")
        self.create_collection("radiocall_set", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "name",
                "type": "string",
                "meta": {"interface": "input", "required": True, "note": "Set name"},
                "schema": {"is_nullable": False}
            },
            {
                "field": "description",
                "type": "text",
                "meta": {"interface": "input-multiline", "note": "What this set covers"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "difficulty",
                "type": "string",
                "meta": {
                    "interface": "select-dropdown",
                    "required": True,
                    "options": {"choices": [
                        {"text": "Super Easy", "value": "super_easy"},
                        {"text": "Easy", "value": "easy"},
                        {"text": "Medium", "value": "medium"},
                        {"text": "Hard", "value": "hard"},
                        {"text": "Mixed", "value": "mixed"}
                    ]}
                },
                "schema": {"is_nullable": False}
            },
            {
                "field": "category",
                "type": "string",
                "meta": {"interface": "input", "note": "Focus category if any"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "airport",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "note": "Airport focus if any"},
                "schema": {"is_nullable": True, "foreign_key_table": "airport"}
            },
            {
                "field": "is_scenario",
                "type": "boolean",
                "meta": {"interface": "boolean", "required": True, "note": "Is this a complete flight scenario?"},
                "schema": {"is_nullable": False, "default_value": False}
            },
            {
                "field": "estimated_duration",
                "type": "integer",
                "meta": {"interface": "input", "note": "Minutes to complete"},
                "schema": {"is_nullable": True}
            },
            {
                "field": "sort_order",
                "type": "integer",
                "meta": {"interface": "input", "note": "For ordering in UI"},
                "schema": {"is_nullable": True}
            }
        ])
        
        # 8. RADIOCALL_SET_ITEMS - Junction table
        print("\n--- 8. RADIOCALL SET ITEMS (Junction) ---")
        print("Purpose: Link radiocalls to practice sets (M2M)")
        self.create_collection("radiocall_set_items", [
            {
                "field": "id",
                "type": "uuid",
                "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                "schema": {"is_primary_key": True}
            },
            {
                "field": "set",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Parent set"},
                "schema": {"is_nullable": False, "foreign_key_table": "radiocall_set"}
            },
            {
                "field": "radiocall",
                "type": "uuid",
                "meta": {"interface": "select-dropdown-m2o", "required": True, "note": "Included radiocall"},
                "schema": {"is_nullable": False, "foreign_key_table": "radiocall"}
            },
            {
                "field": "sequence",
                "type": "integer",
                "meta": {"interface": "input", "required": True, "note": "Order in set"},
                "schema": {"is_nullable": False}
            }
        ])
        
        # Create relations
        print("\n--- RELATIONS ---")
        self.create_relation("radiocall", "airport", "airport")
        self.create_relation("radiocall_instruction", "radiocall", "radiocall")
        self.create_relation("radiocall_instruction", "instruction_type", "instruction_type")
        self.create_relation("acceptable_variation", "radiocall", "radiocall")
        self.create_relation("common_error", "radiocall", "radiocall")
        self.create_relation("common_error", "instruction_affected", "radiocall_instruction")
        self.create_relation("radiocall_set", "airport", "airport")
        self.create_relation("radiocall_set_items", "set", "radiocall_set")
        self.create_relation("radiocall_set_items", "radiocall", "radiocall")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        collections = [a for a in self.planned_actions if a["type"] == "CREATE_COLLECTION"]
        relations = [a for a in self.planned_actions if a["type"] == "CREATE_RELATION"]
        
        print(f"Collections to create: {len(collections)}")
        for c in collections:
            print(f"  • {c['details']['collection']} ({c['details']['field_count']} fields)")
        
        print(f"\nRelations to create: {len(relations)}")
        for r in relations:
            print(f"  • {r['details']['many_collection']}.{r['details']['many_field']} → {r['details']['one_collection']}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN COMPLETE - No changes were made")
            print("Set DRY_RUN = False in config.py to apply these changes")
        else:
            print("\n✓ Schema setup complete!")
        
        return True


def main():
    print(f"Dry Run Mode: {DRY_RUN}")
    
    manager = DirectusSchemaManager(dry_run=DRY_RUN)
    
    if not manager.login():
        print("Failed to authenticate")
        return
    
    manager.setup_all_collections()


if __name__ == "__main__":
    main()
