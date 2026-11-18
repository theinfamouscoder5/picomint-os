# PicoMint OS for Raspberry Pi Pico 2W

# Imports
from machine import Pin, SoftI2C
from oled import OLED
from ui import Button, ButtonStack
from apps import registry
from system import pet_scene, wifi
import keypad
import gc
import network
import time

# Config
SDA_PIN = 22
SCL_PIN = 21
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
Y_OFFSET = 4 # temporary due to dead pixels on the OLED

# Screen
i2c = SoftI2C(scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
oled = OLED(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, y_offset=Y_OFFSET)

# Boot
def boot_step(step, total_steps, status, task=None, min_ms=250):
    start = time.ticks_ms()
    spinner = ("|", "/", "-", "\\")
    
    oled.fill(0)
    oled.text("PicoMint OS", 0, 0)
    oled.text(spinner[step % 4], oled.width - 8, 0)
    oled.hline(0, 10, oled.width, 1)
    oled.text(f"RP2350 520KB\n{status}", 0, 16)
    
    oled.progress_bar((step + 1) / total_steps)
    oled.show()
    
    result = task() if task else None
    elapsed = time.ticks_diff(time.ticks_ms(), start)
    if elapsed < min_ms:
        time.sleep_ms(min_ms - elapsed)
    return result

boot_step(0, 4, "GC COLLECT...", gc.collect)
devices = boot_step(1, 4, "I2C SCAN...", i2c.scan)

wlan = network.WLAN(network.STA_IF)
boot_step(2, 4, "WLAN INIT...", lambda: wlan.active(True))
boot_step(3, 4, f"I2C:{len(devices)} WLAN:OK", min_ms=800)

# Main OS
state = "PET"
tick = 0
last_frame = 0

def launch_app(name, run_fn):
    if run_fn:
        run_fn(oled)
    else:
        oled.fill(0)
        oled.center_screen(f"{name}\nComing Soon\n[ESC] Back")
        oled.show()
        while True:
            k = keypad.get_key()
            if k and k.lower() == "esc":
                break
            time.sleep_ms(20)
    draw_menu()

def open_apps():
    global active_menu, menu_title
    active_menu = apps_menu
    menu_title = "Apps"
    draw_menu()

def open_wifi():
    wifi.run(oled)
    draw_menu()

home_menu = ButtonStack([
    Button("Apps", 0, 0, on_click=open_apps),
    Button("Wi-Fi", 0, 0, on_click=open_wifi),
    Button("Settings", 0, 0, on_click=lambda: print("Settings")),
    Button("System Info", 0, 0, on_click=lambda: print("System Info")),
], x=0, y=14, spacing=3)

apps_menu = ButtonStack([
    Button(name, 0, 0, on_click=lambda n=name, fn=fn: launch_app(n, fn))
    for name, fn in apps.APPS
], x=0, y=14, spacing=3)

active_menu = home_menu
menu_title = "Home Menu"

def draw_menu():
    oled.fill(0)
    oled.text(menu_title, 0, 0)
    oled.hline(0, 10, oled.width, 1)
    active_menu.draw(oled)
    oled.show()

state = "PET"
tick = 0
last_frame = 0

while True:
    key = keypad.get_key()
    if key:
        key = key.lower()

    if state == "PET":
        if key:
            state = "MENU"
            active_menu = home_menu
            menu_title = "Home Menu"
            draw_menu()
        elif time.ticks_diff(time.ticks_ms(), last_frame) >= int(pet_scene.FRAME_DELAY * 1000):
            pet_scene.draw_frame(oled, tick)
            oled.show()
            tick += 1
            last_frame = time.ticks_ms()

    elif state == "MENU":
        if key == "esc":
            if active_menu is apps_menu:
                active_menu = home_menu
                menu_title = "Home Menu"
                draw_menu()
            else:
                state = "PET"
                last_frame = 0
        elif key in ("w", "up"):
            active_menu.move(-1)
            draw_menu()
        elif key in ("s", "down"):
            active_menu.move(1)
            draw_menu()
        elif key in ("enter", "ok", " "):
            active_menu.press_selected()

    time.sleep_ms(10)
