import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from birdie_buddy.practice.models import PracticeSession

User = get_user_model()


@pytest.mark.django_db
class TestPracticeSessionCreateView:
    def test_unauthenticated_user_redirected_to_login(self, client):
        url = reverse("practice:create_session")
        response = client.get(url)
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_authenticated_user_can_access_form(self, authenticated_client):
        url = reverse("practice:create_session")
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "practice/practice_session_form.html")
        assert "form" in response.context

    def test_can_create_practice_session(self, authenticated_client, user):
        url = reverse("practice:create_session")
        data = {
            "practice_type": "FS",
            "outcome": "3",
            "notes": "Great practice session today!",
        }

        response = authenticated_client.post(url, data)

        # Verify session was created
        assert PracticeSession.objects.count() == 1
        session = PracticeSession.objects.first()
        assert session is not None
        assert session.practice_type == "FS"
        assert session.outcome == 3
        assert session.notes == "Great practice session today!"
        assert session.user == user

        # Verify redirect
        assert response.status_code == 302
        assertRedirects(response, reverse("practice:practice_list"))

    def test_invalid_form_returns_errors(self, authenticated_client):
        url = reverse("practice:create_session")
        data = {
            "practice_type": "",  # Missing required field
            "outcome": "3",
            "notes": "Test notes",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        assert PracticeSession.objects.count() == 0
        assert "This field is required" in response.content.decode()

    def test_form_has_correct_fields(self, authenticated_client):
        url = reverse("practice:create_session")
        response = authenticated_client.get(url)
        form = response.context["form"]
        
        expected_fields = {"practice_type", "outcome", "notes"}
        actual_fields = set(form.fields.keys())
        assert actual_fields == expected_fields

    def test_practice_type_field_has_choices(self, authenticated_client):
        url = reverse("practice:create_session")
        response = authenticated_client.get(url)
        form = response.context["form"]
        
        practice_type_field = form.fields["practice_type"]
        choices = dict(practice_type_field.choices)
        expected_choices = {"FS": "Full Swing", "SG": "Short Game", "PT": "Putting"}
        assert choices == expected_choices

    def test_outcome_field_has_choices(self, authenticated_client):
        url = reverse("practice:create_session")
        response = authenticated_client.get(url)
        form = response.context["form"]
        
        outcome_field = form.fields["outcome"]
        choices = dict(outcome_field.choices)
        expected_choices = {1: "Poor", 2: "Average", 3: "Good", 4: "Excellent"}
        assert choices == expected_choices