from .strokes_gained_data import SG_DATA


def avg_strokes_to_holeout(distance, lie):
    # Map penalty to recovery since SG_DATA doesn't have penalty-specific data
    if lie == "penalty":
        lie = "recovery"

    result = SG_DATA[lie][distance]
    return result
