import unittest
from unittest.mock import patch

import psycopg

from app import app


class DashboardTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("app.connect")
    def test_health_reports_database_connected(self, connect):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok", "database": "connected"})
        connect.return_value.__enter__.return_value.execute.assert_called_once_with("SELECT 1")

    @patch("app.connect")
    def test_department_api_returns_rows(self, connect):
        rows = [{
            "department": "Engineering",
            "employees": 42,
            "target_pct": 91.4,
            "satisfaction_pct": 87.2,
            "open_roles": 12,
        }]
        connect.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = rows
        response = self.client.get("/api/departments")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), rows)

    @patch("app.connect")
    def test_dashboard_renders_summary_and_department(self, connect):
        rows = [{
            "department": "Engineering",
            "employees": 42,
            "target_pct": 91.4,
            "satisfaction_pct": 87.2,
            "open_roles": 12,
        }]
        connect.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = rows
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Department Performance", response.data)
        self.assertIn(b"Engineering", response.data)
        self.assertIn(b"42", response.data)

    @patch("app.connect", side_effect=psycopg.OperationalError("database unavailable"))
    def test_health_returns_service_unavailable_when_database_is_down(self, _connect):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["status"], "error")


if __name__ == "__main__":
    unittest.main()
