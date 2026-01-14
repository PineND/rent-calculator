#!/usr/bin/env python3
"""Flexible Rent Calculator"""

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# =============================================================================
# CONFIGURATION
# =============================================================================

TARGET_SEMESTER_INCOME = 48000
MONTHS_PER_SEMESTER = 5

ROOM_RATES = {
    "single": 1100,
    "double": 800,
}

ROOM_TYPES = {
    1: "double",
    2: "double",
    3: "double",
    4: "single",
    5: "double",
    6: "single",
    7: "single",
}

# =============================================================================
# TENANTS: (room_number, name, adjustment)
# =============================================================================

TENANTS = [
    (1, "Thompson", 0),
    (1, "Charles", 0),
    (2, "Manny", 0),
    (3, "Pine", 0),
    (3, "JP", 0),
    (4, "Eddie", 0),
    (5, "Arquime", 0),
    (5, "Nathan", 0),
    (6, "Richard", 0),
    (7, "Alex", 0),
]

# =============================================================================
# CALCULATIONS
# =============================================================================

def generate_report(session_adj=None, rate_adj=None, target_adj=0):
    if session_adj is None:
        session_adj = {}
    if rate_adj is None:
        rate_adj = {}

    rents = []
    for room_num, name, adj in TENANTS:
        room_type = ROOM_TYPES[room_num]
        base = ROOM_RATES[room_type] + rate_adj.get(room_type, 0)
        total_adj = adj + session_adj.get(name, 0)
        rents.append({
            "room": room_num,
            "name": name,
            "type": room_type,
            "base": base,
            "adj": total_adj,
            "monthly": base + total_adj,
        })

    target_semester = TARGET_SEMESTER_INCOME + target_adj
    target_monthly = target_semester / MONTHS_PER_SEMESTER

    total_monthly = sum(r["monthly"] for r in rents)
    total_semester = total_monthly * MONTHS_PER_SEMESTER
    semester_diff = total_semester - target_semester
    percent_diff = (semester_diff / target_semester * 100) if target_semester else 0

    multiplier = target_monthly / total_monthly if total_monthly else 1

    # Build table
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("Room", justify="right")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Base", justify="right")
    table.add_column("Adj", justify="right")
    table.add_column("Monthly", justify="right")
    table.add_column("To Pay", justify="right")
    table.add_column("Semester", justify="right", no_wrap=True)

    for r in rents:
        adj_str = f"{r['adj']:+d}" if r['adj'] else "0"
        adjusted_monthly = r["monthly"] * multiplier
        adj_semester = adjusted_monthly * MONTHS_PER_SEMESTER
        table.add_row(
            str(r["room"]),
            r["name"],
            r["type"],
            f"${r['base']}",
            adj_str,
            f"${r['monthly']}",
            f"${adjusted_monthly:.2f}",
            f"${adj_semester:.2f}",
        )

    # Summary rows
    table.add_section()
    table.add_row("", "", "", "", "TOTAL", f"${total_monthly}", f"${target_monthly:.2f}", f"${total_semester}", style="bold")

    target_label = f"TARGET ({target_adj:+d})" if target_adj else "TARGET"
    table.add_row("", "", "", "", target_label, "", "", f"${target_semester}")

    diff_style = "green" if semester_diff >= 0 else "red"
    diff_text = f"${semester_diff:+.0f} ({percent_diff:+.2f}%)"
    table.add_row("", "", "", "", "DIFF", "", "", diff_text, style=diff_style, end_section=True)

    console.print(table)


def interactive():
    tenant_names = {name.lower(): name for _, name, _ in TENANTS}
    session_adj = {}
    rate_adj = {}
    target_adj = 0

    generate_report(session_adj, rate_adj, target_adj)

    while True:
        print()
        # Show session edits right above Edit prompt
        changes = []
        if target_adj:
            changes.append(f"target {target_adj:+d}")
        if rate_adj:
            changes += [f"{k} {v:+d}" for k, v in rate_adj.items()]
        if session_adj:
            changes += [f"{k} {v:+d}" for k, v in session_adj.items()]
        if changes:
            console.print(f"[dim]Session edits: {', '.join(changes)}[/dim]")

        try:
            cmd = input("Edit: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd.lower() == "exit":
            break

        if cmd.lower() == "reset":
            session_adj = {}
            rate_adj = {}
            target_adj = 0
            console.print("\n" + "=" * 60)
            generate_report(session_adj, rate_adj, target_adj)
            continue

        parts = cmd.split()
        if len(parts) != 2:
            console.print("[yellow]Usage: <name|single|double|target> <+/-amount>  |  reset  |  exit[/yellow]")
            continue

        name_input, amount_str = parts
        name_key = name_input.lower()

        try:
            amount = int(amount_str)
        except ValueError:
            console.print(f"[red]Invalid amount: {amount_str}[/red]")
            continue

        if name_key == "target":
            target_adj += amount
        elif name_key in ("single", "double"):
            rate_adj[name_key] = rate_adj.get(name_key, 0) + amount
            if rate_adj[name_key] == 0:
                del rate_adj[name_key]
        elif name_key in tenant_names:
            actual_name = tenant_names[name_key]
            session_adj[actual_name] = session_adj.get(actual_name, 0) + amount
            if session_adj[actual_name] == 0:
                del session_adj[actual_name]
        else:
            console.print(f"[red]Unknown: {name_input}[/red]")
            continue

        console.print("\n" + "=" * 60)
        generate_report(session_adj, rate_adj, target_adj)


if __name__ == "__main__":
    interactive()
