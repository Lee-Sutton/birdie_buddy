import factory
from django.utils import timezone
from birdie_buddy.round_entry.models import Shot
from birdie_buddy.users.factories import UserFactory


class ShotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shot
        skip_postgeneration_save = True

    created_at = factory.LazyFunction(timezone.now)
    user = factory.SubFactory(UserFactory)
    hole = factory.SubFactory(
        "birdie_buddy.round_entry.factories.hole_factory.HoleFactory"
    )
    start_distance = factory.Faker("random_int", min=1, max=600)
    lie = factory.Faker(
        "random_element", elements=[choice[0] for choice in Shot.LIE_CHOICES]
    )

    @factory.post_generation
    def calculate_sg(self, create, extracted, **kwargs):
        if not create:
            return
        try:
            next_shot = self.get_next_shot()
            self.calculate_strokes_gained(next_shot)
        except KeyError:
            self.strokes_gained = 0
        self.save()
