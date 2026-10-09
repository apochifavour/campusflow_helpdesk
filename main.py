# CampusFlow ticket assignment feature
"""CampusFlow command-line helpdesk application."""

import json
from pathlib import Path

from campusflow.tickets import ValidationError, create_ticket
from campusflow.workflow import (
    WorkflowError,
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    get_queue,
    generate_report,
)

DATA_FILE = Path("data/tickets.json")


def load_tickets():
    """Load saved tickets, or start with an empty list."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
        if not isinstance(tickets, list):
            raise ValueError("Saved ticket data must be a list.")
        return tickets
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Could not load saved tickets: {error}")
        return []


def save_tickets(tickets):
    """Save tickets to a JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=2)


def show_ticket(ticket):
    """Display the details of one ticket."""
    print(f"\nID: {ticket['id']}")
    print(f"Title: {ticket['title']}")
    print(f"Category: {ticket['category']}")
    print(f"Urgency: {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority: {ticket['priority']}")
    print(f"Status: {ticket['status']}")
    print(f"Assigned to: {ticket['assigned_to'] or 'Unassigned'}")


def create_ticket_menu(tickets):
    try:
        ticket = create_ticket(
            tickets,
            input("Title: "),
            input("Category (Network/Hardware/Software/Other): "),
            input("Urgency (low/medium/high): "),
            input("Affected users: "),
        )
        save_tickets(tickets)
        print(f"Created {ticket['id']} with priority {ticket['priority']}.")
    except ValidationError as error:
        print(f"Error: {error}")


def list_tickets(tickets):
    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        show_ticket(ticket)


def get_ticket_id():
    return input("Ticket ID (e.g. T001): ").strip().upper()


def assignment_menu(tickets):
    try:
        ticket_id = get_ticket_id()
        assignee = input("Assign to: ")
        ticket = assign_ticket(tickets, ticket_id, assignee)
        save_tickets(tickets)
        print(f"{ticket['id']} assigned to {ticket['assigned_to']}.")
    except WorkflowError as error:
        print(f"Error: {error}")


def workflow_menu(tickets, action):
    try:
        ticket_id = get_ticket_id()

        if action == "start":
            ticket = start_ticket(tickets, ticket_id)
        elif action == "resolve":
            ticket = resolve_ticket(tickets, ticket_id)
        else:
            ticket = reopen_ticket(tickets, ticket_id)

        save_tickets(tickets)
        print(f"{ticket['id']} status is now {ticket['status']}.")
    except WorkflowError as error:
        print(f"Error: {error}")


def show_queue(tickets):
    queue = get_queue(tickets)

    if not queue:
        print("The queue is empty.")
        return

    print("\n--- Unresolved Ticket Queue ---")
    for ticket in queue:
        print(
            f"{ticket['id']} | {ticket['priority'].upper()} | "
            f"{ticket['status']} | {ticket['title']}"
        )


def show_report(tickets):
    report = generate_report(tickets)

    print("\n--- Helpdesk Report ---")
    print(f"Total tickets: {report['total']}")
    print(f"Assigned: {report['assigned']}")
    print(f"Unassigned: {report['unassigned']}")

    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")


def main():
    tickets = load_tickets()

    while True:
        print(
            "\n=== CampusFlow Helpdesk ===\n"
            "1. Create ticket\n"
            "2. List tickets\n"
            "3. Assign ticket\n"
            "4. Start ticket\n"
            "5. Resolve ticket\n"
            "6. Reopen ticket\n"
            "7. View unresolved queue\n"
            "8. View report\n"
            "9. Exit"
        )

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_ticket_menu(tickets)
        elif choice == "2":
            list_tickets(tickets)
        elif choice == "3":
            assignment_menu(tickets)
        elif choice == "4":
            workflow_menu(tickets, "start")
        elif choice == "5":
            workflow_menu(tickets, "resolve")
        elif choice == "6":
            workflow_menu(tickets, "reopen")
        elif choice == "7":
            show_queue(tickets)
        elif choice == "8":
            show_report(tickets)
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
