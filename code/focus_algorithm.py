# focus_algorithm.py
import sound_engine
import logger

log = logger.Logger()
previous_state = None

def assess_focus(focus_score, eeg_score, final_score):
    """
    Assess focus based on multiple inputs:
    - focus_score: from blink rate (1-10)
    - eeg_score: from EEG attention metrics (0-10)
    - final_score: combined/final score (0-10)
    
    Returns: category, final_score
    Also logs all scores and triggers sound based on focus state.
    """
    global previous_state

    # Determine focus category
    if final_score >= 8:
        category = "Highly Focused"
        if previous_state != "highly_focused":
            sound_engine.stop_sound()  # stop distractions
            previous_state = "highly_focused"
    elif final_score >= 5:
        category = "Focused"
        if previous_state != "focused_group":
            sound_engine.play_focused()
            previous_state = "focused_group"
    else:
        category = "Distracted"
        if previous_state != "distracted":
            sound_engine.play_distracted()
            previous_state = "distracted"

    # Log all scores
    log.log(focus_score, eeg_score, final_score, category)

    return category, final_score
