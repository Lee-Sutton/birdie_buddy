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

User = get_user_model()

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"


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
    authenticated_page: Page, live_server, mock_scorecard_parser, user
):
    """Test that the scorecard upload page loads correctly for authenticated users."""
    # Go to rounds list page (assuming this is where upload functionality is)
    authenticated_page.set_default_timeout(3000)
    url = reverse("round_entry:round_list")
    authenticated_page.goto(f"{live_server.url}/{url}")
    authenticated_page.get_by_role("button", name="Create New").click()
    authenticated_page.get_by_role("menuitem", name="Upload scorecard").click()

    authenticated_page.get_by_role("textbox", name="Course name").fill("sunshine coast")

    # Use absolute path for test image
    test_dir = Path(__file__).parent
    image_path = test_dir / "images" / "scorecard.jpg"

    # Upload the file - use element_handle to bypass Playwright's actionability checks
    # The input is hidden with class="hidden" which Playwright won't interact with normally
    element_handle = authenticated_page.query_selector("input[name='scorecard_image']")
    element_handle.set_input_files(str(image_path))

    authenticated_page.get_by_role("button", name="Upload").click()

    # Wait for the upload to process (the loading overlay should appear and disappear)
    # Or wait for navigation to the review page
    authenticated_page.wait_for_url("**/review", timeout=10000)

    # Verify the mock was called (Claude API was NOT called)
    assert mock_scorecard_parser.called, (
        "Claude API mock was not called - the upload may have failed"
    )
