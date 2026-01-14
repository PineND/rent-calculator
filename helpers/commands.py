"""Command parsing logic."""

from . import config


def parse_command(cmd, tenant_names):
    """
    Parse a command string and return action tuple.

    Returns: (action_type, *args) or None if invalid
        - ("exit",)
        - ("reset",)
        - ("refresh",)
        - ("help",)
        - ("target", amount)
        - ("rate", room_type, amount)
        - ("room", room_num, amount)
        - ("tenant", name, amount)
        - ("error", message)
    """
    if not cmd:
        return None

    cmd_lower = cmd.lower()

    if cmd_lower == "exit":
        return ("exit",)

    if cmd_lower == "reset":
        return ("reset",)

    if cmd_lower == "refresh":
        return ("refresh",)

    if cmd_lower == "help":
        return ("help",)

    parts = cmd.split()

    # Handle "view <rent/config>"
    if len(parts) == 2 and parts[0].lower() == "view":
        view_type = parts[1].lower()
        if view_type in ("rent", "config"):
            return ("view", view_type)
        return ("error", "Usage: view <rent|config>")

    # Handle "room N +/-amount" (3 parts)
    if len(parts) == 3 and parts[0].lower() == "room":
        try:
            room_num = int(parts[1])
            amount = int(parts[2])
        except ValueError:
            return ("error", "Invalid room command (e.g. room 1 +100)")
        if room_num not in config.ROOM_TYPES:
            return ("error", f"Unknown room: {room_num}")
        return ("room", room_num, amount)

    # Handle 2-part commands
    if len(parts) != 2:
        return None

    name_input, amount_str = parts
    name_key = name_input.lower()

    try:
        amount = int(amount_str)
    except ValueError:
        return ("error", f"Invalid amount: {amount_str}")

    if name_key == "target":
        return ("target", amount)

    if name_key in config.ROOM_RATES:
        return ("rate", name_key, amount)

    if name_key in tenant_names:
        return ("tenant", tenant_names[name_key], amount)

    return ("error", f"Unknown: {name_input}")
