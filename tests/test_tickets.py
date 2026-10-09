import unittest

from campusflow.tickets import (
    ValidationError,
    calculate_priority,
    create_ticket,
    generate_ticket_id,
)


class TestPriority(unittest.TestCase):
    def test_high_urgency_12_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_urgency_2_users_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_low_urgency_10_users_is_high(self):  # boundary of rule 2
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_low_urgency_4_users_is_medium(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_urgency_1_user_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")


class TestCreateTicket(unittest.TestCase):
    def test_valid_ticket_has_all_fields(self):
        tickets = []
        t = create_ticket(tickets, "Campus Wi-Fi is down", "network", "HIGH", "15")
        self.assertEqual(t["id"], "T001")
        self.assertEqual(t["category"], "Network")
        self.assertEqual(t["urgency"], "high")
        self.assertEqual(t["affected_users"], 15)
        self.assertEqual(t["priority"], "critical")
        self.assertEqual(t["status"], "open")
        self.assertIsNone(t["assigned_to"])
        self.assertEqual(tickets, [t])

    def test_zero_affected_users_rejected(self):
        tickets = []
        with self.assertRaises(ValidationError):
            create_ticket(tickets, "Printer", "Hardware", "low", 0)
        self.assertEqual(tickets, [])  # nothing stored

    def test_invalid_affected_users_rejected(self):
        for bad in (-3, "abc", "2.5", 2.5, None, True, ""):
            with self.subTest(value=bad):
                with self.assertRaises(ValidationError):
                    create_ticket([], "Printer", "Hardware", "low", bad)

    def test_blank_title_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "   ", "Software", "low", 1)

    def test_invalid_category_and_urgency_rejected(self):
        with self.assertRaises(ValidationError):
            create_ticket([], "Broken", "Plumbing", "low", 1)
        with self.assertRaises(ValidationError):
            create_ticket([], "Broken", "Other", "urgent", 1)


class TestIds(unittest.TestCase):
    def test_ids_increment(self):
        tickets = []
        create_ticket(tickets, "A", "Other", "low", 1)
        create_ticket(tickets, "B", "Other", "low", 1)
        self.assertEqual([t["id"] for t in tickets], ["T001", "T002"])

    def test_new_id_after_reload_does_not_duplicate(self):
        reloaded = [{"id": "T001"}, {"id": "T005"}]  # as if loaded from JSON
        self.assertEqual(generate_ticket_id(reloaded), "T006")


if __name__ == "__main__":
    unittest.main()