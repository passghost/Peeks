import pygame
import random
import speech_recognition as sr
import threading
import time
import subprocess
import pystray
from PIL import Image
import ctypes
from ctypes import wintypes

# Initialize Pygame
pygame.init()

# Set up the display with the eye resolution and application icon
icon_image = pygame.image.load('Images/eyetest2.png')
pygame.display.set_icon(icon_image)
screen = pygame.display.set_mode((1000, 500))
pygame.display.set_caption("Peeks")

# Load images from the Images folder
eye_closed = pygame.image.load('Images/eyetest1.png')
eye_half_open = pygame.image.load('Images/eyetest2.png')
eye_open = pygame.image.load('Images/eyetest3.png')
animation_images = [
    pygame.image.load('Images/Down.png'),
    pygame.image.load('Images/Downleft.png'),
    pygame.image.load('Images/UpRight.png'),
    pygame.image.load('Images/DownRight.png')
]
boredom_images = [
    pygame.image.load('Images/eyetest3.png'),
    pygame.image.load('Images/eyetest5.png'),
    pygame.image.load('Images/eyetest3.png'),
    pygame.image.load('Images/eyetest5.png'),
    pygame.image.load('Images/eyetest6.png'),
    pygame.image.load('Images/eyetest7.png'),
    pygame.image.load('Images/eyetest8.png')
]

# Function to display an image
def display_image(image, hold=False):
    screen.blit(image, (0, 0))
    pygame.display.flip()
    if hold:
        pygame.time.wait(1000)  # Hold this frame longer

# Initialize the speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Global variables to track commands and states
firefox_commands = ["open mozilla", "load mozilla", "open firefox"]
running = True
load_firefox_detected = False
exit_detected = False
enhance_detected = False
last_boredom_time = time.time()
boredom_interval = random.randint(30, 60)
last_move_time = time.time()

def listen_for_commands():
    global load_firefox_detected, exit_detected, enhance_detected, running
    while running:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for commands...")
            try:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                text = recognizer.recognize_google(audio)
                print(f"Heard: {text}")  # Debug print
                if any(command in text.lower() for command in firefox_commands):
                    print("Detected 'firefox' command. Running animation.")
                    load_firefox_detected = True
                elif "exit" in text.lower():
                    print("Detected 'exit'. Closing program.")
                    exit_detected = True
                elif "enhance" in text.lower():
                    print("Detected 'enhance'. Maximizing window.")
                    enhance_detected = True
            except sr.UnknownValueError:
                print("Didn't catch that. Try again.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                pass

# System tray icon setup
def create_image():
    return Image.open("Images/eyetest2.png")

def on_exit(icon, item):
    global running
    running = False
    icon.stop()

icon = pystray.Icon("Peeks", create_image(), menu=pystray.Menu(
    pystray.MenuItem("Exit", on_exit)
))

# Start the system tray icon
icon_thread = threading.Thread(target=icon.run)
icon_thread.start()

# Function to maximize the current window
def maximize_window():
    user32 = ctypes.windll.user32
    user32.ShowWindow(user32.GetForegroundWindow(), 3)

# Function to move the window
def move_window():
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    direction = random.choice(['left', 'right', 'up', 'down'])
    if direction == 'left':
        user32.MoveWindow(hwnd, rect.left - 5, rect.top, rect.right - rect.left, rect.bottom - rect.top, True)
    elif direction == 'right':
        user32.MoveWindow(hwnd, rect.left + 5, rect.top, rect.right - rect.left, rect.bottom - rect.top, True)
    elif direction == 'up':
        user32.MoveWindow(hwnd, rect.left, rect.top - 5, rect.right - rect.left, rect.bottom - rect.top, True)
    elif direction == 'down':
        user32.MoveWindow(hwnd, rect.left, rect.top + 5, rect.right - rect.left, rect.bottom - rect.top, True)

def main():
    global running, load_firefox_detected, exit_detected, enhance_detected, last_boredom_time, boredom_interval, last_move_time
    listening_thread = threading.Thread(target=listen_for_commands)
    listening_thread.daemon = True
    listening_thread.start()
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()
        if current_time - last_boredom_time > boredom_interval:
            last_boredom_time = current_time
            boredom_interval = random.randint(30, 60)
            for image in boredom_images[:-1]:
                display_image(image)
                pygame.time.wait(250)  # Adjust delay for animation speed
            display_image(boredom_images[-1], hold=True)
            continue

        if exit_detected:
            running = False

        if load_firefox_detected:
            start_time = time.time()
            while time.time() - start_time < 5:
                for image in animation_images:
                    display_image(image)
                    pygame.time.wait(250)  # Adjust delay for animation speed
            load_firefox_detected = False  # Reset after animation
            subprocess.Popen([r'C:\Program Files\Mozilla Firefox\firefox.exe'])

        if enhance_detected:
            maximize_window()
            enhance_detected = False

        if current_time - last_move_time > 10:
            move_window()
            last_move_time = current_time

        else:
            display_image(eye_open)
            pygame.time.wait(random.randint(2000, 5000))  # Keep eyes open for 2-5 seconds

            display_image(eye_half_open)
            pygame.time.wait(100)

            display_image(eye_closed)
            pygame.time.wait(100)

            display_image(eye_half_open)
            pygame.time.wait(100)

    pygame.quit()
    icon.stop()

if __name__ == '__main__':
    main()
