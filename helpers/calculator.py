"""Pure calculation logic for rent computations."""

from . import config


def calculate_rents(session_adj=None, rate_adj=None, room_adj=None, target_adj=0):
    """Calculate all rent data and return as dict."""
    if session_adj is None:
        session_adj = {}
    if rate_adj is None:
        rate_adj = {}
    if room_adj is None:
        room_adj = {}

    rents = []
    for room_num, name in config.TENANTS:
        room_type = config.ROOM_TYPES[room_num]
        base = config.ROOM_RATES[room_type]
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
        })

    target_semester = config.TARGET_SEMESTER_INCOME + target_adj
    target_monthly = target_semester / config.MONTHS_PER_SEMESTER

    total_monthly = sum(r["monthly"] for r in rents)
    total_semester = total_monthly * config.MONTHS_PER_SEMESTER
    semester_diff = total_semester - target_semester
    multiplier = target_monthly / total_monthly if total_monthly else 1

    # Add computed fields
    for r in rents:
        r["suggested"] = r["monthly"] * multiplier
        r["delta"] = (r["suggested"] - r["base"]) * config.MONTHS_PER_SEMESTER
        r["semester"] = r["suggested"] * config.MONTHS_PER_SEMESTER

    return {
        "rents": rents,
        "target_semester": target_semester,
        "target_monthly": target_monthly,
        "total_monthly": total_monthly,
        "total_semester": total_semester,
        "semester_diff": semester_diff,
        "target_adj": target_adj,
    }
