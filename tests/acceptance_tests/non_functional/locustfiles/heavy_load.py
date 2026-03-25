"""Locust load test scenarios for auth API endpoints."""

from locust import between
from tests.acceptance_tests.non_functional.locustfiles import normal_load


class AuthUser(normal_load.AuthUser):
    """Simulates a user exercising auth-related API endpoints."""

    wait_time = between(0.02, 0.2)
