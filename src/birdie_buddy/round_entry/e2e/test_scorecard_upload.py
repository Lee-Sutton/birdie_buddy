import os
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import Page

from birdie_buddy.round_entry.services.scorecard_parser_service import (
    ScorecardData,
    HoleData,
    ShotData,
)
from birdie_buddy.round_entry.models import Hole, Round

User = get_user_model()

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"


@pytest.fixture
def scorecard_image_path():
    """Return the path to the test scorecard image."""
    test_dir = Path(__file__).parent
    return test_dir / "images" / "scorecard.jpg"


@pytest.fixture
def mock_scorecard_parser():
    """Mock the Claude API call to avoid costs during e2e tests."""
    mock_scorecard_data = ScorecardData(
        holes=[
            HoleData(
                number=1,
                par=4,
                score=5,
                shots=[
                    ShotData(number=1, start_distance=380, lie="tee"),
                    ShotData(number=2, start_distance=150, lie="fairway"),
                    ShotData(number=3, start_distance=25, lie="green"),
                    ShotData(number=4, start_distance=8, lie="green"),
                    ShotData(number=5, start_distance=2, lie="green"),
                ],
            ),
            HoleData(
                number=2,
                par=3,
                score=4,
                shots=[
                    ShotData(number=1, start_distance=165, lie="tee"),
                    ShotData(number=2, start_distance=20, lie="rough"),
                    ShotData(number=3, start_distance=12, lie="green"),
                    ShotData(number=4, start_distance=3, lie="green"),
                ],
            ),
        ]
    )

    # Mock raw JSON that would be returned from Claude
    mock_raw_json = {
        "holes": [
            {
                "number": 1,
                "par": 4,
                "shots": [
                    {"number": 1, "start_distance": 380, "lie": "tee"},
                    {"number": 2, "start_distance": 150, "lie": "fairway"},
                    {"number": 3, "start_distance": 25, "lie": "green"},
                    {"number": 4, "start_distance": 8, "lie": "green"},
                    {"number": 5, "start_distance": 2, "lie": "green"},
                ],
            },
            {
                "number": 2,
                "par": 3,
                "shots": [
                    {"number": 1, "start_distance": 165, "lie": "tee"},
                    {"number": 2, "start_distance": 20, "lie": "rough"},
                    {"number": 3, "start_distance": 12, "lie": "green"},
                    {"number": 4, "start_distance": 3, "lie": "green"},
                ],
            },
        ]
    }

    # Mock where the class is instantiated and used, not where it's defined
    with patch(
        "birdie_buddy.round_entry.services.scorecard_parser_service.ScorecardParserService.parse_scorecard_image"
    ) as mock:
        mock.return_value = (mock_scorecard_data, mock_raw_json)
        yield mock


def test_scorecard_upload_page_loads(
    authenticated_page: Page,
    live_server,
    mock_scorecard_parser,
    user,
    scorecard_image_path,
):
    """Test that the scorecard upload page loads correctly for authenticated users."""
    # Go to rounds list page (assuming this is where upload functionality is)
    authenticated_page.set_default_timeout(3000)
    url = reverse("round_entry:round_list")
    authenticated_page.goto(f"{live_server.url}/{url}")
    authenticated_page.get_by_role("button", name="Create New").click()
    authenticated_page.get_by_role("menuitem", name="Upload scorecard").click()

    authenticated_page.get_by_role("textbox", name="Course name").fill("sunshine coast")

    # Upload the file - use element_handle to bypass Playwright's actionability checks
    # The input is hidden with class="hidden" which Playwright won't interact with normally
    element_handle = authenticated_page.query_selector("input[name='scorecard_image']")
    element_handle.set_input_files(str(scorecard_image_path))

    authenticated_page.get_by_role("button", name="Upload").click()

    # Wait for the upload to process (the loading overlay should appear and disappear)
    # Or wait for navigation to the review page
    authenticated_page.wait_for_url("**/review", timeout=10000)

    # Verify the mock was called (Claude API was NOT called)
    assert mock_scorecard_parser.called, (
        "Claude API mock was not called - the upload may have failed"
    )


def test_edit_hole_from_scorecard_review_redirects_back(
    authenticated_page: Page,
    live_server,
    mock_scorecard_parser,
    user,
    scorecard_image_path,
):
    """Test that editing a hole from scorecard review returns to scorecard review."""
    authenticated_page.set_default_timeout(3000)

    # Navigate to upload and complete upload flow
    url = reverse("round_entry:round_list")
    authenticated_page.goto(f"{live_server.url}/{url}")
    authenticated_page.get_by_role("button", name="Create New").click()
    authenticated_page.get_by_role("menuitem", name="Upload scorecard").click()

    authenticated_page.get_by_role("textbox", name="Course name").fill("Test Course")

    element_handle = authenticated_page.query_selector("input[name='scorecard_image']")
    element_handle.set_input_files(str(scorecard_image_path))

    authenticated_page.get_by_role("button", name="Upload").click()
    authenticated_page.wait_for_url("**/review", timeout=10000)

    # Click edit button on first hole (find by href pattern)
    authenticated_page.locator('a[href*="holes/1/create"]').first.click()

    # Should navigate to hole edit form
    authenticated_page.wait_for_selector("h1:has-text('Hole 1')")

    # Verify URL contains query parameters
    edit_url = authenticated_page.url
    assert "return_to=scorecard_review" in edit_url
    assert "scorecard_upload_id=" in edit_url

    # Edit the hole (change par and score using field IDs to avoid ambiguity)
    authenticated_page.locator("#id_par").fill("5")
    authenticated_page.locator("#id_score").fill("6")
    authenticated_page.locator("#id_mental_scorecard").fill("6")
    authenticated_page.get_by_role("button", name="Add shots").click()

    # Should redirect back to scorecard review page
    authenticated_page.wait_for_url("**/review", timeout=5000)
    final_url = authenticated_page.url

    # Verify we're back at the review page
    assert "/scorecard/" in final_url and "/review" in final_url
    assert "Review Scorecard" in authenticated_page.content()


def test_delete_hole_from_scorecard_review(
    authenticated_page: Page,
    live_server,
    mock_scorecard_parser,
    user,
    scorecard_image_path,
):
    """Test that deleting a hole renumbers remaining holes and updates round."""
    authenticated_page.set_default_timeout(3000)

    # Navigate to upload and complete upload flow
    url = reverse("round_entry:round_list")
    authenticated_page.goto(f"{live_server.url}/{url}")
    authenticated_page.get_by_role("button", name="Create New").click()
    authenticated_page.get_by_role("menuitem", name="Upload scorecard").click()

    authenticated_page.get_by_role("textbox", name="Course name").fill("Test Course")

    element_handle = authenticated_page.query_selector("input[name='scorecard_image']")
    element_handle.set_input_files(str(scorecard_image_path))

    authenticated_page.get_by_role("button", name="Upload").click()
    authenticated_page.wait_for_url("**/review", timeout=10000)

    # Verify 2 holes exist initially
    content_before = authenticated_page.content()
    assert "Hole 1" in content_before
    assert "Hole 2" in content_before

    # Get the round from the database before deletion
    round_obj = Round.objects.get(user=user, course_name="Test Course")
    assert round_obj.holes_played == 2
    assert Hole.objects.filter(round=round_obj).count() == 2

    # Verify initial hole numbers
    holes_before = list(Hole.objects.filter(round=round_obj).order_by("number"))
    assert len(holes_before) == 2
    assert holes_before[0].number == 1
    assert holes_before[1].number == 2

    # Get the ID of the first hole card before deleting
    first_hole_card_id = f"hole-card-{holes_before[0].id}"

    # Set up dialog handler to accept the confirmation
    authenticated_page.on("dialog", lambda dialog: dialog.accept())

    # Click delete button on first hole
    delete_buttons = authenticated_page.locator('button[title="Delete Hole"]')
    delete_buttons.first.click()

    # Wait for the first hole card to be removed from the DOM
    authenticated_page.wait_for_selector(
        f"#{first_hole_card_id}", state="detached", timeout=5000
    )

    # Count hole cards - should only be 1 now
    hole_cards = authenticated_page.locator('[id^="hole-card-"]')
    assert hole_cards.count() == 1, "Should only have 1 hole card remaining"

    # Verify the remaining hole is numbered as "Hole 1" in the card header
    hole_number_display = authenticated_page.locator(
        ".text-2xl.font-bold.text-center.text-gray-900"
    )
    assert hole_number_display.count() == 1, "Should only have 1 hole number display"
    assert hole_number_display.first.inner_text() == "1", (
        "Remaining hole should display number 1"
    )

    # Verify database state
    round_obj.refresh_from_db()

    # Check holes_played was decremented
    assert round_obj.holes_played == 1, "Round holes_played should be decremented to 1"

    # Check only 1 hole remains
    remaining_holes = list(Hole.objects.filter(round=round_obj).order_by("number"))
    assert len(remaining_holes) == 1, "Should only have 1 hole remaining"

    # Check the remaining hole is renumbered to 1 (was originally hole 2)
    assert remaining_holes[0].number == 1, "Remaining hole should be renumbered to 1"

    # Verify it was originally hole 2 (check by par value)
    assert remaining_holes[0].par == 3, (
        "Remaining hole should have par 3 (original hole 2)"
    )

    # Verify round is still complete (1 hole with shots, holes_played=1)
    assert round_obj.complete is True, "Round should still be complete after deletion"
