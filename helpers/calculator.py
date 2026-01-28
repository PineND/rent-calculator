"""Pure calculation logic for rent computations."""

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
        is_fixed = name in fixed_rents

        if is_fixed:
            # Fixed rent replaces base, no adjustments apply
            base = fixed_rents[name]
            total_adj = 0
            monthly = base
        else:
            # Use custom rate if set, otherwise use room type rate
            base = config.CUSTOM_RATES.get(room_num, config.STANDARD_RATES[room_type])
            total_adj = (
                session_adj.get(name, 0) +
                rate_adj.get(room_type, 0) +
                room_adj.get(room_num, 0)
            )
            monthly = base + total_adj

        rents.append({
            "room": room_num,
            "name": name,
            "type": room_type,
            "base": base,
            "adj": total_adj,
            "monthly": monthly,
            "fixed": is_fixed,
        })

    target_semester = config.TARGET_SEMESTER_INCOME + target_adj
    target_monthly = target_semester / config.MONTHS_PER_SEMESTER

    total_monthly = sum(r["monthly"] for r in rents)
    total_semester = total_monthly * config.MONTHS_PER_SEMESTER
    semester_diff = total_semester - target_semester
    percent_diff = (semester_diff / target_semester * 100) if target_semester else 0

    # Calculate multiplier excluding fixed-rent people
    fixed_monthly = sum(r["monthly"] for r in rents if r["fixed"])
    adjustable_monthly = sum(r["monthly"] for r in rents if not r["fixed"])
    remaining_target = target_monthly - fixed_monthly
    # Ensure multiplier doesn't go negative (when fixed rents exceed target)
    if remaining_target < 0 or adjustable_monthly <= 0:
        multiplier = 1  # Fall back to no scaling
    else:
        multiplier = remaining_target / adjustable_monthly

    # Add computed fields
    for r in rents:
        if r["fixed"]:
            r["suggested"] = None  # Will display as "[fixed]"
            r["delta"] = 0
            r["semester"] = r["monthly"] * config.MONTHS_PER_SEMESTER
        else:
            r["suggested"] = max(0, r["monthly"] * multiplier)
            r["delta"] = (r["suggested"] - r["base"]) * config.MONTHS_PER_SEMESTER
            r["semester"] = r["suggested"] * config.MONTHS_PER_SEMESTER

    # Warning flag when fixed rents exceed target
    fixed_exceeds_target = fixed_monthly > target_monthly

    # Calculate suggested totals
    suggested_monthly = sum(r["suggested"] if r["suggested"] is not None else r["monthly"] for r in rents)
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
        "fixed_exceeds_target": fixed_exceeds_target,
    }
