import sys
import time
from neopixel import NeoPixel
from board import D18

# Konfiguration
# LED_PIN = board.D18  # GPIO-Pin für die LEDs
LED_PIN = D18  # GPIO-Pin für die LEDs
NUM_PIXELS = 24  # Anzahl der LEDs im Strip
BRIGHTNESS = 0.05  # Helligkeit (0.0 - 1.0)

# Farben als RGB-Tuples
COLORS = {
    "off": (0, 0, 0),
    "white": (255, 255, 255),
    "green": (12, 255, 28),
    "blue": (0, 0, 255),
    "red": (255, 0, 0),
}

# LED-Strip initialisieren
strip = NeoPixel(LED_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False)

def fade_led(start_color, end_color, steps=80, delay=0.04, easing=True):
    """ Übergang zwischen zwei Farben mit sanftem Fade-In/Out """
    start_r, start_g, start_b = COLORS[start_color]
    end_r, end_g, end_b = COLORS[end_color]

    for i in range(steps):
        factor = (i / steps) ** 2 if easing else i / steps  # Quadratische Steigerung für sanfteres Fade-In
        r = int(start_r + (end_r - start_r) * factor)
        g = int(start_g + (end_g - start_g) * factor)
        b = int(start_b + (end_b - start_b) * factor)
        strip.fill((r, g, b))
        strip.show()
        time.sleep(delay)

def set_led_color(color, blink=False, blink_times=5, blink_interval=0.5):
    """ Setzt die LED-Farbe und optional ein Blinkmuster mit sanftem Fade """
    if color not in COLORS:
        print(f"Unbekannte Farbe: {color}")
        return
    
    if blink:
        for _ in range(blink_times):
            fade_led("off", color, steps=80, delay=blink_interval / 60, easing=True)  # Sanftes Fade-In
            fade_led(color, "off", steps=80, delay=blink_interval / 60, easing=False)  # Normales Fade-Out
    else:
        strip.fill(COLORS[color])
        strip.show()


if __name__ == "__main__":
    try:
        # Test-Funktion
        print("LED-Test: Weiß")
        set_led_color("white")
        time.sleep(2)

        print("LED-Test: Grün")
        set_led_color("green")
        time.sleep(2)

        print("LED-Test: Rotes Blinken mit Fade")
        set_led_color("red", blink=True)
    finally:
        print("Sicherheitshalber alle LEDs ausschalten...")
        set_led_color("off")
        sys.exit()