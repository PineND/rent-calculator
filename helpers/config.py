"""Config loading and state management."""

import yaml
from pathlib import Path

TARGET_SEMESTER_INCOME = 0
MONTHS_PER_SEMESTER = 5
STANDARD_RATES = {}
ROOM_TYPES = {}
CUSTOM_RATES = {}
TENANTS = []

config_path = Path(__file__).parent.parent / "config.yaml"


def load_config():
    """Load or reload configuration from config.yaml."""
    global TARGET_SEMESTER_INCOME, MONTHS_PER_SEMESTER, STANDARD_RATES, ROOM_TYPES, CUSTOM_RATES, TENANTS

    with open(config_path) as f:
        config = yaml.safe_load(f)

    TARGET_SEMESTER_INCOME = config["target_semester_income"]
    MONTHS_PER_SEMESTER = config["months_per_semester"]
    STANDARD_RATES = config["standard_rates"]

    # Parse rooms - supports "1: double" or "1: {type: double, custom_rate: 1000}"
    ROOM_TYPES = {}
    CUSTOM_RATES = {}
    for room_num, room_config in config["rooms"].items():
        room_num = int(room_num)
        if isinstance(room_config, str):
            ROOM_TYPES[room_num] = room_config
        else:
            ROOM_TYPES[room_num] = room_config["type"]
            if "custom_rate" in room_config:
                CUSTOM_RATES[room_num] = room_config["custom_rate"]

    TENANTS = []
    for room_num, names in config["tenants"].items():
        for name in names:
            TENANTS.append((int(room_num), name))


def get_tenant_names():
    """Return dict mapping lowercase names to actual names."""
    return {name.lower(): name for _, name in TENANTS}


load_config()
