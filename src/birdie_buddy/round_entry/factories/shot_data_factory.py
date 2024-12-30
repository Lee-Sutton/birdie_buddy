from birdie_buddy.round_entry.models.enum import FAIRWAY, GREEN, TEE


class ShotDataFactory:
    @staticmethod
    def from_tee(distance):
        return {"distance": distance, "lie": TEE}

    @staticmethod
    def from_fairway(distance):
        return {"distance": distance, "lie": FAIRWAY}

    @staticmethod
    def from_green(distance):
        return {"distance": distance, "lie": GREEN}

    @staticmethod
    def par_5_birdie():
        return [
            ShotDataFactory.from_tee(500),
            ShotDataFactory.from_fairway(200),
            ShotDataFactory.from_tee(500),
            ShotDataFactory.from_tee(500),
        ]
