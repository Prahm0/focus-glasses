# This script uses the bpm values from the focus algorithm to determine if the user is focused.

def assess_focus (blink_rate):
    """
    Assess focus based on the bpm value.
    Returns True if focused, False otherwise.
    """
    if blink_rate < 5:
        return "Highly Focused."
    elif blink_rate < 10:
        return "Focused."
    elif 10 <= blink_rate < 20:
        return "Moderately focused."
    else: 
        return "Distracted."