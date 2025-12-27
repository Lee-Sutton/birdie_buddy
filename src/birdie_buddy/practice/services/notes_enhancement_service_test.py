from unittest.mock import Mock
from birdie_buddy.practice.services.notes_enhancement_service import (
    NotesEnhancementService,
)


class TestNotesEnhancementService:
    def test_enhance_notes_success(self):
        """Test successful note enhancement with mocked client."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.output_text = "Enhanced: Had an excellent practice session focusing on swing mechanics and tempo control."

        # Mock the OpenAI client
        mock_client = Mock()
        mock_client.responses.create.return_value = mock_response

        # Create service with injected mock client
        service = NotesEnhancementService(client=mock_client)

        # Test the enhancement
        original_notes = "Had a good practice session"
        result = service.enhance_notes(original_notes, "Full Swing")

        # Assertions
        assert (
            result
            == "Enhanced: Had an excellent practice session focusing on swing mechanics and tempo control."
        )
        mock_client.responses.create.assert_called_once()

        # Verify the API call parameters
        call_args = mock_client.responses.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert call_args[1]["instructions"] == "You are a helpful golf coach assistant."
        assert "full swing practice session" in call_args[1]["input"]
        assert original_notes in call_args[1]["input"]

    def test_enhance_notes_failure(self):
        """Test note enhancement failure with mocked client."""
        # Mock client that raises an exception
        mock_client = Mock()
        mock_client.responses.create.side_effect = Exception("API Error: 403 Forbidden")

        # Create service with injected mock client
        service = NotesEnhancementService(client=mock_client)

        # Test the enhancement with failure
        original_notes = "Test notes"
        result = service.enhance_notes(original_notes)

        # Should return original notes on error
        assert result == original_notes
        mock_client.responses.create.assert_called_once()

    def test_enhance_notes_empty_input(self):
        """Test that empty notes are returned unchanged."""
        service = NotesEnhancementService(client=Mock())

        result = service.enhance_notes("")
        assert result == ""

        result = service.enhance_notes("   ")
        assert result == "   "

