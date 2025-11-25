import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from birdie_buddy.practice.models import PracticeSession

User = get_user_model()


@pytest.fixture
def practice_session(user):
    return PracticeSession.objects.create(
        user=user,
        practice_type="FS",
        outcome=3,
        notes="Great practice session today!",
    )


@pytest.mark.django_db
class TestPracticeSessionDetailView:
    def test_unauthenticated_user_redirected_to_login(self, client, practice_session):
        url = reverse("practice:session_detail", kwargs={"id": practice_session.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_authenticated_user_can_view_session(
        self, authenticated_client, practice_session
    ):
        url = reverse("practice:session_detail", kwargs={"id": practice_session.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "practice/practice_session_detail.html")
        assert response.context["session"] == practice_session

    def test_cannot_view_other_users_session(self, authenticated_client):
        other_user = User.objects.create_user(username="other", password="pass123")
        other_session = PracticeSession.objects.create(
            user=other_user,
            practice_type="PT",
            outcome=2,
            notes="Other user's session",
        )

        url = reverse("practice:session_detail", kwargs={"id": other_session.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 404

    def test_detail_displays_correct_information(
        self, authenticated_client, practice_session
    ):
        url = reverse("practice:session_detail", kwargs={"id": practice_session.pk})
        response = authenticated_client.get(url)
        content = response.content.decode()

        assert "Full Swing" in content
        assert "Good" in content
        assert "Great practice session today!" in content


@pytest.mark.django_db
class TestPracticeSessionEditView:
    def test_unauthenticated_user_redirected_to_login(self, client, practice_session):
        url = reverse("practice:edit_session", kwargs={"id": practice_session.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_authenticated_user_can_access_edit_form(
        self, authenticated_client, practice_session
    ):
        url = reverse("practice:edit_session", kwargs={"id": practice_session.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, "practice/practice_session_form.html")
        assert "form" in response.context
        assert response.context["session"] == practice_session

    def test_can_edit_practice_session(
        self, authenticated_client, user, practice_session
    ):
        url = reverse("practice:edit_session", kwargs={"id": practice_session.pk})
        data = {
            "practice_type": "PT",
            "outcome": "4",
            "notes": "Updated notes!",
        }

        response = authenticated_client.post(url, data)

        # Refresh from database
        practice_session.refresh_from_db()
        assert practice_session.practice_type == "PT"
        assert practice_session.outcome == 4
        assert practice_session.notes == "Updated notes!"

        # Verify redirect
        assert response.status_code == 302
        assertRedirects(
            response, reverse("practice:session_detail", kwargs={"id": practice_session.pk})
        )

    def test_invalid_form_returns_errors(
        self, authenticated_client, practice_session
    ):
        url = reverse("practice:edit_session", kwargs={"id": practice_session.pk})
        data = {
            "practice_type": "",  # Missing required field
            "outcome": "3",
            "notes": "Test notes",
        }

        response = authenticated_client.post(url, data)

        assert response.status_code == 200
        # Session should not be updated
        practice_session.refresh_from_db()
        assert practice_session.practice_type == "FS"
        assert "This field is required" in response.content.decode()

    def test_cannot_edit_other_users_session(self, authenticated_client):
        other_user = User.objects.create_user(username="other", password="pass123")
        other_session = PracticeSession.objects.create(
            user=other_user,
            practice_type="PT",
            outcome=2,
            notes="Other user's session",
        )

        url = reverse("practice:edit_session", kwargs={"id": other_session.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 404

    def test_edit_form_has_initial_values(
        self, authenticated_client, practice_session
    ):
        url = reverse("practice:edit_session", kwargs={"id": practice_session.pk})
        response = authenticated_client.get(url)
        form = response.context["form"]

        assert form.initial["practice_type"] == "FS"
        assert form.initial["outcome"] == 3
        assert form.initial["notes"] == "Great practice session today!"


@pytest.mark.django_db
class TestPracticeSessionDeleteView:
    def test_unauthenticated_user_redirected_to_login(self, client, practice_session):
        url = reverse("practice:delete_session", kwargs={"id": practice_session.pk})
        response = client.post(url)
        assert response.status_code == 302
        assert "/users/login/" in response.url

    def test_can_delete_practice_session(
        self, authenticated_client, practice_session
    ):
        url = reverse("practice:delete_session", kwargs={"id": practice_session.pk})
        
        # Verify session exists
        assert PracticeSession.objects.filter(pk=practice_session.pk).exists()
        
        response = authenticated_client.post(url)
        
        # Verify session was deleted
        assert not PracticeSession.objects.filter(pk=practice_session.pk).exists()
        
        # Verify redirect
        assert response.status_code == 302
        assertRedirects(response, reverse("practice:practice_list"))

    def test_cannot_delete_other_users_session(self, authenticated_client):
        other_user = User.objects.create_user(username="other", password="pass123")
        other_session = PracticeSession.objects.create(
            user=other_user,
            practice_type="PT",
            outcome=2,
            notes="Other user's session",
        )

        url = reverse("practice:delete_session", kwargs={"id": other_session.pk})
        response = authenticated_client.post(url)
        
        # Should get 404
        assert response.status_code == 404
        
        # Session should still exist
        assert PracticeSession.objects.filter(pk=other_session.pk).exists()

    def test_delete_only_accepts_post(self, authenticated_client, practice_session):
        url = reverse("practice:delete_session", kwargs={"id": practice_session.pk})
        
        # GET request should not delete
        response = authenticated_client.get(url)
        assert response.status_code == 405  # Method not allowed
        
        # Session should still exist
        assert PracticeSession.objects.filter(pk=practice_session.pk).exists()