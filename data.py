"""
Reference Data for Radiocall Generator
Contains instruction types, callsign formats, and templates
"""

# ============================================================================
# INSTRUCTION TYPES
# ============================================================================
# These define all types of ATC instructions with their grading properties.
# Each type specifies whether it requires readback and is safety-critical.

INSTRUCTION_TYPES = [
    # Runway Operations (Critical)
    {
        "code": "runway_assignment",
        "display_name": "Runway Assignment",
        "category": "ground",
        "requires_readback": True,
        "is_critical": True,
        "description": "Assignment of a runway for takeoff or landing",
        "example_phrase": "runway 25L",
        "grading_weight": 1.0
    },
    {
        "code": "takeoff_clearance",
        "display_name": "Takeoff Clearance",
        "category": "departure",
        "requires_readback": True,
        "is_critical": True,
        "description": "Clearance to take off",
        "example_phrase": "cleared for takeoff",
        "grading_weight": 1.0
    },
    {
        "code": "landing_clearance",
        "display_name": "Landing Clearance",
        "category": "landing",
        "requires_readback": True,
        "is_critical": True,
        "description": "Clearance to land",
        "example_phrase": "cleared to land",
        "grading_weight": 1.0
    },
    {
        "code": "line_up",
        "display_name": "Line Up / Position and Hold",
        "category": "departure",
        "requires_readback": True,
        "is_critical": True,
        "description": "Instruction to enter runway and wait",
        "example_phrase": "line up runway 25L",
        "grading_weight": 1.0
    },
    {
        "code": "hold_short",
        "display_name": "Hold Short",
        "category": "ground",
        "requires_readback": True,
        "is_critical": True,
        "description": "Instruction to hold short of a runway or taxiway",
        "example_phrase": "hold short runway 07R",
        "grading_weight": 1.0
    },
    {
        "code": "crossing_clearance",
        "display_name": "Runway Crossing Clearance",
        "category": "ground",
        "requires_readback": True,
        "is_critical": True,
        "description": "Clearance to cross an active runway",
        "example_phrase": "cross runway 25R",
        "grading_weight": 1.0
    },
    
    # Altitude (Critical)
    {
        "code": "altitude_assignment",
        "display_name": "Altitude Assignment",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Climb or descend to a specific altitude or flight level",
        "example_phrase": "climb and maintain flight level 350",
        "grading_weight": 0.95
    },
    {
        "code": "altitude_restriction",
        "display_name": "Altitude Restriction",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Altitude restrictions (at or above, at or below)",
        "example_phrase": "descend to reach 4000 feet by ALPHA",
        "grading_weight": 0.9
    },
    
    # Heading (Critical)
    {
        "code": "heading_assignment",
        "display_name": "Heading Assignment",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Turn to a specific heading",
        "example_phrase": "turn right heading 090",
        "grading_weight": 0.9
    },
    
    # Speed (Critical)
    {
        "code": "speed_assignment",
        "display_name": "Speed Assignment",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Speed instruction or restriction",
        "example_phrase": "reduce speed 220 knots",
        "grading_weight": 0.85
    },
    
    # Frequency (Required Readback)
    {
        "code": "frequency_change",
        "display_name": "Frequency Change",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Handoff to another controller frequency",
        "example_phrase": "contact approach 119.850",
        "grading_weight": 0.9
    },
    
    # Transponder (Required Readback)
    {
        "code": "squawk_code",
        "display_name": "Squawk/Transponder Code",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Transponder code assignment",
        "example_phrase": "squawk 4521",
        "grading_weight": 0.85
    },
    
    # Taxi (Required Readback)
    {
        "code": "taxi_instruction",
        "display_name": "Taxi Instruction",
        "category": "ground",
        "requires_readback": True,
        "is_critical": False,
        "description": "Taxi route via taxiways",
        "example_phrase": "taxi via Alpha, Bravo, hold short runway 25L",
        "grading_weight": 0.7
    },
    {
        "code": "pushback_approved",
        "display_name": "Pushback Approval",
        "category": "ground",
        "requires_readback": True,
        "is_critical": False,
        "description": "Clearance to push back from gate",
        "example_phrase": "pushback approved, facing west",
        "grading_weight": 0.6
    },
    {
        "code": "startup_approved",
        "display_name": "Startup Approval",
        "category": "ground",
        "requires_readback": True,
        "is_critical": False,
        "description": "Clearance to start engines",
        "example_phrase": "startup approved",
        "grading_weight": 0.5
    },
    
    # Approach (Critical)
    {
        "code": "approach_clearance",
        "display_name": "Approach Clearance",
        "category": "arrival",
        "requires_readback": True,
        "is_critical": True,
        "description": "Clearance for an instrument approach",
        "example_phrase": "cleared ILS approach runway 25L",
        "grading_weight": 0.95
    },
    {
        "code": "go_around",
        "display_name": "Go Around",
        "category": "landing",
        "requires_readback": True,
        "is_critical": True,
        "description": "Instruction to abort landing and go around",
        "example_phrase": "go around, climb 3000 feet",
        "grading_weight": 1.0
    },
    
    # Information (No Readback Required)
    {
        "code": "wind_information",
        "display_name": "Wind Information",
        "category": "departure",
        "requires_readback": False,
        "is_critical": False,
        "description": "Current wind conditions",
        "example_phrase": "wind 270 degrees 8 knots",
        "grading_weight": 0.0
    },
    {
        "code": "traffic_information",
        "display_name": "Traffic Information",
        "category": "enroute",
        "requires_readback": False,
        "is_critical": False,
        "description": "Traffic advisory",
        "example_phrase": "traffic 2 o'clock, 5 miles, opposite direction",
        "grading_weight": 0.0
    },
    {
        "code": "atis_information",
        "display_name": "ATIS Information",
        "category": "ground",
        "requires_readback": False,
        "is_critical": False,
        "description": "ATIS information letter",
        "example_phrase": "information Charlie",
        "grading_weight": 0.0
    },
    
    # Altimeter (Required Readback)
    {
        "code": "altimeter_setting",
        "display_name": "Altimeter Setting",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": False,
        "description": "QNH or altimeter pressure setting",
        "example_phrase": "QNH 1013",
        "grading_weight": 0.6
    },
    
    # SID/STAR (Required Readback)
    {
        "code": "sid_assignment",
        "display_name": "SID Assignment",
        "category": "departure",
        "requires_readback": True,
        "is_critical": True,
        "description": "Standard Instrument Departure assignment",
        "example_phrase": "cleared TOBAK 1 Alpha departure",
        "grading_weight": 0.85
    },
    {
        "code": "star_assignment",
        "display_name": "STAR Assignment",
        "category": "arrival",
        "requires_readback": True,
        "is_critical": True,
        "description": "Standard Terminal Arrival Route assignment",
        "example_phrase": "cleared RILAX 2 Bravo arrival",
        "grading_weight": 0.85
    },
    
    # Direct Routing
    {
        "code": "direct_to",
        "display_name": "Direct To",
        "category": "enroute",
        "requires_readback": True,
        "is_critical": True,
        "description": "Direct routing to a waypoint",
        "example_phrase": "proceed direct ROMEO",
        "grading_weight": 0.8
    },
    
    # Vacate (Required Readback)
    {
        "code": "vacate_instruction",
        "display_name": "Vacate Runway",
        "category": "landing",
        "requires_readback": True,
        "is_critical": False,
        "description": "Instruction to exit the runway",
        "example_phrase": "vacate left Alpha",
        "grading_weight": 0.5
    }
]

# ============================================================================
# CALLSIGN FORMATS
# ============================================================================
# Templates for generating realistic aircraft callsigns by region and type.

CALLSIGN_FORMATS = [
    # German Airlines
    {
        "airline_code": "DLH",
        "airline_callsign": "Lufthansa",
        "format_pattern": "{airline} {number}",
        "region": "DACH",
        "difficulty": "super_easy",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    {
        "airline_code": "EWG",
        "airline_callsign": "Eurowings",
        "format_pattern": "{airline} {number}",
        "region": "DACH",
        "difficulty": "easy",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    {
        "airline_code": "CFG",
        "airline_callsign": "Condor",
        "format_pattern": "{airline} {number}",
        "region": "DACH",
        "difficulty": "easy",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    
    # Austrian Airlines
    {
        "airline_code": "AUA",
        "airline_callsign": "Austrian",
        "format_pattern": "{airline} {number}",
        "region": "DACH",
        "difficulty": "easy",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    
    # Swiss Airlines
    {
        "airline_code": "SWR",
        "airline_callsign": "Swiss",
        "format_pattern": "{airline} {number}",
        "region": "DACH",
        "difficulty": "easy",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    {
        "airline_code": "EDW",
        "airline_callsign": "Edelweiss",
        "format_pattern": "{airline} {number}",
        "region": "DACH",
        "difficulty": "medium",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    
    # Other European
    {
        "airline_code": "BAW",
        "airline_callsign": "Speedbird",
        "format_pattern": "{airline} {number}",
        "region": "EU",
        "difficulty": "medium",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    {
        "airline_code": "AFR",
        "airline_callsign": "Air France",
        "format_pattern": "{airline} {number}",
        "region": "EU",
        "difficulty": "medium",
        "is_registration_based": False,
        "phonetic_template": "{airline} {number_individual}"
    },
    {
        "airline_code": "KLM",
        "airline_callsign": "KLM",
        "format_pattern": "{airline} {number}",
        "region": "EU",
        "difficulty": "easy",
        "is_registration_based": False,
        "phonetic_template": "K L M {number_individual}"
    },
    
    # Registration-based (harder)
    {
        "airline_code": None,
        "airline_callsign": None,
        "format_pattern": "D-{registration}",
        "region": "DACH",
        "difficulty": "medium",
        "is_registration_based": True,
        "phonetic_template": "Delta {registration_phonetic}"
    },
    {
        "airline_code": None,
        "airline_callsign": None,
        "format_pattern": "OE-{registration}",
        "region": "DACH",
        "difficulty": "medium",
        "is_registration_based": True,
        "phonetic_template": "Oscar Echo {registration_phonetic}"
    },
    {
        "airline_code": None,
        "airline_callsign": None,
        "format_pattern": "HB-{registration}",
        "region": "DACH",
        "difficulty": "medium",
        "is_registration_based": True,
        "phonetic_template": "Hotel Bravo {registration_phonetic}"
    },
    
    # US Style (for variety)
    {
        "airline_code": None,
        "airline_callsign": None,
        "format_pattern": "N{number}{letters}",
        "region": "US",
        "difficulty": "hard",
        "is_registration_based": True,
        "phonetic_template": "November {number_individual} {letters_phonetic}"
    }
]

# ============================================================================
# NATO PHONETIC ALPHABET
# ============================================================================

NATO_ALPHABET = {
    'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta',
    'E': 'Echo', 'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel',
    'I': 'India', 'J': 'Juliet', 'K': 'Kilo', 'L': 'Lima',
    'M': 'Mike', 'N': 'November', 'O': 'Oscar', 'P': 'Papa',
    'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
    'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray',
    'Y': 'Yankee', 'Z': 'Zulu'
}

# Number pronunciation (individual digits)
NUMBER_PHONETICS = {
    '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
    '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'niner'
}

# ============================================================================
# DIFFICULTY SETTINGS
# ============================================================================
# Configuration for each difficulty tier

DIFFICULTY_SETTINGS = {
    "super_easy": {
        "instructions_per_call": (1, 1),      # Always single instruction
        "callsign_types": ["airline"],         # Simple airline callsigns only
        "include_conditional": False,          # No conditional clearances
        "include_amendment": False,            # No amendments
        "speaking_pace": "slow",
        "categories": ["ground", "departure", "landing"],  # Basic categories
        "subcategories": [
            "taxi", "takeoff_clearance", "landing_clearance",
            "hold_short", "frequency_change"
        ]
    },
    "easy": {
        "instructions_per_call": (1, 2),
        "callsign_types": ["airline"],
        "include_conditional": False,
        "include_amendment": False,
        "speaking_pace": "normal",
        "categories": ["ground", "departure", "enroute", "arrival", "landing"],
        "subcategories": [
            "taxi", "takeoff_clearance", "landing_clearance",
            "hold_short", "frequency_change", "altitude_change",
            "line_up", "initial_climb"
        ]
    },
    "medium": {
        "instructions_per_call": (2, 3),
        "callsign_types": ["airline", "registration"],
        "include_conditional": True,           # Can have conditionals
        "include_amendment": False,
        "speaking_pace": "normal",
        "categories": ["ground", "departure", "enroute", "arrival", "landing"],
        "subcategories": [
            "taxi", "takeoff_clearance", "landing_clearance",
            "hold_short", "frequency_change", "altitude_change",
            "line_up", "initial_climb", "heading_assignment",
            "speed_control", "approach_clearance"
        ]
    },
    "hard": {
        "instructions_per_call": (3, 4),
        "callsign_types": ["airline", "registration"],
        "include_conditional": True,
        "include_amendment": True,             # Can have amended clearances
        "speaking_pace": "fast",
        "categories": ["ground", "departure", "enroute", "arrival", "landing"],
        "subcategories": [
            "taxi", "takeoff_clearance", "landing_clearance",
            "hold_short", "frequency_change", "altitude_change",
            "line_up", "initial_climb", "heading_assignment",
            "speed_control", "approach_clearance", "go_around",
            "direct_routing", "vacate"
        ]
    }
}

# ============================================================================
# FREQUENCY DATA (DACH Region)
# ============================================================================

FREQUENCIES = {
    "tower": ["118.500", "119.900", "120.775", "118.025", "121.100"],
    "ground": ["121.850", "121.900", "121.750", "121.650", "121.975"],
    "approach": ["119.850", "120.150", "121.025", "118.950", "120.350"],
    "departure": ["120.775", "125.350", "121.225", "119.225", "120.125"],
    "center": ["132.475", "133.650", "125.750", "127.725", "134.225"],
    "clearance": ["121.775", "121.825", "121.925", "118.025", "121.700"]
}

# ============================================================================
# TAXIWAY NAMES (Common at major airports)
# ============================================================================

TAXIWAYS = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf",
    "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November",
    "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango"
]

# ============================================================================
# WAYPOINTS (Common DACH region)
# ============================================================================

WAYPOINTS = [
    "TOBAK", "RILAX", "LANDU", "SPESA", "KERAX", "LUPEN", "ANORA",
    "GIVMI", "OSMIT", "BADGO", "TEKSI", "BOMBI", "VEDOX", "POVEL",
    "RASVO", "UNOKO", "ABTAL", "GULKO", "MAKOS", "XAMOD"
]

# ============================================================================
# APPROACH TYPES
# ============================================================================

APPROACH_TYPES = [
    {"code": "ILS", "display": "ILS", "phonetic": "I L S"},
    {"code": "VOR", "display": "VOR", "phonetic": "V O R"},
    {"code": "RNAV", "display": "RNAV", "phonetic": "R-NAV"},
    {"code": "NDB", "display": "NDB", "phonetic": "N D B"},
    {"code": "VISUAL", "display": "visual", "phonetic": "visual"}
]

# ============================================================================
# COMMON ERROR TEMPLATES
# ============================================================================
# Templates for errors that can occur with each instruction type

COMMON_ERRORS = {
    "runway_assignment": [
        {
            "error_code": "omit_runway",
            "severity": "critical",
            "description": "Pilot omits runway designator from readback",
            "example": "Cleared for takeoff, Lufthansa 450",
            "feedback_text": "CRITICAL: You must always read back the runway assignment. Wrong runway = potential disaster."
        },
        {
            "error_code": "wrong_runway_number",
            "severity": "critical",
            "description": "Pilot reads back incorrect runway number",
            "example": "Runway 25R instead of 25L",
            "feedback_text": "CRITICAL: Wrong runway! This is a potential runway incursion."
        },
        {
            "error_code": "omit_runway_designator",
            "severity": "critical",
            "description": "Pilot omits L/R/C designator",
            "example": "Runway 25 instead of 25L",
            "feedback_text": "You must include the L/R/C designator when present."
        }
    ],
    "altitude_assignment": [
        {
            "error_code": "wrong_altitude",
            "severity": "critical",
            "description": "Pilot reads back incorrect altitude",
            "example": "Flight level 320 instead of FL350",
            "feedback_text": "CRITICAL: Wrong altitude! This could cause a TCAS event or collision."
        },
        {
            "error_code": "omit_altitude",
            "severity": "critical",
            "description": "Pilot omits altitude from readback",
            "example": "Climbing, Lufthansa 450",
            "feedback_text": "CRITICAL: Always read back altitude assignments."
        },
        {
            "error_code": "fl_vs_feet_confusion",
            "severity": "major",
            "description": "Confusing flight level with feet",
            "example": "35000 feet instead of FL350",
            "feedback_text": "Above transition altitude, use Flight Level, not feet."
        }
    ],
    "heading_assignment": [
        {
            "error_code": "wrong_heading",
            "severity": "critical",
            "description": "Pilot reads back incorrect heading",
            "example": "Heading 270 instead of 090",
            "feedback_text": "CRITICAL: Wrong heading! You could be flying the opposite direction."
        },
        {
            "error_code": "omit_heading",
            "severity": "critical",
            "description": "Pilot omits heading from readback",
            "feedback_text": "Always read back heading assignments."
        }
    ],
    "frequency_change": [
        {
            "error_code": "wrong_frequency",
            "severity": "critical",
            "description": "Pilot reads back incorrect frequency",
            "example": "119.850 instead of 119.580",
            "feedback_text": "Wrong frequency! You won't be able to contact the next controller."
        },
        {
            "error_code": "omit_frequency",
            "severity": "major",
            "description": "Pilot doesn't read back frequency",
            "feedback_text": "Read back frequencies to confirm you have them correct."
        }
    ],
    "squawk_code": [
        {
            "error_code": "wrong_squawk",
            "severity": "critical",
            "description": "Pilot reads back incorrect transponder code",
            "example": "Squawk 4512 instead of 4521",
            "feedback_text": "Wrong squawk code! Controller won't be able to identify you."
        }
    ],
    "hold_short": [
        {
            "error_code": "omit_hold_short",
            "severity": "critical",
            "description": "Pilot doesn't acknowledge hold short",
            "feedback_text": "CRITICAL: You MUST acknowledge hold short instructions. This prevents runway incursions."
        },
        {
            "error_code": "continue_instead_hold",
            "severity": "critical",
            "description": "Pilot misunderstands as continue",
            "feedback_text": "CRITICAL: Hold short means STOP. Do not enter the runway."
        }
    ]
}
