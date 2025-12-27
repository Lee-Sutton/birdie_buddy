import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import Page, expect

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def authenticated_client(client, user):
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture()
def authenticated_page(page: Page, live_server, user):
    """Create an authenticated Playwright page instance."""
    # Go to login page
    page.goto(f"{live_server.url}/users/login/")

    # Fill login form
    page.get_by_label("Username").fill("testuser")
    page.get_by_label("Password").fill("testpass123")

    # Submit form
    page.get_by_role("button", name="Log In").click()

    # Wait for navigation to complete
    page.wait_for_url(f"{live_server.url}/**")
    expect(page.get_by_text("Dashboard")).to_be_visible()

    return page
