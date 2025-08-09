import sound_engine
import logger

log = logger.Logger()

previous_state = None

# Function to convert blink rate to focus score
def focus_score_from_blink_rate(blink_rate):
    """
    Converts blink rate to a focus score from 1 (worst) to 10 (best),
    with a smooth gradation.
    """
    blink_rate = max(0, blink_rate)  # Clamp negative values to 0

    if blink_rate <= 3:
        score = 10
    elif blink_rate <= 5:
        score = 9
    elif blink_rate <= 7:
        score = 8
    elif blink_rate <= 9:
        score = 7
    elif blink_rate <= 12:
        score = 6
    elif blink_rate <= 15:
        score = 5
    elif blink_rate <= 18:
        score = 4
    elif blink_rate <= 22:
        score = 3
    elif blink_rate <= 27:
        score = 2
    else:
        score = 1

    return score

# Function to assess focus based on blink rate
def assess_focus(blink_rate):
    global previous_state

    focus_score = focus_score_from_blink_rate(blink_rate)

    if blink_rate < 5:
        if previous_state != "highly_focused":
            sound_engine.stop_sound()
            previous_state = "highly_focused"
        log.log(blink_rate, focus_score, "Highly Focused")
        return "Highly Focused.", focus_score
    
    elif blink_rate < 20:
        if previous_state != "focused_group":
            sound_engine.play_focused()
            previous_state = "focused_group"
        if blink_rate < 10:
            log.log(blink_rate, focus_score, "Focused")
            return "Focused.", focus_score
        else: 
            log.log(blink_rate, focus_score, "Moderately Focused")
            return "Moderately Focused.", focus_score

    else:
        if previous_state != "distracted":
            sound_engine.play_distracted()
            previous_state = "distracted"
        log.log(blink_rate, focus_score, "Distracted")
        return "Distracted.", focus_score
