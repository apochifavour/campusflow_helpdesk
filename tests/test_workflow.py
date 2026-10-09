import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    WorkflowError,
    assign_ticket,
    start_ticket,
    resolve_ticket,
    reopen_ticket,
    get_queue,
    generate_report,
)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi failure", "Network", "high", 15)
        create_ticket(self.tickets, "Broken mouse", "Hardware", "low", 1)
        create_ticket(self.tickets, "App error", "Software", "medium", 4)

    def test_assign_ticket(self):
        ticket = assign_ticket(self.tickets, "T001", "Ada")
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_blank_assignee_rejected(self):
        with self.assertRaises(WorkflowError):
            assign_ticket(self.tickets, "T001", "  ")

    def test_start_requires_assignment(self):
        with self.assertRaises(WorkflowError):
            start_ticket(self.tickets, "T001")

    def test_start_assigned_ticket(self):
        assign_ticket(self.tickets, "T001", "Ada")
        start_ticket(self.tickets, "T001")
        self.assertEqual(self.tickets[0]["status"], "in_progress")

    def test_resolve_ticket(self):
        assign_ticket(self.tickets, "T001", "Ada")
        start_ticket(self.tickets, "T001")
        resolve_ticket(self.tickets, "T001")
        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_reopen_ticket(self):
        assign_ticket(self.tickets, "T001", "Ada")
        start_ticket(self.tickets, "T001")
        resolve_ticket(self.tickets, "T001")
        reopen_ticket(self.tickets, "T001")
        self.assertEqual(self.tickets[0]["status"], "open")

    def test_resolved_ticket_not_in_queue(self):
        assign_ticket(self.tickets, "T001", "Ada")
        start_ticket(self.tickets, "T001")
        resolve_ticket(self.tickets, "T001")
        queue_ids = [ticket["id"] for ticket in get_queue(self.tickets)]
        self.assertNotIn("T001", queue_ids)

    def test_queue_priority_order(self):
        queue = get_queue(self.tickets)
        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T001", "T003", "T002"],
        )

    def test_report_counts(self):
        report = generate_report(self.tickets)
        self.assertEqual(report["total"], 3)
        self.assertEqual(report["by_status"]["open"], 3)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["assigned"], 0)
        self.assertEqual(report["unassigned"], 3)

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(WorkflowError):
            assign_ticket(self.tickets, "T999", "Ada")


if __name__ == "__main__":
    unittest.main()
