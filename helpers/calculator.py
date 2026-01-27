"""Pure calculation logic for rent computations."""

import math
from . import config


def calculate_rents(session_adj=None, rate_adj=None, room_adj=None, target_adj=0, fixed_rents=None):
    """Calculate all rent data and return as dict."""
    if session_adj is None:
        session_adj = {}
    if rate_adj is None:
        rate_adj = {}
    if room_adj is None:
        room_adj = {}
    if fixed_rents is None:
        fixed_rents = {}

    rents = []
    for room_num, name in config.TENANTS:
        room_type = config.ROOM_TYPES[room_num]
        # Use custom rate if set, otherwise use room type rate
        base = config.CUSTOM_RATES.get(room_num, config.STANDARD_RATES[room_type])
        is_fixed = name in fixed_rents
        total_adj = (
            session_adj.get(name, 0) +
            rate_adj.get(room_type, 0) +
            room_adj.get(room_num, 0)
        )
        rents.append({
            "room": room_num,
            "name": name,
            "type": room_type,
            "base": base,
            "adj": total_adj,
            "monthly": base + total_adj,
            "fixed": fixed_rents.get(name),
        })

    target_semester = config.TARGET_SEMESTER_INCOME + target_adj
    target_monthly = target_semester / config.MONTHS_PER_SEMESTER

    total_monthly = sum(r["monthly"] for r in rents)
    total_semester = total_monthly * config.MONTHS_PER_SEMESTER
    semester_diff = total_semester - target_semester
    percent_diff = (semester_diff / target_semester * 100) if target_semester else 0

    # Calculate multiplier excluding fixed-rent people
    fixed_monthly = sum(r["fixed"] for r in rents if r["fixed"] is not None)
    adjustable_monthly = sum(r["monthly"] for r in rents if r["fixed"] is None)
    remaining_target = target_monthly - fixed_monthly
    multiplier = remaining_target / adjustable_monthly if adjustable_monthly else 1

    # Add computed fields (suggested rounded up to whole number)
    for r in rents:
        if r["fixed"] is not None:
            r["suggested"] = r["fixed"]
        else:
            r["suggested"] = math.ceil(r["monthly"] * multiplier)
        r["delta"] = (r["suggested"] - r["base"]) * config.MONTHS_PER_SEMESTER
        r["semester"] = r["suggested"] * config.MONTHS_PER_SEMESTER

    # Calculate suggested totals (rounded)
    suggested_monthly = sum(r["suggested"] for r in rents)
    suggested_semester = suggested_monthly * config.MONTHS_PER_SEMESTER
    suggested_above = suggested_semester - target_semester

    return {
        "rents": rents,
        "target_semester": target_semester,
        "target_monthly": target_monthly,
        "total_monthly": total_monthly,
        "total_semester": total_semester,
        "semester_diff": semester_diff,
        "percent_diff": percent_diff,
        "target_adj": target_adj,
        "suggested_monthly": suggested_monthly,
        "suggested_semester": suggested_semester,
        "suggested_above": suggested_above,
    }
