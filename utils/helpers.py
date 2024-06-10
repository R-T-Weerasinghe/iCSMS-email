# System-wide helper functions and configurations
import math
from datetime import datetime, date

def scale_score(score: float, *, scale_type: str="linear", precision: int=3) -> float:
    """
    Scales the given score based on the specified scale type.
    
    Parameters:
        score (float): The score to be scaled.
        scale_type (str, optional): The type of scaling to be applied. 
            Valid options are "linear", "standard", "aggressive", and "weak".
            Defaults to "linear".
        precision (int): Number of decimal places in score
    Returns:
        float: The scaled score.
    
    Raises:
        ValueError: If an invalid scale type is provided.
    """
    if scale_type == "linear":
        return score
    
    if scale_type == "standard":
        a = 2
        b = 10
        c = 1.23
        d = -1.7
    elif scale_type == "aggressive":
        a = 1.1
        b = 0.5
        c = 1.03
        d = 1
    elif scale_type == "weak":
        a = 4
        b = 10
        c = 1.95
        d = -4.9
    else:
        raise ValueError("Invalid scale type")
    
    scaled_score = a * math.log10(b * (score + c)) + d

    if scaled_score < -1:
        return -1
    if scaled_score > 1:
        return 1

    rounded_scaled_score = round(scale_score, precision) # type: ignore
    return rounded_scaled_score


def date_to_datetime(value):
    """
    Converts a date object to a datetime object. If the object is not a date object, it is returned as is.

    Args:
        value (date | other): The object to convert.

    Returns:
        datetime | other: The converted datetime object or object returned as is.

    """
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time())
    return value
