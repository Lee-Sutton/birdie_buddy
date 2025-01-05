import factory
from django.utils import timezone
from birdie_buddy.round_entry.models import Shot
from birdie_buddy.users.factories import UserFactory


class ShotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shot

    created_at = factory.LazyFunction(timezone.now)
    user = factory.SubFactory(UserFactory)
    hole = factory.SubFactory(
        "birdie_buddy.round_entry.factories.hole_factory.HoleFactory"
    )
    start_distance = factory.Faker("random_int", min=1, max=1000)
    lie = factory.Faker(
        "random_element", elements=[choice[0] for choice in Shot.LIE_CHOICES]
    )
