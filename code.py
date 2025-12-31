import board
import digitalio
import time
import neopixel
import busio

# -------------------------
# HARDWARE CONFIG
# -------------------------

PIXEL_PIN = board.GP0

NUM_PIXELS = 17          # physical LEDs
FIRST_LED = 1            # LED 0 is physically hidden
LAST_LED = 16
LOGICAL_LEDS = 16        # usable LEDs

MIN_LEVEL = 1
MAX_LEVEL = LOGICAL_LEDS
DEFAULT_LEVEL = 10       # medium speed

start_button = digitalio.DigitalInOut(board.GP3)
start_button.direction = digitalio.Direction.INPUT
start_button.pull = digitalio.Pull.UP

speed_button = digitalio.DigitalInOut(board.GP29)
speed_button.direction = digitalio.Direction.INPUT
speed_button.pull = digitalio.Pull.UP

pixels = neopixel.NeoPixel(
    PIXEL_PIN,
    NUM_PIXELS,
    brightness=0.3,
    auto_write=False,
    bpp=4,
    pixel_order=neopixel.GRBW
)

# -------------------------
# DFPLAYER SETUP
# -------------------------

uart = busio.UART(board.GP4, board.GP5, baudrate=9600, timeout=0.1)


def df_send(cmd, high=0x00, low=0x00):
    data = [0x7E, 0xFF, 0x06, cmd, 0x00, high, low]
    checksum = 0xFFFF - (sum(data[1:]) & 0xFFFF) + 1
    frame = bytes(data + [(checksum >> 8) & 0xFF, checksum & 0xFF, 0xEF])
    uart.write(frame)


def df_set_volume(level):
    df_send(0x06, 0x00, max(0, min(30, level)))


def df_play_track(track):
    df_send(0x03, (track >> 8) & 0xFF, track & 0xFF)


def prime_dfplayer_once():
    df_set_volume(80)
    time.sleep(1)
    df_play_track(1)
    time.sleep(0.2)
    df_play_track(1)

# -------------------------
# SPEED HANDLING
# -------------------------


def level_to_delay(level):
    slow = 0.12
    med = 0.05
    fast = 0.02

    if level <= 10:
        t = (level - 1) / 9
        return slow + t * (med - slow)
    else:
        t = (level - 10) / 6
        return med + t * (fast - med)


def show_speed_level(level):
    pixels.fill((0, 0, 0, 0))
    for i in range(FIRST_LED, FIRST_LED + level):
        pixels[i] = (0, 0, 255, 0)
    pixels.show()


def pressed(btn):
    return not btn.value


def wait_release(btn):
    while pressed(btn):
        time.sleep(0.02)


def speed_selection_loop(level):
    show_speed_level(level)
    while True:
        if pressed(speed_button):
            wait_release(speed_button)
            level += 1
            if level > MAX_LEVEL:
                level = MIN_LEVEL
            show_speed_level(level)

        if pressed(start_button):
            wait_release(start_button)
            return level

        time.sleep(0.01)

# -------------------------
# GAME LOGIC
# -------------------------


current_pixel = FIRST_LED
direction = 1
running = False


def wipe(max_pixel=LAST_LED, color=(0, 255, 0, 0), delay=0.05):
    global current_pixel, direction

    pixels.fill((0, 0, 0, 0))
    for i in range(FIRST_LED, max_pixel + 1):
        pixels[i] = color
        pixels.show()
        time.sleep(delay)

    while True:
        pixels.fill((0, 0, 0, 0))
        pixels[max_pixel] = color
        pixels.show()
        time.sleep(0.4)

        for i in range(FIRST_LED, max_pixel):
            pixels[i] = color
        pixels.show()
        time.sleep(0.4)

        if pressed(start_button):
            wait_release(start_button)
            current_pixel = FIRST_LED
            direction = 1
            pixels.fill((0, 0, 0, 0))
            pixels.show()
            return


def ending_routine(delay):
    global running
    running = False

    if current_pixel == LAST_LED:
        df_play_track(2)
        wipe(delay=delay)
    else:
        df_play_track(3)
        wipe(current_pixel, (255, 0, 0, 0), delay)


def play_round(delay):
    global current_pixel, direction, running

    df_play_track(1)
    running = True
    current_pixel = FIRST_LED
    direction = 1

    pixels.fill((0, 0, 0, 0))
    pixels[current_pixel] = (0, 0, 0, 255)
    pixels.show()

    while True:
        if pressed(start_button):
            wait_release(start_button)
            ending_routine(delay)
            return

        pixels[current_pixel] = (0, 0, 0, 0)
        current_pixel += direction

        if current_pixel == LAST_LED or current_pixel == FIRST_LED:
            direction *= -1

        pixels[current_pixel] = (0, 0, 0, 255)
        pixels.show()
        time.sleep(delay)

# -------------------------
# MAIN FLOW
# -------------------------


speed_level = DEFAULT_LEVEL
df_ready = False

while True:
    speed_level = speed_selection_loop(speed_level)
    delay = level_to_delay(speed_level)

    if not df_ready:
        prime_dfplayer_once()
        df_ready = True

    play_round(delay)
