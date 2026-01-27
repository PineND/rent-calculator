#!/usr/bin/env python3
"""Flexible Rent Calculator"""

from helpers import config
from helpers.config import load_config, get_tenant_names
from helpers.calculator import calculate_rents
from helpers.display import render_table, print_help, print_session_edits, print_error, print_separator, print_config
from helpers.commands import parse_command

RENDER_ACTIONS = {"reset", "refresh", "target", "rate", "room", "tenant", "fixed"}


class State:
    def __init__(self):
        self.tenant_names = get_tenant_names()
        self.session_adj = {}
        self.rate_adj = {}
        self.room_adj = {}
        self.fixed_rents = {}
        self.target_adj = 0

    def reset(self):
        self.session_adj = {}
        self.rate_adj = {}
        self.room_adj = {}
        self.fixed_rents = {}
        self.target_adj = 0

    def refresh(self):
        load_config()
        self.tenant_names = get_tenant_names()
        self.reset()

    def render(self):
        data = calculate_rents(self.session_adj, self.rate_adj, self.room_adj, self.target_adj, self.fixed_rents)
        render_table(data)


def process_action(action, state):
    """Process single action. Returns True to exit program."""
    match action[0]:
        case "exit":
            return True
        case "reset":
            state.reset()
        case "refresh":
            state.refresh()
        case "help":
            print_help()
        case "view":
            if action[1] == "config":
                print_config(config)
            elif action[1] == "rent":
                state.render()
        case "target":
            state.target_adj += action[1]
        case "rate":
            room_type, amount = action[1], action[2]
            state.rate_adj[room_type] = state.rate_adj.get(room_type, 0) + amount
            if state.rate_adj[room_type] == 0:
                del state.rate_adj[room_type]
        case "room":
            room_num, amount = action[1], action[2]
            state.room_adj[room_num] = state.room_adj.get(room_num, 0) + amount
            if state.room_adj[room_num] == 0:
                del state.room_adj[room_num]
        case "tenant":
            name, amount = action[1], action[2]
            state.session_adj[name] = state.session_adj.get(name, 0) + amount
            if state.session_adj[name] == 0:
                del state.session_adj[name]
        case "fixed":
            name, amount = action[1], action[2]
            state.fixed_rents[name] = amount
            # Remove from session_adj if exists
            if name in state.session_adj:
                del state.session_adj[name]
    return False


def main():
    state = State()
    state.render()

    while True:
        print()
        print_session_edits(state.target_adj, state.rate_adj, state.room_adj, state.session_adj, state.fixed_rents)

        try:
            cmd = input("Command: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        # Parse comma-separated commands
        commands = [c.strip() for c in cmd.split(",")]
        actions = [parse_command(c, state.tenant_names) for c in commands]
        actions = [a for a in actions if a is not None]

        if not actions:
            continue

        # Check for errors
        errors = [a for a in actions if a[0] == "error"]
        if errors:
            for e in errors:
                print_error(e[1])
            continue

        # Process actions
        for action in actions:
            if process_action(action, state):
                return

        # Render if any action modified state
        if any(a[0] in RENDER_ACTIONS for a in actions):
            print_separator()
            state.render()


if __name__ == "__main__":
    main()
