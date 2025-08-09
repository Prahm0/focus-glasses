# This script uses the bpm values from the focus algorithm to determine if the user is focused.
import sound_engine
import logger

log = logger.Logger()

previous_state = None

def assess_focus(blink_rate):
    global previous_state
    if blink_rate < 5:
        if previous_state != "highly_focused":
            sound_engine.stop_sound()
            previous_state = "highly_focused"
        log.log(blink_rate, previous_state)
        return "Highly Focused."
    
    elif blink_rate < 20:
        if previous_state != "focused_group":
            sound_engine.play_focused()
            previous_state = "focused_group"
        if blink_rate < 10:
            log.log(blink_rate, previous_state)
            return "Focused." 
        else: 
            log.log(blink_rate, previous_state)
            return "Moderately focused."

    else:
        if previous_state != "distracted":
            sound_engine.play_distracted()
            previous_state = "distracted"
        log.log(blink_rate, previous_state)
        return "Distracted."
