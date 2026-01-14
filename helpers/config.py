"""Config loading and state management."""

import yaml
from pathlib import Path

TARGET_SEMESTER_INCOME = 0
MONTHS_PER_SEMESTER = 5
ROOM_RATES = {}
ROOM_TYPES = {}
TENANTS = []

config_path = Path(__file__).parent.parent / "config.yaml"


def load_config():
    """Load or reload configuration from config.yaml."""
    global TARGET_SEMESTER_INCOME, MONTHS_PER_SEMESTER, ROOM_RATES, ROOM_TYPES, TENANTS

    with open(config_path) as f:
        config = yaml.safe_load(f)

    TARGET_SEMESTER_INCOME = config["target_semester_income"]
    MONTHS_PER_SEMESTER = config["months_per_semester"]
    ROOM_RATES = config["room_rates"]
    ROOM_TYPES = {int(k): v for k, v in config["rooms"].items()}

    TENANTS = []
    for room_num, names in config["tenants"].items():
        for name in names:
            TENANTS.append((int(room_num), name))


def get_tenant_names():
    """Return dict mapping lowercase names to actual names."""
    return {name.lower(): name for _, name in TENANTS}


load_config()
