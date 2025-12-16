from playwright.sync_api import Page, expect
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"


def test_login_flow(page: Page, live_server, user):
    """Test the login flow directly."""
    # Go to login page
    page.goto(f"{live_server.url}/users/login/")

    # Verify login form is present
    expect(page.get_by_label("Username")).to_be_visible()
    expect(page.get_by_label("Password")).to_be_visible()

    # Fill and submit login form
    page.get_by_label("Username").fill("testuser")
    page.get_by_label("Password").fill("testpass123")
    page.get_by_role("button", name="Log In").click()

    # Verify successful login (redirected away from login page)
    expect(page).not_to_have_url(f"{live_server.url}/users/login/")
    expect(page.get_by_text("Dashboard")).to_be_visible()


def test_unauthorized_access_redirects_to_login(page: Page, live_server):
    """Test that unauthenticated users are redirected to login."""
    # Try to access a protected page
    page.goto(f"{live_server.url}/")

    # Should be redirected to login or see login prompt
    # Adjust this assertion based on your app's authentication behavior
    current_url = page.url
    assert "login" in current_url.lower() or page.get_by_text("Log In").is_visible()


def test_signup_flow(page: Page, live_server):
    """Test user registration flow."""
    # Go to signup page
    page.goto(f"{live_server.url}/users/signup/")

    # Fill signup form (adjust field names based on your form)
    page.get_by_label("Username").fill("newuser")
    page.get_by_label("Email").fill("newuser@example.com")
    page.get_by_role("textbox", name="Password", exact=True).fill("newpass123")
    page.get_by_role("textbox", name="Password confirmation").fill("newpass123")

    # Submit form
    page.get_by_role("button", name="Sign up").click()

    # Verify successful registration (redirected or logged in)
    expect(page).not_to_have_url(f"{live_server.url}/users/signup/")
