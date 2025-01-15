import factory
from birdie_buddy.round_entry.factories.round_factory import RoundFactory
from birdie_buddy.round_entry.factories.shot_factory import ShotFactory
from birdie_buddy.round_entry.models import Hole
from birdie_buddy.users.factories import UserFactory
import random


class HoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hole

    user = factory.SubFactory(UserFactory)
    round = factory.SubFactory(RoundFactory)

    mental_scorecard = factory.LazyAttribute(lambda o: o.score)
    score = factory.Faker("random_int", min=2, max=6)
    par = factory.Faker("random_int", min=2, max=6)

    @classmethod
    def par_4_hole_in_one(cls) -> Hole:
        obj = cls(par=4)
        obj.shot_set.all().delete()
        create_par_4_hole_in_one(obj)
        HoleFactory._adjust_scores_based_on_shots(obj)
        return obj

    @classmethod
    def par_3_par(cls) -> Hole:
        obj = cls(par=3)
        obj.shot_set.all().delete()
        create_par_3_par(obj)
        HoleFactory._adjust_scores_based_on_shots(obj)
        return obj

    @classmethod
    def par_4_par(cls) -> Hole:
        obj = cls(par=4)
        obj.shot_set.all().delete()
        obj.refresh_from_db()
        create_par_4_par(obj)
        HoleFactory._adjust_scores_based_on_shots(obj)
        return obj

    @staticmethod
    def create_shots(obj, create, extracted, **kwargs):
        if not create:
            return

        # Random selection of realistic golf scenarios
        scenarios = {
            2: [create_par_3_birdie],
            3: [create_par_3_par, create_par_4_birdie],
            4: [
                create_par_3_bogey,
                create_par_4_par,
                create_par_5_birdie,
            ],
            5: [create_par_4_bogey, create_par_5_par],
            6: [create_par_5_bogey],
        }

        random.choice(scenarios[obj.par])(obj)
        HoleFactory._adjust_scores_based_on_shots(obj)

    @staticmethod
    def _adjust_scores_based_on_shots(obj):
        obj.score = obj.shot_set.count()
        obj.mental_scorecard = obj.score - random.choice([0, 1, 2])

        if obj.mental_scorecard < 0:
            obj.mental_scorecard = 1
        obj.save()


def create_par_3_par(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=170, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=20, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=1, lie="green")


def create_par_3_birdie(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=160, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=2, lie="green")


def create_par_3_bogey(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=180, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=40, lie="rough")
    ShotFactory(hole=hole, user=hole.user, start_distance=15, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=1, lie="green")


def create_par_4_par(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=400, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=130, lie="fairway")
    ShotFactory(hole=hole, user=hole.user, start_distance=15, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=1, lie="green")


def create_par_4_birdie(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=380, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=100, lie="fairway")
    ShotFactory(hole=hole, user=hole.user, start_distance=2, lie="green")


def create_par_4_hole_in_one(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=300, lie="tee")


def create_par_4_bogey(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=420, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=180, lie="rough")
    ShotFactory(hole=hole, user=hole.user, start_distance=40, lie="rough")
    ShotFactory(hole=hole, user=hole.user, start_distance=10, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=1, lie="green")


def create_par_5_par(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=520, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=250, lie="fairway")
    ShotFactory(hole=hole, user=hole.user, start_distance=100, lie="fairway")
    ShotFactory(hole=hole, user=hole.user, start_distance=15, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=1, lie="green")


def create_par_5_birdie(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=500, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=200, lie="fairway")
    ShotFactory(hole=hole, user=hole.user, start_distance=30, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=2, lie="green")


def create_par_5_bogey(hole):
    ShotFactory(hole=hole, user=hole.user, start_distance=540, lie="tee")
    ShotFactory(hole=hole, user=hole.user, start_distance=220, lie="rough")
    ShotFactory(hole=hole, user=hole.user, start_distance=160, lie="rough")
    ShotFactory(hole=hole, user=hole.user, start_distance=40, lie="fairway")
    ShotFactory(hole=hole, user=hole.user, start_distance=10, lie="green")
    ShotFactory(hole=hole, user=hole.user, start_distance=1, lie="green")
