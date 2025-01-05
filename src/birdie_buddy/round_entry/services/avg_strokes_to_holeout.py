from .strokes_gained_data import SG_DATA


def avg_strokes_to_holeout(distance, lie):
    result = SG_DATA[lie][distance]
    return result
