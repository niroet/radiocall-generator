"""
Radiocall Generator - Core Generation Logic
Creates realistic ATC radio calls with all grading data
"""

import random
import uuid
from data import (
    NATO_ALPHABET, NUMBER_PHONETICS, DIFFICULTY_SETTINGS,
    FREQUENCIES, TAXIWAYS, WAYPOINTS, APPROACH_TYPES, COMMON_ERRORS
)


class RadiocallGenerator:
    def __init__(self, airports, instruction_types, callsign_formats, instruction_type_map):
        self.airports = airports
        self.instruction_types = instruction_types
        self.callsign_formats = callsign_formats
        self.instruction_type_map = instruction_type_map
        
        # Build callsign lookup by difficulty
        self.callsigns_by_difficulty = {
            "super_easy": [],
            "easy": [],
            "medium": [],
            "hard": []
        }
        
        for cf in callsign_formats:
            diff = cf["difficulty"]
            # Add to this difficulty and all higher difficulties
            difficulties = ["super_easy", "easy", "medium", "hard"]
            idx = difficulties.index(diff)
            for d in difficulties[idx:]:
                self.callsigns_by_difficulty[d].append(cf)
    
    def number_to_phonetic(self, number, individual=True):
        """Convert a number to phonetic pronunciation"""
        num_str = str(number)
        if individual:
            return " ".join(NUMBER_PHONETICS.get(d, d) for d in num_str)
        return num_str
    
    def letters_to_phonetic(self, letters):
        """Convert letters to NATO phonetic"""
        return " ".join(NATO_ALPHABET.get(c.upper(), c) for c in letters)
    
    def generate_callsign(self, difficulty):
        """Generate a realistic callsign for the given difficulty"""
        available = self.callsigns_by_difficulty.get(difficulty, self.callsigns_by_difficulty["easy"])
        if not available:
            available = self.callsigns_by_difficulty["easy"]
        
        format_template = random.choice(available)
        
        if format_template["is_registration_based"]:
            # Generate registration-style callsign
            letters = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=3))
            if format_template["format_pattern"].startswith("N"):
                # US style: N + numbers + letters
                num = random.randint(1, 999)
                callsign = f"N{num}{letters[:2]}"
                phonetic = f"November {self.number_to_phonetic(num)} {self.letters_to_phonetic(letters[:2])}"
            else:
                # European style: XX-XXX
                prefix = format_template["format_pattern"].split("-")[0]
                callsign = f"{prefix}-{letters}"
                phonetic = f"{self.letters_to_phonetic(prefix)} {self.letters_to_phonetic(letters)}"
        else:
            # Airline callsign
            flight_num = random.randint(100, 999)
            callsign = f"{format_template['airline_callsign']} {flight_num}"
            phonetic = f"{format_template['airline_callsign']} {self.number_to_phonetic(flight_num)}"
        
        return callsign, phonetic
    
    def generate_runway(self, airport):
        """Generate a runway designator"""
        # Get runways from airport if available
        runways = airport.get("runways_available", "07L/25R, 07R/25L").split(",")
        runway = random.choice(runways).strip()
        # Pick one direction
        if "/" in runway:
            runway = random.choice(runway.split("/")).strip()
        return runway
    
    def runway_to_phonetic(self, runway):
        """Convert runway to phonetic"""
        result = []
        for c in runway:
            if c.isdigit():
                result.append(NUMBER_PHONETICS.get(c, c))
            elif c == "L":
                result.append("left")
            elif c == "R":
                result.append("right")
            elif c == "C":
                result.append("center")
        return " ".join(result)
    
    def generate_altitude(self, difficulty, phase="cruise"):
        """Generate an altitude/flight level"""
        settings = DIFFICULTY_SETTINGS[difficulty]
        
        if phase in ["climb", "cruise", "descent"]:
            # Flight levels
            if difficulty in ["super_easy", "easy"]:
                fl = random.choice([100, 120, 150, 180, 200, 250, 280, 300, 320, 350])
            else:
                fl = random.randint(80, 410)
                fl = (fl // 10) * 10  # Round to nearest 10
            
            return {
                "raw": str(fl * 100),
                "display": f"flight level {fl}",
                "phonetic": f"flight level {self.number_to_phonetic(fl)}",
                "readback": f"FL{fl}",
                "unit": "FL"
            }
        else:
            # Feet (lower altitudes)
            if difficulty in ["super_easy", "easy"]:
                alt = random.choice([2000, 3000, 4000, 5000, 6000])
            else:
                alt = random.randint(15, 90) * 100
            
            return {
                "raw": str(alt),
                "display": f"{alt} feet",
                "phonetic": f"{self.number_to_phonetic(alt)} feet",
                "readback": f"{alt} feet",
                "unit": "feet"
            }
    
    def generate_heading(self):
        """Generate a heading"""
        heading = random.randint(1, 36) * 10
        heading_str = f"{heading:03d}"
        return {
            "raw": heading_str,
            "display": f"heading {heading_str}",
            "phonetic": f"heading {self.number_to_phonetic(heading_str)}",
            "readback": f"heading {heading_str}",
            "unit": "degrees"
        }
    
    def generate_speed(self):
        """Generate a speed instruction"""
        speed = random.choice([160, 180, 200, 210, 220, 230, 250, 280, 300, 320])
        return {
            "raw": str(speed),
            "display": f"speed {speed} knots",
            "phonetic": f"speed {self.number_to_phonetic(speed)} knots",
            "readback": f"speed {speed} knots",
            "unit": "knots"
        }
    
    def generate_frequency(self, position):
        """Generate a frequency for handoff"""
        freqs = FREQUENCIES.get(position, FREQUENCIES["approach"])
        freq = random.choice(freqs)
        return {
            "raw": freq,
            "display": freq,
            "phonetic": freq.replace(".", " decimal "),
            "readback": freq,
            "unit": "MHz"
        }
    
    def generate_squawk(self):
        """Generate a transponder code"""
        code = f"{random.randint(0, 7)}{random.randint(0, 7)}{random.randint(0, 7)}{random.randint(0, 7)}"
        return {
            "raw": code,
            "display": f"squawk {code}",
            "phonetic": f"squawk {self.number_to_phonetic(code)}",
            "readback": f"squawk {code}",
            "unit": None
        }
    
    def generate_taxi_route(self, difficulty):
        """Generate a taxi route"""
        if difficulty == "super_easy":
            num_taxiways = 1
        elif difficulty == "easy":
            num_taxiways = random.randint(1, 2)
        elif difficulty == "medium":
            num_taxiways = random.randint(2, 3)
        else:
            num_taxiways = random.randint(2, 4)
        
        route = random.sample(TAXIWAYS, min(num_taxiways, len(TAXIWAYS)))
        route_str = ", ".join(route)
        return {
            "raw": route_str,
            "display": f"via {route_str}",
            "phonetic": f"via {route_str}",
            "readback": f"via {route_str}",
            "unit": None
        }
    
    def select_subcategory(self, difficulty):
        """Select a subcategory appropriate for difficulty"""
        settings = DIFFICULTY_SETTINGS[difficulty]
        return random.choice(settings["subcategories"])
    
    def get_category_for_subcategory(self, subcategory):
        """Map subcategory to category"""
        mapping = {
            "startup": "ground",
            "pushback": "ground",
            "taxi": "ground",
            "hold_short": "ground",
            "line_up": "departure",
            "takeoff_clearance": "departure",
            "initial_climb": "departure",
            "frequency_change": "enroute",
            "altitude_change": "enroute",
            "heading_assignment": "enroute",
            "speed_control": "enroute",
            "direct_routing": "enroute",
            "approach_clearance": "arrival",
            "landing_clearance": "landing",
            "go_around": "landing",
            "vacate_runway": "landing"
        }
        return mapping.get(subcategory, "enroute")
    
    def get_controller_for_subcategory(self, subcategory):
        """Map subcategory to controller position"""
        mapping = {
            "startup": "clearance",
            "pushback": "ground",
            "taxi": "ground",
            "hold_short": "ground",
            "line_up": "tower",
            "takeoff_clearance": "tower",
            "initial_climb": "tower",
            "frequency_change": "departure",
            "altitude_change": "center",
            "heading_assignment": "approach",
            "speed_control": "approach",
            "direct_routing": "center",
            "approach_clearance": "approach",
            "landing_clearance": "tower",
            "go_around": "tower",
            "vacate_runway": "tower"
        }
        return mapping.get(subcategory, "tower")
    
    def get_flight_phase(self, subcategory):
        """Map subcategory to flight phase"""
        mapping = {
            "startup": "preflight",
            "pushback": "preflight",
            "taxi": "taxi_out",
            "hold_short": "taxi_out",
            "line_up": "departure",
            "takeoff_clearance": "departure",
            "initial_climb": "climb",
            "frequency_change": "cruise",
            "altitude_change": "cruise",
            "heading_assignment": "approach",
            "speed_control": "approach",
            "direct_routing": "cruise",
            "approach_clearance": "approach",
            "landing_clearance": "landing",
            "go_around": "landing",
            "vacate_runway": "taxi_in"
        }
        return mapping.get(subcategory, "cruise")
    
    def build_instruction(self, instr_type_code, value_data, sequence, instruction_type_record):
        """Build an instruction record"""
        return {
            "instruction_type": instruction_type_record["id"],
            "sequence": sequence,
            "raw_value": value_data["raw"],
            "display_text": value_data["display"],
            "phonetic_text": value_data["phonetic"],
            "readback_text": value_data["readback"],
            "unit": value_data.get("unit"),
            "is_conditional": False,
            "condition_text": None
        }
    
    def generate_radiocall(self, difficulty):
        """Generate a complete radiocall with all related data"""
        settings = DIFFICULTY_SETTINGS[difficulty]
        
        # Select airport and subcategory
        airport = random.choice(self.airports)
        subcategory = self.select_subcategory(difficulty)
        category = self.get_category_for_subcategory(subcategory)
        controller = self.get_controller_for_subcategory(subcategory)
        flight_phase = self.get_flight_phase(subcategory)
        
        # Generate callsign
        callsign, callsign_phonetic = self.generate_callsign(difficulty)
        
        # Determine number of instructions
        min_instr, max_instr = settings["instructions_per_call"]
        num_instructions = random.randint(min_instr, max_instr)
        
        # Build instructions based on subcategory
        instructions = []
        transmission_parts = [f"{callsign},"]
        readback_parts = []
        critical_elements = []
        
        sequence = 1
        runway = self.generate_runway(airport)
        
        # Generate instructions based on subcategory
        if subcategory == "taxi":
            # Taxi instruction
            route = self.generate_taxi_route(difficulty)
            it = self.instruction_type_map.get("taxi_instruction")
            if it:
                instructions.append(self.build_instruction("taxi_instruction", route, sequence, it))
                transmission_parts.append(f"taxi to holding point runway {runway} {route['display']}")
                readback_parts.append(f"Taxi holding point runway {runway} {route['readback']}")
                sequence += 1
            
            # Maybe add hold short
            if num_instructions > 1:
                it = self.instruction_type_map.get("hold_short")
                if it:
                    hold_data = {
                        "raw": runway,
                        "display": f"hold short runway {runway}",
                        "phonetic": f"hold short runway {self.runway_to_phonetic(runway)}",
                        "readback": f"hold short runway {runway}"
                    }
                    instructions.append(self.build_instruction("hold_short", hold_data, sequence, it))
                    critical_elements.append("hold_short")
                    sequence += 1
        
        elif subcategory == "takeoff_clearance":
            # Wind info (no readback)
            wind_dir = random.randint(1, 36) * 10
            wind_spd = random.randint(3, 20)
            transmission_parts.append(f"wind {wind_dir:03d} degrees {wind_spd} knots,")
            
            # Runway
            it = self.instruction_type_map.get("runway_assignment")
            if it:
                rwy_data = {
                    "raw": runway,
                    "display": f"runway {runway}",
                    "phonetic": f"runway {self.runway_to_phonetic(runway)}",
                    "readback": f"runway {runway}"
                }
                instructions.append(self.build_instruction("runway_assignment", rwy_data, sequence, it))
                transmission_parts.append(f"runway {runway},")
                readback_parts.append(f"runway {runway}")
                critical_elements.append("runway_assignment")
                sequence += 1
            
            # Cleared for takeoff
            it = self.instruction_type_map.get("takeoff_clearance")
            if it:
                to_data = {
                    "raw": "cleared_takeoff",
                    "display": "cleared for takeoff",
                    "phonetic": "cleared for takeoff",
                    "readback": "cleared for takeoff"
                }
                instructions.append(self.build_instruction("takeoff_clearance", to_data, sequence, it))
                transmission_parts.append("cleared for takeoff")
                readback_parts.insert(0, "Cleared for takeoff")
                critical_elements.append("takeoff_clearance")
                sequence += 1
        
        elif subcategory == "landing_clearance":
            # Wind info
            wind_dir = random.randint(1, 36) * 10
            wind_spd = random.randint(3, 20)
            transmission_parts.append(f"wind {wind_dir:03d} degrees {wind_spd} knots,")
            
            # Runway
            it = self.instruction_type_map.get("runway_assignment")
            if it:
                rwy_data = {
                    "raw": runway,
                    "display": f"runway {runway}",
                    "phonetic": f"runway {self.runway_to_phonetic(runway)}",
                    "readback": f"runway {runway}"
                }
                instructions.append(self.build_instruction("runway_assignment", rwy_data, sequence, it))
                transmission_parts.append(f"runway {runway},")
                readback_parts.append(f"runway {runway}")
                critical_elements.append("runway_assignment")
                sequence += 1
            
            # Cleared to land
            it = self.instruction_type_map.get("landing_clearance")
            if it:
                land_data = {
                    "raw": "cleared_land",
                    "display": "cleared to land",
                    "phonetic": "cleared to land",
                    "readback": "cleared to land"
                }
                instructions.append(self.build_instruction("landing_clearance", land_data, sequence, it))
                transmission_parts.append("cleared to land")
                readback_parts.insert(0, "Cleared to land")
                critical_elements.append("landing_clearance")
                sequence += 1
        
        elif subcategory == "altitude_change":
            alt = self.generate_altitude(difficulty, "cruise")
            action = random.choice(["climb and maintain", "descend and maintain"])
            it = self.instruction_type_map.get("altitude_assignment")
            if it:
                alt_data = {
                    "raw": alt["raw"],
                    "display": f"{action} {alt['display']}",
                    "phonetic": f"{action} {alt['phonetic']}",
                    "readback": f"{action.split()[0]} {alt['readback']}"
                }
                instructions.append(self.build_instruction("altitude_assignment", alt_data, sequence, it))
                transmission_parts.append(alt_data["display"])
                readback_parts.append(alt_data["readback"])
                critical_elements.append("altitude_assignment")
                sequence += 1
            
            # Maybe add speed
            if num_instructions > 1 and random.random() > 0.5:
                speed = self.generate_speed()
                it = self.instruction_type_map.get("speed_assignment")
                if it:
                    instructions.append(self.build_instruction("speed_assignment", speed, sequence, it))
                    transmission_parts.append(speed["display"])
                    readback_parts.append(speed["readback"])
                    critical_elements.append("speed_assignment")
                    sequence += 1
        
        elif subcategory == "heading_assignment":
            direction = random.choice(["turn left", "turn right"])
            heading = self.generate_heading()
            it = self.instruction_type_map.get("heading_assignment")
            if it:
                hdg_data = {
                    "raw": heading["raw"],
                    "display": f"{direction} {heading['display']}",
                    "phonetic": f"{direction} {heading['phonetic']}",
                    "readback": f"{direction} {heading['readback']}"
                }
                instructions.append(self.build_instruction("heading_assignment", hdg_data, sequence, it))
                transmission_parts.append(hdg_data["display"])
                readback_parts.append(hdg_data["readback"])
                critical_elements.append("heading_assignment")
                sequence += 1
        
        elif subcategory == "frequency_change":
            next_pos = random.choice(["approach", "departure", "center", "tower"])
            freq = self.generate_frequency(next_pos)
            it = self.instruction_type_map.get("frequency_change")
            if it:
                freq_data = {
                    "raw": freq["raw"],
                    "display": f"contact {next_pos} {freq['display']}",
                    "phonetic": f"contact {next_pos} {freq['phonetic']}",
                    "readback": f"{next_pos} {freq['readback']}"
                }
                instructions.append(self.build_instruction("frequency_change", freq_data, sequence, it))
                transmission_parts.append(freq_data["display"])
                readback_parts.append(freq_data["readback"])
                critical_elements.append("frequency_change")
                sequence += 1
        
        elif subcategory == "approach_clearance":
            approach = random.choice(APPROACH_TYPES)
            it = self.instruction_type_map.get("approach_clearance")
            if it:
                app_data = {
                    "raw": f"{approach['code']}_{runway}",
                    "display": f"cleared {approach['display']} approach runway {runway}",
                    "phonetic": f"cleared {approach['phonetic']} approach runway {self.runway_to_phonetic(runway)}",
                    "readback": f"cleared {approach['display']} approach runway {runway}"
                }
                instructions.append(self.build_instruction("approach_clearance", app_data, sequence, it))
                transmission_parts.append(app_data["display"])
                readback_parts.append(app_data["readback"])
                critical_elements.append("approach_clearance")
                critical_elements.append("runway_assignment")
                sequence += 1
        
        elif subcategory == "hold_short":
            it = self.instruction_type_map.get("hold_short")
            if it:
                hold_data = {
                    "raw": runway,
                    "display": f"hold short runway {runway}",
                    "phonetic": f"hold short runway {self.runway_to_phonetic(runway)}",
                    "readback": f"hold short runway {runway}"
                }
                instructions.append(self.build_instruction("hold_short", hold_data, sequence, it))
                transmission_parts.append(hold_data["display"])
                readback_parts.append(f"Hold short runway {runway}")
                critical_elements.append("hold_short")
                sequence += 1
        
        elif subcategory == "line_up":
            it = self.instruction_type_map.get("line_up")
            if it:
                lineup_data = {
                    "raw": runway,
                    "display": f"line up and wait runway {runway}",
                    "phonetic": f"line up and wait runway {self.runway_to_phonetic(runway)}",
                    "readback": f"lining up runway {runway}"
                }
                instructions.append(self.build_instruction("line_up", lineup_data, sequence, it))
                transmission_parts.append(lineup_data["display"])
                readback_parts.append(f"Lining up runway {runway}")
                critical_elements.append("line_up")
                sequence += 1
        
        else:
            # Generic altitude/heading combo for other subcategories
            alt = self.generate_altitude(difficulty, "cruise")
            it = self.instruction_type_map.get("altitude_assignment")
            if it:
                instructions.append(self.build_instruction("altitude_assignment", alt, sequence, it))
                transmission_parts.append(alt["display"])
                readback_parts.append(alt["readback"])
                critical_elements.append("altitude_assignment")
                sequence += 1
        
        # If no instructions generated, skip this one
        if not instructions:
            return None
        
        # Build full transmission and expected readback
        full_transmission = " ".join(transmission_parts)
        expected_readback = ", ".join(readback_parts) + f", {callsign}"
        
        # Build main radiocall record
        radiocall = {
            "airport": airport["id"],
            "category": category,
            "subcategory": subcategory,
            "difficulty": difficulty,
            "flight_phase": flight_phase,
            "controller_position": controller,
            "aircraft_callsign": callsign,
            "callsign_phonetic": callsign_phonetic,
            "full_transmission": full_transmission,
            "expected_readback": expected_readback,
            "critical_elements": critical_elements,
            "instruction_count": len(instructions),
            "has_conditional": False,
            "is_amendment": False,
            "notes": None
        }
        
        # Build acceptable variations
        variations = []
        # Alternative: different word order
        if len(readback_parts) > 1:
            alt_readback = f"{callsign}, " + ", ".join(reversed(readback_parts))
            variations.append({
                "variation_text": alt_readback,
                "notes": "Callsign first, reversed order"
            })
        
        # Build common errors based on instruction types
        errors = []
        for instr in instructions:
            instr_type = None
            for it in self.instruction_types:
                if it["id"] == instr["instruction_type"]:
                    instr_type = it
                    break
            
            if instr_type and instr_type["code"] in COMMON_ERRORS:
                for err_template in COMMON_ERRORS[instr_type["code"]][:1]:  # Just first error
                    errors.append({
                        "error_code": err_template["error_code"],
                        "description": err_template["description"],
                        "example": err_template.get("example", ""),
                        "severity": err_template["severity"],
                        "feedback_text": err_template.get("feedback_text", "")
                    })
        
        return {
            "radiocall": radiocall,
            "instructions": instructions,
            "variations": variations,
            "errors": errors
        }
