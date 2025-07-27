import pygame
import time

pygame.mixer.init()
current_sound = None
last_distracted_played = 0

# Load the buzzer sound seperately using Sound (not music)
buzzer = pygame.mixer.Sound("sounds/buzzer.wav")
buzzer.set_volume(1.0)

def play_sound(path):
    global current_sound
    if current_sound != path:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1) # Loop background music
        current_sound = path
        

def stop_sound():
    global current_sound
    pygame.mixer.music.fadeout(500)
    current_sound = None

def play_focused():
    play_sound("sounds/bb.mp3")

def play_distracted():
    global last_distracted_played
    current_time = time.time()

    if current_time - last_distracted_played > 3:
        # Dont interrupt background music and just play buzzer over it
        buzzer.play() # Play once
        last_distracted_played = current_time
