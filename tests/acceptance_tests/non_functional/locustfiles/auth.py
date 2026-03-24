"""Locust load test scenarios for auth API endpoints."""

import uuid

from locust import HttpUser, between, task


class AuthUser(HttpUser):
    """Simulates a user exercising auth-related API endpoints."""

    wait_time = between(0.1, 0.5)

    @task(3)
    def get_server_info(self) -> None:
        """GET /api/server-info — lightweight health-check style endpoint."""
        self.client.get("/api/server-info")

    @task(1)
    def create_user(self) -> None:
        """POST /api/auth/users — create a unique user per request."""
        unique = uuid.uuid4().hex[:8]
        self.client.post(
            "/api/auth/users",
            json={
                "fullName": f"Load Test User {unique}",
                "email": f"load_{unique}@test.example",
                "password": "loadtestpassword",
            },
        )
