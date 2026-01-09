# Directus Configuration for Radiocall Generator
# Uses the same backend as ATIS Generator

DIRECTUS_URL = "https://directus.aevoli.org"
DIRECTUS_EMAIL = "niroeth@outlook.com"
DIRECTUS_PASSWORD = "(Doge_420420)"

# Generation Settings
NUM_RADIOCALLS_TO_GENERATE = 500

# Dry Run Mode - Set to True to preview without making changes
DRY_RUN = False

# Difficulty distribution (should sum to 100)
DIFFICULTY_DISTRIBUTION = {
    "super_easy": 20,  # 20% - beginners
    "easy": 30,        # 30% - student pilots
    "medium": 35,      # 35% - PPL/instrument students
    "hard": 15         # 15% - advanced/CPL
}
