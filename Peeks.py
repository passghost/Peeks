import pygame
import pygame_gui
import random
import time
from PIL import Image
import speech_recognition as sr
import threading
import subprocess
import pystray
import ctypes
from ctypes import wintypes

# Initialize Pygame and pygame_gui
pygame.init()

# Load the images as Pillow images for easier hue manipulation
eye_closed = Image.open('Images/eyetest1.png')
eye_half_open = Image.open('Images/eyetest2.png')
eye_open = Image.open('Images/eyetest3.png')

# Convert the Pillow image to Pygame format
def pil_to_pygame(image):
    return pygame.image.frombuffer(image.tobytes(), image.size, image.mode).convert_alpha()

# Use image dimensions to set the display mode
image_width, image_height = eye_open.size
screen = pygame.display.set_mode((image_width, image_height))
pygame.display.set_caption("Peeks")

# Convert images to Pygame after display mode is set
eye_closed_pygame = pil_to_pygame(eye_closed)
eye_half_open_pygame = pil_to_pygame(eye_half_open)
eye_open_pygame = pil_to_pygame(eye_open)

# Set the icon
icon_image = pygame.image.load('Images/eyetest2.png').convert_alpha()
pygame.display.set_icon(icon_image)

# Create a UI manager
manager = pygame_gui.UIManager((image_width, image_height))

# Create a label for the hue slider
hue_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 10), (50, 20)),
    text="Hue",
    manager=manager
)

# Create a smaller horizontal hue slider
hue_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((70, 10), (200, 20)),  
    start_value=1.0,
    value_range=(0.0, 2.0),  # 0.0 - 2.0 for color enhancement factor
    manager=manager
)

# Function to adjust the hue using ImageEnhance
def adjust_hue(image, hue_shift):
    # Convert image to HSV
    hsv_image = image.convert('HSV')
    h, s, v = hsv_image.split()

    # Adjust the hue
    h = h.point(lambda p: (p + int(hue_shift * 255)) % 256)

    # Recombine back into an image
    adjusted_image = Image.merge('HSV', (h, s, v)).convert('RGB')
    return adjusted_image

# Function to display an image with optional hue adjustment
def display_image(image, hue_shift, hold=False):
    adjusted_image = adjust_hue(image, hue_shift)
    pygame_image = pil_to_pygame(adjusted_image)
    
    screen.fill((50, 50, 50))  # Background color
    screen.blit(pygame_image, (0, 0))  # Blit at (0,0) since window is scaled to the image size
    manager.draw_ui(screen)  # Draw UI on top of the image
    pygame.display.flip()
    if hold:
        pygame.time.wait(1000)  # Hold the frame longer if needed

# Function to run the blinking animation (eye_closed -> eye_half_open -> eye_open)
def run_blinking_animation(hue_shift):
    display_image(eye_closed, hue_shift)
    pygame.time.wait(150)  # Closed for 150ms
    display_image(eye_half_open, hue_shift)
    pygame.time.wait(150)  # Half-open for 150ms
    display_image(eye_open, hue_shift)
    pygame.time.wait(2000)  # Open for 2 seconds before next blink

# Initialize the speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Global variables to track commands and states
firefox_commands = ["open mozilla", "load mozilla", "open firefox"]
running = True
load_firefox_detected = False
exit_detected = False
enhance_detected = False

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

def main():
    global running, load_firefox_detected, exit_detected, enhance_detected
    listening_thread = threading.Thread(target=listen_for_commands)
    listening_thread.daemon = True
    listening_thread.start()
    clock = pygame.time.Clock()

    blink_interval = random.randint(3, 6)  # Randomize blink interval between 3 to 6 seconds
    last_blink_time = time.time()

    while running:
        time_delta = clock.tick(60) / 1000.0  # 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

        current_time = time.time()

        # Run the blinking animation if enough time has passed since the last blink
        if current_time - last_blink_time > blink_interval:
            run_blinking_animation(hue_slider.get_current_value())
            last_blink_time = current_time
            blink_interval = random.randint(3, 6)  # Reset interval for next blink

        if load_firefox_detected:
            subprocess.Popen([r'C:\Program Files\Mozilla Firefox\firefox.exe'])
            load_firefox_detected = False

        if exit_detected:
            running = False

        if enhance_detected:
            maximize_window()
            enhance_detected = False

        display_image(eye_open, hue_slider.get_current_value())
        manager.update(time_delta)
        manager.draw_ui(screen)

    pygame.quit()
    icon.stop()

if __name__ == '__main__':
    main()
