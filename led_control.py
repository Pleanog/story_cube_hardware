import sys
import time
import threading
import queue
from neopixel import NeoPixel
from board import D18

# GPIO-Pin für LEDs
LED_PIN = D18
NUM_PIXELS = 24
BRIGHTNESS = 1

# Farben definieren
COLORS = {
    "off": (0, 0, 0),
    "white": (255, 255, 255),
    "green": (12, 255, 28),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange-red": (255, 120, 0),
    "red": (255, 0, 0),
}

# LED-Strip initialisieren
strip = NeoPixel(LED_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

# Queue für LED-Befehle
led_queue = queue.Queue()
current_effect = None 
stop_event = threading.Event()

def led_worker():
    """Thread, der ständig auf neue LED-Befehle wartet"""
    global current_effect
    while True:  # Check if the script wants to stop
        try:
            color, mode, params = led_queue.get(timeout=1)  # Avoid blocking forever
        except queue.Empty:
            continue  # Loop again and check exit_event
      
        # Stoppt aktuelle Animation
        stop_event.set()
        if current_effect and current_effect.is_alive():
            current_effect.join()  # Warten, bis vorherige Animation stoppt
        stop_event.clear()

        if mode == "static":
            set_led(color)
        elif mode == "blink":
            current_effect = threading.Thread(target=blink_led, args=(color,), kwargs=params)
            current_effect.start()
        elif mode == "pulse":
            current_effect = threading.Thread(target=pulse_led, args=(color,), kwargs=params)
            current_effect.start()

def set_led(color):
    """Setzt eine statische LED-Farbe"""
    if color not in COLORS:
        print(f"Ungültige Farbe: {color}")
        return
    strip.fill(COLORS[color])
    strip.show()

def blink_led(color, repeat=5, blink_interval=0.3):
    """Blinkt die LEDs in einer bestimmten Farbe"""
    for _ in range(repeat):
        if stop_event.is_set():
            return  # Abbrechen, falls neuer Befehl kommt
        set_led(color)
        time.sleep(blink_interval)
        set_led("white")
        time.sleep(blink_interval)

def bezier_ease(t, p0=0, p1=0.25, p2=0.5, p3=1):
    """Cubic Bezier easing function."""
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

def pulse_led(color, repeat=5, delay=0.3):
    """Pulse LEDs in a certain color."""
    if color not in COLORS:
        print(f"Ungültige Farbe: {color}")
        return

    # Create nearly off color by dimming the color slightly
    dim_factor = 0.1
    nearly_off = tuple(max(0, min(255, int(COLORS[color][i] * dim_factor))) for i in range(3))

    for _ in range(repeat):
        if stop_event.is_set():
            return

        # Fade in and fade out using bezier easing
        fade_led(nearly_off, COLORS[color], steps=100, delay=delay / 60, easing=True)  # Fade-In
        fade_led(COLORS[color], nearly_off, steps=100, delay=delay / 60, easing=True)  # Fade-Out

    fade_led(nearly_off, (255, 255, 255), steps=100, delay=delay / 60, easing=True)  # Fade-In to White


def fade_led(start_color, end_color, steps=80, delay=0.04, easing=True):
    """Transition between two colors with a smooth fade-in/out."""
    start_r, start_g, start_b = start_color
    end_r, end_g, end_b = end_color

    for i in range(steps):
        factor = bezier_ease(i / steps) if easing else i / steps  # Apply bezier easing if needed

        # Calculate the RGB values based on the factor
        r = int(start_r + (end_r - start_r) * factor)
        g = int(start_g + (end_g - start_g) * factor)
        b = int(start_b + (end_b - start_b) * factor)

        # Clamp values to prevent overflow
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        strip.fill((r, g, b))
        strip.show()
        time.sleep(delay)


# def fade_led(color, steps=50, delay=0.04, repeat=3):
#     """Fade LEDs to nearly off and back to the original intensity, repeating `repeat` times."""
#     if color not in COLORS:
#         print(f"Ungültige Farbe: {color}")
#         return
    
#     target_r, target_g, target_b = COLORS[color]
#     dim_factor = 0.1  # Dim factor to get a color nearly off but not quite.
#     dim_r, dim_g, dim_b = int(target_r * dim_factor), int(target_g * dim_factor), int(target_b * dim_factor)

#     def clamp(value):
#         """Clamp the value between 0 and 255."""
#         return max(0, min(255, value))

#     for _ in range(repeat):
#         # Fade in and fade out (one loop for both directions)
#         for direction in [1, -1]:
#             for i in range(steps):
#                 if stop_event.is_set():
#                     return  # Cancel the fade
#                 factor = i / (steps - 1)
#                 eased_factor = ease_in_out(factor)  # Apply easing to the factor

#                 # Calculate current color intensity with eased factor
#                 current_r = int(target_r * (1 - eased_factor * direction) + dim_r * eased_factor * direction)
#                 current_g = int(target_g * (1 - eased_factor * direction) + dim_g * eased_factor * direction)
#                 current_b = int(target_b * (1 - eased_factor * direction) + dim_b * eased_factor * direction)

#                 # Clamp the color values to ensure they're within the valid range
#                 current_r = clamp(current_r)
#                 current_g = clamp(current_g)
#                 current_b = clamp(current_b)

#                 # Set the LED color
#                 strip.fill((current_r, current_g, current_b))
#                 strip.show()
#                 time.sleep(delay)

#     set_led("white")  # Ensure the final color is set




# def fade_led(color, steps=50, delay=0.04):
#     """Fadet die LEDs zu einer neuen Farbe"""
#     if color not in COLORS:
#         print(f"Ungültige Farbe: {color}")
#         return
#     target_r, target_g, target_b = COLORS[color]

#     for i in range(steps):
#         if stop_event.is_set():
#             return  # Abbrechen
#         factor = i / steps
#         strip.fill((int(target_r * factor), int(target_g * factor), int(target_b * factor)))
#         strip.show()
#         time.sleep(delay)
#     set_led(color)


# LED-Thread starten
led_thread = threading.Thread(target=led_worker, daemon=True)
led_thread.start()

def led_shutdown():
    """Stops the LED worker thread and turns off LEDs"""
    print("Stopping LED worker...")
    stop_event.set() 
    led_queue.queue.clear()
    set_led("off")


def set_led_color(color, mode="static", **kwargs):
    """Schiebt einen neuen LED-Befehl in die Queue"""
    if color not in COLORS:
        print(f"Ungültige Farbe: {color}")
        return
    elif mode not in ["static", "blink", "pulse", "fade"]:
        print(f"Ungültiger Modus: {mode}")
        return
    else :
        print(f"Set LED color: {color}, mode: {mode}, kwargs: {kwargs}")
    led_queue.put((color, mode, kwargs))

if __name__ == "__main__":
    try:
        while True:
            # print("Setting blue for 3 sek color...")
            # set_led_color("blue", mode="static")
            # time.sleep(3)

            print("Fading green 5 times in and out with default delay ...")
            set_led_color("green", mode="pulse", repeat=5)
            time.sleep(10)
            set_led_color("white", mode="static")
            time.sleep(1)

            print("Fading red 10 times in and out with faster delay 0.01 ...")
            set_led_color("red", mode="pulse", repeat=10, delay=0.01)
            time.sleep(10)
            set_led_color("white", mode="static")
            time.sleep(1)

            print("Blinking blue 5 times with default interval 0.3 ...")
            set_led_color("blue", mode="blink", repeat=5)
            time.sleep(5)
            set_led_color("white", mode="static")
            time.sleep(5)
            print("--------------\n")
    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        led_shutdown()