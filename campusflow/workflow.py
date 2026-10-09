"""Ticket assignment, workflow, queue management, and reports."""

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

VALID_STATUSES = ("open", "in_progress", "resolved")


class WorkflowError(ValueError):
    """Raised when a ticket workflow operation is invalid."""


def _find_ticket(tickets, ticket_id):
    """Find a ticket by ID or raise an error."""
    for ticket in tickets:
        if ticket.get("id") == ticket_id:
            return ticket
    raise WorkflowError(f"Ticket {ticket_id!r} was not found.")


def assign_ticket(tickets, ticket_id, assignee):
    """Assign an open or in-progress ticket to a staff member."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") == "resolved":
        raise WorkflowError("Cannot assign a resolved ticket. Reopen it first.")

    if not isinstance(assignee, str) or not assignee.strip():
        raise WorkflowError("Assignee must not be blank.")

    ticket["assigned_to"] = assignee.strip()
    return ticket


def start_ticket(tickets, ticket_id):
    """Move an assigned open ticket to in_progress."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") != "open":
        raise WorkflowError("Only open tickets can be started.")

    if not ticket.get("assigned_to"):
        raise WorkflowError("Assign the ticket before starting it.")

    ticket["status"] = "in_progress"
    return ticket


def resolve_ticket(tickets, ticket_id):
    """Resolve a ticket that is currently in progress."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") != "in_progress":
        raise WorkflowError("Only in-progress tickets can be resolved.")

    ticket["status"] = "resolved"
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Explicitly reopen a resolved ticket."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket.get("status") != "resolved":
        raise WorkflowError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"
    return ticket


def get_queue(tickets):
    """Return unresolved tickets by priority, then numeric ticket ID."""
    unresolved = [
        ticket for ticket in tickets
        if ticket.get("status") in ("open", "in_progress")
    ]

    def sort_key(ticket):
        ticket_id = str(ticket.get("id", ""))
        digits = ticket_id[1:] if ticket_id.startswith("T") else ""
        numeric_id = int(digits) if digits.isdigit() else float("inf")

        return (
            PRIORITY_ORDER.get(ticket.get("priority"), 99),
            numeric_id,
        )

    return sorted(unresolved, key=sort_key)


def generate_report(tickets):
    """Summarize tickets by status and priority."""
    status_counts = {status: 0 for status in VALID_STATUSES}
    priority_counts = {priority: 0 for priority in PRIORITY_ORDER}

    assigned = 0

    for ticket in tickets:
        status = ticket.get("status")
        priority = ticket.get("priority")

        if status in status_counts:
            status_counts[status] += 1

        if priority in priority_counts:
            priority_counts[priority] += 1

        if ticket.get("assigned_to"):
            assigned += 1

    return {
        "total": len(tickets),
        "by_status": status_counts,
        "by_priority": priority_counts,
        "assigned": assigned,
        "unassigned": len(tickets) - assigned,
    }
