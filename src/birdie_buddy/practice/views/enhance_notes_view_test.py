import json
import pytest
from unittest.mock import Mock, patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertTemplateUsed

User = get_user_model()


@pytest.mark.django_db
class TestEnhanceNotesView:
    def test_unauthenticated_user_cannot_access(self, client):
        """Test that unauthenticated users get 401 error."""
        url = reverse("practice:enhance_notes")
        response = client.post(
            url,
            data=json.dumps({"notes": "test notes"}),
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_empty_notes_return_error(self, authenticated_client):
        """Test that empty notes return validation error."""
        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url, data=json.dumps({"notes": ""}), content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "Notes cannot be empty" in data["error"]

    def test_whitespace_only_notes_return_error(self, authenticated_client):
        """Test that whitespace-only notes return validation error."""
        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url, data=json.dumps({"notes": "   "}), content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "Notes cannot be empty" in data["error"]

    @patch("birdie_buddy.practice.views.NotesEnhancementService")
    def test_successful_enhancement(self, mock_service_class, authenticated_client):
        """Test successful note enhancement."""
        mock_service = Mock()
        mock_service.enhance_notes.return_value = "Enhanced notes content"
        mock_service_class.return_value = mock_service

        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url,
            data=json.dumps({"notes": "original notes", "practice_type": "Full Swing"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["enhanced_notes"] == "Enhanced notes content"
        mock_service.enhance_notes.assert_called_once_with(
            "original notes", "Full Swing"
        )

    @patch("birdie_buddy.practice.views.NotesEnhancementService")
    def test_enhancement_service_failure(
        self, mock_service_class, authenticated_client
    ):
        """Test handling when enhancement service fails."""
        mock_service = Mock()
        mock_service.enhance_notes.return_value = None
        mock_service_class.return_value = mock_service

        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url,
            data=json.dumps({"notes": "test notes"}),
            content_type="application/json",
        )
        assert response.status_code == 500
        data = json.loads(response.content)
        assert "Failed to enhance notes" in data["error"]

    @patch("birdie_buddy.practice.views.NotesEnhancementService")
    def test_service_exception_handling(self, mock_service_class, authenticated_client):
        """Test handling of exceptions from enhancement service."""
        mock_service = Mock()
        mock_service.is_configured.return_value = True
        mock_service.enhance_notes.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service

        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url,
            data=json.dumps({"notes": "test notes"}),
            content_type="application/json",
        )
        assert response.status_code == 500
        data = json.loads(response.content)
        assert "An unexpected error occurred" in data["error"]

    def test_invalid_json_request(self, authenticated_client):
        """Test handling of invalid JSON in request."""
        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url, data="invalid json", content_type="application/json"
        )
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "Invalid request format" in data["error"]

    def test_missing_notes_in_request(self, authenticated_client):
        """Test handling when notes field is missing from request."""
        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url,
            data=json.dumps({"practice_type": "Full Swing"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "Notes cannot be empty" in data["error"]

    @patch("birdie_buddy.practice.views.NotesEnhancementService")
    def test_practice_type_optional(self, mock_service_class, authenticated_client):
        """Test that practice_type is optional and defaults to empty string."""
        mock_service = Mock()
        mock_service.is_configured.return_value = True
        mock_service.enhance_notes.return_value = "Enhanced notes"
        mock_service_class.return_value = mock_service

        url = reverse("practice:enhance_notes")
        response = authenticated_client.post(
            url,
            data=json.dumps({"notes": "test notes"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        mock_service.enhance_notes.assert_called_once_with("test notes", "")

