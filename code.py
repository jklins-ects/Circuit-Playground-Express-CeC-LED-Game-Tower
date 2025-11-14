from adafruit_circuitplayground import cp
import board
import digitalio
import time
import neopixel

PIXEL_PIN = board.A1      # Data pin connected to the strip
NUM_PIXELS = 17          # Number of LEDs on your strip
SPEED = .05
pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=0.3,  # <- full brightness is 1, which is insanely bright and unnecessary
    auto_write=False,
    # <- difference from RGB strips (RGB uses 3 / no bpp needed)
    bpp=4,
    pixel_order=neopixel.GRBW    # <- tells CircuitPython what order the colors are in
)

button = digitalio.DigitalInOut(board.A3)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
running = False
current_pixel = 0


def wipe(max_pixel=NUM_PIXELS-1, color=(0, 255, 0, 0), delay=SPEED, blink_delay=.5, sound="correct.wav"):
    global running, current_pixel, direction
    pixels.fill((0, 0, 0, 0))
    pixels[max_pixel] = color
    pixels.show()
    cp.play_file(sound)
    for i in range(max_pixel):
        pixels[i] = color          # Set the current pixel
        pixels.show()              # Update the strip
        time.sleep(delay)
    while True:
        pixels.fill((0, 0, 0, 0))
        pixels[max_pixel] = color
        pixels.show()
        time.sleep(blink_delay)
        for i in range(max_pixel):
            pixels[i] = color          # Set the current pixel
            # Small delay between each pixel
        pixels.show()
        time.sleep(blink_delay)
        if (not button.value) or cp.button_b:
            pixels.fill((0, 0, 0, 0))
            current_pixel = 0
            direction = 1
            while (not button.value) or cp.button_b:
                continue  # wait til button up
            return


def ending_routine():
    if current_pixel == NUM_PIXELS - 1:
        wipe()
    else:
        wipe(current_pixel, (255, 0, 0, 0), sound="wrong.wav")


direction = 1
while True:
    if (not button.value) or cp.button_b:  # button pressed (because it went LOW)
        while (not button.value) or cp.button_b:
            time.sleep(.01)
            continue  # wait til button up
        ending_routine()
    else:
        pixels[current_pixel] = (0, 0, 0, 0)
        current_pixel += direction
        if current_pixel == NUM_PIXELS - 1 or current_pixel == 0:
            direction *= -1
        pixels[current_pixel] = (0, 0, 0, 255)
        pixels.show()

        time.sleep(SPEED)
