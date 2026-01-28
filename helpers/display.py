"""Display logic using rich tables."""

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def render_table(data):
    """Render the rent table from calculated data."""
    table = Table(show_header=True, header_style="bold", box=box.SIMPLE, expand=False)
    table.add_column("Room", justify="right")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Base", justify="right")
    table.add_column("Adj", justify="right")
    table.add_column("Monthly", justify="right")
    table.add_column("Semester", justify="right")
    table.add_column("Sem Delta", justify="right")
    table.add_column("Suggested", justify="right")

    for r in data["rents"]:
        if r["fixed"]:
            adj_str = "[dim]Fixed[/dim]"
            suggested_display = "[dim][fixed][/dim]"
            base_display = f"[bold]${r['base']}[/bold]"
        else:
            adj_str = f"{r['adj']:+d}" if r['adj'] else "0"
            suggested_display = f"${r['suggested']:.2f}"
            base_display = f"${r['base']}"
        table.add_row(
            str(r["room"]),
            r["name"],
            r["type"],
            base_display,
            adj_str,
            f"${r['monthly']}",
            f"${r['semester']:.2f}",
            f"${r['delta']:+.2f}",
            suggested_display,
        )

    # Summary rows
    table.add_section()
    table.add_row(
        "", "", "", "", "TOTAL",
        f"${data['total_monthly']}",
        f"${data['total_semester']:.2f}",
        "",
        f"${data['suggested_monthly']:.2f}",
        style="bold"
    )

    target_label = f"TARGET ({data['target_adj']:+d})" if data['target_adj'] else "TARGET"
    table.add_row("", "", "", "", target_label, "", f"${data['target_semester']:.2f}", "", "")

    above_value = data['total_semester'] - data['target_semester']
    above_style = "green" if above_value >= 0 else "red"
    above_label = "ABOVE" if above_value >= 0 else "BELOW"
    table.add_row(
        "", "", "", "", above_label,
        "",
        f"${above_value:+.2f}",
        "", "",
        style=above_style,
        end_section=True
    )

    console.print(table)

    # Show warning if fixed rents exceed target
    if data.get("fixed_exceeds_target"):
        console.print("[bold red]Warning: Fixed rents exceed target! Suggested rents may be inaccurate.[/bold red]")


def print_help():
    """Print help commands."""
    console.print("[yellow]Commands:[/yellow]")
    console.print("  [dim]<name> <+/-amount>[/dim]   Adjust person's rent (e.g. pine +50)")
    console.print("  [dim]<name> =<amount>[/dim]     Fix person's rent (e.g. pine =800)")
    console.print("  [dim]single/double <+/-n>[/dim] Adjust room type rate (e.g. double +20)")
    console.print("  [dim]room <n> <+/-amount>[/dim] Adjust specific room (e.g. room 1 +100)")
    console.print("  [dim]target <+/-amount>[/dim]   Adjust semester target")
    console.print("  [dim]view <rent|config>[/dim]   Show rent table or config")
    console.print("  [dim]reset[/dim]                Clear all session edits")
    console.print("  [dim]refresh[/dim]              Reload config.yaml")
    console.print("  [dim]exit[/dim]                 Quit")


def print_config(cfg):
    """Print current configuration."""
    console.print("[yellow]Current Config:[/yellow]")
    console.print(f"  Target Semester Income: ${cfg.TARGET_SEMESTER_INCOME}")
    console.print(f"  Months per Semester: {cfg.MONTHS_PER_SEMESTER}")
    console.print(f"  Standard Rates:")
    for room_type, rate in cfg.STANDARD_RATES.items():
        console.print(f"    {room_type}: ${rate}")
    console.print(f"  Rooms:")
    for room_num, room_type in cfg.ROOM_TYPES.items():
        if room_num in cfg.CUSTOM_RATES:
            console.print(f"    {room_num}: {room_type} (${cfg.CUSTOM_RATES[room_num]})")
        else:
            console.print(f"    {room_num}: {room_type}")
    console.print(f"  Tenants:")
    for room_num, name in cfg.TENANTS:
        console.print(f"    Room {room_num}: {name}")


def print_session_edits(target_adj, rate_adj, room_adj, session_adj, fixed_rents=None):
    """Print current session edits."""
    if fixed_rents is None:
        fixed_rents = {}
    changes = []
    if target_adj:
        changes.append(f"target {target_adj:+d}")
    if rate_adj:
        changes += [f"{k} {v:+d}" for k, v in rate_adj.items()]
    if room_adj:
        changes += [f"room {k} {v:+d}" for k, v in room_adj.items()]
    if session_adj:
        changes += [f"{k} {v:+d}" for k, v in session_adj.items()]
    if fixed_rents:
        changes += [f"{k} ={v}" for k, v in fixed_rents.items()]
    if changes:
        console.print(f"[dim]Session edits: {', '.join(changes)}[/dim]")
    console.print("[dim]Type 'help' for commands[/dim]")


def print_error(msg):
    """Print error message."""
    console.print(f"[red]{msg}[/red]")


def print_separator():
    """Print section separator."""
    console.print("\n" + "=" * 60)
