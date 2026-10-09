from campusflow.tickets import ValidationError, create_ticket


def create_ticket_menu(tickets):
    """Ask the user for ticket details and create the ticket."""
    try:
        ticket = create_ticket(
            tickets,
            input("Title: "),
            input("Category (Network/Hardware/Software/Other): "),
            input("Urgency (low/medium/high): "),
            input("Affected users: "),
        )
        print(f"Created {ticket['id']} with priority {ticket['priority']}.")
    except ValidationError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    # Temporary test run. Engineer B or the team replaces this with the real menu.
    tickets = []
    create_ticket_menu(tickets)
    print(tickets)