#!/usr/bin/env python3
"""Flexible Rent Calculator"""

from helpers import config
from helpers.config import load_config, get_tenant_names
from helpers.calculator import calculate_rents
from helpers.display import render_table, print_help, print_session_edits, print_error, print_separator, print_config
from helpers.commands import parse_command


def main():
    tenant_names = get_tenant_names()
    session_adj = {}
    rate_adj = {}
    room_adj = {}
    target_adj = 0

    # Initial render
    data = calculate_rents(session_adj, rate_adj, room_adj, target_adj)
    render_table(data)

    while True:
        print()
        print_session_edits(target_adj, rate_adj, room_adj, session_adj)

        try:
            cmd = input("Command: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        action = parse_command(cmd, tenant_names)

        if action is None:
            continue

        match action[0]:
            case "exit":
                break

            case "reset":
                session_adj = {}
                rate_adj = {}
                room_adj = {}
                target_adj = 0

            case "refresh":
                load_config()
                tenant_names = get_tenant_names()
                session_adj = {}
                rate_adj = {}
                room_adj = {}
                target_adj = 0

            case "help":
                print_help()
                continue

            case "view":
                if action[1] == "config":
                    print_config(config)
                elif action[1] == "rent":
                    data = calculate_rents(session_adj, rate_adj, room_adj, target_adj)
                    render_table(data)
                continue

            case "error":
                print_error(action[1])
                continue

            case "target":
                target_adj += action[1]

            case "rate":
                room_type, amount = action[1], action[2]
                rate_adj[room_type] = rate_adj.get(room_type, 0) + amount
                if rate_adj[room_type] == 0:
                    del rate_adj[room_type]

            case "room":
                room_num, amount = action[1], action[2]
                room_adj[room_num] = room_adj.get(room_num, 0) + amount
                if room_adj[room_num] == 0:
                    del room_adj[room_num]

            case "tenant":
                name, amount = action[1], action[2]
                session_adj[name] = session_adj.get(name, 0) + amount
                if session_adj[name] == 0:
                    del session_adj[name]

        print_separator()
        data = calculate_rents(session_adj, rate_adj, room_adj, target_adj)
        render_table(data)


if __name__ == "__main__":
    main()
