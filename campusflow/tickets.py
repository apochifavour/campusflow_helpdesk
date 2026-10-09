"""Ticket creation, validation and priority calculation."""

import re

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCY_LEVELS = ("low", "medium", "high")
_ID_PATTERN = re.compile(r"^T(\d+)$")


class ValidationError(ValueError):
    """Raised when ticket input is invalid."""


def validate_title(title):
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Title must not be blank.")
    return title.strip()


def validate_category(category):
    if isinstance(category, str):
        for allowed in CATEGORIES:
            if category.strip().lower() == allowed.lower():
                return allowed  # canonical form, e.g. "network" -> "Network"
    raise ValidationError(
        f"Category must be one of: {', '.join(CATEGORIES)}."
    )


def validate_urgency(urgency):
    if isinstance(urgency, str):
        value = urgency.strip().lower()
        if value in URGENCY_LEVELS:
            return value
    raise ValidationError(
        f"Urgency must be one of: {', '.join(URGENCY_LEVELS)}."
    )


def validate_affected_users(value):
    """Accept a positive whole number, as an int or a digit string."""
    # bool is a subclass of int in Python, so reject it explicitly
    if isinstance(value, bool):
        raise ValidationError("Affected users must be a positive whole number.")
    if isinstance(value, int):
        number = value
    elif isinstance(value, str):
        text = value.strip()
        if not (text.isascii() and text.isdigit()):  # rejects "3.5", "-2", "abc"
            raise ValidationError(
                "Affected users must be a positive whole number."
            )
        number = int(text)
    else:  # floats, None, lists...
        raise ValidationError("Affected users must be a positive whole number.")
    if number < 1:
        raise ValidationError("Affected users must be at least 1.")
    return number


def calculate_priority(urgency, affected_users):
    """Apply the four rules in order; the first match wins."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"


def generate_ticket_id(tickets):
    """Next ID = highest existing numeric ID + 1 (safe after reload)."""
    highest = 0
    for ticket in tickets:
        match = _ID_PATTERN.match(str(ticket.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    # Validate EVERYTHING first so a bad input never changes `tickets`.
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    ticket = {
        "id": generate_ticket_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": calculate_priority(urgency, affected_users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket